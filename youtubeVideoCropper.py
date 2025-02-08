from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
CROPPED_FOLDER = os.path.join(DOWNLOAD_FOLDER, "Cropped Videos")

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
if not os.path.exists(CROPPED_FOLDER):
    os.makedirs(CROPPED_FOLDER)


def download_video(url):
    """Downloads YouTube video and returns file path."""
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension="mp4", progressive=True).first()
    file_path = stream.download(DOWNLOAD_FOLDER)
    return file_path


def crop_video(input_path, start_time, end_time):
    """Crops the video and saves it in the Cropped Videos folder."""
    clip = VideoFileClip(input_path).subclip(start_time, end_time)
    output_file = os.path.join(CROPPED_FOLDER, os.path.basename(input_path))
    clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

    clip.close()  # Fix file-in-use issue
    os.remove(input_path)  # Delete original
    return output_file


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        try:
            # Convert MM.SS format to seconds
            start_seconds = int(start_time.split(".")[0]) * 60 + int(start_time.split(".")[1])
            end_seconds = int(end_time.split(".")[0]) * 60 + int(end_time.split(".")[1])

            # Process video
            downloaded_video = download_video(url)
            cropped_video = crop_video(downloaded_video, start_seconds, end_seconds)

            return render_template("index.html", success=True, cropped_video=os.path.basename(cropped_video))
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")


@app.route("/download/<filename>")
def download(filename):
    """Allows user to download the cropped video."""
    return send_file(os.path.join(CROPPED_FOLDER, filename), as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
