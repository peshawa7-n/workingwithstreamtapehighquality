import os
import requests
import yt_dlp
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load API key from .env
load_dotenv()
STREAMTAPE_API_USER = os.getenv("STREAMTAPE_API_USER")
STREAMTAPE_API_KEY = os.getenv("STREAMTAPE_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- Download YouTube video using yt_dlp ---
def download_video(url, output_dir=DOWNLOAD_DIR):
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title).100s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info).replace(".webm", ".mp4")
        return file_path


# --- Upload video to StreamTape ---
def upload_to_streamtape(file_path):
    # 1. Get upload URL
    get_url = requests.get(f"https://api.streamtape.com/file/ul?login={STREAMTAPE_API_USER}&key={STREAMTAPE_API_KEY}")
    res_json = get_url.json()
    upload_url = res_json["result"]["url"]

    # 2. Upload video
    with open(file_path, 'rb') as f:
        response = requests.post(upload_url, files={'file1': f})
    return response.text


# --- Telegram Command Handler ---
async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please send a valid YouTube video link.")
        return

    url = context.args[0]
    await update.message.reply_text(f"🔽 Downloading: {url}")

    try:
        file_path = download_video(url)
        await update.message.reply_text("⏫ Uploading to StreamTape...")
        result = upload_to_streamtape(file_path)
        await update.message.reply_text(f"✅ Uploaded to StreamTape:\n{result}")
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# --- Run Bot ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("upload", upload_command))
    print("✅ Bot is running...")
    app.run_polling()
