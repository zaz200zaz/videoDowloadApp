"""
Main Entry Point
Điểm chạy chính của ứng dụng Douyin Video Downloader

Mục tiêu:
- Khởi tạo và chạy ứng dụng Douyin Video Downloader
- Thiết lập logging toàn cục
- Quản lý vòng đời ứng dụng

Input: Không có (entry point)
Output: Ứng dụng GUI chạy cho đến khi người dùng đóng
"""

import tkinter as tk
import sys
import os
import logging
from datetime import datetime

# Thêm thư mục hiện tại vào path để import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.cookie_manager import CookieManager
from ui.main_window import MainWindow
from utils.log_helper import write_log, get_logger
# Import Main Dashboard (FR-001)
try:
    from gui.main_dashboard import MainDashboard
    from gui.download_douyin_screen import DownloadDouyinScreen
    from gui.edit_video_screen import EditVideoScreen
    from gui.controllers.navigation_controller import NavigationController
    GUI_AVAILABLE = True
except ImportError as e:
    GUI_AVAILABLE = False
    print(f"Warning: GUI modules not available: {e}")

# Import MainWindow cũ (theo FR-001: mở trực tiếp màn hình cũ, giữ nguyên logic)
try:
    from ui.main_window import MainWindow as LegacyMainWindow
    MAINWINDOW_AVAILABLE = True
except ImportError as e:
    MAINWINDOW_AVAILABLE = False
    print(f"Warning: MainWindow not available: {e}")


def setup_global_logging():
    """
    Thiết lập logging toàn cục cho ứng dụng
    
    Returns:
        tuple: (logger, log_file_path) hoặc (None, None) nếu lỗi
        
    Exceptions:
        Exception: Bất kỳ lỗi nào khi thiết lập logging
    """
    function_name = "setup_global_logging"
    
    try:
        # Tạo thư mục logs (theo System Instruction: tự động tạo thư mục logs/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Xóa log file cũ (giữ lại 10 file gần nhất để debug)
        try:
            import glob
            log_files = glob.glob(os.path.join(log_dir, "*.log"))
            if len(log_files) > 10:
                # Sắp xếp theo thời gian sửa đổi (cũ nhất trước)
                log_files.sort(key=lambda x: os.path.getmtime(x))
                # Xóa các file cũ (giữ lại 10 file gần nhất)
                files_to_delete = log_files[:-10]
                deleted_count = 0
                for log_file in files_to_delete:
                    try:
                        os.remove(log_file)
                        deleted_count += 1
                    except Exception as e:
                        # Log warning nhưng không dừng quá trình
                        temp_logger = get_logger('App')
                        write_log('WARNING', function_name, 
                                 f"Không thể xóa log file {log_file}: {e}", 
                                 temp_logger, exc_info=True)
                
                if deleted_count > 0:
                    temp_logger = get_logger('App')
                    write_log('INFO', function_name, 
                             f"Đã xóa {deleted_count} log file cũ (giữ lại 10 file gần nhất)", 
                             temp_logger)
        except Exception as e:
            # Log warning nhưng không dừng quá trình
            temp_logger = get_logger('App')
            write_log('WARNING', function_name, 
                     f"Không thể xóa log file cũ: {e}", 
                     temp_logger, exc_info=True)
        
        # Tạo file log với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"app_{timestamp}.log")
        
        # Cấu hình logging theo System Instruction format
        # Format: [timestamp] [LEVEL] [Function] Message
        # Note: write_log() đã thêm [Function] vào message, nên formatter chỉ cần [timestamp] [LEVEL] message
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', mode='w'),
                logging.StreamHandler()
            ],
            force=True  # Force reload configuration
        )
        
        # Tắt urllib3 DEBUG logs để giảm log file size (theo System Instruction)
        # Phải thiết lập trước khi có bất kỳ request nào
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
        
        logger = get_logger('App')
        write_log('INFO', function_name, "=" * 60, logger)
        write_log('INFO', function_name, "Douyin Video Downloader - Application Started", logger)
        write_log('INFO', function_name, f"Log file: {log_file}", logger)
        write_log('INFO', function_name, "=" * 60, logger)
        
        return logger, log_file
        
    except Exception as e:
        # Log lỗi đầy đủ theo System Instruction
        temp_logger = get_logger('App')
        write_log('ERROR', function_name, 
                 f"Không thể thiết lập logging: {e}", 
                 temp_logger, exc_info=True)
        print(f"[ERROR] Không thể thiết lập logging: {e}")
        return None, None


def main():
    """
    Hàm main để khởi chạy ứng dụng
    
    Flow:
    1. Thiết lập logging
    2. Khởi tạo root window
    3. Khởi tạo CookieManager
    4. Khởi tạo MainWindow
    5. Chạy mainloop
    
    Exceptions:
        KeyboardInterrupt: Người dùng dừng ứng dụng (Ctrl+C)
        Exception: Bất kỳ lỗi nào khi khởi chạy ứng dụng
    """
    function_name = "main"
    
    # Bước 1: Thiết lập logging
    logger, log_file = setup_global_logging()
    if logger:
        write_log('INFO', function_name, "Bắt đầu khởi chạy ứng dụng", logger)
    
    try:
        # Bước 2: Khởi tạo root window
        if logger:
            write_log('INFO', function_name, "Đang khởi tạo root window...", logger)
        root = tk.Tk()
        if logger:
            write_log('INFO', function_name, "Root window đã được tạo thành công", logger)
        
        # Bước 3: Khởi tạo CookieManager
        if logger:
            write_log('INFO', function_name, "Đang khởi tạo CookieManager...", logger)
        cookie_manager = CookieManager()
        if logger:
            write_log('INFO', function_name, "CookieManager đã được khởi tạo thành công", logger)
        
        # Bước 4: Khởi tạo Main Dashboard (FR-001) hoặc MainWindow (legacy)
        if GUI_AVAILABLE:
            # Sử dụng Main Dashboard mới (FR-001)
            if logger:
                write_log('INFO', function_name, "Đang khởi tạo Main Dashboard (FR-001)...", logger)
            
            # Thiết lập root window cho Main Dashboard
            root.title("Douyin Video Downloader")
            root.geometry("800x600")
            root.configure(bg="#f0f0f0")
            
            # Mobile-style layout: Header (Nav Bar) + Content Container
            header = tk.Frame(root, bg="#ffffff", height=48)
            header.pack(side=tk.TOP, fill=tk.X)
            content_container = tk.Frame(root, bg="#f0f0f0")
            content_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Header: Back button + Title
            back_btn = tk.Button(header, text="← Back", relief=tk.FLAT, bg="#ffffff", activebackground="#f2f2f2", cursor="hand2")
            back_btn.pack(side=tk.LEFT, padx=12, pady=8)
            title_var = tk.StringVar(value="Home")
            title_lbl = tk.Label(header, textvariable=title_var, bg="#ffffff", font=("Arial", 14, "bold"))
            title_lbl.pack(side=tk.TOP, pady=8)
            
            # Tạo navigation controller với mobile_mode (frame-based stack)
            navigation_controller = NavigationController(
                root, logger, home_screen_name="MainDashboard",
                content_container=content_container, mobile_mode=True
            )
            
            # Đăng ký screens (theo FR-001: hệ thống dễ dàng mở rộng)
            # Đăng ký MainWindow cũ (theo FR-001: mở trực tiếp màn hình cũ, giữ nguyên logic)
            if MAINWINDOW_AVAILABLE:
                navigation_controller.register_screen("MainWindow", LegacyMainWindow)
            navigation_controller.register_screen("EditVideoScreen", EditVideoScreen)
            
            # Đăng ký MainDashboard làm Home
            navigation_controller.register_screen("MainDashboard", MainDashboard)
            
            # Wire back button
            def on_back():
                if navigation_controller.go_back():
                    # Update title based on current screen
                    current = navigation_controller.current_screen or "MainDashboard"
                    title_var.set("Home" if current == "MainDashboard" else ("Douyin Download" if current == "MainWindow" else current))
            back_btn.config(command=on_back)

            # Provide title update callback to navigation controller
            def set_title(screen_name: str):
                title_var.set("Home" if screen_name == "MainDashboard" else ("Douyin Download" if screen_name == "MainWindow" else screen_name))
            setattr(navigation_controller, 'set_title_callback', set_title)
            
            # Open Home
            navigation_controller.open_screen("MainDashboard", from_screen="App", cookie_manager=cookie_manager)
            title_var.set("Home")
            
            if logger:
                write_log('INFO', function_name, "Main Dashboard đã được khởi tạo thành công (FR-001)", logger)
                write_log('INFO', function_name, "Ứng dụng sẵn sàng!", logger)
        else:
            # Fallback to legacy MainWindow
            if logger:
                write_log('INFO', function_name, "Đang khởi tạo MainWindow (legacy)...", logger)
            app = MainWindow(root, cookie_manager, logger)
            if logger:
                write_log('INFO', function_name, "MainWindow đã được khởi tạo thành công", logger)
                write_log('INFO', function_name, "Ứng dụng sẵn sàng!", logger)
        
        # Bước 5: Chạy ứng dụng
        if logger:
            write_log('INFO', function_name, "Bắt đầu mainloop...", logger)
        root.mainloop()
        
        if logger:
            write_log('INFO', function_name, "Ứng dụng đã được đóng bởi người dùng", logger)
        
    except KeyboardInterrupt:
        # Người dùng dừng ứng dụng (Ctrl+C)
        if logger:
            write_log('WARNING', function_name, 
                     "Ứng dụng đã được dừng bởi người dùng (Ctrl+C)", logger)
        print("\nỨng dụng đã được dừng bởi người dùng")
        sys.exit(0)
        
    except Exception as e:
        # Lỗi khi khởi chạy ứng dụng - log đầy đủ theo System Instruction
        if logger:
            write_log('ERROR', function_name, 
                     f"Lỗi khi khởi chạy ứng dụng: {e}", 
                     logger, exc_info=True)
        else:
            # Fallback: nếu logger chưa sẵn sàng, in tối thiểu
            print(f"[ERROR] Lỗi khi khởi chạy ứng dụng: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


