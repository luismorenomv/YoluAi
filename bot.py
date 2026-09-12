import os
import tempfile
from threading import Thread
from flask import Flask
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot Erome ON"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

async def erome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "erome.com" not in url:
        return
    await update.message.reply_text("⏳ Descargando de Erome...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ydl_opts = {
                'outtmpl': f'{tmp}/%(title)s.%(ext)s',
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
            
            with open(file_path, 'rb') as f:
                await update.message.reply_video(video=f, caption="✅ Listo")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, erome_handler))
    print("Bot Erome iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()
