FROM python:3.12-slim

RUN apt-get update && apt-get install -y wget curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install playwright \
    && playwright install chromium

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
