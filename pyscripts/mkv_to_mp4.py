import subprocess
from tkinter import Tk, filedialog


def convert_mkv_to_mp4():
    root = Tk()
    root.withdraw()
    root.title("Select MKV File")
    mkv_file = filedialog.askopenfilename(
        title="Select MKV File", filetypes=[("MKV files", "*.mkv")]
    )

    if not mkv_file:
        print("No file selected. Exiting.")
        return

    output_file = filedialog.asksaveasfilename(
        title="Save MP4 File As",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4")],
    )

    if not output_file:
        print("No save location selected. Exiting.")
        return

    try:
        command = [
            "ffmpeg",
            "-i",
            mkv_file,  # Input file
            "-c:v",
            "copy",  # Copy video codec without re-encoding
            "-c:a",
            "aac",  # Convert audio to AAC (if needed)
            output_file,  # Output file
        ]

        print("Converting...")
        subprocess.run(command, check=True)
        print(f"Conversion complete. File saved to: {output_file}")

    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e)


if __name__ == "__main__":
    convert_mkv_to_mp4()
