#!/usr/bin/env python3

import os
import re
import requests
import yt_dlp
from urllib.parse import urlparse
from typing import Optional, Dict, Any

class VideoDownloader:
    """A class to handle video downloads from various sources."""
    
    def __init__(self, download_path: str = "downloads"):
        """
        Initialize the VideoDownloader.
        
        Args:
            download_path (str): Directory where videos will be saved
        """
        self.download_path = download_path
        # Create downloads directory if it doesn't exist
        os.makedirs(download_path, exist_ok=True)
    
    def download_video(self, url: str) -> Optional[str]:
        """
        Download a video from the given URL.
        
        Args:
            url (str): URL of the video to download
            
        Returns:
            Optional[str]: Path to the downloaded file or None if download fails
        """
        try:
            # Check if URL is valid
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")

            # Handle YouTube and other supported platforms
            if any(domain in url for domain in ['youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com']):
                return self._download_with_ytdlp(url)
            
            # Handle direct video URLs
            return self._download_direct_video(url)
            
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Progress hook for yt-dlp downloads.
        
        Args:
            d: Progress information dictionary
        """
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
                print(f"\rDownload Progress: {percentage:.1f}%", end="")
            elif 'downloaded_bytes' in d:
                print(f"\rDownloaded: {d['downloaded_bytes'] / 1024 / 1024:.1f}MB", end="")
        elif d['status'] == 'finished':
            print("\nDownload completed. Processing video...")
    
    def _download_with_ytdlp(self, url: str) -> Optional[str]:
        """
        Download a video using yt-dlp.
        
        Args:
            url (str): Video URL
            
        Returns:
            Optional[str]: Path to the downloaded file or None if download fails
        """
        try:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Prefer MP4
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': False,
                'no_warnings': False,
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'extract_flat': False,
                'force_generic_extractor': False,
                'concurrent_fragment_downloads': 5,  # Speed up download with multiple connections
                'http_chunk_size': 10485760,  # 10MB chunks for better progress reporting
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

            # Get video info first
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                print(f"\nTitle: {info.get('title', 'Unknown')}")
                print(f"Duration: {info.get('duration', 0)} seconds")
                print(f"Description: {info.get('description', 'No description')[:200]}...")
                
                # Show available formats
                formats = info.get('formats', [])
                print("\nAvailable formats:")
                for f in formats:
                    if 'height' in f and 'ext' in f:
                        print(f"- {f.get('height', 'N/A')}p ({f.get('ext', 'N/A')})")
                
                # Download the video
                print("\nStarting download...")
                ydl.download([url])
                
                # Get the output filename
                output_path = os.path.join(
                    self.download_path,
                    self._sanitize_filename(info['title']) + '.mp4'
                )
                
                print(f"\nSuccessfully downloaded: {os.path.basename(output_path)}")
                return output_path
            
        except Exception as e:
            print(f"\nError downloading video: {str(e)}")
            if "429" in str(e):
                print("Too many requests. Please try again later.")
            elif "403" in str(e):
                print("Access forbidden. This might be due to regional restrictions.")
            return None
    
    def _download_direct_video(self, url: str) -> Optional[str]:
        """
        Download a video from a direct URL.
        
        Args:
            url (str): Direct video URL
            
        Returns:
            Optional[str]: Path to the downloaded file or None if download fails
        """
        try:
            # Send a GET request with stream=True to handle large files
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()
            
            # Try to get filename from Content-Disposition header
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                filename = re.findall("filename=(.+)", content_disposition)[0]
            else:
                # Generate filename from URL
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    filename = "video.mp4"
            
            filename = self._sanitize_filename(filename)
            output_path = os.path.join(self.download_path, filename)
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            # Download the file in chunks with progress
            print(f"\nDownloading: {filename}")
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percentage = (downloaded / total_size) * 100
                            print(f"\rDownload Progress: {percentage:.1f}%", end="")
            
            print(f"\nSuccessfully downloaded: {filename}")
            return output_path
            
        except Exception as e:
            print(f"\nError downloading video: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Remove invalid characters from filename.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Limit length
        return filename[:255]

def main():
    """Main function to demonstrate usage."""
    downloader = VideoDownloader()
    
    # Example usage
    url = input("Enter video URL to download: ")
    result = downloader.download_video(url)
    
    if result:
        print(f"Video downloaded successfully to: {result}")
    else:
        print("Failed to download video")

if __name__ == "__main__":
    main() 