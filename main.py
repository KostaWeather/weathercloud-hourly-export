import os
import json
import asyncio
import tempfile
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from playwright.async_api import async_playwright

WEATHER_LOGIN = os.environ["WEATHER_LOGIN"]
WEATHER_PASSWORD = os.environ["WEATHER_PASSWORD"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1ruHPdZpo0U5NN_1qDfb46QA8x-Zihax6soA7pQ5fvu8/edit#gid=0"


async def download_csv():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context()
        page = await context.new_page()

        print("Opening Weathercloud...")
        await page.goto("https://app.weathercloud.net/")

        # Cookie banner
        try:
            await page.click("text=I agree", timeout=5000)
        except:
            pass

        print("Opening login...")
        await page.click("text=Login")

        await page.wait_for_selector("input[type='text']")

        print("Filling credentials...")
        await page.fill("input[type='text']", WEATHER_LOGIN)
        await page.fill("input[type='password']", WEATHER_PASSWORD)

        await page.click("button[type='submit']")

        # ждём вход
        await page.wait_for_selector("text=Database", timeout=60000)

        print("Opening database...")
        await page.goto("https://app.weathercloud.net/database")
        await page.wait_for_load_state("networkidle")

        print("Triggering export...")

        async with page.expect_response(
            lambda response: "/data/csv/" in response.url
            and response.request.method == "POST"
        ) as resp_info:
            await page.click("text=Export")

        response = await resp_info.value
        content = await response.body()

        # сохраняем во временный файл
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp_file.write(content)
        tmp_file.close()

        await browser.close()

        print("CSV downloaded.")
        return tmp_file.name


def upload_to_google(csv_path):
    print("Uploading to Google Sheets...")

    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)

    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(SPREADSHEET_URL)
    worksheet = sh.sheet1

    df = pd.read_csv(csv_path)

    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("Upload complete.")


async def main():
    csv_path = await download_csv()
    upload_to_google(csv_path)


if __name__ == "__main__":
    asyncio.run(main())
