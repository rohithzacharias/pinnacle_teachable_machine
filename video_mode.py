# video_mode.py
import cv2
from image_mode import get_image_description
from transformers import pipeline

# Load summarization model once at startup
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_video_description(
    video_path: str,
    start_time: float = 0,
    end_time: float = None,
    frame_interval: int = 30,
    progress_callback=None
) -> str:
    """
    Generate a summarized textual description of the video content.
    - Samples one frame every `frame_interval`.
    - Filters duplicate captions.
    - Uses a BART summarizer to produce a concise summary.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        # Crop to specified time range
        if end_time is None or end_time > duration:
            end_time = duration
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        descriptions = []
        frame_num = start_frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        while frame_num < end_frame:
            success, frame = cap.read()
            if not success:
                break

            # Sample frames at intervals
            if frame_num % frame_interval == 0:
                temp_path = f"temp_frame_{frame_num}.jpg"
                cv2.imwrite(temp_path, frame)
                desc = get_image_description(temp_path)
                descriptions.append(desc)

            frame_num += 1

            # Update progress bar
            if progress_callback:
                progress = (frame_num - start_frame) / (end_frame - start_frame)
                progress_callback(progress)

        cap.release()

        return summarize_descriptions(descriptions)

    except Exception as e:
        return f"Error generating video summary: {e}"

def summarize_descriptions(descriptions):
    """Filter duplicate descriptions and generate a concise summary."""
    if not descriptions:
        return "No descriptions available."

    # Remove duplicates
    unique_descriptions = list(dict.fromkeys(descriptions))  # preserves order
    combined_text = " ".join(unique_descriptions)

    # Summarize into a single, concise sentence
    summary = summarizer(
        combined_text,
        max_length=100,
        min_length=30,
        do_sample=False
    )[0]['summary_text']

    return summary