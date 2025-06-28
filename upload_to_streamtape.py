import os
from streamtape import Upload # Assuming 'Upload' is the class for direct file uploads

# IMPORTANT: Replace with your actual Streamtape API credentials
STREAMTAPE_API_USER_KEY = os.getenv('STREAMTAPE_API_USERNAME')
STREAMTAPE_API_PASSWORD = os.getenv('STREAMTAPE_API_KEY')

def upload_videos_to_streamtape(video_folder):
    """
    Uploads all videos from a specified folder to Streamtape.

    Args:
        video_folder (str): Directory containing the videos to upload.
    """
    if not os.path.exists(video_folder):
        print(f"Error: The folder '{video_folder}' does not exist.")
        return

    uploader = Upload(STREAMTAPE_API_USER_KEY, STREAMTAPE_API_PASSWORD)

    uploaded_count = 0
    failed_uploads = []

    for filename in os.listdir(video_folder):
        if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')): # Add/remove video formats as needed
            file_path = os.path.join(video_folder, filename)
            print(f"\n--- Attempting to upload: {filename} ---")
            try:
                # The 'upload' method in the streamtape library might take an optional folder_id
                # if you want to organize videos within Streamtape. Check their documentation.
                response = uploader.upload(file_path)

                if response and response.get('status') == 200:
                    print(f"Successfully uploaded {filename} to Streamtape. File ID: {response.get('result', {}).get('filecode')}")
                    uploaded_count += 1
                else:
                    print(f"Failed to upload {filename}. Response: {response.get('msg', 'No message')} (Status: {response.get('status', 'N/A')})")
                    failed_uploads.append(filename)
            except Exception as e:
                print(f"Error uploading {filename}: {e}")
                failed_uploads.append(filename)

    print(f"\n--- Upload Summary ---")
    print(f"Total files attempted: {len(os.listdir(video_folder))}")
    print(f"Successfully uploaded: {uploaded_count}")
    if failed_uploads:
        print(f"Failed uploads: {len(failed_uploads)} videos: {', '.join(failed_uploads)}")
    else:
        print("All videos uploaded successfully!")

if __name__ == "__main__":
    download_destination = "downloaded_videos" # This should match the output_folder from the download script
    upload_videos_to_streamtape(download_destination)
