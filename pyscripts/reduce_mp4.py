"""
Video Compression Tool

This script provides a Tkinter-based GUI for compressing MP4 video files to reduce their size
while maintaining acceptable quality. It uses FFmpeg for video processing and allows users to
specify target file size and quality parameters.

Features:
- Automatic bitrate calculation based on target file size
- CRF (Constant Rate Factor) quality control (18-28 recommended)
- FFmpeg-based compression using H.264 codec
- Audio compression to AAC format
- Input validation and error handling
- Progress feedback through message boxes

Dependencies:
- FFmpeg (system requirement for video processing)
- tkinter (standard library for GUI)
- subprocess (standard library for FFmpeg calls)

Usage:
    uv run python pyscripts/reduce_mp4.py
    or
    poetry run python pyscripts/reduce_mp4.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
from math import ceil


def get_video_info(input_file):
    """Retrieve video duration and bitrate using FFmpeg."""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "format=duration,bit_rate",
            "-of",
            "default=noprint_wrappers=1",
            input_file,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        metadata = result.stdout.splitlines()
        duration = float(metadata[0].split("=")[1])
        original_bitrate = float(metadata[1].split("=")[1])
        return duration, original_bitrate
    except Exception as e:
        messagebox.showerror("Error", f"Could not retrieve video info: {e}")
        return None, None


def compress_video(input_file, output_file, target_size_mb, crf=23, preset="medium"):
    """Compress the video to meet the target file size."""
    try:
        # Get video duration and original bitrate
        duration, original_bitrate = get_video_info(input_file)
        if not duration or not original_bitrate:
            return

        # Calculate target bitrate
        target_size_bits = target_size_mb * 8 * 1024 * 1024  # MB to bits
        target_bitrate = target_size_bits / duration

        # Ensure the target bitrate is lower than the original
        if target_bitrate >= original_bitrate:
            messagebox.showinfo(
                "Info",
                "Target size is larger than the original file. No compression needed.",
            )
            return

        # Run FFmpeg compression
        cmd = [
            "ffmpeg",
            "-i",
            input_file,
            "-c:v",
            "libx264",
            "-b:v",
            f"{ceil(target_bitrate)}",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            output_file,
        ]
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Compressed video saved to {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Compression failed: {e}")


def select_input_file():
    """Open a file dialog to select the input video file."""
    file_path = filedialog.askopenfilename(
        title="Select Input Video File",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )
    input_path_var.set(file_path)


def select_output_file():
    """Open a file dialog to save the output video file."""
    file_path = filedialog.asksaveasfilename(
        title="Save Compressed Video As",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )
    output_path_var.set(file_path)


def start_compression():
    """Start the video compression process."""
    input_file = input_path_var.get()
    output_file = output_path_var.get()
    try:
        target_size_mb = float(target_size_var.get())
        crf = int(crf_var.get())
    except ValueError:
        messagebox.showerror(
            "Error", "Please enter valid numeric values for target size and CRF."
        )
        return

    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select both input and output files.")
        return

    compress_video(input_file, output_file, target_size_mb, crf)


# Initialize Tkinter root
root = tk.Tk()
root.title("Video Compression Tool")

# Tkinter Variables
input_path_var = tk.StringVar()
output_path_var = tk.StringVar()
target_size_var = tk.StringVar()
crf_var = tk.StringVar(value="23")

# GUI Elements
tk.Label(root, text="Input Video:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=input_path_var, width=50).grid(
    row=0, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_input_file).grid(
    row=0, column=2, padx=10, pady=5
)

tk.Label(root, text="Output Video:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=output_path_var, width=50).grid(
    row=1, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_output_file).grid(
    row=1, column=2, padx=10, pady=5
)

tk.Label(root, text="Target Size (MB):").grid(
    row=2, column=0, padx=10, pady=5, sticky="e"
)
tk.Entry(root, textvariable=target_size_var, width=10).grid(
    row=2, column=1, padx=10, pady=5, sticky="w"
)

tk.Label(root, text="CRF (Quality):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=crf_var, width=10).grid(
    row=3, column=1, padx=10, pady=5, sticky="w"
)

tk.Button(root, text="Compress Video", command=start_compression).grid(
    row=4, column=1, pady=20
)

# Run the Tkinter event loop
root.mainloop()
