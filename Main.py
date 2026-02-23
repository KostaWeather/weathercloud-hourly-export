import asyncio
import os
import json
import tempfile
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from playwright.async_api import async_playwright

WEATHER_LOGIN = os.getenv("WEATHER_LOGIN")
WEATHER_PASSWORD = os.getenv("WEATHER_PASSWORD")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS_JSON")

SPREADSHEET_ID = "1ruHPdZpo0U5NN_1qDfb46QA8x-Zihax6soA7pQ5fvu8"

async def download_csv():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        await page.goto("https://app.weathercloud.net/")
        await page.fill('input[name="email"]', WEATHER_LOGIN)
        await page.fill('input[name="password"]', WEATHER_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(4000)

        await page.goto("https://app.weathercloud.net/database")
        await page.wait_for_timeout(3000)

        async with page.expect_download() as download_info:
            await page.click("text=Export")

        download = await download_info.value

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        await download.save_as(temp_file.name)

        await browser.close()
        return temp_file.name

def upload_to_sheets(csv_path):
    creds_dict = json.loads(GOOGLE_CREDENTIALS)
    creds = Credentials.from_service_account_info(creds_dict)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    df = pd.read_csv(csv_path)

    existing_data = sheet.get_all_values()
    existing_rows = len(existing_data)

    new_data = df.values.tolist()

    if existing_rows == 0:
        sheet.append_rows([df.columns.tolist()])
        sheet.append_rows(new_data)
    else:
        sheet.append_rows(new_data)

async def main():
    csv_path = await download_csv()
    upload_to_sheets(csv_path)

asyncio.run(main())
