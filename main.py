import os
import asyncio
from playwright.async_api import async_playwright
import csv
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

WEATHER_LOGIN = os.getenv("WEATHER_LOGIN")
WEATHER_PASSWORD = os.getenv("WEATHER_PASSWORD")

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS_JSON")
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1ruHPdZpo0U5NN_1qDfb46QA8x-Zihax6soA7pQ5fvu8/edit#gid=0"


async def download_csv():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        await page.goto("https://app.weathercloud.net/")

        # Cookie banner
        try:
            await page.click("text=I agree", timeout=5000)
        except:
            pass

        # Нажимаем "Войти"
        await page.click("text=Войти")

        # Ждём форму
        await page.wait_for_selector("input[type='text']", timeout=60000)

        await page.fill("input[type='text']", WEATHER_LOGIN)
        await page.fill("input[type='password']", WEATHER_PASSWORD)

        await page.click("button:has-text('Войти')")

        await page.wait_for_load_state("networkidle")

        # Закрываем popup Upgrade если появится
        try:
            await page.click("text=Try it free for 30 days", timeout=3000)
        except:
            pass

        # Переходим в Database
        await page.goto("https://app.weathercloud.net/database")
        await page.wait_for_load_state("networkidle")

        # Нажимаем Export
        async with page.expect_download() as download_info:
            await page.click("text=Export")
        download = await download_info.value

        file_path = await download.path()

        await browser.close()
        return file_path


def upload_to_sheets(csv_path):
    creds_dict = eval(GOOGLE_CREDENTIALS)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(SPREADSHEET_URL)
    worksheet = sh.sheet1

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    worksheet.clear()
    worksheet.update(rows)


async def main():
    csv_path = await download_csv()
    upload_to_sheets(csv_path)
    print("SUCCESS: Weather data updated.")


if __name__ == "__main__":
    asyncio.run(main())
