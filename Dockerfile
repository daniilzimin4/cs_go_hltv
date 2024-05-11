FROM python:3.9-slim

ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}

WORKDIR /main

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]