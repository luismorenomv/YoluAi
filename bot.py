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
    return "Bot Erome ON - funcionando"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

def get_erome_medias(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    html = requests.get(url, headers=headers, timeout=20).text
    soup = BeautifulSoup(html, 'html.parser')
    medias = []
    for v in soup.find_all('video'):
        s = v.find('source')
        if s and s.get('src'):
            medias.append(s['src'])
        if v.get('src'):
            medias.append(v.get('src'))
    for img in soup.select('img.img-front,.media-group img'):
        src = img.get('data-src') or img.get('src') or img.get('data-lazy-src')
        if src and src.startswith('http'):
            medias.append(src)
    # quitar duplicados manteniendo orden
    return list(dict.fromkeys(medias))

async def erome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "erome.com/a/" not in text:
        return

    # extraer url
    url = text.split()[0]

    await update.message.reply_text("⏳ Descargando de Erome...")

    try:
        medias = get_erome_medias(url)
        if not medias:
            await update.message.reply_text("❌ No encontré nada. Álbum privado o borrado.")
            return

        for media_url in medias[:15]:
            try:
                headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.erome.com/"}
                r = requests.get(media_url, headers=headers, timeout=30
