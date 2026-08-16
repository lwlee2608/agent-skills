# OpenRouter media API reference

Base URL `https://openrouter.ai/api/v1`. Every request needs `Authorization: Bearer $OPENROUTER_API_KEY`.

## Flow

```
 1. key check ----> GET  /key                  (credit left?)
 2. discover  ----> GET  /models?output_modalities=image|video
 3. generate  ----> POST /images    (sync, returns base64)
              \---> POST /videos    (async, 202 + polling_url)
 4. save      ----> generations/NNN-slug.png|mp4
 5. log       ----> generations/log.jsonl      (append one line)
 6. gallery   ----> generations/index.html     (build_gallery.py, rebuilt)
```

## 1. Key and credit check

```bash
curl -s https://openrouter.ai/api/v1/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq .
```

```json
{ "data": { "label": "...", "limit": null, "limit_remaining": null,
            "usage": 12.4, "usage_daily": 0.8, "is_free_tier": false } }
```

`limit_remaining` is `null` when the key has no cap. `usage` is all-time spend, so it is not a per-run counter — track the run total from `log.jsonl` instead.

## 2. Model discovery

```bash
curl -s "https://openrouter.ai/api/v1/models?output_modalities=image" \
  | jq -r '.data[] | "\(.id)\t\(.pricing.image // "-")\t\(.pricing.image_output // "-")"'
```

Pricing fields, in order of usefulness:

| Field | Meaning |
|---|---|
| `pricing.image` | USD per image. Present on some models only. |
| `pricing.image_output` | USD per **output token**. Not per image. Cannot be converted without the token count. |
| `pricing.prompt` | USD per input text token. |

⚠ Video models report `"prompt": "0", "completion": "0"` and carry no per-second field. The API cannot tell you what a clip costs. Use the table below for planning, then take the true figure from `usage.cost` in the response.

### Video price per second

Rates are floors — every ByteDance model bills on
`(width * height * duration * 24) / 1024` tokens, so 1080p costs far more than 480p at the
same duration. Kling bills a flat per-second rate.

| Model | From | Notes |
|---|---|---|
| `bytedance/seedance-2.0-mini` | $0.01345/s | 4–15 s, 480p and 720p only. Cheapest draft. |
| `bytedance/seedance-2.0-fast` | $0.04035/s | Speed and cost first. |
| `bytedance/seedance-2.0` | $0.06726/s | Best character, style, and camera consistency. |
| `kwaivgi/kling-v3.0-std` | $0.126/s | Flat rate, 3–15 s. |

A 6-second 720p clip: about **$0.08** on seedance-2.0-mini, **$0.40** on seedance-2.0,
**$0.76** on kling-v3.0-std.

The Seedance 2.x family accepts `text+image+audio+video` input — first **and** last frame
control, plus reference-to-video from an existing clip. Kling v3.0 takes text and images
only.

Per-provider detail and uptime for one model:

```bash
curl -s "https://openrouter.ai/api/v1/models/kwaivgi/kling-v3.0-std/endpoints" | jq .
```

## 3a. Images — POST /images (synchronous)

```bash
curl -s -X POST "https://openrouter.ai/api/v1/images" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-image-2",
    "prompt": "product photo of a green apple energy shot, studio lighting",
    "resolution": "2K",
    "aspect_ratio": "1:1",
    "output_format": "png"
  }' > resp.json
```

Request fields:

| Field | Values |
|---|---|
| `model` | required, e.g. `openai/gpt-image-2`, `google/gemini-3-pro-image` |
| `prompt` | required |
| `n` | 1–10. Single-image providers reject `n > 1`. |
| `resolution` | `512`, `1K`, `2K`, `4K` |
| `aspect_ratio` | `1:1`, `16:9`, `9:16`, `4:3`, … (clamped per provider) |
| `size` | `"2048x2048"` or a tier — shorthand for the two fields above |
| `output_format` | `png`, `jpeg`, `webp`, `svg` |
| `input_references` | array — reference or edit images |
| `seed` | integer |

Reference images (style transfer, editing). URL or base64 data URL only — never a bare local path:

```json
"input_references": [
  { "type": "image_url", "image_url": { "url": "https://example.com/ref.jpg" } },
  { "type": "image_url", "image_url": { "url": "data:image/png;base64,iVBORw0..." } }
]
```

Build a data URL from a local file:

```bash
REF="data:image/png;base64,$(base64 -w0 ./brand/logo.png)"
```

Response:

```json
{ "created": 1748372400,
  "data": [ { "b64_json": "<base64>", "media_type": "image/png" } ],
  "usage": { "total_tokens": 4175, "cost": 0.032 } }
```

Save and read the true cost:

```bash
jq -r '.data[0].b64_json' resp.json | base64 -d > generations/001-hero.png
jq -r '.usage.cost' resp.json
```

## 3b. Videos — POST /videos (asynchronous)

```bash
curl -s -X POST "https://openrouter.ai/api/v1/videos" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kwaivgi/kling-v3.0-std",
    "prompt": "slow push in on the bottle, condensation forming",
    "duration": 5,
    "resolution": "720p",
    "aspect_ratio": "16:9"
  }' > job.json
```

Extra fields beyond the image set: `duration` (seconds), `generate_audio` (boolean), `callback_url`, plus two image inputs:

`frame_images` — image-to-video. Each entry needs a `frame_type` of `first_frame` or `last_frame`. Omitting `frame_type` is rejected:

```json
"frame_images": [
  { "type": "image_url",
    "image_url": { "url": "data:image/png;base64,iVBORw0..." },
    "frame_type": "first_frame" }
]
```

`input_references` — style guidance, not exact frames. Same shape, no `frame_type`.

Submission response is `202`:

```json
{ "id": "abc123", "polling_url": "https://openrouter.ai/api/v1/videos/abc123", "status": "pending" }
```

Poll about every 30 seconds. Status goes `pending` → `in_progress` → `completed` | `failed`:

```bash
JOB=$(jq -r .id job.json)
curl -s "https://openrouter.ai/api/v1/videos/$JOB" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.status, .usage.cost'
```

Completed response:

```json
{ "id": "abc123", "status": "completed",
  "unsigned_urls": ["https://openrouter.ai/api/v1/videos/abc123/content?index=0"],
  "usage": { "cost": 0.63 } }
```

Download:

```bash
curl -sL "https://openrouter.ai/api/v1/videos/$JOB/content?index=0" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  --output generations/002-bottle-push-in.mp4
```

## 4. Log format

One JSON object per line in `generations/log.jsonl`, appended after every attempt:

```json
{"n":1,"file":"generations/001-hero.png","model":"openai/gpt-image-2","prompt":"product photo of ...","size":"2K","aspect_ratio":"1:1","cost":0.032,"status":"ok"}
{"n":2,"file":null,"model":"kwaivgi/kling-v3.0-std","prompt":"slow push in ...","cost":0,"status":"failed","error":"job status failed"}
```

Run total:

```bash
jq -s 'map(.cost) | add' generations/log.jsonl
```

## Useful model IDs

Verify with the discovery call — this list ages.

| Need | Model |
|---|---|
| Legible text in image | `openai/gpt-image-2` |
| Cheap image draft | `openai/gpt-image-1-mini`, `krea/krea-2-medium-turbo` |
| Photoreal / editing | `google/gemini-3-pro-image`, `bytedance-seed/seedream-4.5` |
| Vector / SVG output | `recraft/recraft-v4.1-vector` |
| Video draft, cheapest | `bytedance/seedance-2.0-mini` |
| Video, style and character consistency | `bytedance/seedance-2.0` |
| Video, flat predictable price | `kwaivgi/kling-v3.0-std` |
| Video, high quality | `google/veo-3.1`, `openai/sora-2-pro` |
