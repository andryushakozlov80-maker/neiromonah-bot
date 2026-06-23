import os
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "8515311616:AAFB2CKRdXvD6XM0xaUCWcAhIF-acCu3__Y"
HEYGEN_API_KEY = "c344227bf182450889004b93f8006fd7"
AVATAR_ID = "3f56a997304e41bc8bd73ab33fc8fd71"
VOICE_ID = "c344227bf182450889004b93f8006fd7

SCRIPT = "Ты живёшь чужую жизнь. И где-то внутри ты это знаешь. Я — Нейро Монах. Медитация, Рейки, древние знания. Астрология. Руны. Human Design. Не магия — карта твоей души. Хочешь понять кто ты — подписывайся."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧘 Нейро Монах\n\n/video — создать видео")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Создаю видео...")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://api.heygen.com/v2/video/generate",
                headers={"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"},
                json={"video_inputs": [{"character": {"type": "talking_photo", "talking_photo_id": AVATAR_ID}, "voice": {"type": "text", "input_text": SCRIPT, "voice_id": VOICE_ID}}], "dimension": {"width": 720, "height": 1280}}
            ) as r:
                data = await r.json()
        vid = data.get("data", {}).get("video_id")
        if vid:
            await update.message.reply_text(f"✅ ID: {vid}\nПроверь через 5 мин: /status {vid}")
        else:
            await update.message.reply_text(f"❌ Ответ HeyGen: {str(data)[:300]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи ID: /status ID")
        return
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={context.args[0]}",
                headers={"X-Api-Key": HEYGEN_API_KEY}
            ) as r:
                data = await r.json()
        d = data.get("data", {})
        if d.get("status") == "completed":
            await update.message.reply_text(f"🎬 Готово!\n{d.get('video_url')}")
        else:
            await update.message.reply_text(f"Статус: {d.get('status')}\n{str(data)[:200]}")
    except Exception as e:
        await update.message.reply_text(f"❌ {str(e)}")

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(CommandHandler("status", status))
    app.run_polling()
  
