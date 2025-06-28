import os
import requests
import mimetypes
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from pytube import YouTube
import torch
from tempfile import NamedTemporaryFile

# Load BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def describe_from_image_file(path):
    image = Image.open(path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def describe_from_link(path_or_url, start_time=None, end_time=None):
    try:
        # ✅ If it's a local path (used internally), skip download
        if os.path.exists(path_or_url):
            file_path = path_or_url
        elif path_or_url.startswith("http"):
            if "youtube.com" in path_or_url or "youtu.be" in path_or_url:
                file_path = download_youtube_video(path_or_url)
            else:
                file_path = download_file_from_url(path_or_url)
        else:
            return "Unsupported input: Not a valid URL or file."

        mimetype, _ = mimetypes.guess_type(file_path)

        if mimetype and mimetype.startswith("image"):
            return describe_from_image_file(file_path)

        elif mimetype and mimetype.startswith("video"):
            return f"Video downloaded: {os.path.basename(file_path)}\n(Preview only - not describing video yet.)"

        else:
            return "Unsupported file type."

    except Exception as e:
        return f"❌ Error processing link:\n{e}"

def download_file_from_url(url):
    if not url.startswith("http"):
        raise Exception("Invalid URL provided.")

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Error downloading file: {response.status_code}")

    ext = mimetypes.guess_extension(response.headers.get("content-type", "").split(";")[0])
    with NamedTemporaryFile(delete=False, suffix=ext or ".bin") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
        return f.name

def download_youtube_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not stream:
        raise Exception("No downloadable stream found.")
    out_file = stream.download(filename_prefix="yt_")
    return out_file
