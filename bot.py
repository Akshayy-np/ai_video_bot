import os
import threading
import yt_dlp

from flask import Flask
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# ==============================
# TELEGRAM BOT TOKEN
# ==============================
TOKEN = "8599234323:AAGkiqwUbbabe-H2UD13BXOUranrq77GoY0"


# ==============================
# FLASK KEEP-ALIVE SERVER
# (Needed for Render FREE)
# ==============================
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)


# ==============================
# DOWNLOAD FUNCTION
# ==============================
def download(update: Update, context: CallbackContext):

    url = update.message.text
    update.message.reply_text("Downloading... please wait")

    filename = "video.%(ext)s"

    # yt-dlp options
    ydl_opts = {
        "outtmpl": filename,
        "format": "best",
        "noplaylist": True,

        # Android client (fix YouTube bot verification)
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        # Send video
        with open(file_name, "rb") as f:
            update.message.reply_video(f)

        os.remove(file_name)

    except Exception as e:
        print(e)
        update.message.reply_text("❌ Download failed.")


# ==============================
# MAIN BOT START
# ==============================
def main():

    print("Bot starting...")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download))

    updater.start_polling()
    updater.idle()


# ==============================
# START BOTH FLASK + BOT
# ==============================
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    main()
