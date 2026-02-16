import os
import threading
import yt_dlp
from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8599234323:AAGkiqwUbbabe-H2UD13BXOUranrq77GoY0"

# ---------------- FLASK KEEP ALIVE ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

# ---------------- URL RECEIVED ----------------
async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("1080p", callback_data="1080"),
            InlineKeyboardButton("720p", callback_data="720"),
        ],
        [
            InlineKeyboardButton("480p", callback_data="480"),
            InlineKeyboardButton("144p", callback_data="144"),
        ],
        [InlineKeyboardButton("MP3 Audio", callback_data="mp3")],
    ]

    await update.message.reply_text(
        "Choose download option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ---------------- BUTTON CLICK ----------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    choice = query.data

    await query.message.reply_text("Downloading...")

    try:
        if choice == "mp3":
            ydl_opts = {
                "format": "bestaudio",
                "outtmpl": "audio.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
        else:
            ydl_opts = {
                "format": f"bestvideo[height<={choice}]+bestaudio/best",
                "outtmpl": "video.%(ext)s",
                "merge_output_format": "mp4",

                # Android client helps bypass YouTube checks
                "extractor_args": {
                    "youtube": {"player_client": ["android"]}
                },
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if choice == "mp3":
            await query.message.reply_audio(open(filename, "rb"))
        else:
            await query.message.reply_video(open(filename, "rb"))

        os.remove(filename)

    except Exception as e:
        print(e)
        await query.message.reply_text("❌ Download failed.")

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link))
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    main()
