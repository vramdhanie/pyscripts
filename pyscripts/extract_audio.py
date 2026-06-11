"""
Video to M4A Audio Extractor

Extract the audio track from a video file and save it as an M4A file using FFmpeg.
AAC audio is copied without re-encoding when possible; other codecs are converted to AAC.

Requires: FFmpeg (system), tkinter (standard library)

Usage:
    uv run python pyscripts/extract_audio.py
"""

import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


def get_audio_codec(input_file):
    """Return the first audio stream codec name, or None if no audio."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_file,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    codec = result.stdout.strip()
    return codec or None


def extract_audio(input_file, output_file):
    try:
        audio_codec = get_audio_codec(input_file)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Could not read video file: {e}")
        return

    if not audio_codec:
        messagebox.showerror("Error", "No audio track found in the selected file.")
        return

    cmd = ["ffmpeg", "-y", "-i", input_file, "-vn"]

    if audio_codec == "aac":
        cmd.extend(["-c:a", "copy"])
        mode = "stream copy (lossless)"
    else:
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        mode = f"converted from {audio_codec} to AAC"

    cmd.extend(["-movflags", "+faststart", output_file])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        messagebox.showinfo(
            "Success",
            f"Audio saved to {output_file}\nMode: {mode}",
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else str(e)
        messagebox.showerror("Error", f"Audio extraction failed:\n{stderr}")


def select_input_file():
    file_path = filedialog.askopenfilename(
        title="Select Input Video File",
        filetypes=[
            ("Video files", "*.mp4 *.mkv *.mov *.avi *.webm"),
            ("All files", "*.*"),
        ],
    )
    if file_path:
        input_path_var.set(file_path)


def select_output_file():
    file_path = filedialog.asksaveasfilename(
        title="Save M4A File As",
        defaultextension=".m4a",
        filetypes=[("M4A files", "*.m4a"), ("All files", "*.*")],
    )
    if file_path:
        output_path_var.set(file_path)


def extract_audio_from_gui():
    input_file = input_path_var.get()
    output_file = output_path_var.get()

    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select both input and output file paths.")
        return

    extract_audio(input_file, output_file)


root = tk.Tk()
root.title("Extract Audio to M4A")

input_path_var = tk.StringVar()
output_path_var = tk.StringVar()

tk.Label(root, text="Input Video:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=input_path_var, width=50).grid(
    row=0, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_input_file).grid(
    row=0, column=2, padx=10, pady=5
)

tk.Label(root, text="Output M4A:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=output_path_var, width=50).grid(
    row=1, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_output_file).grid(
    row=1, column=2, padx=10, pady=5
)

tk.Button(root, text="Extract Audio", command=extract_audio_from_gui).grid(
    row=2, column=1, pady=20
)

root.mainloop()
