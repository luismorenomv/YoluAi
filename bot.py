import os, re, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Yolu bot activo 💙"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Soy Yolu 💙 Mándame link de YouTube o TikTok 🚀")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    m = re.search(r'https?://\S+', text)
    if not m: return
    url = m.group(0)
    await update.message.reply_text("Bajando... ⏳")
    ydl_opts = {'format': 'best[ext=mp4]/best', 'outtmpl': '/tmp/%(id)s.%(ext)s', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
        with open(file, 'rb') as v:
            await update.message.reply_video(v, caption="Listo bro 💙")
        os.remove(file)
    except Exception as e:
        print(e)
        await update.message.reply_text("No pude con ese link 😅")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("Bot iniciando polling...")
    app.run_polling()
