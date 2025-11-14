"""
Main Entry Point
Điểm chạy chính của ứng dụng Douyin Video Downloader
"""

import tkinter as tk
import sys
import os

# Thêm thư mục hiện tại vào path để import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cookie_manager import CookieManager
from downloader import VideoDownloader
from ui.main_window import MainWindow


def main():
    """Hàm main để khởi chạy ứng dụng"""
    try:
        # Khởi tạo root window
        root = tk.Tk()
        
        # Khởi tạo các module
        cookie_manager = CookieManager()
        
        # Khởi tạo main window
        app = MainWindow(root, cookie_manager, VideoDownloader)
        
        # Chạy ứng dụng
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nỨng dụng đã được dừng bởi người dùng")
        sys.exit(0)
    except Exception as e:
        print(f"Lỗi khi khởi chạy ứng dụng: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


