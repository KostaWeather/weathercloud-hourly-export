import asyncio
import os
import csv
import json
from playwright.async_api import async_playwright
import gspread
from google.oauth2.service_account import Credentials


# =========================
# ENV
# =========================
WEATHER_LOGIN = os.getenv("WEATHER_LOGIN")
WEATHER_PASSWORD = os.getenv("WEATHER_PASSWORD")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

SPREADSHEET_ID = "1ruHPdZpo0U5NN_1qDfb46QA8x-Zihax6soA7pQ5fvu8"


# =========================
# DOWNLOAD CSV
# =========================
async def download_csv():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        print("Opening Weathercloud...")
        await page.goto("https://app.weathercloud.net/")

        # Cookie
        try:
            await page.click("text=I agree", timeout=5000)
        except:
            pass

        print("Opening login modal...")
        await page.click("text=Войти")

        await page.wait_for_selector("input[type='text']", timeout=60000)

        print("Filling credentials...")
        await page.fill("input[type='text']", WEATHER_LOGIN)
        await page.fill("input[type='password']", WEATHER_PASSWORD)

        await page.click("button:has-text('Войти')")

        await page.wait_for_load_state("networkidle")

        # Upgrade popup если есть
        try:
            await page.click("text=Try it free for 30 days", timeout=3000)
        except:
            pass

        await page.goto("https://app.weathercloud.net/database")
        await page.wait_for_load_state("networkidle")

        print("Downloading CSV...")
        async with page.expect_download() as download_info:
            await page.click("text=Export")

        download = await download_info.value

        # 🔥 ВАЖНО — сохраняем вручную
        file_path = "/tmp/weather.csv"
        await download.save_as(file_path)

        await browser.close()

        print("Download complete")
        return file_path


# =========================
# UPLOAD TO GOOGLE SHEETS
# =========================
def upload_to_sheets(csv_path):
    print("Uploading to Google Sheets...")

    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.sheet1

    worksheet.clear()

    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = list(csv.reader(f))

    worksheet.update("A1", reader)

    print("Upload complete")


# =========================
# MAIN
# =========================
async def main():
    csv_path = await download_csv()
    upload_to_sheets(csv_path)


if __name__ == "__main__":
    asyncio.run(main())
