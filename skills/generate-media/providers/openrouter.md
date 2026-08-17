# OpenRouter media API

Base URL `https://openrouter.ai/api/v1`. Every request needs `Authorization: Bearer $OPENROUTER_API_KEY`.

```
 1. key check ----> GET  /key
 2. discover  ----> GET  /models?output_modalities=image|video
 3. generate  ----> POST /images   (sync, base64 back)
              \---> POST /videos   (async, 202 + polling_url)
 4. save      ----> $OUT_DIR/slug.png|mp4
 5. report    ----> path + usage.cost
```

Set the output directory first. Use `$HOME`, not `~` — a quoted tilde does not expand and silently creates a literal `./~/` directory:

```bash
OUT_DIR="$HOME/.cache/generate-media"
mkdir -p "$OUT_DIR"
```

## 1. Key check

```bash
curl -s https://openrouter.ai/api/v1/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq .
```

`limit_remaining` is `null` when the key has no cap. `usage` is all-time spend, not this run.

## 2. Model discovery

```bash
curl -s "https://openrouter.ai/api/v1/models?output_modalities=image" \
  | jq -r '.data[] | "\(.id)\t\(.pricing.image // "-")\t\(.pricing.image_output // "-")"'
```

Use `output_modalities=video` for video. `pricing.image` is USD per image and only some models have it; `pricing.image_output` is per **output token**, not per image.

### Video price per second

Video models report `0` for every pricing field, so quote from this table and take the real figure from `usage.cost`. These rates are floors: ByteDance bills `(width * height * duration * 24) / 1024` tokens, so 1080p costs far more than 480p at the same duration. Kling is a flat per-second rate.

| Model | From | Notes |
|---|---|---|
| `bytedance/seedance-2.0-mini` | $0.01345/s | 4–15 s, 480p/720p. Cheapest draft. |
| `bytedance/seedance-2.0-fast` | $0.04035/s | Speed and cost first. |
| `bytedance/seedance-2.0` | $0.06726/s | Best character, style, camera consistency. |
| `kwaivgi/kling-v3.0-std` | $0.126/s | Flat rate, 3–15 s. |
| `google/veo-3.1` | no published rate | Ask the user first. |
| `openai/sora-2-pro` | no published rate | Ask the user first. |

Rate × duration lands at roughly the 720p figure — a 6-second 720p clip is ~**$0.08** on seedance-2.0-mini, ~**$0.40** on seedance-2.0, ~**$0.76** on kling-v3.0-std. Scale down for 480p, up for 1080p. A model missing from this table has no obtainable price — never guess one; the unrated models are the premium tiers.

Seedance 2.x takes `text+image+audio+video` (first *and* last frame control, reference-to-video). Kling v3.0 takes text and images only.

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

| Field | Values |
|---|---|
| `model`, `prompt` | required |
| `n` | 1–10. Single-image providers reject `n > 1`. |
| `resolution` | `512`, `1K`, `2K`, `4K` |
| `aspect_ratio` | `1:1`, `16:9`, `9:16`, `4:3`, … (clamped per provider) |
| `size` | `"2048x2048"` — shorthand for the two above |
| `output_format` | `png`, `jpeg`, `webp`, `svg` |
| `input_references` | array — reference or edit images |
| `seed` | integer |

Reference images take a URL or a base64 data URL, never a bare path:

```json
"input_references": [
  { "type": "image_url", "image_url": { "url": "https://example.com/ref.jpg" } },
  { "type": "image_url", "image_url": { "url": "data:image/png;base64,iVBORw0..." } }
]
```

```bash
REF="data:image/png;base64,$(base64 -w0 ./brand/logo.png)"
```

Response is `{ "data": [{ "b64_json": ..., "media_type": ... }], "usage": { "cost": 0.032 } }`:

```bash
OUT="$OUT_DIR/hero.png"
jq -r '.data[0].b64_json' resp.json | base64 -d > "$OUT"
test -s "$OUT" || echo "FAILED: empty file"
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

Extra fields beyond the image set: `duration` (seconds), `generate_audio`, `callback_url`, plus two image inputs.

`frame_images` — image-to-video. Each entry needs `frame_type` of `first_frame` or `last_frame`; omitting it is rejected:

```json
"frame_images": [
  { "type": "image_url",
    "image_url": { "url": "data:image/png;base64,iVBORw0..." },
    "frame_type": "first_frame" }
]
```

`input_references` — style guidance, not exact frames. Same shape, no `frame_type`.

Submission returns `202` with `{ "id", "polling_url", "status": "pending" }`. Poll ~every 30 s; status goes `pending` → `in_progress` → `completed` | `failed`:

```bash
JOB=$(jq -r .id job.json)
curl -s "https://openrouter.ai/api/v1/videos/$JOB" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.status, .usage.cost'

OUT="$OUT_DIR/bottle-push-in.mp4"
curl -sL "https://openrouter.ai/api/v1/videos/$JOB/content?index=0" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  --output "$OUT"
file "$OUT"
```

The job stays fetchable after a failed download, so re-run the content call rather than regenerating — the clip is already paid for.

## Model IDs worth knowing

Verify with the discovery call — this list ages.

| Need | Model |
|---|---|
| Legible text in image | `openai/gpt-image-2` |
| Cheap image draft | `openai/gpt-image-1-mini`, `krea/krea-2-medium-turbo` |
| Photoreal / editing | `google/gemini-3-pro-image`, `bytedance-seed/seedream-4.5` |
| Vector / SVG | `recraft/recraft-v4.1-vector` |
| Video draft, cheapest | `bytedance/seedance-2.0-mini` |
| Video, consistency | `bytedance/seedance-2.0` |
| Video, flat price | `kwaivgi/kling-v3.0-std` |
| Video, high quality | `google/veo-3.1`, `openai/sora-2-pro` — unpriced, confirm first |
