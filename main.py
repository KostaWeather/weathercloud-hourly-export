import os
import asyncio
import json
import csv
import requests
import gspread
from google.oauth2.service_account import Credentials
from playwright.async_api import async_playwright

WEATHER_LOGIN = os.getenv("WEATHER_LOGIN")
WEATHER_PASSWORD = os.getenv("WEATHER_PASSWORD")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1ruHPdZpo0U5NN_1qDfb46QA8x-Zihax6soA7pQ5fvu8/edit#gid=0"


async def login_and_get_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://app.weathercloud.net/", wait_until="domcontentloaded")

        # Открываем логин сразу через JS
        await page.evaluate("""
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({
                    username: '%s',
                    password: '%s'
                })
            })
        """ % (WEATHER_LOGIN, WEATHER_PASSWORD))

        await page.wait_for_timeout(5000)

        cookies = await context.cookies()
        await browser.close()

        return cookies


def download_csv_with_requests(cookies):
    session = requests.Session()

    for c in cookies:
        session.cookies.set(c["name"], c["value"])

    response = session.get("https://app.weathercloud.net/data/download/file/Weathercloud%20Yagody%20ru%202026-02.csv")

    with open("weather.csv", "wb") as f:
        f.write(response.content)

    return "weather.csv"


def upload_to_sheets(csv_path):
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)

    sheet = client.open_by_url(SPREADSHEET_URL).sheet1

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    sheet.clear()
    sheet.update(rows)


async def main():
    cookies = await login_and_get_cookies()
    csv_path = download_csv_with_requests(cookies)
    upload_to_sheets(csv_path)
    print("SUCCESS")


if __name__ == "__main__":
    asyncio.run(main())
