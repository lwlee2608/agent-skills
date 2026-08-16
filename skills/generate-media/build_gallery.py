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
.meta{color:var(--dim);margin-bottom:24px}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.card img,.card video{display:block;width:100%;aspect-ratio:1;object-fit:cover;background:#000}
.card .body{padding:10px 12px}
.card .top{display:flex;justify-content:space-between;gap:8px;font-size:12px;margin-bottom:6px}
.card .model{color:var(--fg);font-weight:600;word-break:break-all}
.card .cost{color:var(--dim);white-space:nowrap}
.card .prompt{color:var(--dim);font-size:12px;max-height:4.5em;overflow:hidden}
.card.failed{border-color:var(--bad)}
.card .err{color:var(--bad);font-size:12px;padding:24px 12px}
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
    body = (
        f'<div class="body"><div class="top"><span class="model">{model}</span>'
        f'<span class="cost">${cost:.3f}</span></div>'
        f'<div class="prompt">{prompt}</div></div>'
    )
    path = row.get("file")
    if row.get("status") != "ok" or not path:
        err = e(str(row.get("error", "failed")))
        return f'<div class="card failed"><div class="err">{err}</div>{body}</div>'

    src = e(os.path.relpath(path, outdir))
    if path.lower().endswith(VIDEO_EXT):
        media = f'<video src="{src}" controls muted loop playsinline preload="metadata"></video>'
    else:
        media = f'<a href="{src}" target="_blank"><img src="{src}" loading="lazy" alt=""></a>'
    return f'<div class="card">{media}{body}</div>'


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "generations"
    log_path = os.path.join(outdir, "log.jsonl")
    if not os.path.exists(log_path):
        sys.exit(f"no log at {log_path}")

    rows = load(log_path)
    total = sum(r.get("cost") or 0 for r in rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")
    tiles = "\n".join(tile(r, outdir) for r in reversed(rows))

    page = (
        "<!doctype html><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>generations</title>"
        f"<style>{CSS}</style>"
        "<h1>generations</h1>"
        f'<div class="meta">{ok}/{len(rows)} ok &middot; ${total:.2f} spent</div>'
        f'<div class="grid">{tiles}</div>'
    )

    index = os.path.join(outdir, "index.html")
    with open(index, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"{index} — {ok}/{len(rows)} ok, ${total:.2f}")


if __name__ == "__main__":
    main()
