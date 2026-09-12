import os
import re
import tempfile
import requests
from threading import Thread
from flask import Flask
from bs4 import BeautifulSoup
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

def get_erome_medias(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    html = requests.get(url, headers=headers, timeout=15).text
    soup = BeautifulSoup(html, 'html.parser')
    medias = []
    # videos
    for v in soup.find_all('video'):
        s = v.find('source')
        if s and s.get('src'):
            medias.append(s['src'])
        elif v.get('src'):
            medias.append(v.get('src'))
    # imagenes
    for img in soup.select('.media-group img, img.img-front'):
        src = img.get('data-src') or img.get('src')
        if src and 'erome' in src:
            medias.append(src)
    return list(dict.fromkeys(medias)) # sin duplicados

async def erome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "erome.com/a/" not in url:
        return

    await update.message.reply_text("⏳ Descargando de Erome...")

    try:
        medias = get_erome_medias(url)
        if not medias:
            await update.message.reply_text("❌ No encontré archivos. El álbum puede ser privado o fue borrado.")
            return

        for media_url in medias[:15]:
            try:
                if any(x in media_url for x in ['.mp4','.m4v','.mov']):
                    await update.message.reply_video(video=media_url)
                else:
                    await update.message.reply_photo(photo=media_url)
            except Exception as e:
                # Si falla enviar por URL, intenta descargar
                r = requests.get(media_url, headers={"User-Agent":"Mozilla/5.0"})
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4" if ".mp4" in media_url else ".jpg") as tmp:
                    tmp.write(r.content)
                    tmp_path = tmp.name
                if ".mp4" in media_url:
                    await update.message.reply_video(video=open(tmp_path,'rb'))
                else:
                    await update.message.reply_photo(photo=open(tmp_path,'rb'))
                os.remove(tmp_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, erome_handler))
    print("Bot Erome iniciado...")
    app.run_polling()
