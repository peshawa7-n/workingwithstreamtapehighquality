import os
import subprocess
import requests
import logging
import sys
import argparse
from urllib.parse import urlparse, parse_qs

# Configure logging for better visibility of the script's progress and errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Streamtape API details should be loaded from environment variables for security.
# DO NOT hardcode your API Key or User ID directly in the script.
STREAMTAPE_UID = os.getenv('STREAMTAPE_UID')
STREAMTAPE_API_KEY = os.getenv('STREAMTAPE_API_KEY')

STREAMTAPE_UPLOAD_BASE_URL = "https://api.streamtape.com"
STREAMTAPE_UPLOAD_PATH = "/file/ul"

# Directory to store downloaded videos temporarily
TEMP_DOWNLOAD_DIR = "temp_downloads"

def get_youtube_video_id(youtube_url):
    """
    Extracts the YouTube video ID from a given URL.
    This is useful for creating unique temporary filenames.
    """
    query = urlparse(youtube_url).query
    params = parse_qs(query)
    if 'v' in params:
        return params['v'][0]
    # Handle shortened YouTube URLs (e.g., youtu.be)
    path = urlparse(youtube_url).path
    if "youtu.be" in youtube_url and len(path) > 1:
        return path[1:]
    return None

def download_youtube_video(youtube_url, output_dir=TEMP_DOWNLOAD_DIR):
    """
    Downloads a YouTube video in the best available quality using yt-dlp.

    Args:
        youtube_url (str): The URL of the YouTube video.
        output_dir (str): The directory where the video will be saved temporarily.

    Returns:
        str or None: The path to the downloaded video file if successful, else None.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created temporary download directory: {output_dir}")

    video_id = get_youtube_video_id(youtube_url)
    if not video_id:
        logging.error(f"Could not extract video ID from URL: {youtube_url}")
        return None

    # Use video ID in the filename to ensure uniqueness and avoid conflicts
    # yt-dlp automatically appends the best quality extension.
    temp_filename_pattern = os.path.join(output_dir, f"{video_id}.%(ext)s")

    logging.info(f"Attempting to download video from: {youtube_url}")
    logging.info(f"Saving to: {temp_filename_pattern}")

    try:
        # Command to download the best video and audio quality and merge them
        # --progress: Show download progress (might be verbose for subprocess)
        # --output: Specify output template
        # --restrict-filenames: Keep filenames simple
        # --no-playlist: Ensure only a single video is downloaded if URL is part of a playlist
        # --embed-chapters --embed-metadata: Embed metadata (optional, can be removed)
        # --print-json --skip-download: Get video info without downloading (for pre-check, not used here)
        command = [
            sys.executable,  # Use the current Python executable
            "-m", "yt_dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", # Prioritize MP4, then best
            "--merge-output-format", "mp4", # Ensure output is MP4
            "--output", temp_filename_pattern,
            "--restrict-filenames",
            "--no-playlist",
            youtube_url
        ]

        process = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info("YouTube download command output:")
        logging.info(process.stdout)
        if process.stderr:
            logging.warning("YouTube download command errors/warnings:")
            logging.warning(process.stderr)

        # After successful download, yt-dlp will have created a file.
        # We need to find the actual filename, as %(ext)s is replaced.
        # This is a bit tricky, but we can list files in the directory and find the one that matches our ID.
        downloaded_file = None
        for f_name in os.listdir(output_dir):
            if f_name.startswith(video_id) and f_name.endswith(".mp4"):
                downloaded_file = os.path.join(output_dir, f_name)
                break

        if downloaded_file and os.path.exists(downloaded_file):
            logging.info(f"Video downloaded successfully to: {downloaded_file}")
            return downloaded_file
        else:
            logging.error("Could not find the downloaded video file after yt-dlp execution.")
            return None

    except subprocess.CalledProcessError as e:
        logging.error(f"Error during YouTube download: {e}")
        logging.error(f"yt-dlp stdout: {e.stdout}")
        logging.error(f"yt-dlp stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        logging.error("yt-dlp command not found. Please ensure yt-dlp is installed (pip install yt-dlp).")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during download: {e}")
        return None

def get_streamtape_upload_url(uid, api_key):
    """
    Fetches the actual upload URL from Streamtape's /file/ul_direct endpoint.
    This is often required for large file uploads.
    """
    if not uid or not api_key:
        logging.error("Streamtape UID or API Key not set. Cannot proceed with upload URL request.")
        return None

    params = {'login': uid, 'key': api_key}
    try:
        response = requests.get(f"{STREAMTAPE_UPLOAD_BASE_URL}/file/ul_direct", params=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        if data['status'] == 200:
            upload_url = data['result']['url']
            logging.info(f"Successfully fetched Streamtape upload URL: {upload_url}")
            return upload_url
        else:
            logging.error(f"Failed to get Streamtape upload URL: {data.get('msg', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching Streamtape upload URL: {e}")
        return None
    except ValueError as e:
        logging.error(f"Error parsing JSON response from Streamtape upload URL request: {e}")
        return None

def upload_to_streamtape(file_path, uid, api_key):
    """
    Uploads a video file to Streamtape.

    Args:
        file_path (str): The path to the video file to upload.
        uid (str): Your Streamtape User ID.
        api_key (str): Your Streamtape API Key.

    Returns:
        str or None: The URL of the uploaded video on Streamtape if successful, else None.
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None
    if not uid or not api_key:
        logging.error("Streamtape UID or API Key not set. Cannot proceed with upload.")
        return None

    logging.info(f"Attempting to upload file to Streamtape: {file_path}")

    # Step 1: Get the direct upload URL
    upload_url = get_streamtape_upload_url(uid, api_key)
    if not upload_url:
        logging.error("Failed to obtain Streamtape direct upload URL. Aborting upload.")
        return None

    # Step 2: Perform the actual file upload
    try:
        with open(file_path, 'rb') as f:
            files = {'file1': (os.path.basename(file_path), f, 'video/mp4')}
            # Streamtape's /file/ul_direct endpoint often doesn't need login/key in params
            # because the URL already contains necessary tokens, but some APIs might.
            # Let's double check by looking at API docs. The direct upload URL often
            # has the authentication embedded. So, no additional params are needed here.
            response = requests.post(upload_url, files=files, timeout=3600) # Set a long timeout (1 hour)
            response.raise_for_status() # Raise an exception for HTTP errors

            data = response.json()
            if data['status'] == 200:
                streamtape_file_code = data['result']['id']
                streamtape_url = f"https://streamtape.com/v/{streamtape_file_code}"
                logging.info(f"Video uploaded successfully to Streamtape! URL: {streamtape_url}")
                return streamtape_url
            else:
                logging.error(f"Failed to upload to Streamtape: {data.get('msg', 'Unknown error')}")
                # Streamtape sometimes gives 'msg' or 'message' for errors
                return None
    except requests.exceptions.Timeout:
        logging.error(f"Upload to Streamtape timed out after 3600 seconds for file: {file_path}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during Streamtape upload: {e}")
        return None
    except ValueError as e:
        logging.error(f"Error parsing JSON response from Streamtape after upload: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during Streamtape upload: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Download a YouTube video in full quality and upload it to Streamtape."
    )
    parser.add_argument(
        "youtube_url",
        help="The full URL of the YouTube video to process."
    )
    args = parser.parse_args()

    youtube_url = args.youtube_url

    # Check for Streamtape credentials before starting
    if not STREAMTAPE_UID or not STREAMTAPE_API_KEY:
        logging.critical(
            "Streamtape UID and API Key must be set as environment variables "
            "STREAMTAPE_UID and STREAMTAPE_API_KEY. Aborting."
        )
        sys.exit(1)

    downloaded_file_path = None
    try:
        # Step 1: Download the YouTube video
        downloaded_file_path = download_youtube_video(youtube_url, TEMP_DOWNLOAD_DIR)

        if downloaded_file_path:
            # Step 2: Upload the downloaded video to Streamtape
            streamtape_video_url = upload_to_streamtape(
                downloaded_file_path,
                STREAMTAPE_UID,
                STREAMTAPE_API_KEY
            )

            if streamtape_video_url:
                logging.info(f"Process completed successfully. Streamtape URL: {streamtape_video_url}")
            else:
                logging.error("Failed to upload video to Streamtape.")
        else:
            logging.error("Failed to download YouTube video.")

    finally:
        # Clean up the downloaded file regardless of success or failure
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            try:
                os.remove(downloaded_file_path)
                logging.info(f"Cleaned up temporary file: {downloaded_file_path}")
            except OSError as e:
                logging.error(f"Error deleting temporary file {downloaded_file_path}: {e}")

if __name__ == "__main__":
    main()
