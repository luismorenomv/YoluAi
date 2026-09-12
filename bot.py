import os, re, tempfile, shutil, threading, asyncio, glob
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Yolu Activo"

async def saludo(update: Update):
    nombre = update.effective_user.first_name
    await update.message.reply_text(f"Hola {nombre} Envía el link que yo te lo descargo 📥⚡")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await saludo(update)

async def descargar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    m = re.search(r'https?://\S+', txt)
    if not m:
        await saludo(update)
        return

    url = m.group(0)
    if "erome" in url:
        url = url.split("?")[0].split("#")[0]

    aviso = await update.message.reply_text("descargando⌛")
    tmpdir = tempfile.mkdtemp()

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{tmpdir}/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            files = glob.glob(f"{tmpdir}/*")
            if not files:
                raise Exception("No se descargó")
            real_file = files[0]

        with open(real_file, 'rb') as f:
            await update.message.reply_video(video=f)

        await aviso.delete()
    except Exception as e:
        print(f"ERROR: {e}")
        await aviso.edit_text("No pude bajarlo bro, manda otro link 😅")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
threading.Thread(target=run_flask, daemon=True).start()

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, descargar))
app.run_polling()
