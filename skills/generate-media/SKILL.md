---
name: generate-media
description: Use when generating or editing an image or video with an AI model — ads, mockups, style variations, image-to-video — through the OpenRouter API. Looks up a real model ID, picks the cheapest model that fits, saves the file to local disk, and reports what it actually cost.
user-invocable: true
argument-hint: "[<what to generate>]"
---

# Generate Media with OpenRouter

One generation per invocation, through one OpenRouter API key instead of a per-tool subscription. The file and its real cost land on local disk under `generations/`.

Exact endpoints, fields, and curl commands: [openrouter-api.md](openrouter-api.md). Read that file before the first API call.

## Rules

1. **Stop if `OPENROUTER_API_KEY` is not set.** Check `.env` in the project root, then the environment. Never write the key into a file that git tracks. If it is missing, tell the user to get one from <https://openrouter.ai/settings/keys> and stop.

2. **Look up model IDs from the API. Never guess them.** Model IDs change and a wrong ID wastes a round trip:
   ```bash
   curl -s "https://openrouter.ai/api/v1/models?output_modalities=image" \
     | jq -r '.data[] | "\(.id)\t\(.pricing.image // .pricing.image_output)"'
   ```
   Use `output_modalities=video` for video models.

3. **Pick the cheapest model that meets the stated need**, unless the user named a model. Sort the list from rule 2 by price. Two exceptions worth stating to the user: `openai/gpt-image-2` for legible text inside an image, and a `-pro` tier when the user asked for final production quality.

4. **Quote the cost before calling, and only quote a figure you can source.** OpenRouter charges per generation with no monthly cap, and video runs 10× to 50× an image.
   - **Video** — read the figure off the per-second rate table in [openrouter-api.md](openrouter-api.md). A model with no row there has no published rate anywhere: the pricing fields all return `0`, so say the cost is unknown and wait for the user. The unrated models are the expensive ones.
   - **Image** — the API cannot price an image before the call: `pricing.image_output` is per output token, not per image. Name the model and say the cost is unknown until the response returns. Never invent a figure. A still normally lands within a few cents, so go ahead without waiting.
   - **Wait for the user** when a sourced figure is above about $0.50, or when a video's cost is unknown.

   A cheap draft at `bytedance/seedance-2.0-mini` 480p — about $0.05 for 6 seconds — settles the motion before anything expensive gets paid for. Price scales with `width × height × duration`, so halving the resolution is the cheapest way to test an idea.

5. **Write the result to `generations/` with a slugged name** — `generations/green-apple-hero.png`. Never leave a result only in the API response or in a temp directory, and never overwrite an existing file: add a suffix instead. The point of this skill is that the user owns the files. If `generations/` sits inside a git repository, add it to `.gitignore` before writing the first file — see the size warning below.

6. **Report the file path and the real cost** from `usage.cost` in the response. Never estimate it — see the pricing trap below.

## Shipping a generation to a web page

`generations/` is an archive, not a web asset directory. Never point a page at a file in it. Copy the chosen generation out to the site's own directory and derive sized versions there, so the archive and the shipped asset can change independently.

Model output is raw — image models return 2000–2800 px stills at 2–3.5 MB each and video models return 6 Mbps clips. Committing that puts it in git history for good, and getting it out later needs a history rewrite and a force push. Keep `generations/` out of git entirely, and resize on the way to a page.

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
2. **File check** — the saved file is non-empty: `find generations -size -1k -type f`. A base64 decode that silently failed leaves a 0-byte file.
3. **Video check** — the job status reached `completed` and the downloaded `.mp4` plays as a file, not a JSON error body: `file generations/*.mp4`.
4. **Cost check** — the figure reported to the user came from `usage.cost` in the response, not from a pricing field.

## Common mistakes to watch for

- **Treating the video endpoint as synchronous.** `POST /api/v1/videos` returns `202` with a `polling_url`. The video is not ready. Poll it about every 30 seconds until `status` is `completed`, then download the content URL.
- **Estimating cost from `pricing.image_output`.** That field is per output token for most image models, not per image. Video models report `0` for every price field. Read `usage.cost` from the actual response instead.
- **Piping base64 straight into a file.** The image arrives as `data[0].b64_json`. It must be decoded: `jq -r '.data[0].b64_json' resp.json | base64 -d > out.png`.
- **Overwriting an earlier result.** Check `generations/` for the name first. Re-running the skill must not destroy what is already there.
- **Sending a local file path as a reference image.** `input_references` takes an HTTP(S) URL or a base64 data URL. A bare path fails.
- **Committing the raw output.** A 2–3.5 MB still or a 6 Mbps clip in git is permanent. Gitignore `generations/`, and resize anything copied out of it.
