import os
import yt_dlp
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8599234323:AAGkiqwUbbabe-H2UD13BXOUranrq77GoY0"


# ---------------- START MESSAGE ----------------
async def start_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        ]
    ]

    await update.message.reply_text(
        "Choose download quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- PROGRESS DISPLAY ----------------
def progress_hook(d, message):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()

        text = f"⬇ Downloading...\n{percent}\nSpeed: {speed}\nETA: {eta}"

        try:
            message.edit_text(text)
        except:
            pass


# ---------------- BUTTON HANDLER ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality = query.data
    url = context.user_data["url"]

    progress_msg = await query.message.reply_text("Starting download...")

    filename = "video.%(ext)s"

    # ---- FORMAT OPTIONS ----
    if quality == "mp3":
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': filename,
            'noplaylist': True,
            'progress_hooks': [lambda d: progress_hook(d, progress_msg)],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    else:
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best',
            'outtmpl': filename,
            'noplaylist': True,
            'progress_hooks': [lambda d: progress_hook(d, progress_msg)],
        }

    try:
        # Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        # Fix mp3 filename
        if quality == "mp3":
            file_name = file_name.rsplit(".", 1)[0] + ".mp3"

        await progress_msg.edit_text("📤 Uploading...")

        # Send file
        with open(file_name, "rb") as f:
            if quality == "mp3":
                await query.message.reply_audio(InputFile(f), timeout=120)
            else:
                await query.message.reply_video(InputFile(f), timeout=120)

        os.remove(file_name)

    except Exception as e:
        print(e)
        await query.message.reply_text("❌ Download failed.")


# ---------------- BOT START ----------------
app = (
    ApplicationBuilder()
    .token(TOKEN)
    .connect_timeout(60)
    .read_timeout(60)
    .write_timeout(60)
    .pool_timeout(60)
    .build()
)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start_download))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot running...")
app.run_polling()
