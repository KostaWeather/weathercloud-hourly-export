# WeatherCloud Hourly Export + Weather Presenter Demo

This repository contains the existing WeatherCloud-to-Google-Sheets export script and a new bilingual demo website for a weather presenter concept.

## Existing exporter

`main.py` logs into WeatherCloud, exports a CSV from the database page, and uploads it to Google Sheets. It expects these environment variables:

- `WEATHER_LOGIN`
- `WEATHER_PASSWORD`
- `GOOGLE_CREDENTIALS_JSON`

Run it with:

```bash
python main.py
```

## Bilingual weather presenter website

The static website is in [`site/`](site/). It works in Russian and English, asks the visitor for a city and country, shows a live map background, receives weather from a free API, and lets the visitor choose:

- current weather;
- 3-day forecast;
- 10-day forecast.

### Free data sources selected

- **Weather:** [Open-Meteo](https://open-meteo.com/) Forecast API and Geocoding API. It is free for non-commercial use and does not require an API key for the basic public API.
- **Maps:** [OpenStreetMap](https://www.openstreetmap.org/) tiles through Leaflet. The demo includes required attribution. For production traffic, use a dedicated tile provider or self-host tiles to comply with OpenStreetMap tile usage limits.
- **Voice:** browser Web Speech API (`speechSynthesis`) for a no-cost prototype. For production, replace it with a licensed TTS provider if consistent voices are required.
- **Animated presenter:** a CSS/SVG prototype avatar. For production, see [`site/AI_AVATAR_PLAN.md`](site/AI_AVATAR_PLAN.md) for an AI model, animation, lip-sync, and safety pipeline.



### Публикация в облаке

Для публикации сайта без локального запуска добавлен GitHub Pages workflow и конфиг Netlify. Подробные шаги описаны в [`CLOUD_DEPLOY_RU.md`](CLOUD_DEPLOY_RU.md).

### Русская инструкция по запуску

Если вы хотите просто запустить сайт, откройте подробную инструкцию: [`RUN_SITE_RU.md`](RUN_SITE_RU.md). Коротко:

```bash
python -m http.server 8000 --directory site
```

Затем откройте <http://localhost:8000>. Не открывайте `site/index.html` через `file://`, потому что карте, JavaScript-модулям и погодным API нужен HTTP-сервер.

### Run the website locally

```bash
python -m http.server 8000 --directory site
```

Open <http://localhost:8000> in a browser.
