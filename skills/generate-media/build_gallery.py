#!/usr/bin/env python3
import html
import json
import os
import sys

VIDEO_EXT = (".mp4", ".webm", ".mov")

CSS = """
:root{--bg:#111214;--fg:#e8e8ea;--dim:#8b8d93;--card:#1a1c1f;--line:#2a2d31;--bad:#e05252}
*{box-sizing:border-box}
body{margin:0;padding:24px;background:var(--bg);color:var(--fg);
     font:14px/1.5 ui-sans-serif,system-ui,-apple-system,sans-serif}
h1{font-size:18px;margin:0 0 4px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;margin:32px 0 12px;
   padding-bottom:8px;border-bottom:1px solid var(--line);display:flex;
   justify-content:space-between;align-items:baseline;gap:12px}
h2 .note{color:var(--dim);font-size:12px;text-transform:none;letter-spacing:0}
.empty{color:var(--dim);font-size:13px;padding:8px 0 4px}
.meta{color:var(--dim);margin-bottom:24px}
.card iframe{display:block;width:100%;aspect-ratio:16/9;border:0;background:#fff;
   pointer-events:none}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.card img,.card video{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#000}
.card .body{padding:10px 12px}
.card .top{display:flex;align-items:center;gap:8px;font-size:12px;margin-bottom:6px}
.card .id{background:#e86c6d;color:#fff;font-weight:700;padding:1px 7px;border-radius:4px}
.card .model{color:var(--fg);font-weight:600;word-break:break-all;flex:1}
.card .cost{color:var(--dim);white-space:nowrap}
.card .prompt{color:var(--dim);font-size:12px;max-height:4.5em;overflow:hidden}
.card.failed{border-color:var(--bad)}
.card.gone{opacity:.55}
.card .err{color:var(--bad);font-size:12px;padding:24px 12px}
.card .gonemsg{color:var(--dim);font-size:12px;padding:24px 12px}
a{color:inherit;text-decoration:none}
"""


def load(log_path):
    rows = []
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def tile(row, outdir):
    e = html.escape
    model = e(str(row.get("model", "?")))
    prompt = e(str(row.get("prompt", "")))
    cost = row.get("cost") or 0
    ident = e(str(row.get("n", "?")))
    body = (
        f'<div class="body"><div class="top"><span class="id">#{ident}</span>'
        f'<span class="model">{model}</span>'
        f'<span class="cost">${cost:.3f}</span></div>'
        f'<div class="prompt">{prompt}</div></div>'
    )
    path = row.get("file")
    status = row.get("status")
    if status == "deleted":
        msg = e(str(row.get("error", "deleted")))
        return f'<div class="card gone"><div class="gonemsg">{msg}</div>{body}</div>'
    if status != "ok" or not path:
        err = e(str(row.get("error", "failed")))
        return f'<div class="card failed"><div class="err">{err}</div>{body}</div>'

    src = e(os.path.relpath(path, outdir))
    if path.lower().endswith(VIDEO_EXT):
        media = f'<video src="{src}" controls muted loop playsinline preload="metadata"></video>'
    else:
        media = f'<a href="{src}" target="_blank"><img src="{src}" loading="lazy" alt=""></a>'
    return f'<div class="card">{media}{body}</div>'


def is_video(row):
    path = row.get("file") or ""
    return path.lower().endswith(VIDEO_EXT)


def page_tile(path, outdir):
    e = html.escape
    src = e(os.path.relpath(path, outdir))
    name = e(os.path.basename(path))
    return (
        f'<div class="card"><a href="{src}" target="_blank">'
        f'<iframe src="{src}" loading="lazy" scrolling="no" title="{name}"></iframe></a>'
        f'<div class="body"><div class="top"><span class="model">{name}</span>'
        f'<span class="cost">open</span></div></div></div>'
    )


def find_pages(outdir):
    """Saved landing pages: generations/pages/*.html, then the project's index.html."""
    found = []
    pdir = os.path.join(outdir, "pages")
    if os.path.isdir(pdir):
        found += sorted(
            (os.path.join(pdir, f) for f in os.listdir(pdir) if f.endswith(".html")),
            reverse=True,
        )
    live = os.path.join(os.path.dirname(os.path.abspath(outdir)), "index.html")
    if os.path.exists(live):
        found.insert(0, live)
    return found


def section(title, note, tiles):
    inner = f'<div class="grid">{tiles}</div>' if tiles else '<div class="empty">nothing yet</div>'
    return f'<h2>{title}<span class="note">{note}</span></h2>{inner}'


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "generations"
    log_path = os.path.join(outdir, "log.jsonl")
    if not os.path.exists(log_path):
        sys.exit(f"no log at {log_path}")

    rows = load(log_path)
    total = sum(r.get("cost") or 0 for r in rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")

    photos = [r for r in rows if not is_video(r)]
    videos = [r for r in rows if is_video(r)]
    pages = find_pages(outdir)

    def cost_of(group):
        return sum(r.get("cost") or 0 for r in group)

    body = (
        section(
            "Photos",
            f"{sum(1 for r in photos if r.get('status') == 'ok')} items &middot; ${cost_of(photos):.2f}",
            "\n".join(tile(r, outdir) for r in reversed(photos)),
        )
        + section(
            "Videos",
            f"{sum(1 for r in videos if r.get('status') == 'ok')} items &middot; ${cost_of(videos):.2f}",
            "\n".join(tile(r, outdir) for r in reversed(videos)),
        )
        + section(
            "Landing pages",
            f"{len(pages)} version(s) &middot; $0.00",
            "\n".join(page_tile(p, outdir) for p in pages),
        )
    )

    page = (
        "<!doctype html><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>generations</title>"
        f"<style>{CSS}</style>"
        "<h1>generations</h1>"
        f'<div class="meta">{ok}/{len(rows)} ok &middot; ${total:.2f} spent</div>'
        f"{body}"
    )

    index = os.path.join(outdir, "index.html")
    with open(index, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(
        f"{index} — {ok}/{len(rows)} ok, ${total:.2f} "
        f"(photos {len(photos)}, videos {len(videos)}, pages {len(pages)})"
    )


if __name__ == "__main__":
    main()
