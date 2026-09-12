import os
import re
import tempfile
import requests
from threading import Thread
from flask import Flask
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot ON"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name
    await update.message.reply_text(f"Hola, {nombre} 👋\n\nMándame un link de Erome y te lo descargo directo.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 Solo pega el link de Erome aquí.")

def get_medias(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.erome.com/",
        "Accept": "text/html,application/xhtml+xml"
    }
    session = requests.Session()
    html = session.get(url, headers=headers, timeout=20).text
    soup = BeautifulSoup(html, 'html.parser')
    medias = []

    # Metodo 1: tag video
    for v in soup.find_all('video'):
        s = v.find('source')
        if s and s.get('src'):
            medias.append(s['src'])

    # Metodo 2: Buscar mp4 con regex en todo el html (este es el que funciona)
    mp4s = re.findall(r'https://[^"\'"]+\.mp4[^"\'"]*', html)
    medias.extend(mp4s)

    # Fotos
    for img in soup.select('img.img-front'):
        src = img.get('data-src') or img.get('src')
        if src and src.startswith('http') and 'avatar' not in src:
            medias.append(src)

    return list(dict.fromkeys(medias))

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "erome.com/a/" not in text:
        return
    url = text.split()[0]
    await update.message.reply_text("⏳ Bajando video...")
    try:
        medias = get_medias(url)
        if not medias:
            await update.message.reply_text("❌ Privado o borrado")
            return

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.erome.com/",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9"
        }

        for media_url in medias[:10]:
            try:
                media_url = media_url.replace('\\u002F', '/').replace('\\', '')
                r = requests.get(media_url, headers=headers, stream=True, timeout=90)

                if 'text/html' in r.headers.get('Content-Type',''):
                    continue # Era una pagina de error, no un video

                ext = ".mp4" if ".mp4" in media_url else ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    for chunk in r.iter_content(1024*128):
                        if chunk:
                            tmp.write(chunk)
                    path = tmp.name

                if os.path.getsize(path) < 10000:
                    os.remove(path)
                    continue

                if ext == ".mp4":
                    await update.message.reply_video(video=open(path,'rb'), supports_streaming=True)
                else:
                    await update.message.reply_photo(photo=open(path,'rb'))
                os.remove(path)
            except Exception as e:
                print(f"Error media: {e}")
                continue
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    print("Bot iniciado...")
    app.run_polling()
