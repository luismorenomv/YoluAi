import os
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
    return "Bot ON"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

def get_medias(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, headers=headers, timeout=20).text
    soup = BeautifulSoup(html, 'html.parser')
    medias = []
    for v in soup.find_all('video'):
        s = v.find('source')
        if s and s.get('src'):
            medias.append(s['src'])
        if v.get('src'):
            medias.append(v.get('src'))
    for img in soup.select('img.img-front'):
        src = img.get('data-src') or img.get('src')
        if src and src.startswith('http'):
            medias.append(src)
    return list(dict.fromkeys(medias))

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "erome.com/a/" not in text:
        return
    url = text.split()[0]
    await update.message.reply_text("⏳ Descargando...")
    try:
        medias = get_medias(url)
        if not medias:
            await update.message.reply_text("❌ No encontre nada")
            return
        for media_url in medias[:15]:
            try:
                r = requests.get(media_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
                ext = ".mp4" if ".mp4" in media_url else ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(r.content)
                    path = tmp.name
                if ext == ".mp4":
                    await update.message.reply_video(video=open(path, 'rb'))
                else:
                    await update.message.reply_photo(photo=open(path, 'rb'))
                os.remove(path)
            except:
                continue
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    print("Bot iniciado...")
    app.run_polling()
