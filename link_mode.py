# link_mode.py
import os
import mimetypes
import requests
import yt_dlp
from image_mode import get_image_description
from video_mode import get_video_description

def download_file_from_url(url: str, download_folder="downloads") -> str:
    """Download a file directly from a URL and return its local path."""
    os.makedirs(download_folder, exist_ok=True)
    file_name = url.split("/")[-1].split("?")[0]
    local_path = os.path.join(download_folder, file_name)

    resp = requests.get(
        url, stream=True, headers={"User-Agent": "Mozilla/5.0"}
    )
    resp.raise_for_status()

    with open(local_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return local_path

def download_youtube_video(url: str, download_folder="downloads") -> str:
    """Download a YouTube video with yt-dlp and return its local path."""
    os.makedirs(download_folder, exist_ok=True)
    output_path = os.path.join(download_folder, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "mp4",
        "outtmpl": output_path,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename

def describe_from_link(
    file_path: str,
    start_time: float = 0,
    end_time: float = None
) -> str:
    """Generate a description for a file path that was previously downloaded."""
    mimetype, _ = mimetypes.guess_type(file_path)
    mimetype = mimetype or ""

    if mimetype.startswith("image"):
        return get_image_description(file_path)
    elif mimetype.startswith("video"):
        return get_video_description(file_path, start_time, end_time)
    else:
        return f"Error: Unsupported file type ({mimetype})"