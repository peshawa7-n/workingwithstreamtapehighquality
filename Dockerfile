# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Ensure the download directory exists and has correct permissions
# Railway Volumes are mounted as root by default. 
# If your Python script runs as a non-root user within the container, 
# you might need to adjust permissions. For now, we assume root is fine.
RUN mkdir -p downloaded_videos

# Define the command to run your application
# We'll use a single Python script to orchestrate the download and upload.
# This script will in turn call your download_videos.py and upload_to_streamtape.py
CMD ["python", "main_workflow.py"]
