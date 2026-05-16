const translations = {
  ru: {
    eyebrow: "Погодная ведущая с ИИ",
    title: "Узнайте прогноз для своего города",
    lead: "Выберите город и страну — цифровая ведущая расскажет текущую погоду или прогноз на несколько дней.",
    cityLabel: "Город",
    countryLabel: "Страна",
    forecastLegend: "Период прогноза",
    modeCurrent: "Сейчас",
    mode3: "3 дня",
    mode10: "7–10 дней",
    submit: "Показать прогноз",
    sourcePrefix: "Данные:",
    welcomeSpeech: "Привет! Я готова рассказать прогноз. Введите город и выберите период.",
    forecastEyebrow: "Прогноз",
    forecastTitle: "Карточки погоды",
    loading: "Ищу город и загружаю прогноз…",
    notFound: "Город не найден. Уточните название города и страны.",
    networkError: "Не удалось загрузить прогноз. Попробуйте ещё раз.",
    currentIntro: "Сейчас в {place}: {temperature}°C, {condition}. Ветер {wind} км/ч.",
    forecastIntro: "Прогноз для {place} на {days} дн.: от {min}°C до {max}°C. {condition}.",
    today: "Сегодня",
    max: "Макс.",
    min: "Мин.",
    rain: "Осадки",
    wind: "Ветер",
    cityPlaceholder: "Москва",
    countryPlaceholder: "Россия",
    locale: "ru-RU",
  },
  en: {
    eyebrow: "AI weather presenter",
    title: "Get the forecast for your city",
    lead: "Choose a city and country — the digital presenter will speak the current weather or a multi-day forecast.",
    cityLabel: "City",
    countryLabel: "Country",
    forecastLegend: "Forecast period",
    modeCurrent: "Current",
    mode3: "3 days",
    mode10: "7–10 days",
    submit: "Show forecast",
    sourcePrefix: "Data:",
    welcomeSpeech: "Hi! I am ready to present your forecast. Enter a city and choose a period.",
    forecastEyebrow: "Forecast",
    forecastTitle: "Weather cards",
    loading: "Finding the city and loading the forecast…",
    notFound: "City not found. Please refine the city and country names.",
    networkError: "Could not load the forecast. Please try again.",
    currentIntro: "Right now in {place}: {temperature}°C, {condition}. Wind {wind} km/h.",
    forecastIntro: "Forecast for {place} for {days} days: from {min}°C to {max}°C. {condition}.",
    today: "Today",
    max: "High",
    min: "Low",
    rain: "Precip.",
    wind: "Wind",
    cityPlaceholder: "London",
    countryPlaceholder: "United Kingdom",
    locale: "en-US",
  },
};

const weatherCodes = {
  0: { icon: "☀", ru: "ясно", en: "clear sky" },
  1: { icon: "🌤", ru: "преимущественно ясно", en: "mainly clear" },
  2: { icon: "⛅", ru: "переменная облачность", en: "partly cloudy" },
  3: { icon: "☁", ru: "пасмурно", en: "overcast" },
  45: { icon: "🌫", ru: "туман", en: "fog" },
  48: { icon: "🌫", ru: "изморозь и туман", en: "depositing rime fog" },
  51: { icon: "🌦", ru: "слабая морось", en: "light drizzle" },
  53: { icon: "🌦", ru: "морось", en: "drizzle" },
  55: { icon: "🌧", ru: "сильная морось", en: "dense drizzle" },
  61: { icon: "🌦", ru: "небольшой дождь", en: "slight rain" },
  63: { icon: "🌧", ru: "дождь", en: "rain" },
  65: { icon: "🌧", ru: "сильный дождь", en: "heavy rain" },
  71: { icon: "🌨", ru: "небольшой снег", en: "slight snow" },
  73: { icon: "🌨", ru: "снег", en: "snow" },
  75: { icon: "❄", ru: "сильный снег", en: "heavy snow" },
  80: { icon: "🌦", ru: "ливни", en: "rain showers" },
  81: { icon: "🌧", ru: "сильные ливни", en: "heavy rain showers" },
  82: { icon: "⛈", ru: "очень сильные ливни", en: "violent rain showers" },
  95: { icon: "⛈", ru: "гроза", en: "thunderstorm" },
  96: { icon: "⛈", ru: "гроза с градом", en: "thunderstorm with hail" },
  99: { icon: "⛈", ru: "сильная гроза с градом", en: "heavy thunderstorm with hail" },
};

const dom = {
  form: document.querySelector("#weather-form"),
  city: document.querySelector("#city"),
  country: document.querySelector("#country"),
  status: document.querySelector("#status"),
  speech: document.querySelector("#speech-text"),
  cards: document.querySelector("#forecast-cards"),
  orb: document.querySelector("#weather-orb"),
  langButtons: document.querySelectorAll(".lang-button"),
};

let currentLang = localStorage.getItem("weather-muse-lang") || "ru";
let map;
let marker;

function t(key) {
  return translations[currentLang][key];
}

function interpolate(template, values) {
  return Object.entries(values).reduce((message, [key, value]) => message.replace(`{${key}}`, value), template);
}

function initMap() {
  map = L.map("map", {
    zoomControl: false,
    attributionControl: true,
  }).setView([48.8566, 2.3522], 5);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("weather-muse-lang", lang);
  document.documentElement.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    node.textContent = translations[lang][key];
  });

  dom.city.placeholder = t("cityPlaceholder");
  dom.country.placeholder = t("countryPlaceholder");
  dom.langButtons.forEach((button) => button.classList.toggle("is-active", button.dataset.lang === lang));
}

function setStatus(message, isError = false) {
  dom.status.textContent = message;
  dom.status.classList.toggle("is-error", isError);
}

function getWeatherMeta(code) {
  return weatherCodes[code] || { icon: "🌡", ru: "погодные условия обновляются", en: "weather conditions are updating" };
}

async function geocode(city, country) {
  const url = new URL("https://geocoding-api.open-meteo.com/v1/search");
  url.search = new URLSearchParams({
    name: `${city}, ${country}`,
    count: "5",
    language: currentLang,
    format: "json",
  });

  const response = await fetch(url);
  if (!response.ok) throw new Error("Geocoding failed");
  const data = await response.json();
  const normalizedCountry = country.trim().toLocaleLowerCase();
  const candidates = data.results || [];

  return candidates.find((item) => item.country?.toLocaleLowerCase() === normalizedCountry) || candidates[0];
}

async function fetchForecast(location) {
  const url = new URL("https://api.open-meteo.com/v1/forecast");
  url.search = new URLSearchParams({
    latitude: location.latitude,
    longitude: location.longitude,
    current: "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
    daily: "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
    forecast_days: "10",
    timezone: "auto",
  });

  const response = await fetch(url);
  if (!response.ok) throw new Error("Forecast failed");
  return response.json();
}

function moveMap(location) {
  const latLng = [location.latitude, location.longitude];
  map.setView(latLng, 10, { animate: true });

  if (marker) {
    marker.setLatLng(latLng);
  } else {
    marker = L.marker(latLng).addTo(map);
  }

  marker.bindPopup(`${location.name}, ${location.country}`).openPopup();
}

function speak(message) {
  dom.speech.textContent = message;

  if (!("speechSynthesis" in window)) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(message);
  utterance.lang = t("locale");
  utterance.rate = 0.96;
  utterance.pitch = 1.05;
  window.speechSynthesis.speak(utterance);
}

function formatDate(dateString, index) {
  if (index === 0) return t("today");
  return new Intl.DateTimeFormat(t("locale"), { weekday: "short", day: "numeric", month: "short" }).format(new Date(dateString));
}

function renderCards(forecast, days) {
  const count = days === "current" ? 1 : Number(days);
  const cards = forecast.daily.time.slice(0, count).map((date, index) => {
    const code = forecast.daily.weather_code[index];
    const meta = getWeatherMeta(code);
    return `
      <article class="forecast-card">
        <strong>${formatDate(date, index)}</strong>
        <div class="icon" aria-hidden="true">${meta.icon}</div>
        <dl>
          <div><dt>${t("max")}</dt><dd>${Math.round(forecast.daily.temperature_2m_max[index])}°C</dd></div>
          <div><dt>${t("min")}</dt><dd>${Math.round(forecast.daily.temperature_2m_min[index])}°C</dd></div>
          <div><dt>${t("rain")}</dt><dd>${forecast.daily.precipitation_probability_max[index]}%</dd></div>
          <div><dt>${t("wind")}</dt><dd>${Math.round(forecast.daily.wind_speed_10m_max[index])} km/h</dd></div>
        </dl>
      </article>
    `;
  });

  dom.cards.innerHTML = cards.join("");
}

function buildSpeech(location, forecast, mode) {
  const place = `${location.name}, ${location.country}`;

  if (mode === "current") {
    const meta = getWeatherMeta(forecast.current.weather_code);
    dom.orb.textContent = meta.icon;
    return interpolate(t("currentIntro"), {
      place,
      temperature: Math.round(forecast.current.temperature_2m),
      condition: meta[currentLang],
      wind: Math.round(forecast.current.wind_speed_10m),
    });
  }

  const days = Number(mode);
  const codes = forecast.daily.weather_code.slice(0, days);
  const dominantCode = codes.sort((a, b) => codes.filter((code) => code === b).length - codes.filter((code) => code === a).length)[0];
  const meta = getWeatherMeta(dominantCode);
  const min = Math.round(Math.min(...forecast.daily.temperature_2m_min.slice(0, days)));
  const max = Math.round(Math.max(...forecast.daily.temperature_2m_max.slice(0, days)));
  dom.orb.textContent = meta.icon;

  return interpolate(t("forecastIntro"), {
    place,
    days,
    min,
    max,
    condition: meta[currentLang],
  });
}

async function handleSubmit(event) {
  event.preventDefault();
  setStatus(t("loading"));

  try {
    const formData = new FormData(dom.form);
    const city = formData.get("city").toString().trim();
    const country = formData.get("country").toString().trim();
    const mode = formData.get("mode").toString();
    const location = await geocode(city, country);

    if (!location) {
      setStatus(t("notFound"), true);
      speak(t("notFound"));
      return;
    }

    const forecast = await fetchForecast(location);
    moveMap(location);
    renderCards(forecast, mode);
    speak(buildSpeech(location, forecast, mode));
    setStatus("");
  } catch (error) {
    console.error(error);
    setStatus(t("networkError"), true);
    speak(t("networkError"));
  }
}

dom.langButtons.forEach((button) => button.addEventListener("click", () => setLanguage(button.dataset.lang)));
dom.form.addEventListener("submit", handleSubmit);

initMap();
setLanguage(currentLang);
