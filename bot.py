import os, re, tempfile, shutil, threading, glob
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("FALTA BOT_TOKEN en Render!")

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Yolu activo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hola {update.effective_user.first_name} Envía el link 📥")

async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    m = re.search(r'https?://\S+', text)
    if not m: return
    url = m.group(0).strip()

    status = await update.message.reply_text("descargando⌛")
    tmpdir = tempfile.mkdtemp()

    opts = {
        'format': 'best[filesize<1800M]/best',
        'outtmpl': f'{tmpdir}/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': False,
        'merge_output_format': 'mp4',
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        files = glob.glob(f"{tmpdir}/*")
        if not files:
            raise Exception("No se descargó nada")

        for f in files[:5]:
            with open(f,'rb') as v:
                await update.message.reply_video(video=v, caption="Aquí tienes 💙")
        await status.delete()
    except Exception as e:
        print(f"ERROR: {e}")
        await status.edit_text(f"No pude 😅 {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

# Flask en hilo
threading.Thread(target=run_flask, daemon=True).start()

print("Iniciando bot...")
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dl))
app.run_polling()
