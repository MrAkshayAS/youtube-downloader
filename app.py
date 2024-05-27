from flask import Flask, render_template, request, Response
import logging
import os
import platform
import tempfile

import googleapiclient.discovery
from pytube import YouTube

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# Function to fetch playlist information from YouTube Data API
def fetch_playlist_info(playlist_url):
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("No Google API key found in environment variables")
    
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    playlist_id = playlist_url.split("list=")[-1]

    request = youtube.playlists().list(
        part="snippet",
        id=playlist_id
    )
    response = request.execute()

    playlist_title = response["items"][0]["snippet"]["title"]

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    video_metadata = []
    for item in response["items"]:
        video_id = item["snippet"]["resourceId"]["videoId"]
        video_title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Fetch available video streams to get quality options
        yt = YouTube(video_url)
        video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()

        quality_options = []
        for stream in video_streams:
            quality_options.append({
                "itag": stream.itag,
                "resolution": stream.resolution,
                "mime_type": stream.mime_type
            })

        video_metadata.append({
            "title": video_title,
            "url": video_url,
            "id": video_id,
            "quality_options": quality_options  # Add quality options to metadata
        })

    return {
        "title": playlist_title,
        "total_videos": len(video_metadata),
        "videos": video_metadata
    }

# Function to download a video with selected quality using pytube
def download_video(video_id, output_dir, selected_quality):
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    stream = yt.streams.get_by_itag(selected_quality)
    if not stream:
        raise ValueError(f"Video with ID {video_id} does not have selected quality {selected_quality}")
    stream.download(output_dir)
    return yt.title

# Route for home page and handling form submission
@app.route("/", methods=["GET", "POST"])
def home_route():
    if request.method == "POST":
        playlist_url = request.form["playlist_url"]
        playlist_info = fetch_playlist_info(playlist_url)
        return render_template("home.html", playlist_info=playlist_info)
    return render_template("home.html")

@app.route("/single_video", methods=["GET", "POST"])
def single_video_route():
    if request.method == "POST":
        video_url = request.form["video_url"]
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                yt = YouTube(video_url)
                video_title = yt.title
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                if not stream:
                    raise ValueError(f"No downloadable stream found for {video_url}")
                
                stream.download(output_path=temp_dir)
                video_path = os.path.join(temp_dir, f"{video_title}.mp4")

                # Open the file in binary mode
                with open(video_path, 'rb') as f:
                    data = f.read()

                # Create a response with the file data
                response = Response(data, headers={
                    'Content-Type': 'application/octet-stream',
                    'Content-Disposition': f'attachment; filename="{video_title}.mp4"'
                })

                return response

        except Exception as e:
            logging.error(f"Error downloading single video from {video_url}: {str(e)}")
            return f"Error downloading single video from {video_url}: {str(e)}", 500

    return render_template("single_video.html")




# Route for downloading a video with selected quality
@app.route("/download/<video_id>", methods=["POST"])
def download_video_route(video_id):
    try:
        selected_quality = request.form.get("quality")  # Get selected quality from form
        with tempfile.TemporaryDirectory() as temp_dir:
            video_title = download_video(video_id, temp_dir, selected_quality)
            video_path = os.path.join(temp_dir, f"{video_title}.mp4")

            # Open the file in binary mode
            with open(video_path, 'rb') as f:
                data = f.read()

            # Create a response with the file data
            response = Response(data, headers={
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename="{video_title}.mp4"'
            })

            return response

    except Exception as e:
        logging.error(f"Error downloading video {video_id}: {str(e)}")
        return f"Error downloading video {video_id}: {str(e)}", 500

if __name__ == "__main__":
    if platform.system() == "Windows":
        from waitress import serve
        serve(app, host="0.0.0.0", port=8080)