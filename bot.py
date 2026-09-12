from keep_alive import keep_alive
keep_alive()
import os, re, yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
URL_REGEX = r"https?://[^\s]+"

async def start(update, context):
    await update.message.reply_text("Soy Yolu 💙 Mandame links y te los bajo. Si escribes mp3 te bajo solo audio.")

async def handle(update, context):
    text = update.message.text or ""
    urls = re.findall(URL_REGEX, text)
    if not urls:
        await update.message.reply_text("Te escucho bro")
        return
    url = urls[0]
    is_mp3 = "mp3" in text.lower()
    await update.message.reply_text("Bajando...")
    try:
        if is_mp3:
            opts = {'format':'bestaudio/best','outtmpl':'audio.%(ext)s','postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}],'quiet':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            await update.message.reply_audio(open('audio.mp3','rb'))
            os.remove('audio.mp3')
        else:
            opts = {'outtmpl':'video.%(ext)s','format':'best','quiet':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)
            await update.message.reply_video(open(file,'rb'))
            os.remove(file)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
