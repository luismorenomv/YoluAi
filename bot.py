import os, re, tempfile
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Yolu Downloader Activo 💙"

# /start simple
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mándame el link y te lo bajo 💙\nFB / IG / YT / Erome / Threads / X / TikTok")

# Función principal de descarga
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    match = re.search(r'https?://\S+', text)
    if not match:
        return
    url = match.group(0)

    # Quitar parametros que joden
    url = url.split('?')[0] if 'erome.com' in url else url

    msg = await update.message.reply_text("Bajando... ⏳")

    tmpdir = tempfile.mkdtemp()
    ydl_opts = {
        'format': 'mp4/best/bestvideo+bestaudio',
        'outtmpl': f'{tmpdir}/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'max_filesize': 1900 * 1024 * 1024, # 1.9GB limite telegram
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', '')
            desc = info.get('description', '')
            caption = f"{title}\n\n{desc[:400]}" if desc else title
            caption = caption[:1024] # limite de telegram

        # Enviar
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, caption=caption[:1000] + " 💙" if caption else "Listo bro 💙")

        await msg.delete()

    except Exception as e:
        print(f"Error con {url}: {e}")
        await msg.edit_text(f"No pude bajar ese link 😅\nPrueba con otro.\nError: {str(e)[:200]}")
    finally:
        # limpiar
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    # Flask en segundo plano
    threading.Thread(target=run_flask, daemon=True).start()

    print("Bot iniciando polling...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()
