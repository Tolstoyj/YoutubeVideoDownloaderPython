#!/usr/bin/env python3

import os
import sys
import yt_dlp
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QProgressBar,
    QLabel, QMessageBox, QHeaderView, QFrame, QGraphicsOpacityEffect,
    QStyleOption, QStyle, QScrollArea, QMenu, QToolButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QSize, QRect, QUrl
from PyQt6.QtGui import QIcon, QColor, QPainter, QPalette, QDesktopServices, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from qt_material import apply_stylesheet, list_themes

class MaterialFrame(QFrame):
    """A custom frame with material design shadow and hover effects."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("materialFrame")
        self._hover = False
        self.setStyleSheet("""
            #materialFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw base style
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        
        # Draw hover effect
        if self._hover:
            p.fillRect(self.rect(), QColor(255, 255, 255, 20))

class AnimatedButton(QPushButton):
    """A button with hover and click animations."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("animatedButton")
        self.setStyleSheet("""
            #animatedButton {
                background-color: #009688;
                border-radius: 20px;
                padding: 10px;
                color: white;
                font-weight: bold;
            }
            #animatedButton:hover {
                background-color: #00796B;
            }
            #animatedButton:pressed {
                background-color: #00695C;
            }
        """)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(100)
        
    def enterEvent(self, event):
        self._animate_hover(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._animate_hover(False)
        super().leaveEvent(event)
        
    def _animate_hover(self, hover: bool):
        rect = self.geometry()
        if hover:
            target = QRect(rect.x(), rect.y() - 2, rect.width(), rect.height())
        else:
            target = QRect(rect.x(), rect.y() + 2, rect.width(), rect.height())
        self._animation.setEndValue(target)
        self._animation.start()

class MaterialLineEdit(QLineEdit):
    """A custom line edit with material design styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("materialLineEdit")
        self.setStyleSheet("""
            #materialLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                color: white;
                font-size: 14px;
            }
            #materialLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)

class MaterialTable(QTableWidget):
    """A custom table with material design styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("materialTable")
        self.setStyleSheet("""
            #materialTable {
                background-color: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 10px;
                gridline-color: rgba(255, 255, 255, 0.1);
            }
            #materialTable::item {
                padding: 10px;
            }
            #materialTable::item:selected {
                background-color: rgba(0, 150, 136, 0.3);
            }
        """)
        self.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: rgba(255, 255, 255, 0.1);
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)

class MaterialProgressBar(QProgressBar):
    """A custom progress bar with material design styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("materialProgressBar")
        self.setStyleSheet("""
            #materialProgressBar {
                border: none;
                border-radius: 15px;
                background-color: rgba(255, 255, 255, 0.1);
                text-align: center;
            }
            #materialProgressBar::chunk {
                background-color: #009688;
                border-radius: 15px;
            }
        """)

class DownloaderThread(QThread):
    """Worker thread for downloading videos."""
    
    progress = pyqtSignal(float)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, url: str, format_id: str, download_path: str):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.download_path = download_path
        
    def progress_hook(self, d: Dict[str, Any]) -> None:
        """Progress callback for yt-dlp."""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress.emit(percentage)
            elif 'downloaded_bytes' in d:
                self.progress.emit(float(d['downloaded_bytes'] / 1024 / 1024))
                
    def run(self):
        """Run the download process."""
        try:
            ydl_opts = {
                'format': self.format_id,
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filename = ydl.prepare_filename(info)
                self.finished.emit(filename)
                
        except Exception as e:
            self.error.emit(str(e))

class VideoPreviewWidget(QFrame):
    """A widget to show video preview and thumbnail."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("previewFrame")
        self.setStyleSheet("""
            #previewFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Thumbnail label
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setMinimumHeight(200)
        self.thumbnail_label.setStyleSheet("border-radius: 5px;")
        layout.addWidget(self.thumbnail_label)
        
        # Web view for video preview
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(300)
        self.web_view.setStyleSheet("border-radius: 5px;")
        layout.addWidget(self.web_view)
        
        # Initially hide the preview
        self.setVisible(False)
    
    def set_thumbnail(self, url: str):
        """Set the video thumbnail."""
        # Download thumbnail using yt-dlp
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info.get('thumbnail')
                if thumbnail_url:
                    # Download thumbnail using requests
                    import requests
                    response = requests.get(thumbnail_url)
                    if response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(response.content)
                        scaled_pixmap = pixmap.scaled(640, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.thumbnail_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
    
    def set_preview(self, video_id: str):
        """Set the video preview using YouTube embed."""
        self.web_view.setHtml(f'''
            <html>
                <body style="margin: 0; background-color: #121212;">
                    <iframe 
                        width="100%" 
                        height="100%" 
                        src="https://www.youtube.com/embed/{video_id}"
                        frameborder="0" 
                        allowfullscreen>
                    </iframe>
                </body>
            </html>
        ''')
        self.setVisible(True)

class DownloadHistoryWidget(MaterialFrame):
    """Widget to show download history and quick actions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Recent Downloads")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #009688;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # Downloads list
        self.downloads_list = QTableWidget()
        self.downloads_list.setColumnCount(2)
        self.downloads_list.setHorizontalHeaderLabels(["File", "Actions"])
        self.downloads_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.downloads_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.downloads_list.setColumnWidth(1, 100)
        self.downloads_list.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.downloads_list)
    
    def add_download(self, filename: str):
        """Add a new download to the history."""
        row = self.downloads_list.rowCount()
        self.downloads_list.insertRow(row)
        
        # File name
        self.downloads_list.setItem(row, 0, QTableWidgetItem(os.path.basename(filename)))
        
        # Actions button
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        actions_btn = QToolButton()
        actions_btn.setText("⋮")
        actions_btn.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
                color: white;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        
        menu = QMenu(actions_btn)
        menu.setStyleSheet("""
            QMenu {
                background-color: #424242;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: white;
            }
            QMenu::item:selected {
                background-color: #009688;
            }
        """)
        
        open_action = menu.addAction("Open File")
        open_folder_action = menu.addAction("Show in Folder")
        
        actions_btn.setMenu(menu)
        actions_layout.addWidget(actions_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.downloads_list.setCellWidget(row, 1, actions_widget)
        
        # Connect actions
        open_action.triggered.connect(lambda: self.open_file(filename))
        open_folder_action.triggered.connect(lambda: self.show_in_folder(filename))
    
    def open_file(self, filename: str):
        """Open the downloaded file."""
        QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
    
    def show_in_folder(self, filename: str):
        """Show the file in its folder."""
        try:
            if platform.system() == 'Windows':
                os.startfile(os.path.dirname(filename))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', '-R', filename])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.dirname(filename)])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {str(e)}")

class VideoDownloaderGUI(QMainWindow):
    """Main window for the video downloader application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Downloader")
        self.setMinimumSize(1200, 800)
        
        # Create downloads directory using pathlib for cross-platform compatibility
        self.download_path = Path.home() / "Downloads" / "VideoDownloader"
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize UI
        self.init_ui()
        
        # Add fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.centralWidget().setGraphicsEffect(self.opacity_effect)
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        QTimer.singleShot(100, self.fade_in_animation.start)
        
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Left panel (download controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("YouTube Video Downloader")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #009688;
            margin-bottom: 20px;
        """)
        left_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # URL input
        url_frame = MaterialFrame()
        url_layout = QHBoxLayout(url_frame)
        url_layout.setSpacing(15)
        
        self.url_input = MaterialLineEdit()
        self.url_input.setPlaceholderText("Enter video URL...")
        self.url_input.setMinimumHeight(45)
        
        self.fetch_button = AnimatedButton("Fetch Info")
        self.fetch_button.setMinimumHeight(45)
        self.fetch_button.clicked.connect(self.fetch_video_info)
        
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.fetch_button)
        left_layout.addWidget(url_frame)
        
        # Video info
        info_frame = MaterialFrame()
        info_layout = QVBoxLayout(info_frame)
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.87);
            padding: 10px;
        """)
        info_layout.addWidget(self.info_label)
        left_layout.addWidget(info_frame)
        
        # Formats table
        table_frame = MaterialFrame()
        table_layout = QVBoxLayout(table_frame)
        self.formats_table = MaterialTable()
        self.formats_table.setColumnCount(4)
        self.formats_table.setHorizontalHeaderLabels(["Quality", "Extension", "Size", "Format Code"])
        self.formats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.formats_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table_layout.addWidget(self.formats_table)
        left_layout.addWidget(table_frame)
        
        # Progress section
        progress_frame = MaterialFrame()
        progress_layout = QVBoxLayout(progress_frame)
        self.progress_bar = MaterialProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
        """)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        left_layout.addWidget(progress_frame)
        
        # Download button
        self.download_button = AnimatedButton("Download")
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setEnabled(False)
        left_layout.addWidget(self.download_button)
        
        main_layout.addWidget(left_panel)
        
        # Right panel (preview and history)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # Video preview
        self.preview_widget = VideoPreviewWidget()
        right_layout.addWidget(self.preview_widget)
        
        # Download history
        self.history_widget = DownloadHistoryWidget()
        right_layout.addWidget(self.history_widget)
        
        main_layout.addWidget(right_panel)
        
        # Set layout proportions
        main_layout.setStretch(0, 3)  # Left panel
        main_layout.setStretch(1, 2)  # Right panel
    
    def fade_widget(self, widget: QWidget, fade_in: bool):
        """Create a fade animation for a widget."""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0 if fade_in else 1)
        animation.setEndValue(1 if fade_in else 0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.start()
        
    def fetch_video_info(self):
        """Fetch video information and available formats."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a video URL")
            return
        
        try:
            self.fetch_button.setEnabled(False)
            self.info_label.setText("Fetching video information...")
            self.fade_widget(self.info_label, True)
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Update preview
                if 'id' in info:
                    self.preview_widget.set_thumbnail(url)
                    self.preview_widget.set_preview(info['id'])
                
                # Display video info with fade animation
                self.fade_widget(self.info_label, False)
                QTimer.singleShot(300, lambda: self.update_video_info(info))
                
                # Update formats table
                self.formats_table.setRowCount(0)
                formats = info.get('formats', [])
                
                for f in formats:
                    if 'height' in f and f.get('vcodec', 'none') != 'none':
                        row = self.formats_table.rowCount()
                        self.formats_table.insertRow(row)
                        
                        # Quality
                        quality = f"{f.get('height', 'N/A')}p"
                        if f.get('fps'):
                            quality += f" {f['fps']}fps"
                        self.formats_table.setItem(row, 0, QTableWidgetItem(quality))
                        
                        # Extension
                        self.formats_table.setItem(row, 1, QTableWidgetItem(f.get('ext', 'N/A')))
                        
                        # Size
                        filesize = f.get('filesize', 0)
                        if filesize > 0:
                            size = f"{filesize / 1024 / 1024:.1f} MB"
                        else:
                            size = "N/A"
                        self.formats_table.setItem(row, 2, QTableWidgetItem(size))
                        
                        # Format code
                        self.formats_table.setItem(row, 3, QTableWidgetItem(str(f['format_id'])))
                
                self.download_button.setEnabled(True)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error fetching video info: {str(e)}")
        finally:
            self.fetch_button.setEnabled(True)
    
    def update_video_info(self, info: Dict[str, Any]):
        """Update video information with fade effect."""
        self.info_label.setText(
            f"Title: {info['title']}\n"
            f"Duration: {info.get('duration', 0)} seconds\n"
            f"Channel: {info.get('uploader', 'Unknown')}"
        )
        self.fade_widget(self.info_label, True)
    
    def start_download(self):
        """Start the video download process."""
        selected_rows = self.formats_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Please select a format")
            return
            
        format_id = self.formats_table.item(selected_rows[0].row(), 3).text()
        url = self.url_input.text().strip()
        
        # Create and start download thread
        self.download_thread = DownloaderThread(url, format_id, self.download_path)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.download_error)
        
        self.download_button.setEnabled(False)
        self.fetch_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloading...")
        
        self.download_thread.start()
    
    def update_progress(self, percentage: float):
        """Update the progress bar."""
        self.progress_bar.setValue(int(percentage))
    
    def download_finished(self, filename: str):
        """Handle download completion."""
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Downloaded: {os.path.basename(filename)}")
        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)
        
        # Add to download history
        self.history_widget.add_download(filename)
        
        # Show success message with options
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText("Download completed!")
        msg.setInformativeText(f"File saved as: {os.path.basename(filename)}")
        
        open_button = msg.addButton("Open File", QMessageBox.ButtonRole.ActionRole)
        show_folder_button = msg.addButton("Show in Folder", QMessageBox.ButtonRole.ActionRole)
        close_button = msg.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #424242;
            }
            QMessageBox QLabel {
                color: white;
            }
            QPushButton {
                background-color: #009688;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
        """)
        
        msg.exec()
        
        try:
            if msg.clickedButton() == open_button:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
            elif msg.clickedButton() == show_folder_button:
                if platform.system() == 'Windows':
                    os.startfile(os.path.dirname(filename))
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', filename])
                else:  # Linux
                    subprocess.run(['xdg-open', os.path.dirname(filename)])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file or folder: {str(e)}")
    
    def download_error(self, error: str):
        """Handle download errors."""
        self.status_label.setText("Error")
        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.setText("Download failed!")
        msg.setInformativeText(str(error))
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #424242;
            }
            QMessageBox QLabel {
                color: white;
            }
            QPushButton {
                background-color: #009688;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
        """)
        msg.exec()

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Apply material design theme with custom colors
    apply_stylesheet(app, theme='dark_teal.xml')
    
    # Override some styles with platform-specific fonts
    if platform.system() == 'Windows':
        font_family = 'Segoe UI'
    elif platform.system() == 'Darwin':  # macOS
        font_family = '-apple-system'  # Changed from SF Pro Text
    else:  # Linux
        font_family = 'Roboto'
    
    app.setStyleSheet(f"""
        QMainWindow {{
            background-color: #121212;
        }}
        QWidget {{
            font-family: {font_family}, BlinkMacSystemFont, 'Roboto', sans-serif;
        }}
        QTableWidget {{
            gridline-color: rgba(255, 255, 255, 0.1);
        }}
        QHeaderView::section {{
            background-color: #1e1e1e;
            padding: 5px;
            border: none;
            font-weight: bold;
        }}
    """)
    
    # Create and show main window
    window = VideoDownloaderGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 