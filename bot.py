import os, re, tempfile, shutil, threading, asyncio, glob
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Yolu activo - online"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name
    await update.message.reply_text(f"Hola {nombre} Envía el link que yo te lo descargo 📥⚡")

async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    m = re.search(r'https?://\S+', text)
    if not m:
        nombre = update.effective_user.first_name
        await update.message.reply_text(f"Hola {nombre} Envía el link que yo te lo descargo 📥⚡")
        return

    url = m.group(0).strip()
    # limpia erome que trae?v= etc
    if "erome.com" in url:
        url = url.split("?")[0].split("&")[0]

    status = await update.message.reply_text("Por favor espere un momento...⌛")
    tmpdir = tempfile.mkdtemp()

    opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{tmpdir}/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
        'extractor_args': {'youtube': {'player_client': ['android','web']}},
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info: # si es playlist/album de erome
                info = info['entries'][0]

            # ESTA ES LA CORRECCIÓN DEL.NA - busca cualquier archivo que se haya bajado
            files = glob.glob(f"{tmpdir}/*.*")
            if not files:
                files = glob.glob(f"{tmpdir}/*")

            if not files:
                raise FileNotFoundError("yt-dlp no creó archivo")

            file_path = files[0]
            title = info.get('title','')[:900]

        with open(file_path,'rb') as v:
            await update.message.reply_video(video=v, caption=f"{title} 💙")

        await status.delete()

    except Exception as e:
        print(f"ERROR URL {url}: {e}")
        await status.edit_text(f"No pude 😅 {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

# Flask en hilo aparte
threading.Thread(target=run_flask, daemon=True).start()

# Bot polling
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dl))

print("Bot Yolu iniciando...")
app.run_polling()
