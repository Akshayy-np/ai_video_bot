from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8599234323:AAGkiqwUbbabe-H2UD13BXOUranrq77GoY0"

from telegram import InputFile

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("Downloading video...")

    filename = "video.mp4"

    ydl_opts = {
        'outtmpl': filename,
        'format': 'best'
    }

    try:
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Send video safely (long timeout)
        with open(filename, "rb") as video:
            await update.message.reply_video(
                video=InputFile(video),
                timeout=120
            )

        # Delete file after sending
        os.remove(filename)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Download or upload failed.")

    url = update.message.text

    await update.message.reply_text("Downloading video...")

    filename = "video.mp4"

    ydl_opts = {
        'outtmpl': filename,
        'format': 'best'
    }

    try:
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Send video back
        with open(filename, "rb") as video:
            await update.message.reply_video(video)

        # Delete after sending
        os.remove(filename)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Download or upload failed.")
    url = update.message.text

    await update.message.reply_text("Downloading video...")

    filename = "video.mp4"

    ydl_opts = {
        'outtmpl': filename,
        'format': 'best'
    }

    try:
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Send video back
        with open(filename, "rb") as video:
            await update.message.reply_video(video)

        # Delete after sending
        os.remove(filename)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Download or upload failed.")
    url = update.message.text

    await update.message.reply_text("Downloading video...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir():
            if file.startswith("video"):
                await update.message.reply_document(open(file, "rb"))
                os.remove(file)

    except Exception:
        await update.message.reply_text("Download failed.")

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .connect_timeout(60)
    .read_timeout(60)
    .write_timeout(60)
    .pool_timeout(60)
    .build()
)
app.add_handler(MessageHandler(filters.TEXT, download))

print("Bot running...")
app.run_polling()
