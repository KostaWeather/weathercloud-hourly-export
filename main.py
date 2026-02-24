import os
import csv
import json
import requests
import gspread
from google.oauth2.service_account import Credentials


WEATHER_LOGIN = os.getenv("WEATHER_LOGIN")
WEATHER_PASSWORD = os.getenv("WEATHER_PASSWORD")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

SPREADSHEET_ID = "1ruHPdZpo0U5NN_1qDfb46QA8x-Zihax6soA7pQ5fvu8"


def download_csv():
    session = requests.Session()

    # 1️⃣ Получаем страницу логина чтобы получить csrf-token
    r = session.get("https://app.weathercloud.net/login")
    r.raise_for_status()

    # Laravel CSRF
    import re
    token = re.search(r'name="csrf-token" content="([^"]+)"', r.text)
    if not token:
        raise Exception("CSRF token not found")

    csrf_token = token.group(1)

    # 2️⃣ Логинимся
    login_data = {
        "_token": csrf_token,
        "email": WEATHER_LOGIN,
        "password": WEATHER_PASSWORD
    }

    headers = {
        "Referer": "https://app.weathercloud.net/login"
    }

    r = session.post(
        "https://app.weathercloud.net/login",
        data=login_data,
        headers=headers
    )

    r.raise_for_status()

    # 3️⃣ Запрашиваем CSV напрямую
    csv_response = session.get("https://app.weathercloud.net/database/export")

    csv_response.raise_for_status()

    if "text/csv" not in csv_response.headers.get("Content-Type", ""):
        raise Exception("Did not receive CSV file")

    file_path = "/tmp/weather.csv"
    with open(file_path, "wb") as f:
        f.write(csv_response.content)

    return file_path


def upload_to_sheets(csv_path):
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


def main():
    csv_path = download_csv()
    upload_to_sheets(csv_path)


if __name__ == "__main__":
    main()
