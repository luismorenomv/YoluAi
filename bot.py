import os, re, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Soy Yolu 💙 Mándame un link de YouTube o TikTok y te lo bajo sin marca 🚀")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    m = re.search(r'https?://\S+', text)
    if not m:
        await update.message.reply_text("Mándame un link válido bro 😅")
        return
    url = m.group(0)

    if "facebook.com" in url or "fb.watch" in url or "instagram.com" in url:
        await update.message.reply_text("Bro, Meta bloqueó FB e IG en bots 😭\nPero YouTube y TikTok sí sirven al 100%. Mándame uno de esos!")
        return

    await update.message.reply_text("Bajando... ⏳")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': '/tmp/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        def run():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        file = await asyncio.to_thread(run)
        with open(file, 'rb') as v:
            await update.message.reply_video(v, caption="Listo bro 💙 @YoluAiBot")
        os.remove(file)
    except Exception as e:
        await update.message.reply_text(f"No pude con ese link 😅 Prueba con YouTube")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.run_polling()

if __name__ == "__main__":
    main()
