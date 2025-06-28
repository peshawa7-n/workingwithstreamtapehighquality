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
