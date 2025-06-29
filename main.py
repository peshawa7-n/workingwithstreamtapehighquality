import os
import requests
from dotenv import load_dotenv

# Load API credentials
load_dotenv()
API_LOGIN = os.getenv("STREAMTAPE_API_USERNAME")
API_KEY = os.getenv("STREAMTAPE_API_KEY")

def get_upload_url():
    url = f"https://api.streamtape.com/file/ul?login={API_LOGIN}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 200:
        return data['result']['url']
    else:
        raise Exception("Failed to get upload URL: " + str(data))
        
file_path = "downloads".strip()

def upload_video(file_path):
    print(f"Uploading: {file_path}")
    upload_url = get_upload_url()
    with open(file_path, 'rb') as f:
        files = {'file1': (os.path.basename(file_path), f)}
        response = requests.post(upload_url, files=files)
        result = response.json()
        if result["status"] == 200:
            print("✅ Upload Success!")
            print("🎥 Video URL:", result["result"]["url"])
        else:
            print("❌ Upload Failed:", result)

if __name__ == "__main__":
    file_path = input("📂 Enter full path to video file: ").strip()
    if os.path.isfile(file_path):
        upload_video(file_path)
    else:
        print("❌ File not found. Please enter a valid path.")
