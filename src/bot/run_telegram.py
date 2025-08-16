import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from .dialog import BotCore, UserState

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
core = BotCore()
users = {}

def get_state(uid):
    if uid not in users:
        users[uid] = UserState()
    return users[uid]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    state.stage = "greet"
    await update.message.reply_text(core.welcome())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(core.help_text())

async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    await update.message.reply_text(core.reset(state))

async def compare_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    await update.message.reply_text(core.compare_programs(state))

async def recommend_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    await update.message.reply_text(core.recommend(state))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    text = update.message.text.strip()
    if state.stage == "greet":
        msg = core.handle_profile(text, state)
        await update.message.reply_text(msg)
    else:
        msg = core.answer(text, state)
        await update.message.reply_text(msg)

def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN отсутствует в .env")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CommandHandler("compare", compare_cmd))
    app.add_handler(CommandHandler("recommend", recommend_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
