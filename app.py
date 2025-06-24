import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import mimetypes

from image_mode import get_image_description
from video_mode import get_video_description
from link_mode import describe_from_link, download_youtube_video, download_file_from_url
from audio_mode import transcribe_and_answer  # <-- CHANGED THIS

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("🤖 Teachable AI Machine")
app.geometry("900x800")

title_label = ctk.CTkLabel(
    app, text="🤖 Teachable AI Machine",
    font=ctk.CTkFont(size=28, weight="bold")
)
title_label.pack(pady=10)

tabview = ctk.CTkTabview(app, width=860, height=680)
tabview.pack(padx=10, pady=10)

# ==================== Image Mode ====================
image_tab = tabview.add("Image Mode")

image_path_var = ctk.StringVar()
image_output_text = ctk.CTkTextbox(image_tab, width=800, height=180)
image_preview_label = ctk.CTkLabel(image_tab, text="")
image_preview_label.pack(pady=5)

def browse_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        image_path_var.set(file_path)
        img = Image.open(file_path).resize((200, 200))
        preview = ImageTk.PhotoImage(img)
        image_preview_label.configure(image=preview)
        image_preview_label.image = preview

def describe_image():
    path = image_path_var.get()
    if path:
        description = get_image_description(path)
        image_output_text.delete("1.0", "end")
        image_output_text.insert("end", description)

ctk.CTkButton(image_tab, text="Browse Image", command=browse_image, width=180).pack(pady=5)
ctk.CTkLabel(image_tab, textvariable=image_path_var).pack(pady=5)
ctk.CTkButton(image_tab, text="Describe Image", command=describe_image, width=180).pack(pady=5)
image_output_text.pack(pady=10)

# ==================== Video Mode ====================
video_tab = tabview.add("Video Mode")

video_path_var = ctk.StringVar()
start_time_var = ctk.StringVar(value="0")
end_time_var = ctk.StringVar(value="")
video_output_text = ctk.CTkTextbox(video_tab, width=800, height=180)
video_preview_label = ctk.CTkLabel(video_tab, text="")
progress_label = ctk.CTkLabel(video_tab, text="")
progress_bar = ctk.CTkProgressBar(video_tab, width=800)
progress_bar.set(0)

def browse_video():
    file_path = filedialog.askopenfilename(
        filetypes=[("Videos", "*.mp4;*.avi;*.mkv;*.mov")]
    )
    if file_path:
        video_path_var.set(file_path)
        cap = cv2.VideoCapture(file_path)
        success, frame = cap.read()
        cap.release()
        if success:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((200, 200))
            preview = ImageTk.PhotoImage(img)
            video_preview_label.configure(image=preview)
            video_preview_label.image = preview

def describe_video():
    path = video_path_var.get()
    if path:
        try:
            start_time = float(start_time_var.get()) if start_time_var.get() else 0
            end_time = float(end_time_var.get()) if end_time_var.get() else None
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for time!")
            return

        import threading
        def progress_cb(progress):
            progress_bar.set(progress)
            progress_label.configure(text=f"Processing... {progress*100:.1f}%")

        def work():
            summary = get_video_description(path, start_time, end_time, progress_callback=progress_cb)
            video_output_text.delete("1.0", "end")
            video_output_text.insert("end", summary)
            progress_label.configure(text="✅ Done!")

        threading.Thread(target=work, daemon=True).start()

ctk.CTkButton(video_tab, text="Browse Video", command=browse_video, width=180).pack(pady=5)
ctk.CTkLabel(video_tab, textvariable=video_path_var).pack(pady=5)

time_frame = ctk.CTkFrame(video_tab)
ctk.CTkLabel(time_frame, text="Start Time (s):").pack(side="left", padx=5)
ctk.CTkEntry(time_frame, width=60, textvariable=start_time_var).pack(side="left", padx=5)
ctk.CTkLabel(time_frame, text="End Time (s):").pack(side="left", padx=5)
ctk.CTkEntry(time_frame, width=60, textvariable=end_time_var).pack(side="left", padx=5)
time_frame.pack(pady=5)

ctk.CTkButton(video_tab, text="Describe Video", command=describe_video, width=180).pack(pady=5)
video_preview_label.pack(pady=5)
progress_bar.pack(pady=5)
progress_label.pack(pady=5)
video_output_text.pack(pady=10)

# ==================== Link Mode ====================
link_tab = tabview.add("Link Mode")

link_var = ctk.StringVar()
link_start_time_var = ctk.StringVar(value="0")
link_end_time_var = ctk.StringVar(value="")
link_output_text = ctk.CTkTextbox(link_tab, width=800, height=180)
link_preview_label = ctk.CTkLabel(link_tab, text="")
link_preview_label.pack(pady=5)

def describe_link():
    url = link_var.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a link!")
        return
    try:
        start_time = float(link_start_time_var.get()) if link_start_time_var.get() else 0
        end_time = float(link_end_time_var.get()) if link_end_time_var.get() else None
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for time!")
        return

    file_path = None
    if "youtube.com" in url or "youtu.be" in url:
        file_path = download_youtube_video(url)
    else:
        file_path = download_file_from_url(url)

    mimetype, _ = mimetypes.guess_type(file_path)
    mimetype = mimetype or ""

    if mimetype.startswith("image"):
        img = Image.open(file_path).resize((200, 200))
        preview = ImageTk.PhotoImage(img)
        link_preview_label.configure(image=preview)
        link_preview_label.image = preview
    elif mimetype.startswith("video"):
        cap = cv2.VideoCapture(file_path)
        success, frame = cap.read()
        cap.release()
        if success:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((200, 200))
            preview = ImageTk.PhotoImage(img)
            link_preview_label.configure(image=preview)
            link_preview_label.image = preview

    summary = describe_from_link(file_path, start_time, end_time)
    link_output_text.delete("1.0", "end")
    link_output_text.insert("end", summary)

ctk.CTkLabel(link_tab, text="Paste Image/Video Link:").pack(pady=5)
ctk.CTkEntry(link_tab, textvariable=link_var, width=600).pack(pady=5)

link_time_frame = ctk.CTkFrame(link_tab)
ctk.CTkLabel(link_time_frame, text="Start Time (s):").pack(side="left", padx=5)
ctk.CTkEntry(link_time_frame, width=60, textvariable=link_start_time_var).pack(side="left", padx=5)
ctk.CTkLabel(link_time_frame, text="End Time (s):").pack(side="left", padx=5)
ctk.CTkEntry(link_time_frame, width=60, textvariable=link_end_time_var).pack(side="left", padx=5)
link_time_frame.pack(pady=5)

ctk.CTkButton(link_tab, text="Describe Link Media", command=describe_link, width=180).pack(pady=5)
link_output_text.pack(pady=10)

# ==================== Speech Mode ====================
audio_tab = tabview.add("Speech Mode")

audio_output_text = ctk.CTkTextbox(audio_tab, width=800, height=180)

def record_and_answer():
    answer = transcribe_and_answer()
    audio_output_text.delete("1.0", "end")
    audio_output_text.insert("end", answer)

ctk.CTkButton(audio_tab, text="Ask a Question (Speak)", command=record_and_answer, width=220).pack(pady=20)
audio_output_text.pack(pady=10)

# Run app
app.mainloop()