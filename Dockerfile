# Simple Dockerfile to run the Telegram bot
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Expect TELEGRAM_TOKEN provided via environment
CMD ["python", "-m", "src.bot.run_telegram"]
