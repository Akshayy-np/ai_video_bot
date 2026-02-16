import os
import threading
import yt_dlp
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8599234323:AAGkiqwUbbabe-H2UD13BXOUranrq77GoY0"

# -------- Flask keep alive --------
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

# -------- Download handler --------
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Downloading...")

    ydl_opts = {
        "format": "best",
        "outtmpl": "video.%(ext)s",
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(open(filename, "rb"))
        os.remove(filename)

    except Exception as e:
        print(e)
        await update.message.reply_text("Download failed.")

# -------- Main --------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    main()
