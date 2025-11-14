"""
Main Entry Point
Điểm chạy chính của ứng dụng Douyin Video Downloader
"""

import tkinter as tk
import sys
import os
import logging
from datetime import datetime

# Thêm thư mục hiện tại vào path để import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cookie_manager import CookieManager
from downloader import VideoDownloader
from ui.main_window import MainWindow


def setup_global_logging():
    """Thiết lập logging toàn cục cho ứng dụng"""
    try:
        # Tạo thư mục logs
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Xóa tất cả log file cũ khi khởi động app
        try:
            import glob
            log_files = glob.glob(os.path.join(log_dir, "*.log"))
            deleted_count = 0
            for log_file in log_files:
                try:
                    os.remove(log_file)
                    deleted_count += 1
                except Exception as e:
                    print(f"[WARNING] Không thể xóa log file {log_file}: {e}")
            if deleted_count > 0:
                print(f"[INFO] Đã xóa {deleted_count} log file cũ")
        except Exception as e:
            print(f"[WARNING] Không thể xóa log file cũ: {e}")
        
        # Tạo file log với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"app_{timestamp}.log")
        
        # Cấu hình logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', mode='w'),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger('App')
        logger.info("=" * 60)
        logger.info("Douyin Video Downloader - Application Started")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 60)
        
        return logger, log_file
    except Exception as e:
        print(f"[ERROR] Không thể thiết lập logging: {e}")
        return None, None


def main():
    """Hàm main để khởi chạy ứng dụng"""
    logger, log_file = setup_global_logging()
    
    try:
        if logger:
            logger.info("Đang khởi tạo ứng dụng...")
        
        # Khởi tạo root window
        root = tk.Tk()
        if logger:
            logger.info("Root window đã được tạo")
        
        # Khởi tạo các module
        cookie_manager = CookieManager()
        if logger:
            logger.info("CookieManager đã được khởi tạo")
        
        # Khởi tạo main window
        app = MainWindow(root, cookie_manager, VideoDownloader, logger)
        if logger:
            logger.info("MainWindow đã được khởi tạo")
            logger.info("Ứng dụng sẵn sàng!")
        
        # Chạy ứng dụng
        if logger:
            logger.info("Bắt đầu mainloop...")
        root.mainloop()
        
        if logger:
            logger.info("Ứng dụng đã được đóng")
        
    except KeyboardInterrupt:
        if logger:
            logger.warning("Ứng dụng đã được dừng bởi người dùng (Ctrl+C)")
        print("\nỨng dụng đã được dừng bởi người dùng")
        sys.exit(0)
    except Exception as e:
        if logger:
            logger.error(f"Lỗi khi khởi chạy ứng dụng: {e}", exc_info=True)
        print(f"Lỗi khi khởi chạy ứng dụng: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


