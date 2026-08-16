#!/usr/bin/env python3
"""Shrink generated media in place and keep log.jsonl pointing at the right files."""
import argparse
import json
import os
import shutil
import subprocess
import sys

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")
VIDEO_EXT = (".mp4", ".webm", ".mov")


def kb(path):
    return os.path.getsize(path) / 1024


def probe(path, *fields):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=" + ",".join(fields), "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True,
    )
    return out.stdout.split()


def shrink_image(path, max_edge, quality, raw_dir):
    from PIL import Image

    im = Image.open(path)
    w, h = im.size
    dest = os.path.splitext(path)[0] + ".webp"
    if path.lower().endswith(".webp") and max(w, h) <= max_edge:
        return None
    im = im.convert("RGB")
    if max(w, h) > max_edge:
        s = max_edge / max(w, h)
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    before = kb(path)
    tmp = dest + ".tmp.webp"
    im.save(tmp, "WEBP", quality=quality, method=6)
    stash(path, raw_dir)
    os.replace(tmp, dest)
    return before, kb(dest), dest


def shrink_video(path, max_width, crf, raw_dir):
    dims = probe(path, "width", "height")
    width = int(dims[0]) if dims else 0
    rate = probe(path, "bit_rate")
    bitrate = int(rate[0]) if rate and rate[0].isdigit() else 0
    if width and width <= max_width and 0 < bitrate < 1_500_000:
        return None
    before = kb(path)
    tmp = path + ".tmp.mp4"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", path,
         "-vf", f"scale='min({max_width},iw)':-2",
         "-c:v", "libx264", "-crf", str(crf), "-preset", "slow",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "96k", tmp],
        check=True,
    )
    stash(path, raw_dir)
    os.replace(tmp, path)
    return before, kb(path), path


def stash(path, raw_dir):
    """Keep the untouched original, or drop it."""
    if raw_dir:
        os.makedirs(raw_dir, exist_ok=True)
        shutil.move(path, os.path.join(raw_dir, os.path.basename(path)))
    else:
        os.remove(path)


def relog(log_path, renames):
    """Repoint log rows at renamed files so the gallery still resolves them."""
    if not renames or not os.path.exists(log_path):
        return 0
    rows, hits = [], 0
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            new = renames.get(os.path.basename(row.get("file") or ""))
            if new:
                row["file"] = os.path.join(os.path.dirname(row["file"]), new)
                hits += 1
            rows.append(row)
    with open(log_path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("outdir", nargs="?", default="generations")
    ap.add_argument("--max-edge", type=int, default=1600, help="longest image side, px")
    ap.add_argument("--quality", type=int, default=78, help="WebP quality")
    ap.add_argument("--video-width", type=int, default=960)
    ap.add_argument("--crf", type=int, default=30, help="x264 quality, higher is smaller")
    ap.add_argument("--keep-raw", action="store_true",
                    help="move originals to <outdir>/raw/ instead of replacing them")
    a = ap.parse_args()

    if not os.path.isdir(a.outdir):
        sys.exit(f"no directory at {a.outdir}")
    raw_dir = os.path.join(a.outdir, "raw") if a.keep_raw else None

    names = sorted(os.listdir(a.outdir))
    renames, done, before, after = {}, [], 0.0, 0.0
    for name in names:
        path = os.path.join(a.outdir, name)
        if not os.path.isfile(path):
            continue
        low = name.lower()
        try:
            if low.endswith(IMAGE_EXT):
                res = shrink_image(path, a.max_edge, a.quality, raw_dir)
            elif low.endswith(VIDEO_EXT):
                res = shrink_video(path, a.video_width, a.crf, raw_dir)
            else:
                continue
        except Exception as exc:
            print(f"skip {name}: {exc}", file=sys.stderr)
            continue
        if not res:
            continue
        b, af, dest = res
        newname = os.path.basename(dest)
        if newname != name:
            renames[name] = newname
        before, after = before + b, after + af
        done.append((name, newname, b, af))
        print(f"{name:48} {b:8.0f}K -> {af:7.0f}K")

    if not done:
        print("nothing to compress")
        return
    hits = relog(os.path.join(a.outdir, "log.jsonl"), renames)
    print(f"{'TOTAL':48} {before:8.0f}K -> {after:7.0f}K "
          f"({100 * (1 - after / before):.0f}% smaller, {len(done)} files, {hits} log rows repointed)")
    if raw_dir:
        print(f"originals kept in {raw_dir} — add it to .gitignore")
    print("now rebuild the gallery: python3 <skill-dir>/build_gallery.py " + a.outdir)


if __name__ == "__main__":
    main()
