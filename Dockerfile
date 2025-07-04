FROM python:3.10-slim

WORKDIR /app

# Add ffmpeg for yt-dlp merging
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
