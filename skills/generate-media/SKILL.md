---
name: generate-media
description: Use when generating or editing images and videos with AI models — ads, mockups, style variations, image-to-video — through the OpenRouter API. Picks the cheapest model that fits, stops at a spend budget, logs every prompt, model, and cost to local disk, and compresses the raw multi-megabyte output before it reaches git or a web page.
user-invocable: true
argument-hint: "[<what to generate>]"
---

# Generate Media with OpenRouter

Generate images and videos through one OpenRouter API key instead of a per-tool subscription. Every file, prompt, and cost stays on local disk under `generations/`.

Exact endpoints, fields, and curl commands: [openrouter-api.md](openrouter-api.md). Read that file before the first API call.

## Rules

1. **Stop if `OPENROUTER_API_KEY` is not set.** Check `.env` in the project root, then the environment. Never write the key into a file that git tracks. If it is missing, tell the user to get one from <https://openrouter.ai/settings/keys> and stop.

2. **Agree a budget before any generation, and never exceed it.** If the user gave no dollar figure, ask for one and propose `$2`. Then say what you plan to spend and wait. Reason: one careless instruction ("make 100 variations") drains real credit, and OpenRouter charges per generation with no monthly cap.

3. **Probe with one generation before a batch.** Video pricing is absent from the models API and image pricing is often per output token, so a pre-flight estimate is unreliable. Generate item 1, read the true `usage.cost` from the response, then compute `remaining = budget - cost_so_far` and how many more items fit. Report that number to the user before continuing.

4. **Generate one item at a time. Never run generation calls in parallel.** The running total is checked between calls; parallel calls skip the check and overshoot the budget.

5. **Look up model IDs from the API. Never guess them.** Model IDs change and a wrong ID wastes a round trip:
   ```bash
   curl -s "https://openrouter.ai/api/v1/models?output_modalities=image" \
     | jq -r '.data[] | "\(.id)\t\(.pricing.image // .pricing.image_output)"'
   ```
   Use `output_modalities=video` for video models.

6. **Pick the cheapest model that meets the stated need**, unless the user named a model. Sort the list from rule 5 by price. Two exceptions worth stating to the user: `openai/gpt-image-2` for legible text inside an image, and a `-pro` tier when the user asked for final production quality.

7. **Draft video on a cheap model before paying for the final.** Video costs 10× to 50× an image, and the failure is usually the motion, not the pixels. Generate at `bytedance/seedance-2.0-mini` 480p first — about $0.05 for 6 seconds — and only re-run the approved motion on the final model. Video price scales with `width × height × duration`, so halving the resolution is the cheapest way to test an idea. See [openrouter-api.md](openrouter-api.md) for the rate table.

8. **Write each result to `generations/` with a numbered, slugged name** — `generations/001-green-apple-hero.png`. Never leave a result only in the API response or in a temp directory. The point of this skill is that the user owns the files.

9. **Append one JSON line to `generations/log.jsonl` after every generation**, including failures:
   ```json
   {"n":1,"file":"generations/001-green-apple-hero.png","model":"openai/gpt-image-2","prompt":"...","size":"2K","aspect_ratio":"1:1","cost":0.032,"status":"ok"}
   ```
   Use the `cost` value the API returned. Never estimate it into the log.

10. **Compress the batch before it lands anywhere permanent.** Model output is raw: image models return 2000–2800 px stills at 2–3.5 MB each and video models return 6 Mbps clips, so a 14-item batch weighs about 40 MB. Once that is committed it sits in git history for good, and getting it out later needs a history rewrite and a force push. Run this after the batch, before the gallery rebuild:
   ```bash
   python3 <skill-dir>/compress.py generations
   ```
   It downscales stills to 1600 px WebP, re-encodes clips to x264 CRF 30 at 960 px wide, repoints the `file` field in `log.jsonl`, and skips anything already small enough, so it is safe to re-run. Expect roughly a 95% cut with no visible loss at gallery size. Needs `ffmpeg` and Pillow. Pass `--keep-raw` to move the originals to `generations/raw/` instead of replacing them, then add that directory to `.gitignore` — do this whenever a full-resolution copy may still be wanted, because the compression is otherwise irreversible.

11. **Rebuild the gallery after every batch**, so the user can compare results side by side instead of opening files one at a time:
   ```bash
   python3 <skill-dir>/build_gallery.py generations
   ```
   The script reads `log.jsonl` and overwrites `generations/index.html`. It needs no arguments beyond the directory and no third-party packages. Never hand-write the HTML.

12. **Report the real total when done**: number of files, the path to `generations/index.html`, and the summed `cost` from the log. If you stopped early because of the budget, say so and say what is left undone.

## Shipping a generation to a web page

`generations/` is an archive, not a web asset directory. Never point a page at a file in it. Copy the chosen generation out to the site's own directory and derive sized versions there, so the archive and the shipped asset can change independently.

A full-bleed hero from a 1536×2752 still, cut from 2.2 MB to 35 KB on a phone:

```html
<picture>
  <source type="image/webp" sizes="100vw"
          srcset="public/hero-768.webp 768w, public/hero-1152.webp 1152w, public/hero-1536.webp 1536w">
  <img src="public/hero.jpg" alt="" fetchpriority="high" decoding="async">
</picture>
```

- **Never ship above the source resolution.** Upscaling past what the model returned adds bytes and no detail.
- **Push quality harder when the image sits under an overlay.** A hero behind a dark veil, a gradient, or a grain layer holds up at WebP q72 where a product shot on white would band.
- **Keep one JPEG fallback** at around 1400 px for the `<img>` element. Everything else is WebP.
- **Check a gradient before accepting the quality.** Open the encoded file and look at the largest flat area — sky, backdrop, shadow. Banding shows there first.

## Verification procedure

1. **Key check** — `OPENROUTER_API_KEY` resolved, and `curl -s https://openrouter.ai/api/v1/key -H "Authorization: Bearer $OPENROUTER_API_KEY"` returns 200.
2. **File check** — every file in `generations/` is non-empty: `find generations -size -1k -type f`. A base64 decode that silently failed leaves a 0-byte file.
3. **Log check** — the line count of `log.jsonl` equals the number of generation attempts, and `jq -s 'map(.cost) | add' generations/log.jsonl` is at or under the agreed budget.
4. **Video check** — the job status reached `completed` and the downloaded `.mp4` plays as a file, not a JSON error body: `file generations/00X-*.mp4`.
5. **Gallery check** — `generations/index.html` exists and its card count matches the log: `grep -c 'class="card' generations/index.html`.
6. **Size check** — nothing about to be committed is oversized: `find generations -type f -size +500k -not -path '*/raw/*'`. A still over 500 KB or a 6-second clip over 1 MB means the compression step was skipped. `generations/raw/` is exempt because it is gitignored.
7. **Link check** — every `file` in the log exists after compression: `jq -r 'select(.status=="ok").file' generations/log.jsonl | xargs -r ls >/dev/null`. This catches a rename that never reached the log.

## Common mistakes to watch for

- **Treating the video endpoint as synchronous.** `POST /api/v1/videos` returns `202` with a `polling_url`. The video is not ready. Poll it about every 30 seconds until `status` is `completed`, then download the content URL.
- **Estimating cost from `pricing.image_output`.** That field is per output token for most image models, not per image. Video models report `0` for every price field. Read `usage.cost` from the actual response instead.
- **Piping base64 straight into a file.** The image arrives as `data[0].b64_json`. It must be decoded: `jq -r '.data[0].b64_json' resp.json | base64 -d > out.png`.
- **Overwriting earlier results.** Read the highest existing number in `generations/` first and continue from there. Re-running the skill must not destroy the previous batch.
- **Sending a local file path as a reference image.** `input_references` takes an HTTP(S) URL or a base64 data URL. A bare path fails.
- **Renaming a file without updating `log.jsonl`.** The gallery resolves every card through the log's `file` field, so a still converted to `.webp` by hand leaves a broken card. Let `compress.py` do the rename, or edit the log in the same step. Never patch `generations/index.html` directly — the next gallery rebuild overwrites it.
- **Committing intermediate working copies.** Labelled contact sheets, upscales, and crops made while comparing options are usually referenced by nothing once a winner is picked. Delete them before committing rather than compressing them.
- **Assuming a compressed archive is still a master.** After `compress.py` without `--keep-raw`, 1600 px WebP is all that is left. Derive any production asset from the original first, then compress.
