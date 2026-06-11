"""
Video Clipper GUI Tool

This script provides a simple Tkinter-based GUI for clipping segments from MP4 video files.
Users can select an input video, specify start and end times, and save the clipped segment as a new file.

Uses FFmpeg for reliable clipping. Fast mode copies streams without re-encoding (lossless).
Accurate mode re-encodes for frame-precise cuts when stream copy is not exact enough.

Requires: FFmpeg (system), tkinter (standard library)
"""

import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


def get_video_duration(input_file):
    """Return video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_file,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def clip_video(input_file, output_file, start_time, end_time, accurate=False):
    try:
        duration = get_video_duration(input_file)
    except (subprocess.CalledProcessError, ValueError) as e:
        messagebox.showerror("Error", f"Could not read video file: {e}")
        return

    if start_time < 0 or end_time > duration or start_time >= end_time:
        messagebox.showerror(
            "Error",
            f"Invalid time range. Video duration is {duration:.2f}s. "
            f"Use start < end, both within 0–{duration:.2f}.",
        )
        return

    clip_duration = end_time - start_time

    if accurate:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-i",
            input_file,
            "-t",
            str(clip_duration),
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            output_file,
        ]
    else:
        # Stream copy: no re-encoding, preserves original quality.
        # Cuts align to nearest keyframes, so start may be slightly earlier.
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-to",
            str(end_time),
            "-i",
            input_file,
            "-c",
            "copy",
            "-avoid_negative_ts",
            "make_zero",
            output_file,
        ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        mode = "accurate (re-encoded)" if accurate else "fast (stream copy)"
        messagebox.showinfo(
            "Success",
            f"Clipped video saved to {output_file}\nMode: {mode}",
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else str(e)
        messagebox.showerror("Error", f"Clipping failed:\n{stderr}")


def select_input_file():
    file_path = filedialog.askopenfilename(
        title="Select Input Video File",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )
    if not file_path:
        return
    input_path_var.set(file_path)
    try:
        duration = get_video_duration(file_path)
        duration_var.set(f"{duration:.2f}s")
    except (subprocess.CalledProcessError, ValueError):
        duration_var.set("unknown")


def select_output_file():
    file_path = filedialog.asksaveasfilename(
        title="Save Clipped Video As",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )
    if file_path:
        output_path_var.set(file_path)


def clip_video_from_gui():
    input_file = input_path_var.get()
    output_file = output_path_var.get()
    try:
        start_time = float(start_time_var.get())
        end_time = float(end_time_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values for start and end times.")
        return

    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select both input and output file paths.")
        return

    clip_video(
        input_file,
        output_file,
        start_time,
        end_time,
        accurate=accurate_var.get(),
    )


# Tkinter GUI setup
root = tk.Tk()
root.title("Video Clipper")

# Variables
input_path_var = tk.StringVar()
output_path_var = tk.StringVar()
start_time_var = tk.StringVar()
end_time_var = tk.StringVar()
duration_var = tk.StringVar(value="—")
accurate_var = tk.BooleanVar(value=False)

# GUI Elements
tk.Label(root, text="Input Video:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=input_path_var, width=40).grid(
    row=0, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_input_file).grid(
    row=0, column=2, padx=10, pady=5
)

tk.Label(root, text="Duration:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, textvariable=duration_var).grid(row=1, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Output Video:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=output_path_var, width=40).grid(
    row=2, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_output_file).grid(
    row=2, column=2, padx=10, pady=5
)

tk.Label(root, text="Start Time (seconds):").grid(
    row=3, column=0, padx=10, pady=5, sticky="e"
)
tk.Entry(root, textvariable=start_time_var, width=20).grid(
    row=3, column=1, padx=10, pady=5, sticky="w"
)

tk.Label(root, text="End Time (seconds):").grid(
    row=4, column=0, padx=10, pady=5, sticky="e"
)
tk.Entry(root, textvariable=end_time_var, width=20).grid(
    row=4, column=1, padx=10, pady=5, sticky="w"
)

tk.Checkbutton(
    root,
    text="Accurate cut (re-encode, frame-precise but slower)",
    variable=accurate_var,
).grid(row=5, column=1, padx=10, pady=5, sticky="w")

tk.Button(root, text="Clip Video", command=clip_video_from_gui).grid(
    row=6, column=1, pady=20
)

# Run the application
root.mainloop()
