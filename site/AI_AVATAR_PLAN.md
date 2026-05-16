# AI presenter production plan

The demo uses a lightweight CSS/SVG avatar and the browser Web Speech API so it can run for free without accounts or paid APIs. A production version can replace that prototype with a generated and animated digital presenter.

## 1. Visual identity and consent-safe dataset

1. Define the presenter as a fully fictional adult character with a style guide: age range, wardrobe, hair, brand colors, tone of voice, and prohibited content.
2. Generate a base character sheet with an image model licensed for commercial use.
3. Keep all training and reference assets consent-safe: no real person likeness, no celebrity resemblance, no scraped personal photos.
4. Store prompt, seed, model version, and license notes for every asset.

## 2. Motion and lip-sync

Recommended MVP stack:

- **Avatar image/video generation:** generate a short idle loop of the presenter in tasteful beachwear.
- **Text-to-speech:** use a licensed TTS voice for Russian and English.
- **Lip-sync:** drive mouth movement from generated audio with a lip-sync model or avatar SDK.
- **Frontend playback:** stream the final video or render a WebGL/Live2D avatar with separate idle, talking, and gesture animations.

For lower latency, use a 2D/3D rigged avatar instead of generating a new video for every forecast. The browser receives text, creates speech audio, and the rig animates mouth shapes and gestures in real time.

## 3. Weather script generation

The frontend currently builds deterministic weather phrases. For production:

1. Fetch structured weather data from Open-Meteo.
2. Build a safe prompt from the weather JSON and user-selected language.
3. Ask an LLM to produce a concise presenter script with strict length, no medical or safety overclaims, and no unsupported meteorological claims.
4. Send the final script to TTS and lip-sync.

## 4. Safety and moderation

- Keep the presenter adult-coded and non-explicit.
- Avoid overly sexualized camera angles, poses, or copy.
- Disallow user prompts that request nudity, sexual content, impersonation, or real-person likenesses.
- Add content moderation before any custom user-generated script is spoken.

## 5. Deployment notes

- Use a backend proxy for paid keys, rate limits, cache, and analytics-free logging.
- Cache geocoding results and forecast responses for each city for 10–30 minutes.
- For map traffic above prototype level, use a commercial tile provider or self-host OpenStreetMap tiles.
- Add an accessibility mode that disables animation and replaces speech with readable cards.
