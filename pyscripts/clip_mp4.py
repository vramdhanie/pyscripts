"""
Video Clipper GUI Tool

This script provides a simple Tkinter-based GUI for clipping segments from MP4 video files.
Users can select an input video, specify start and end times, and save the clipped segment as a new file.

Requires: moviepy, tkinter (standard library)
"""

import tkinter as tk
from tkinter import filedialog
from moviepy.video.io.VideoFileClip import VideoFileClip


def clip_video(input_file, output_file, start_time, end_time):
    try:
        video = VideoFileClip(input_file)

        # Ensure valid time range
        if start_time < 0 or end_time > video.duration or start_time >= end_time:
            print("Invalid time range. Please check the start and end times.")
            return

        # Clip the video
        clipped_video = video.subclip(start_time, end_time)
        clipped_video.write_videofile(output_file, codec="libx264", audio_codec="aac")
        print(f"Clipped video saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")


def select_input_file():
    file_path = filedialog.askopenfilename(
        title="Select Input Video File",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )
    input_path_var.set(file_path)


def select_output_file():
    file_path = filedialog.asksaveasfilename(
        title="Save Clipped Video As",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )
    output_path_var.set(file_path)


def clip_video_from_gui():
    input_file = input_path_var.get()
    output_file = output_path_var.get()
    try:
        start_time = float(start_time_var.get())
        end_time = float(end_time_var.get())
    except ValueError:
        print("Please enter valid numeric values for start and end times.")
        return

    if not input_file or not output_file:
        print("Please select both input and output file paths.")
        return

    clip_video(input_file, output_file, start_time, end_time)


# Tkinter GUI setup
root = tk.Tk()
root.title("Video Clipper")

# Variables
input_path_var = tk.StringVar()
output_path_var = tk.StringVar()
start_time_var = tk.StringVar()
end_time_var = tk.StringVar()

# GUI Elements
tk.Label(root, text="Input Video:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=input_path_var, width=40).grid(
    row=0, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_input_file).grid(
    row=0, column=2, padx=10, pady=5
)

tk.Label(root, text="Output Video:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=output_path_var, width=40).grid(
    row=1, column=1, padx=10, pady=5
)
tk.Button(root, text="Browse", command=select_output_file).grid(
    row=1, column=2, padx=10, pady=5
)

tk.Label(root, text="Start Time (seconds):").grid(
    row=2, column=0, padx=10, pady=5, sticky="e"
)
tk.Entry(root, textvariable=start_time_var, width=20).grid(
    row=2, column=1, padx=10, pady=5, sticky="w"
)

tk.Label(root, text="End Time (seconds):").grid(
    row=3, column=0, padx=10, pady=5, sticky="e"
)
tk.Entry(root, textvariable=end_time_var, width=20).grid(
    row=3, column=1, padx=10, pady=5, sticky="w"
)

tk.Button(root, text="Clip Video", command=clip_video_from_gui).grid(
    row=4, column=1, pady=20
)

# Run the application
root.mainloop()
