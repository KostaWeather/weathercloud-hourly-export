import os
import asyncio
import json
import csv
from playwright.async_api import async_playwright
import gspread
from google.oauth2.service_account import Credentials

WEATHER_LOGIN = os.getenv("WEATHER_LOGIN")
WEATHER_PASSWORD = os.getenv("WEATHER_PASSWORD")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1ruHPdZpo0U5NN_1qDfb46QA8x-Zihax6soA7pQ5fvu8/edit#gid=0"


async def download_csv():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        print("Opening Weathercloud...")
        await page.goto("https://app.weathercloud.net/", wait_until="domcontentloaded")

        # Cookie banner
        try:
            await page.click("text=I agree", timeout=5000)
            print("Cookie accepted")
        except:
            pass

        print("Opening login modal...")
        await page.click("text=Войти")

        # Ждём появления формы логина
        await page.wait_for_selector("input[type='text']", timeout=60000)

        print("Filling credentials...")
        await page.fill("input[type='text']", WEATHER_LOGIN)
        await page.fill("input[type='password']", WEATHER_PASSWORD)

        await page.click("button:has-text('Войти')")

        # Ждём смены URL (признак входа)
        await page.wait_for_url("**/home", timeout=60000)

        print("Login successful")

        # Закрываем popup Upgrade если появится
        try:
            await page.click("text=Try it free for 30 days", timeout=3000)
        except:
            pass

        print("Going to database...")
        await page.goto("https://app.weathercloud.net/database", wait_until="domcontentloaded")

        # Ждём появления кнопки Export
        await page.wait_for_selector("button", timeout=60000)

        print("Downloading CSV...")
        async with page.expect_download() as download_info:
            await page.click("button:has-text('Export')")

        download = await download_info.value
        path = await download.path()

        print("Download complete")

        await browser.close()
        return path


def upload_to_sheets(csv_path):
    print("Uploading to Google Sheets...")

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

    print("Google Sheets updated successfully")


async def main():
    csv_path = await download_csv()
    upload_to_sheets(csv_path)
    print("SUCCESS")


if __name__ == "__main__":
    asyncio.run(main())
