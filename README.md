# Video Downloader

A modern, cross-platform video downloader application with a beautiful Material Design interface. Built with Python and PyQt6.

## Features

- Modern Material Design UI with animations and hover effects
- Support for YouTube and other video platforms
- Video preview and thumbnail display
- Multiple format and quality options
- Download progress tracking
- Download history with quick actions
- Cross-platform support (Windows, macOS, Linux)

## Requirements

- Python 3.9 or higher
- FFmpeg (required for some video formats)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Tolstoyj/YoutubeVideoDownloaderPython.git
cd video-downloader
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo dnf install ffmpeg` (Fedora)

## Usage

Run the application:
```bash
python video_downloader_gui.py
```

1. Enter a video URL in the input field
2. Click "Fetch Info" to load video information
3. Select your preferred format from the table
4. Click "Download" to start downloading
5. The file will be saved to your Downloads/VideoDownloader folder

## Known Issues

1. **SSL Warning**: When using urllib3 v2 with LibreSSL on macOS, you may see a warning about OpenSSL compatibility. This doesn't affect functionality.

2. **YouTube Embed**: Some browsers may show a warning about the Permissions-Policy header. This is a YouTube embed issue and doesn't affect functionality.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
