import os
import requests
import yt_dlp
import time

# 🔐 Read your API key from env vars
STREAMTAPE_API_KEY = os.getenv("STREAMTAPE_API_KEY")

# 📺 List of YouTube URLs (replace or expand to 50)
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=BaW_jenozKc",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    # Add more up to 50...
]

def download_video(url, filename):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def get_upload_url():
    res = requests.get(f"https://api.streamtape.com/file/ul?login=&key={STREAMTAPE_API_KEY}")
    return res.json()['result']['url']

def upload_to_streamtape(filename):
    upload_url = get_upload_url()
    with open(filename, 'rb') as f:
        files = {'file1': (filename, f)}
        response = requests.post(upload_url, files=files)
        print("✅ Uploaded:", filename)
        print("🌐 URL:", response.json())
    os.remove(filename)  # Optional: delete after upload

def main():
    for index, video_url in enumerate(VIDEO_URLS, start=1):
        filename = f"video_{index}.mp4"
        print(f"⏬ Downloading {video_url}")
        try:
            download_video(video_url, filename)
            print("🚀 Uploading to StreamTape...")
            upload_to_streamtape(filename)
        except Exception as e:
            print("❌ Error with video:", video_url)
            print(e)
        time.sleep(2)  # Slight delay to prevent rate limits

if __name__ == "__main__":
    main()
