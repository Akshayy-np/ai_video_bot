import os
import yt_dlp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ---------------- BOT TOKEN ----------------
TOKEN = "8599234323:AAGkiqwUbbabe-H2UD13BXOUranrq77GoY0"
# -------------------------------------------


# ========= STEP 1 : USER SENDS LINK =========
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
        [
            InlineKeyboardButton("🎵 MP3 Audio", callback_data="mp3")
        ],
    ]

    await update.message.reply_text(
        "Choose download quality:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ========= STEP 2 : BUTTON CLICK =========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality = query.data
    url = context.user_data.get("url")

    await query.message.reply_text("⬇ Downloading...")

    filename = "video.%(ext)s"

    # -------- yt-dlp OPTIONS --------
    # Android client FIXES YouTube cloud blocking
    base_opts = {
        "outtmpl": filename,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },
        "quiet": True,
    }

    # AUDIO OPTION
    if quality == "mp3":
        ydl_opts = {
            **base_opts,
            "format": "bestaudio",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

    # VIDEO QUALITY
    else:
        ydl_opts = {
            **base_opts,
            "format": f"bestvideo[height<={quality}]+bestaudio/best",
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # MP3 filename correction
        if quality == "mp3":
            file_path = file_path.rsplit(".", 1)[0] + ".mp3"

        # Send faster as video when possible
        with open(file_path, "rb") as f:
            if file_path.endswith(".mp4"):
                await query.message.reply_video(
                    video=InputFile(f),
                    timeout=120,
                )
            else:
                await query.message.reply_document(
                    document=InputFile(f),
                    timeout=120,
                )

        os.remove(file_path)

    except Exception as e:
        print(e)
        await query.message.reply_text("❌ Download failed.")


# ========= BOT START =========
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
