import yt_dlp
import os

def download_youtube_videos(video_urls_file, output_folder="downloaded_videos"):
    """
    Downloads YouTube videos from a list of URLs in full quality.

    Args:
        video_urls_file (str): Path to a text file containing one YouTube URL per line.
        output_folder (str): Directory where videos will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        with open(video_urls_file, 'r') as f:
            video_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{video_urls_file}' was not found.")
        return

    if not video_urls:
        print("No video URLs found in the provided file.")
        return

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'verbose': True,
        'progress_hooks': [lambda d: print(f"Downloading: {d['filename']} - {d['_percent_str']}") if d['status'] == 'downloading' else None],
    }

    print(f"Starting download of {len(video_urls)} videos...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(video_urls):
            print(f"\n--- Processing video {i+1}/{len(video_urls)}: {url} ---")
            try:
                ydl.download([url])
                print(f"Successfully downloaded: {url}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")
    print("\nAll download attempts completed.")

if __name__ == "__main__":
    # Create a file named 'youtube_urls.txt' in the same directory as this script.
    # Add one YouTube video URL per line to this file.
    # Example content for youtube_urls.txt:
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ
    # https://www.youtube.com/watch?v=some_other_video_id
    # https://www.youtube.com/watch?v=another_long_video

    urls_file = "youtube_urls.txt"
    download_destination = "downloaded_videos"
    download_youtube_videos(urls_file, download_destination)


import os
import subprocess
import sys
import time

# Define paths and filenames
DOWNLOAD_SCRIPT = "download_videos.py"
UPLOAD_SCRIPT = "upload_to_streamtape.py"
URLS_FILE = "youtube_urls.txt"
# This path MUST match the mount path of your Railway Volume
# For example, if you mount a volume at /app/downloaded_videos, this should be "downloaded_videos"
# because WORKDIR is /app. If you mount it directly to /, then it would be "/downloaded_videos".
DOWNLOAD_DESTINATION = "downloaded_videos" 

def run_script(script_name, *args):
    """Helper function to run a Python script."""
    print(f"\n--- Running {script_name} ---")
    try:
        # Use subprocess.run for better control and error handling
        result = subprocess.run(
            [sys.executable, script_name, *args],
            capture_output=True,
            text=True,
            check=True # Raise an exception if the command returns a non-zero exit code
        )
        print(result.stdout)
        if result.stderr:
            print(f"Errors/Warnings from {script_name}:\n{result.stderr}")
        print(f"--- {script_name} completed successfully ---")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(f"Command: {e.cmd}")
        print(f"Return Code: {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        sys.exit(1) # Exit if any script fails
    except FileNotFoundError:
        print(f"Error: {script_name} not found. Make sure it's in the correct directory.")
        sys.exit(1)

def main():
    print("--- Starting the video processing workflow ---")

    # Ensure the download folder exists.
    # On Railway, this must be the directory mounted by your persistent volume.
    if not os.path.exists(DOWNLOAD_DESTINATION):
        print(f"Creating download directory: {DOWNLOAD_DESTINATION}")
        os.makedirs(DOWNLOAD_DESTINATION)
    else:
        print(f"Download directory already exists: {DOWNLOAD_DESTINATION}")

    # Step 1: Run the download script
    # The download script expects 'youtube_urls.txt' in the same directory.
    # It also has the output_folder parameter that needs to match DOWNLOAD_DESTINATION.
    # Make sure download_videos.py is updated to accept output_folder as an argument if needed,
    # or ensure it defaults to 'downloaded_videos' (which it does in the previous example).
    run_script(DOWNLOAD_SCRIPT)

    # Step 2: Run the upload script
    # The upload script expects the video_folder parameter to match DOWNLOAD_DESTINATION.
    run_script(UPLOAD_SCRIPT) # The upload script will read from DOWNLOAD_DESTINATION

    print("--- Video processing workflow completed ---")

if __name__ == "__main__":
    main()

