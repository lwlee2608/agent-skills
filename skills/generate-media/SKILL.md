---
name: generate-media
description: Use when generating or editing images and videos with AI models — ads, mockups, style variations, image-to-video — through the OpenRouter API. Picks the cheapest model that fits, stops at a spend budget, and logs every prompt, model, and cost to local disk.
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

7. **Write each result to `generations/` with a numbered, slugged name** — `generations/001-green-apple-hero.png`. Never leave a result only in the API response or in a temp directory. The point of this skill is that the user owns the files.

8. **Append one JSON line to `generations/log.jsonl` after every generation**, including failures:
   ```json
   {"n":1,"file":"generations/001-green-apple-hero.png","model":"openai/gpt-image-2","prompt":"...","size":"2K","aspect_ratio":"1:1","cost":0.032,"status":"ok"}
   ```
   Use the `cost` value the API returned. Never estimate it into the log.

9. **Rebuild the gallery after every batch**, so the user can compare results side by side instead of opening files one at a time:
   ```bash
   python3 <skill-dir>/build_gallery.py generations
   ```
   The script reads `log.jsonl` and overwrites `generations/index.html`. It needs no arguments beyond the directory and no third-party packages. Never hand-write the HTML.

10. **Report the real total when done**: number of files, the path to `generations/index.html`, and the summed `cost` from the log. If you stopped early because of the budget, say so and say what is left undone.

## Verification procedure

1. **Key check** — `OPENROUTER_API_KEY` resolved, and `curl -s https://openrouter.ai/api/v1/key -H "Authorization: Bearer $OPENROUTER_API_KEY"` returns 200.
2. **File check** — every file in `generations/` is non-empty: `find generations -size -1k -type f`. A base64 decode that silently failed leaves a 0-byte file.
3. **Log check** — the line count of `log.jsonl` equals the number of generation attempts, and `jq -s 'map(.cost) | add' generations/log.jsonl` is at or under the agreed budget.
4. **Video check** — the job status reached `completed` and the downloaded `.mp4` plays as a file, not a JSON error body: `file generations/00X-*.mp4`.
5. **Gallery check** — `generations/index.html` exists and its card count matches the log: `grep -c 'class="card' generations/index.html`.

## Common mistakes to watch for

- **Treating the video endpoint as synchronous.** `POST /api/v1/videos` returns `202` with a `polling_url`. The video is not ready. Poll it about every 30 seconds until `status` is `completed`, then download the content URL.
- **Estimating cost from `pricing.image_output`.** That field is per output token for most image models, not per image. Video models report `0` for every price field. Read `usage.cost` from the actual response instead.
- **Piping base64 straight into a file.** The image arrives as `data[0].b64_json`. It must be decoded: `jq -r '.data[0].b64_json' resp.json | base64 -d > out.png`.
- **Overwriting earlier results.** Read the highest existing number in `generations/` first and continue from there. Re-running the skill must not destroy the previous batch.
- **Sending a local file path as a reference image.** `input_references` takes an HTTP(S) URL or a base64 data URL. A bare path fails.
