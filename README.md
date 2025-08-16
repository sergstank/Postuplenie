# ITMO Programs Helper Bot (AI vs AI Product)

Быстрый MVP-бот для поступающего, который:
1) собирает данные с двух страниц программ ИТМО и учебных планов,
2) строит локальный поиск по корпусу (TF‑IDF),
3) отвечает только по этим двум программам,
4) рекомендует элективы на основе профиля абитуриента.

## Запуск (быстрый путь)
```bash
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # вставьте TELEGRAM_TOKEN
python -m src.scraping.fetch_programs            # скачает страницы/планы и соберёт programs.json
python -m src.rag.build_index                    # построит индекс для поиска
python -m src.bot.run_telegram                   # запустит Telegram‑бота
# при отсутствии токена можно запустить CLI:
python -m src.bot.cli_demo
```

## Что внутри
- **scraping/fetch_programs.py** — качает 2 страницы и PDF-планы, парсит/нормализует в `src/data/programs.json`.
- **rag/build_index.py** — собирает корпус (описания + планы) и строит TF‑IDF индекс.
- **bot/run_telegram.py** — Telegram-бот (aiogram-like поведение на python-telegram-bot).
- **bot/recommend.py** — простые рекомендации по элективам.
- **bot/dialog.py** — логика диалога и guardrails (проверка релевантности).
- **bot/cli_demo.py** — консольная версия для проверки без Telegram.

## Архитектура
```
Scraper -> programs.json + corpus -> TF-IDF index -> Dialog Bot (Retriever + Recommender + Guardrails)
```

## Замечания
- Парсинг PDF сделан «best effort». Если структура нестандартна, в `programs.json` можно руками поправить раздел `courses`/`electives`.
- Индекс небольшой и локальный, без LLM и эмбеддингов — быстро и воспроизводимо.
- Бот отвечает только по двум программам — все нерелевантные вопросы отсекаются.

## Что отправлять в решении
- Архив/репозиторий **со всем кодом**, `programs.json`, краткое описание подхода (этот README).
- Скриншот/видео работы бота (опционально).
```


## Быстро выложить в GitHub

```bash
# в корне проекта (itmo-bot)
git init
git branch -M main
git remote add origin https://github.com/sergstank/Postuplenie.git
git add .
git commit -m "Initial commit: ITMO helper bot MVP"
git push -u origin main
```

> Не коммитьте `.env` — токен храните локально или в Secrets репозитория.

## Docker запуск

Локально через Docker:

```bash
docker build -t itmo-bot .
docker run -e TELEGRAM_TOKEN=YOUR_TOKEN --name itmo-bot --rm itmo-bot
```

Или через `docker-compose`:

```bash
export TELEGRAM_TOKEN=YOUR_TOKEN
docker compose up --build -d
```

