import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8515311616:AAFB2CKRdXvD6XM0xaUCWcAhIF-acCu3__Y")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "c344227bf182450889004b93f8006fd7")
AVATAR_ID = "3f56a997304e41bc8bd73ab33fc8fd71"

SCRIPT = """Ты живёшь чужую жизнь. И где-то внутри ты это знаешь.

Я — Нейро Монах. Медитация, Рейки, древние знания — и современное понимание себя.

Астрология. Руны. Human Design. Не магия — карта твоей души.

Хочешь понять кто ты — подписывайся."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧘 Нейро Монах Бот\n\n/video — создать видео\n/status <video_id> — проверить статус")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Создаю видео через HeyGen...")
    headers = {"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"}
    payload = {
        "video_inputs": [{
            "character": {"type": "talking_photo", "talking_photo_id": AVATAR_ID},
            "voice": {"type": "text", "input_text": SCRIPT, "voice_id": HEYGEN_API_KEY}
        }],
        "dimension": {"width": 720, "height": 1280},
        "title": "Нейро Монах"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.heygen.com/v2/video/generate", json=payload, headers=headers) as resp:
                data = await resp.json()
        video_id = data.get("data", {}).get("video_id") or data.get("video_id")
        if video_id:
            await update.message.reply_text(f"✅ Видео создаётся!\n\nID: `{video_id}`\n\nЧерез 3-5 минут:\n/status {video_id}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ Ошибка: {str(data)[:200]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи ID: /status <video_id>")
        return
    video_id = context.args[0]
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.heygen.com/v1/video_status.get?video_id={video_id}", headers=headers) as resp:
                data = await resp.json()
        video_data = data.get("data", {})
        status_val = video_data.get("status", "unknown")
        video_url = video_data.get("video_url", "")
        if status_val == "completed" and video_url:
            await update.message.reply_text(f"🎬 Готово!\n\n⬇️ {video_url}")
        elif status_val == "processing":
            await update.message.reply_text("⏳ Ещё рендерится...")
        else:
            await update.message.reply_text(f"Статус: {status_val}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(CommandHandler("status", status))
    print("Бот запущен...")
    app.run_polling()
  
