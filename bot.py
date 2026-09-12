import os, re, tempfile, shutil, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
print(f"Token cargado: {'SI' if TOKEN else 'NO'}")

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Yolu activo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola [Nombre] envía el link y te lo descargo📥⚡")

async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    m = re.search(r'https?://\S+', text)
    if not m: return
    url = m.group(0)
    status = await update.message.reply_text("por favor espere un momento... ⏳")
    tmpdir = tempfile.mkdtemp()
    opts = {'format':'mp4/best','outtmpl':f'{tmpdir}/%(id)s.%(ext)s','quiet':True,'noplaylist':True,'nocheckcertificate':True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
            cap = (info.get('title','')[:900])+" 💙"
        with open(file,'rb') as v:
            await update.message.reply_video(v, caption=cap)
        await status.delete()
    except Exception as e:
        print(e)
        await status.edit_text(f"No pude 😅 {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dl))
    print("Bot iniciando polling...")
    app.run_polling()
