# Публикация сайта в облаке

Сайт с погодной ведущей находится в папке `site/`. Это статический сайт: ему не нужна сборка, база данных или Python-сервер в продакшене. Достаточно опубликовать содержимое папки `site/` на статическом хостинге.

## Вариант 1: GitHub Pages

Я добавил workflow `.github/workflows/deploy-site.yml`, который публикует папку `site/` в GitHub Pages.

Что нужно сделать в GitHub:

1. Запушить текущую ветку в GitHub.
2. Открыть репозиторий на GitHub.
3. Перейти в `Settings` → `Pages`.
4. В поле `Source` выбрать `GitHub Actions`.
5. Перейти во вкладку `Actions`.
6. Запустить workflow `Deploy Weather Muse site to GitHub Pages` вручную или сделать push в ветку `main`/`work`.
7. После успешного запуска GitHub покажет URL опубликованного сайта в результате workflow.

Плюсы: бесплатно, без отдельного сервера, деплой будет повторяться автоматически после изменений в `site/`.

## Вариант 2: Netlify

Я добавил файл `netlify.toml`, чтобы Netlify сразу понимал, какую папку публиковать.

Настройки при создании сайта в Netlify:

- Repository: этот репозиторий.
- Build command: можно оставить пустым или использовать команду из `netlify.toml`.
- Publish directory: `site`.

После деплоя Netlify выдаст публичный URL вида `https://your-site-name.netlify.app`.

## Вариант 3: Cloudflare Pages

Настройки проекта в Cloudflare Pages:

- Framework preset: `None` или `Static HTML`.
- Build command: пусто.
- Build output directory: `site`.

После деплоя Cloudflare выдаст URL вида `https://project-name.pages.dev`.

## Вариант 4: Vercel

Настройки проекта в Vercel:

- Framework preset: `Other`.
- Build command: пусто.
- Output directory: `site`.

Если Vercel попросит команду сборки, укажите:

```bash
echo "Static site: no build required"
```

## Важные требования после публикации

У опубликованного сайта должен быть доступ из браузера пользователя к внешним сервисам:

- `https://api.open-meteo.com` — прогноз погоды.
- `https://geocoding-api.open-meteo.com` — поиск города по названию.
- `https://tile.openstreetmap.org` — тайлы карты.
- `https://unpkg.com` — библиотека Leaflet.

Если какой-то из этих адресов заблокирован, сайт откроется, но карта или прогноз могут не работать.

## Что нужно от владельца проекта

Я могу подготовить код и конфиги для деплоя, но для фактической публикации нужен доступ к вашему GitHub/Netlify/Cloudflare/Vercel аккаунту. Самый простой путь — GitHub Pages:

1. Запушить этот репозиторий в GitHub.
2. Включить `Settings` → `Pages` → `GitHub Actions`.
3. Запустить workflow `Deploy Weather Muse site to GitHub Pages`.
