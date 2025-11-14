# PyScripts

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/lint-ruff-red.svg)](https://github.com/astral-sh/ruff)

A collection of Python scripts for video processing and data analysis tasks. This project provides simple GUI tools for common video operations and data analysis utilities.

## Features

- **Video Clipping**: Extract specific segments from MP4 videos with a user-friendly GUI
- **Video Compression**: Reduce video file sizes while maintaining quality
- **Format Conversion**: Convert MKV files to MP4 format using FFmpeg
- **Processing Date Estimator**: Analyze historical data to estimate when processing dates will reach a target
 - **Google Drive Folder Copy**: Recursively copy a Drive folder to another location on Drive

## Prerequisites

- Python 3.11 or higher
- FFmpeg (for video compression and format conversion)
- uv (for dependency management)

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html) or use Chocolatey:
```bash
choco install ffmpeg
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pyscripts
   ```

2. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies and create virtual environment:**
   ```bash
   uv sync
   ```

## Usage

### Video Clipper (`clip_mp4.py`)

Extract a specific segment from an MP4 video file.

```bash
uv run python pyscripts/clip_mp4.py
```

**Features:**
- Select input video file
- Specify start and end times in seconds
- Choose output location
- Preview video duration

### Video Compressor (`reduce_mp4.py`)

Compress MP4 videos to reduce file size while maintaining quality.

```bash
uv run python pyscripts/reduce_mp4.py
```

**Features:**
- Set target file size in MB
- Adjust CRF (Constant Rate Factor) for quality control
- Automatic bitrate calculation
- Progress feedback

### MKV to MP4 Converter (`mkv_to_mp4.py`)

Convert MKV files to MP4 format using FFmpeg.

```bash
uv run python pyscripts/mkv_to_mp4.py
```

**Features:**
- Fast conversion without re-encoding video
- Audio conversion to AAC format
- Simple file selection interface

### Processing Date Estimator (`estimator.py`)

Analyze historical processing date data to estimate when a specific eligibility date will be reached.

```bash
uv run python pyscripts/estimator.py
```

**Features:**
- Linear regression analysis of processing trends
- Interactive matplotlib visualizations
- Automatic date parsing and conversion
- Projection lines for future estimates
- Visual markers for target dates
- Reads data from `data/processing_data.json`

**Data Format:**
The script reads from `data/processing_data.json` which should contain:
- `eligibility_date_str`: Target date to estimate (e.g., "1 March 2024")
- `data`: Object with "Recorded Date" and "Current Processing Date" arrays (actual data)
- `speculative_data`: Optional object with "Recorded Date" and "Current Processing Date" arrays (speculative scenario)

**Example JSON structure:**
```json
{
  "eligibility_date_str": "1 March 2024",
  "data": {
    "Recorded Date": ["April 2024", "May 2024", ...],
    "Current Processing Date": ["15 Jan 2023", "15 Jan 2023", ...]
  },
  "speculative_data": {
    "Recorded Date": ["April 2024", "May 2024", ...],
    "Current Processing Date": ["15 Feb 2023", "15 Feb 2023", ...]
  }
}
```

### Google Drive Folder Copy (`copy_drive_folder.py`)

Recursively copy a folder (and all its contents) to another location on your Google Drive.

```bash
uv run python pyscripts/copy_drive_folder.py --src-id <SRC_FOLDER_ID> --dst-id <DEST_PARENT_FOLDER_ID> [--new-name "<NEW_NAME>"] [--dry-run]
```

- `--src-id`: ID of the source folder to copy
- `--dst-id`: ID of the destination parent folder where the copy will be created
- `--new-name`: Optional new name for the root of the copied folder tree
- `--dry-run`: Print the plan without creating anything
- `--credentials`: Path to OAuth client secrets JSON (default: `credentials.json`)
- `--token`: Path to token cache JSON (default: `token.json`)

Notes:
- Folder IDs can be obtained from the URL in Google Drive (the long alphanumeric string).
- On first run, a browser window will open to authorize access; a `token.json` will be created for subsequent runs.

Prerequisites for Drive:
1. In Google Cloud Console, create an OAuth 2.0 Client ID (Desktop app) and download the JSON.
2. Save it as `credentials.json` in the project root (or pass `--credentials`).
3. Ensure the scopes requested are acceptable (`https://www.googleapis.com/auth/drive` is used).

## Development

### Project Structure

```
pyscripts/
├── pyscripts/
│   ├── __init__.py
│   ├── clip_mp4.py      # Video clipping tool
│   ├── reduce_mp4.py    # Video compression tool
│   ├── mkv_to_mp4.py    # MKV to MP4 converter
│   ├── estimator.py     # Processing date estimator
│   └── copy_drive_folder.py  # Google Drive folder copy tool
├── data/
│   └── processing_data.json  # Input data for estimator
├── tests/
├── pyproject.toml       # Project configuration
├── uv.lock             # Dependency lock file
└── README.md
```

### Dependencies

- **moviepy**: Video editing and processing
- **pandas**: Data manipulation and analysis
- **matplotlib**: Data visualization and plotting
- **numpy**: Numerical computations
- **google-api-python-client**, **google-auth-httplib2**, **google-auth-oauthlib**: Google Drive API access
- **tkinter**: GUI framework (included with Python)
- **subprocess**: System command execution (standard library)

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black pyscripts/
uv run ruff check pyscripts/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 PyScripts Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Make sure FFmpeg is installed and available in your PATH
2. **MoviePy import error**: Ensure you're running within the uv virtual environment
3. **Tkinter errors**: On Linux, install `python3-tk` package

### Getting Help

If you encounter any issues, please:
1. Check the troubleshooting section above
2. Search existing issues
3. Create a new issue with detailed information about your problem

## Acknowledgments

- [MoviePy](https://zulko.github.io/moviepy/) for video processing capabilities
- [FFmpeg](https://ffmpeg.org/) for video conversion and compression
- [uv](https://github.com/astral-sh/uv) for fast Python package management
