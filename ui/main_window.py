"""
Main Window UI Module
Giao diện chính của ứng dụng sử dụng Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from typing import List, Callable, Optional, Dict
import queue
import logging


class MainWindow:
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self, root: tk.Tk, cookie_manager, logger=None):
        """
        Khởi tạo MainWindow
        
        Args:
            root: Tkinter root window
            cookie_manager: CookieManager instance
            logger: Logger instance (optional)
        """
        self.root = root
        self.cookie_manager = cookie_manager
        self.logger = logger or logging.getLogger('MainWindow')
        
        # Controllersを初期化
        from controllers.cookie_controller import CookieController
        from controllers.download_controller import DownloadController
        
        self.cookie_controller = CookieController(cookie_manager)
        self.download_controller = DownloadController(cookie_manager)
        
        if self.logger:
            self.logger.info("MainWindow.__init__ - Bắt đầu khởi tạo UI")
        
        # Trạng thái
        self.is_downloading = False
        self.should_stop = False
        self.download_queue = queue.Queue()
        self.results = []
        # Thống kê orientation filter (mới)
        self.filtered_videos = []  # Danh sách video bị filter do orientation
        
        # Thiết lập giao diện
        self._setup_ui()
        if self.logger:
            self.logger.info("MainWindow.__init__ - UI đã được thiết lập")
        self._load_saved_cookie()
        if self.logger:
            self.logger.info("MainWindow.__init__ - Khởi tạo hoàn tất")
    
    def _setup_ui(self):
        """Thiết lập giao diện"""
        self.root.title("Douyin Video Downloader")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Container chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ========== PHẦN 1: COOKIE ==========
        cookie_frame = ttk.LabelFrame(main_frame, text="1. Cookie Douyin", padding="10")
        cookie_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        cookie_frame.columnconfigure(0, weight=1)
        
        ttk.Label(cookie_frame, text="Nhập cookie Douyin:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.cookie_text = scrolledtext.ScrolledText(cookie_frame, height=4, wrap=tk.WORD)
        self.cookie_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        cookie_buttons = ttk.Frame(cookie_frame)
        cookie_buttons.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.load_cookie_btn = ttk.Button(cookie_buttons, text="Chọn file Cookie", command=self._load_cookie_from_file)
        self.load_cookie_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_cookie_btn = ttk.Button(cookie_buttons, text="Lưu Cookie", command=self._save_cookie)
        self.save_cookie_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_cookie_btn = ttk.Button(cookie_buttons, text="Xóa Cookie", command=self._clear_cookie)
        self.clear_cookie_btn.pack(side=tk.LEFT, padx=5)
        
        self.cookie_status_label = ttk.Label(cookie_frame, text="", foreground="gray")
        self.cookie_status_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # ========== PHẦN 2: LINK VIDEO ==========
        links_frame = ttk.LabelFrame(main_frame, text="2. Danh sách Link Video", padding="10")
        links_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        links_frame.columnconfigure(0, weight=1)
        links_frame.rowconfigure(1, weight=1, minsize=150)  # Đảm bảo có chiều cao tối thiểu
        main_frame.rowconfigure(1, weight=1)
        
        links_buttons = ttk.Frame(links_frame)
        links_buttons.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.import_btn = ttk.Button(links_buttons, text="Import từ file .txt", command=self._import_links)
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        self.get_user_videos_btn = ttk.Button(links_buttons, text="Lấy video từ user", command=self._get_user_videos)
        self.get_user_videos_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_links_btn = ttk.Button(links_buttons, text="Xóa tất cả", command=self._clear_links)
        self.clear_links_btn.pack(side=tk.LEFT, padx=5)
        
        # Tạo frame cho text area để đảm bảo hiển thị đúng
        text_frame = ttk.Frame(links_frame)
        text_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.links_text = scrolledtext.ScrolledText(text_frame, height=8, wrap=tk.WORD, state=tk.NORMAL)
        self.links_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(links_frame, text="Mỗi dòng một link video Douyin", foreground="gray").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=2
        )
        
        # ========== PHẦN 3: TẢI VIDEO ==========
        download_frame = ttk.LabelFrame(main_frame, text="3. Tải Video", padding="10")
        download_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        download_frame.columnconfigure(0, weight=1)
        
        download_buttons = ttk.Frame(download_frame)
        download_buttons.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.start_btn = ttk.Button(download_buttons, text="Bắt đầu tải", command=self._start_download)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(download_buttons, text="Dừng", command=self._stop_download, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.select_folder_btn = ttk.Button(download_buttons, text="Chọn thư mục", command=self._select_folder)
        self.select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Hiển thị đường dẫn lưu video
        download_folder = self.cookie_manager.get_download_folder()
        folder_label_text = f"Thư mục lưu: {download_folder}" if download_folder else "Thư mục lưu: Chưa chọn"
        self.folder_path_label = ttk.Label(download_frame, text=folder_label_text, foreground="blue", cursor="hand2")
        self.folder_path_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        # Thêm sự kiện click để mở thư mục
        self.folder_path_label.bind("<Button-1>", lambda e: self._open_download_folder())
        
        # Chọn định dạng video
        format_frame = ttk.Frame(download_frame)
        format_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(format_frame, text="Định dạng video:").pack(side=tk.LEFT, padx=5)
        saved_format = self.cookie_manager.get_setting("video_format", "auto")
        # Tìm text tương ứng với saved_format
        format_text = "Tự động (mặc định)"
        format_options_map = {
            "highest": "Chất lượng cao nhất",
            "high": "Chất lượng cao",
            "medium": "Chất lượng trung bình",
            "low": "Chất lượng thấp",
            "auto": "Tự động (mặc định)"
        }
        format_text = format_options_map.get(saved_format, "Tự động (mặc định)")
        self.video_format_var = tk.StringVar(value=format_text)
        format_options = [
            ("Chất lượng cao nhất", "highest"),
            ("Chất lượng cao", "high"),
            ("Chất lượng trung bình", "medium"),
            ("Chất lượng thấp", "low"),
            ("Tự động (mặc định)", "auto")
        ]
        self.video_format_combo = ttk.Combobox(format_frame, textvariable=self.video_format_var, 
                                               values=[opt[0] for opt in format_options], 
                                               state="readonly", width=25)
        self.video_format_combo.pack(side=tk.LEFT, padx=5)
        self.video_format_combo.bind("<<ComboboxSelected>>", self._on_format_changed)
        
        # Chọn lọc theo hướng video
        orientation_frame = ttk.Frame(download_frame)
        orientation_frame.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(orientation_frame, text="Lọc theo hướng (Landscape/Portrait):").pack(side=tk.LEFT, padx=5)
        saved_orientation = self.cookie_manager.get_setting("orientation_filter", "all")
        orientation_text_map = {
            "all": "Tất cả",
            "vertical": "Portrait (Video dọc)",
            "horizontal": "Landscape (Video ngang)"
        }
        orientation_text = orientation_text_map.get(saved_orientation, "Tất cả")
        self.orientation_var = tk.StringVar(value=orientation_text)
        orientation_options = [
            ("Tất cả", "all"),
            ("Portrait (Video dọc)", "vertical"),
            ("Landscape (Video ngang)", "horizontal")
        ]
        self.orientation_combo = ttk.Combobox(orientation_frame, textvariable=self.orientation_var,
                                              values=[opt[0] for opt in orientation_options],
                                              state="readonly", width=20)
        self.orientation_combo.pack(side=tk.LEFT, padx=5)
        self.orientation_combo.bind("<<ComboboxSelected>>", self._on_orientation_changed)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(download_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(download_frame, text="Sẵn sàng")
        self.progress_label.grid(row=5, column=0, sticky=tk.W, pady=2)
        
        # ========== PHẦN 4: DANH SÁCH TRẠNG THÁI ==========
        status_frame = ttk.LabelFrame(main_frame, text="4. Trạng thái tải", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Treeview để hiển thị danh sách
        columns = ('url', 'status', 'file')
        self.status_tree = ttk.Treeview(status_frame, columns=columns, show='headings', height=8)
        self.status_tree.heading('url', text='URL')
        self.status_tree.heading('status', text='Trạng thái')
        self.status_tree.heading('file', text='File')
        self.status_tree.column('url', width=300)
        self.status_tree.column('status', width=150)
        self.status_tree.column('file', width=200)
        self.status_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar cho treeview
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_tree.configure(yscrollcommand=scrollbar.set)
        
        # Thống kê
        self.stats_label = ttk.Label(status_frame, text="Tổng: 0 | Thành công: 0 | Thất bại: 0")
        self.stats_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Nút reset, log và xóa video
        reset_buttons = ttk.Frame(status_frame)
        reset_buttons.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.reset_btn = ttk.Button(reset_buttons, text="Reset App", command=self._reset_app)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_log_btn = ttk.Button(reset_buttons, text="Mở thư mục Log", command=self._open_log_folder)
        self.open_log_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_videos_btn = ttk.Button(reset_buttons, text="Xóa video đã tải", command=self._delete_downloaded_videos)
        self.delete_videos_btn.pack(side=tk.LEFT, padx=5)
    
    def _load_saved_cookie(self):
        """Tải cookie đã lưu vào ô nhập"""
        cookie = self.cookie_manager.get_cookie()
        if cookie:
            self.cookie_text.insert('1.0', cookie)
            self.cookie_status_label.config(text="✓ Đã tải cookie đã lưu", foreground="green")
        
        # Cập nhật hiển thị đường dẫn lưu video
        if hasattr(self, 'folder_path_label'):
            download_folder = self.cookie_manager.get_download_folder()
            if download_folder:
                self.folder_path_label.config(text=f"Thư mục lưu: {download_folder}")
            else:
                self.folder_path_label.config(text="Thư mục lưu: Chưa chọn")
    
    def _load_cookie_from_file(self):
        """Tải cookie từ file"""
        if self.logger:
            self.logger.info("User clicked: Chọn file Cookie button")
        file_path = filedialog.askopenfilename(
            title="Chọn file Cookie",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            if self.logger:
                self.logger.info("Chọn file Cookie - Người dùng đã hủy")
            return
        
        if self.logger:
            self.logger.info(f"Chọn file Cookie - File được chọn: {file_path}")
        
        # Controllerを使用してファイルから読み込み
        success, message, cookie_value = self.cookie_controller.load_cookie_from_file(file_path)
        
        if success and cookie_value:
            # UIを更新
            self.cookie_text.delete('1.0', tk.END)
            self.cookie_text.insert('1.0', cookie_value)
            self.cookie_status_label.config(
                text=f"✓ Đã tải cookie từ file: {os.path.basename(file_path)}",
                foreground="green"
            )
            if self.logger:
                self.logger.info(f"Chọn file Cookie - Thành công: {message}")
            messagebox.showinfo("Thành công", f"{message}\n\nFile: {os.path.basename(file_path)}")
        else:
            if self.logger:
                self.logger.error(f"Chọn file Cookie - {message}")
            messagebox.showerror("Lỗi", message)
    
    def _save_cookie(self):
        """Lưu cookie"""
        if self.logger:
            self.logger.info("User clicked: Lưu Cookie button")
        cookie = self.cookie_text.get('1.0', tk.END).strip()
        
        if not cookie:
            if self.logger:
                self.logger.warning("Lưu Cookie - Cookie rỗng, hiển thị cảnh báo")
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập cookie!")
            return
        
        # Controllerを使用して保存
        success, message = self.cookie_controller.save_cookie(cookie)
        
        if success:
            if self.logger:
                self.logger.info(f"Lưu Cookie - Thành công (length: {len(cookie)})")
            self.cookie_status_label.config(text="✓ Cookie đã được lưu", foreground="green")
            messagebox.showinfo("Thành công", message)
        else:
            if self.logger:
                self.logger.error(f"Lưu Cookie - {message}")
            self.cookie_status_label.config(text="✗ Lỗi khi lưu cookie", foreground="red")
            messagebox.showerror("Lỗi", message)
    
    def _import_links(self):
        """Import danh sách link từ file .txt"""
        if self.logger:
            self.logger.info("User clicked: Import từ file .txt button")
        file_path = filedialog.askopenfilename(
            title="Chọn file .txt (ví dụ: douyin-video-links.txt)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.logger:
                self.logger.info(f"Import links - File được chọn: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    messagebox.showwarning("Cảnh báo", "File rỗng!")
                    return
                
                # Đếm số link hợp lệ
                lines = content.split('\n')
                valid_links = []
                for line in lines:
                    line = line.strip()
                    if line and ('douyin.com' in line.lower() or 'http' in line.lower()):
                        valid_links.append(line)
                
                if not valid_links:
                    messagebox.showwarning("Cảnh báo", "Không tìm thấy link hợp lệ trong file!")
                    return
                
                # Xóa nội dung cũ và thêm link mới
                self.links_text.config(state=tk.NORMAL)  # Đảm bảo có thể chỉnh sửa
                self.links_text.delete('1.0', tk.END)
                links_to_insert = '\n'.join(valid_links)
                self.links_text.insert('1.0', links_to_insert)
                if self.logger:
                    self.logger.debug(f"Import links - Đã chèn {len(valid_links)} link vào text box, length: {len(links_to_insert)} characters")
                    # Kiểm tra lại nội dung sau khi chèn
                    content_after = self.links_text.get('1.0', tk.END).strip()
                    self.logger.debug(f"Import links - Nội dung sau khi chèn: {len(content_after)} characters, {len(content_after.split(chr(10)))} dòng")
                
                # Hỏi có muốn tự động bắt đầu tải không
                if self.logger:
                    self.logger.info(f"Import links - Đã import {len(valid_links)} link hợp lệ")
                result = messagebox.askyesno(
                    "Thành công",
                    f"Đã import {len(valid_links)} link từ file!\n\n"
                    f"Bạn có muốn bắt đầu tải ngay không?"
                )
                
                if result:
                    if self.logger:
                        self.logger.info("Import links - Người dùng chọn tự động bắt đầu tải")
                    # Tự động bắt đầu tải
                    self._start_download()
                else:
                    if self.logger:
                        self.logger.info("Import links - Người dùng chọn không tự động bắt đầu tải")
                    messagebox.showinfo("Thông tin", f"Đã import {len(valid_links)} link!\n\nNhấn 'Bắt đầu tải' để bắt đầu tải video.")
                    
            except UnicodeDecodeError:
                # Thử với encoding khác
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read().strip()
                    
                    lines = content.split('\n')
                    valid_links = []
                    for line in lines:
                        line = line.strip()
                        if line and ('douyin.com' in line.lower() or 'http' in line.lower()):
                            valid_links.append(line)
                    
                    if valid_links:
                        self.links_text.delete('1.0', tk.END)
                        self.links_text.insert('1.0', '\n'.join(valid_links))
                        
                        result = messagebox.askyesno(
                            "Thành công",
                            f"Đã import {len(valid_links)} link từ file!\n\n"
                            f"Bạn có muốn bắt đầu tải ngay không?"
                        )
                        
                        if result:
                            self._start_download()
                    else:
                        if self.logger:
                            self.logger.warning("Import links - Không tìm thấy link hợp lệ trong file (encoding khác), hiển thị cảnh báo")
                        messagebox.showwarning("Cảnh báo", "Không tìm thấy link hợp lệ trong file!")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Import links - Lỗi khi đọc file với encoding khác: {e}", exc_info=True)
                    messagebox.showerror("Lỗi", f"Không thể đọc file với encoding khác: {e}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Import links - Lỗi khi đọc file: {e}", exc_info=True)
                messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")
    
    def _get_user_videos(self):
        """Lấy tất cả video từ user profile (giống như JavaScript code)"""
        import tkinter.simpledialog as simpledialog
        
        # Nhập user URL
        user_url = simpledialog.askstring(
            "Lấy video từ User",
            "Nhập URL user profile Douyin:\n(Ví dụ: https://www.douyin.com/user/MS4wLjABAAAA...)\n\nHoặc chỉ cần user ID:",
            initialvalue=""
        )
        
        if not user_url:
            return
        
        # Nếu chỉ có user ID, thêm URL prefix
        if not user_url.startswith('http'):
            user_url = f"https://www.douyin.com/user/{user_url}"
        
        # Kiểm tra cookie
        cookie = self.cookie_manager.get_cookie()
        if not cookie:
            if self.logger:
                self.logger.warning("Lấy video từ user - Cookie chưa được lưu, hiển thị lỗi")
            messagebox.showerror("Lỗi", "Vui lòng nhập và lưu cookie trước!")
            return
        
        # Xác nhận
        result = messagebox.askyesno(
            "Xác nhận",
            f"Bạn có muốn lấy tất cả video từ user này không?\n\nURL: {user_url}\n\nQuá trình này có thể mất vài phút..."
        )
        
        if not result:
            if self.logger:
                self.logger.info("Lấy video từ user - Người dùng đã hủy")
            return
        
        if self.logger:
            self.logger.info("Lấy video từ user - Người dùng đã xác nhận")
        
        # Tạo progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Đang lấy video từ user...")
        progress_window.geometry("500x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Center window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
        progress_window.geometry(f"500x150+{x}+{y}")
        
        # Progress label
        progress_label = tk.Label(progress_window, text="Đang khởi tạo...", font=("Arial", 10))
        progress_label.pack(pady=20)
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = tk.ttk.Progressbar(progress_window, variable=progress_var, maximum=100, length=400, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start(10)  # Start indeterminate progress
        
        # Status label
        status_label = tk.Label(progress_window, text="", font=("Arial", 9), fg="gray")
        status_label.pack(pady=5)
        
        progress_window.update()
        
        # Progress callback function
        def update_progress(current, total, message):
            """Update progress in UI thread"""
            self.root.after(0, lambda: _update_progress_ui(current, total, message))
        
        def _update_progress_ui(current, total, message):
            """Update progress UI (called in main thread)"""
            progress_label.config(text=message)
            status_label.config(text=f"Đã tìm thấy: {current} video" if current > 0 else "")
            progress_window.update()
        
        # Lấy video URLs trong background thread
        def fetch_videos():
            try:
                from services.video_downloader import VideoDownloader
                import os
                from datetime import datetime
                import threading
                
                # Tạo log file cho việc lấy video từ user (sử dụng script directory)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # Nếu script_dir là ui/, lên một cấp
                if os.path.basename(script_dir) == 'ui':
                    script_dir = os.path.dirname(script_dir)
                log_dir = os.path.join(script_dir, "logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = os.path.join(log_dir, f"get_user_videos_{timestamp}.log")
                
                downloader = VideoDownloader(cookie, log_file)
                
                # Disable button trong khi xử lý
                self.root.after(0, lambda: self.get_user_videos_btn.config(state=tk.DISABLED))
                
                # Lấy video với progress callback
                video_urls = downloader.get_all_videos_from_user(user_url, progress_callback=update_progress)
                
                # Close progress window and show results in main thread
                self.root.after(0, lambda: _handle_results(video_urls))
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Lấy video từ user - Lỗi: {e}", exc_info=True)
                self.root.after(0, lambda: _handle_error(e))
        
        def _handle_results(video_urls):
            """Handle results in main thread"""
            # Stop progress bar
            progress_bar.stop()
            progress_bar.config(mode='determinate', maximum=100, value=100)
            
            # Close progress window
            progress_window.destroy()
            
            if video_urls:
                if self.logger:
                    self.logger.info(f"Lấy video từ user - Thành công, đã lấy {len(video_urls)} video")
                # Thêm vào text box
                links_text = '\n'.join(video_urls)
                self.links_text.delete('1.0', tk.END)
                self.links_text.insert('1.0', links_text)
                
                # Lưu vào file (giống như JavaScript code)
                save_path = filedialog.asksaveasfilename(
                    title="Lưu danh sách video",
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    initialfile="douyin-video-links.txt"
                )
                
                if save_path:
                    try:
                        with open(save_path, 'w', encoding='utf-8') as f:
                            f.write(links_text)
                        if self.logger:
                            self.logger.info(f"Lấy video từ user - Đã lưu vào file: {save_path}")
                        messagebox.showinfo(
                            "Thành công",
                            f"Đã lấy {len(video_urls)} video!\n\n"
                            f"Đã lưu vào file: {save_path}\n\n"
                            f"Bạn có thể:\n"
                            f"1. Sử dụng danh sách này để tải video\n"
                            f"2. Import vào IDM để tải hàng loạt"
                        )
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Lấy video từ user - Lỗi khi lưu file: {e}", exc_info=True)
                        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
                else:
                    if self.logger:
                        self.logger.info("Lấy video từ user - Người dùng đã hủy lưu file")
                    messagebox.showinfo(
                        "Thành công",
                        f"Đã lấy {len(video_urls)} video!\n\n"
                        f"Danh sách đã được thêm vào ô link video."
                    )
            else:
                if self.logger:
                    self.logger.warning("Lấy video từ user - Không tìm thấy video nào, hiển thị cảnh báo")
                messagebox.showwarning(
                    "Cảnh báo",
                    "Không tìm thấy video nào!\n\n"
                    "Có thể:\n"
                    "1. User không có video công khai\n"
                    "2. Cookie không hợp lệ\n"
                    "3. User ID không đúng"
                )
            
            # Re-enable button
            self.get_user_videos_btn.config(state=tk.NORMAL)
        
        def _handle_error(error):
            """Handle error in main thread"""
            # Stop progress bar
            progress_bar.stop()
            progress_bar.config(mode='determinate', maximum=100, value=0)
            
            # Close progress window
            progress_window.destroy()
            
            messagebox.showerror("Lỗi", f"Lỗi khi lấy video từ user: {error}")
            
            # Re-enable button
            self.get_user_videos_btn.config(state=tk.NORMAL)
        
        # Start fetching in background thread
        import threading
        thread = threading.Thread(target=fetch_videos, daemon=True)
        thread.start()
    
    def _clear_links(self):
        """Xóa tất cả link"""
        self.links_text.config(state=tk.NORMAL)
        self.links_text.delete('1.0', tk.END)
    
    def _clear_cookie(self):
        """Xóa cookie đã lưu"""
        if self.logger:
            self.logger.info("User clicked: Xóa Cookie button")
        result = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa cookie đã lưu không?"
        )
        
        if result:
            if self.logger:
                self.logger.info("Xóa Cookie - Người dùng đã xác nhận")
            if self.cookie_manager.clear_cookie():
                if self.logger:
                    self.logger.info("Xóa Cookie - Thành công")
                # Xóa cookie trong text box
                self.cookie_text.delete('1.0', tk.END)
                self.cookie_status_label.config(text="✓ Cookie đã được xóa", foreground="green")
                messagebox.showinfo("Thành công", "Cookie đã được xóa!")
            else:
                if self.logger:
                    self.logger.error("Xóa Cookie - Lỗi khi xóa cookie")
                messagebox.showerror("Lỗi", "Không thể xóa cookie!")
        else:
            if self.logger:
                self.logger.info("Xóa Cookie - Người dùng đã hủy")
    
    def _reset_app(self):
        """Reset toàn bộ app về trạng thái ban đầu"""
        if self.logger:
            self.logger.info("User clicked: Reset App button")
        result = messagebox.askyesno(
            "Xác nhận Reset",
            "Bạn có chắc chắn muốn reset toàn bộ app về trạng thái ban đầu không?\n\n"
            "Điều này sẽ:\n"
            "- Xóa cookie đã lưu\n"
            "- Reset các settings về mặc định\n"
            "- Xóa danh sách link video\n"
            "- Xóa trạng thái tải\n\n"
            "Thư mục download sẽ không bị xóa."
        )
        
        if result:
            if self.logger:
                self.logger.info("Reset App - Người dùng đã xác nhận")
            if self.cookie_manager.reset_all():
                # Xóa cookie trong text box
                self.cookie_text.delete('1.0', tk.END)
                self.cookie_status_label.config(text="", foreground="gray")
                
                # Xóa danh sách link
                self.links_text.config(state=tk.NORMAL)
                self.links_text.delete('1.0', tk.END)
                
                # Reset trạng thái tải
                self.status_tree.delete(*self.status_tree.get_children())
                self.stats_label.config(text="Tổng: 0 | Thành công: 0 | Thất bại: 0")
                self.progress_var.set(0)
                self.progress_label.config(text="Sẵn sàng")
                
                # Reset buttons
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                
                # Đảm bảo links_text có thể nhập được
                self.links_text.config(state=tk.NORMAL)
                
                messagebox.showinfo("Thành công", "App đã được reset về trạng thái ban đầu!")
            else:
                messagebox.showerror("Lỗi", "Không thể reset app!")
    
    def _on_format_changed(self, event=None):
        """Xử lý khi người dùng thay đổi định dạng video"""
        selected_format = self.video_format_var.get()
        # Lưu setting
        format_map = {
            "Chất lượng cao nhất": "highest",
            "Chất lượng cao": "high",
            "Chất lượng trung bình": "medium",
            "Chất lượng thấp": "low",
            "Tự động (mặc định)": "auto"
        }
        format_value = format_map.get(selected_format, "auto")
        self.cookie_manager.set_setting("video_format", format_value)
        if self.logger:
            self.logger.info(f"Định dạng video đã thay đổi: {selected_format} ({format_value})")
    
    def _on_orientation_changed(self, event=None):
        """Xử lý khi người dùng thay đổi lọc theo hướng video"""
        selected_orientation = self.orientation_var.get()
        # Lưu setting
        orientation_map = {
            "Tất cả": "all",
            "Portrait (Video dọc)": "vertical",
            "Landscape (Video ngang)": "horizontal",
            # Backward compatibility
            "Video dọc": "vertical",
            "Video ngang": "horizontal"
        }
        orientation_value = orientation_map.get(selected_orientation, "all")
        self.cookie_manager.set_setting("orientation_filter", orientation_value)
        if self.logger:
            filter_display_map = {
                "all": "Tất cả",
                "vertical": "Portrait (Video dọc)",
                "horizontal": "Landscape (Video ngang)"
            }
            filter_display = filter_display_map.get(orientation_value, orientation_value)
            self.logger.info(f"Lọc theo hướng video đã thay đổi: {selected_orientation} ({orientation_value})")
            self.logger.info(f"  - Filter: {filter_display}")
            self.logger.info(f"  - Mô tả: {'Tải tất cả video' if orientation_value == 'all' else ('Chỉ tải video dọc (height > width)' if orientation_value == 'vertical' else 'Chỉ tải video ngang (width > height)')}")
    
    def _select_folder(self):
        """Chọn thư mục lưu video"""
        if self.logger:
            self.logger.info("User clicked: Chọn thư mục button")
        folder = filedialog.askdirectory(title="Chọn thư mục lưu video")
        if folder:
            if self.logger:
                self.logger.info(f"Chọn thư mục - Thư mục được chọn: {folder}")
            self.cookie_manager.set_download_folder(folder)
            # Cập nhật label hiển thị đường dẫn
            self.folder_path_label.config(text=f"Thư mục lưu: {folder}")
            messagebox.showinfo("Thành công", f"Đã chọn thư mục: {folder}")
        else:
            if self.logger:
                self.logger.info("Chọn thư mục - Người dùng đã hủy")
    
    def _open_download_folder(self):
        """Mở thư mục download"""
        import subprocess
        import platform
        
        download_folder = self.cookie_manager.get_download_folder()
        if not download_folder:
            if self.logger:
                self.logger.warning("Mở thư mục download - Chưa chọn thư mục")
            messagebox.showwarning("Cảnh báo", "Chưa chọn thư mục lưu video!")
            return
        
        if not os.path.exists(download_folder):
            if self.logger:
                self.logger.warning(f"Mở thư mục download - Thư mục không tồn tại: {download_folder}")
            messagebox.showerror("Lỗi", f"Thư mục không tồn tại:\n{download_folder}")
            return
        
        try:
            if self.logger:
                self.logger.info(f"Mở thư mục download - Đang mở: {download_folder}")
            if platform.system() == 'Windows':
                os.startfile(download_folder)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', download_folder])
            else:  # Linux
                subprocess.Popen(['xdg-open', download_folder])
        except Exception as e:
            if self.logger:
                self.logger.error(f"Mở thư mục download - Lỗi: {e}", exc_info=True)
            messagebox.showerror("Lỗi", f"Không thể mở thư mục:\n{download_folder}\n\nLỗi: {e}")
    
    def _open_log_folder(self):
        """Mở thư mục chứa log files"""
        import os
        import subprocess
        import platform
        
        # Sử dụng script directory thay vì current working directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Nếu script_dir là ui/, lên một cấp
        if os.path.basename(script_dir) == 'ui':
            script_dir = os.path.dirname(script_dir)
        log_dir = os.path.join(script_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        try:
            if platform.system() == 'Windows':
                os.startfile(log_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', log_dir])
            else:  # Linux
                subprocess.Popen(['xdg-open', log_dir])
        except Exception as e:
            if self.logger:
                self.logger.error(f"Mở thư mục log - Lỗi: {e}", exc_info=True)
            messagebox.showerror("Lỗi", f"Không thể mở thư mục log: {e}\n\nThư mục log: {log_dir}")
    
    def _delete_downloaded_videos(self):
        """Xóa các video đã tải thành công"""
        if self.logger:
            self.logger.info("User clicked: Xóa video đã tải button")
            self.logger.info(f"Current self.results count: {len(self.results)}")
            for idx, r in enumerate(self.results):
                self.logger.info(f"  Result {idx}: success={r.get('success')}, file_path={r.get('file_path')}")
        
        # Kiểm tra xem có video nào đã tải thành công không
        successful_videos = [r for r in self.results if r.get('success') and r.get('file_path')]
        
        if self.logger:
            self.logger.info(f"Found {len(successful_videos)} successful videos in self.results")
        
        # ダウンロードフォルダからも直接ファイルを探す
        download_folder = self.cookie_manager.get_download_folder()
        all_video_files = []
        if download_folder and os.path.exists(download_folder):
            if self.logger:
                self.logger.info(f"Scanning download folder: {download_folder}")
            # 再帰的にすべてのビデオファイルを探す
            for root, dirs, files in os.walk(download_folder):
                for file in files:
                    if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.webm')):
                        full_path = os.path.join(root, file)
                        all_video_files.append(full_path)
            if self.logger:
                self.logger.info(f"Found {len(all_video_files)} video files in download folder")
        
        # どちらか一方でもファイルがあれば削除を実行
        if not successful_videos and not all_video_files:
            if self.logger:
                self.logger.info("Xóa video - Không có video nào đã tải thành công")
            messagebox.showinfo("Thông tin", "Không có video nào đã tải thành công để xóa.")
            return
        
        # 削除対象のファイル数を計算
        total_files = len(successful_videos) if successful_videos else len(all_video_files)
        
        # Xác nhận xóa
        result = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa {total_files} video đã tải thành công không?\n\n"
            f"Thao tác này không thể hoàn tác!"
        )
        
        if not result:
            if self.logger:
                self.logger.info("Xóa video - Người dùng đã hủy")
            return
        
        # Controllerを使用して削除（self.resultsから）
        deleted_count = 0
        failed_count = 0
        failed_files = []
        
        if successful_videos:
            deleted_count, failed_count, failed_files = self.download_controller.delete_downloaded_videos(self.results)
        
        # ダウンロードフォルダから直接削除（self.resultsにない場合）
        if all_video_files:
            for file_path in all_video_files:
                # self.resultsに含まれているかチェック
                already_deleted = False
                if successful_videos:
                    for video_result in successful_videos:
                        if video_result.get('file_path') == file_path:
                            already_deleted = True
                            break
                
                if not already_deleted and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        if self.logger:
                            self.logger.info(f"Deleted file from filesystem: {file_path}")
                    except Exception as e:
                        failed_count += 1
                        failed_files.append(file_path)
                        if self.logger:
                            self.logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
        
        # UIを更新
        for video_result in successful_videos:
            file_path = video_result.get('file_path')
            if file_path:
                file_basename = os.path.basename(file_path)
                for item in self.status_tree.get_children():
                    values = self.status_tree.item(item, 'values')
                    if len(values) >= 3:
                        if values[2] == file_basename or values[2] == file_path:
                            self.status_tree.item(item, values=(values[0], 'Đã xóa', ''))
                            break
        
        # Hiển thị kết quả
        if failed_count == 0:
            if self.logger:
                self.logger.info(f"Xóa video - Thành công: Đã xóa {deleted_count} video")
            messagebox.showinfo("Thành công", f"Đã xóa {deleted_count} video thành công!")
        else:
            if self.logger:
                self.logger.warning(f"Xóa video - Một số file không thể xóa: {deleted_count} thành công, {failed_count} thất bại")
            messagebox.showwarning(
                "Cảnh báo",
                f"Đã xóa {deleted_count} video thành công.\n"
                f"{failed_count} video không thể xóa:\n\n" +
                "\n".join([os.path.basename(f) for f in failed_files[:5]]) +
                (f"\n... và {len(failed_files) - 5} file khác" if len(failed_files) > 5 else "")
            )
        
        # Cập nhật thống kê
        total = len(self.results)
        success = sum(1 for r in self.results if r.get('success'))
        failed = total - success
        self.stats_label.config(text=f"Tổng: {total} | Thành công: {success} | Thất bại: {failed}")
    
    def _get_links(self) -> List[str]:
        """Lấy danh sách link từ text box"""
        content = self.links_text.get('1.0', tk.END).strip()
        if self.logger:
            self.logger.debug(f"_get_links - Content length: {len(content)} characters")
        
        if not content:
            if self.logger:
                self.logger.warning("_get_links - Content rỗng")
            return []
        
        links = []
        lines = content.split('\n')
        if self.logger:
            self.logger.debug(f"_get_links - Tổng số dòng: {len(lines)}")
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Tìm URL trong dòng (có thể có text khác)
            import re
            # Tìm URL pattern
            url_pattern = r'https?://[^\s]+'
            matches = re.findall(url_pattern, line)
            if matches:
                # Lấy URL đầu tiên tìm thấy
                url = matches[0]
                # Loại bỏ ký tự đặc biệt ở cuối URL nếu có
                url = url.rstrip('.,;!?')
                
                # Kiểm tra URL có hợp lệ không
                # Bỏ qua audio file (MP3)
                if '.mp3' in url.lower() or 'ies-music' in url.lower() or '/music/' in url.lower():
                    if self.logger:
                        self.logger.debug(f"_get_links - Dòng {idx+1}: Bỏ qua audio file (MP3): {url[:100]}...")
                    continue
                
                # Chấp nhận cả video page URL và direct video URL
                is_douyin_page = 'douyin.com' in url.lower() or 'v.douyin.com' in url.lower() or 'iesdouyin.com' in url.lower()
                is_direct_video = (url.endswith('.mp4') or '.mp4?' in url or 
                                  'zjcdn.com' in url.lower() or 
                                  'douyinstatic.com' in url.lower() or
                                  '/video/' in url.lower())
                
                if is_douyin_page:
                    # Video page URL (ưu tiên)
                    links.append(url)
                    if self.logger:
                        self.logger.debug(f"_get_links - Dòng {idx+1}: Thêm video page URL: {url[:100]}...")
                elif is_direct_video:
                    # Direct video URL (có thể hết hạn nhưng vẫn thử)
                    links.append(url)
                    if self.logger:
                        self.logger.debug(f"_get_links - Dòng {idx+1}: Thêm direct video URL (có thể hết hạn): {url[:100]}...")
                else:
                    if self.logger:
                        self.logger.debug(f"_get_links - Dòng {idx+1}: Bỏ qua URL không hợp lệ: {url[:100]}...")
            elif 'douyin.com' in line.lower() or 'v.douyin.com' in line.lower() or 'iesdouyin.com' in line.lower():
                # Nếu dòng chứa douyin nhưng không match pattern, thử lấy toàn bộ
                links.append(line)
                if self.logger:
                    self.logger.debug(f"_get_links - Dòng {idx+1}: Thêm link (không match pattern nhưng có douyin): {line[:100]}...")
            else:
                if self.logger:
                    self.logger.debug(f"_get_links - Dòng {idx+1}: Bỏ qua dòng không chứa URL hợp lệ: {line[:100]}...")
        
        if self.logger:
            self.logger.info(f"_get_links - Tổng cộng tìm thấy {len(links)} link hợp lệ")
        
        return links
    
    def _start_download(self):
        """Bắt đầu tải video"""
        if self.logger:
            self.logger.info("User clicked: Bắt đầu tải button")
        
        # Kiểm tra cookie
        cookie = self.cookie_manager.get_cookie()
        if not cookie:
            if self.logger:
                self.logger.warning("Bắt đầu tải - Cookie chưa được lưu, hiển thị lỗi")
            messagebox.showerror("Lỗi", "Vui lòng nhập và lưu cookie trước!")
            return
        
        # Lấy danh sách link
        links = self._get_links()
        if self.logger:
            self.logger.info(f"Bắt đầu tải - Tìm thấy {len(links)} link")
        
        # Log thông tin bắt đầu
        if hasattr(self, 'downloader') and hasattr(self.downloader, 'log'):
            self.downloader.log('info', f"Bắt đầu tải {len(links)} video")
        if not links:
            if self.logger:
                self.logger.warning("Bắt đầu tải - Không có link nào, hiển thị cảnh báo")
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ít nhất một link video!")
            return
        
        # Controllerを使用してダウンロードを開始
        try:
            success, error = self.download_controller.initialize_downloader(self.logger)
            if not success:
                if self.logger:
                    self.logger.error(f"Bắt đầu tải - Không thể khởi tạo downloader: {error}")
                messagebox.showerror("Lỗi", error)
                return
        except Exception as e:
            if self.logger:
                self.logger.error(f"Bắt đầu tải - Exception khi khởi tạo downloader: {e}", exc_info=True)
            messagebox.showerror("Lỗi", f"Lỗi khi khởi tạo downloader: {e}")
            return
        
        # Reset trạng thái
        self.results = []
        self.filtered_videos = []  # Reset filtered videos list (mới)
        self.status_tree.delete(*self.status_tree.get_children())
        
        # Cập nhật UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.progress_label.config(text=f"Đang tải 0/{len(links)}...")
        
        # Thêm các link vào treeview
        for link in links:
            self.status_tree.insert('', tk.END, values=(link, 'Đang chờ...', ''))
        
        # Controllerを使用してダウンロードを開始
        try:
            success, error = self.download_controller.start_download(
                links=links,
                progress_callback=self._on_progress_update,
                result_callback=self._on_download_result,
                complete_callback=self._on_download_complete
            )
            
            if not success:
                if self.logger:
                    self.logger.error(f"Bắt đầu tải - Lỗi: {error}")
                messagebox.showerror("Lỗi", error)
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Bắt đầu tải - Exception: {e}", exc_info=True)
            messagebox.showerror("Lỗi", f"Lỗi khi bắt đầu tải: {e}")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def _on_progress_update(self, progress: float, current: int, total: int):
        """進捗更新コールバック"""
        self.root.after(0, lambda: self._update_progress(progress, current, total))
    
    def _on_download_result(self, result: Dict):
        """ダウンロード結果コールバック"""
        try:
            if self.logger:
                self.logger.debug(f"_on_download_result - Received result: success={result.get('success')}, video_id={result.get('video_id')}")
            
            # Thu thập thống kê orientation filter (mới)
            if result.get('filtered_by_orientation'):
                self.filtered_videos.append({
                    'video_id': result.get('video_id', 'N/A'),
                    'url': result.get('url', 'N/A'),
                    'author': result.get('author', 'N/A'),
                    'orientation': result.get('orientation', 'unknown'),
                    'width': result.get('width', 0),
                    'height': result.get('height', 0),
                    'error': result.get('error', 'Unknown error')
                })
                # Log để debug
                if self.logger:
                    self.logger.debug(f"Video bị filter: video_id={result.get('video_id')}, orientation={result.get('orientation')}")
            
            # 絶対パスに変換
            if result.get('file_path'):
                file_path = result.get('file_path')
                if not os.path.isabs(file_path):
                    download_folder = self.cookie_manager.get_download_folder()
                    if download_folder:
                        file_path = os.path.join(download_folder, file_path)
                        result['file_path'] = file_path
            
            self.results.append(result)
            # UIを更新
            url = result.get('url', '')
            status = "✓ Thành công" if result.get('success') else f"✗ {result.get('error', 'Lỗi')}"
            file_path = result.get('file_path', '')
            file_basename = os.path.basename(file_path) if file_path else ''
            
            # Treeviewを更新
            self.root.after(0, lambda: self._update_status_in_treeview(url, status, file_basename))
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in _on_download_result: {e}", exc_info=True)
    
    def _update_status_in_treeview(self, url: str, status: str, file_basename: str):
        """Treeviewのステータスを更新"""
        try:
            for item in self.status_tree.get_children():
                values = self.status_tree.item(item, 'values')
                if len(values) >= 1 and values[0] == url:
                    self.status_tree.item(item, values=(url, status, file_basename))
                    break
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in _update_status_in_treeview: {e}", exc_info=True)
    
    def _on_download_complete(self):
        """ダウンロード完了コールバック"""
        self.root.after(0, self._download_complete)
    
    def _update_progress(self, progress: float, current: int, total: int):
        """Cập nhật progress bar"""
        try:
            self.progress_var.set(progress)
            self.progress_label.config(text=f"Đang tải {current}/{total}...")
            if self.logger and current % 10 == 0:  # Log mỗi 10 video để tránh spam
                self.logger.debug(f"Progress update: {current}/{total} ({progress:.1f}%)")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in _update_progress: {e}", exc_info=True)
    
    def _download_complete(self):
        """Hoàn tất quá trình tải"""
        if self.logger:
            self.logger.info("Download - Quá trình tải đã hoàn tất")
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        # Thống kê
        total = len(self.results)
        success = sum(1 for r in self.results if r['success'])
        failed = total - success
        
        # Thống kê orientation filter (mới)
        filtered_count = len(self.filtered_videos)
        
        if self.logger:
            self.logger.info(f"Download - Thống kê: Tổng={total}, Thành công={success}, Thất bại={failed}")
            if filtered_count > 0:
                self.logger.info(f"Download - Video bị bỏ qua do orientation filter: {filtered_count}")
        
        # Hiển thị thông báo với thống kê orientation filter (mới)
        orientation_filter = self.cookie_manager.get_setting("orientation_filter", "all")
        filter_display_map = {
            "all": "Tất cả",
            "vertical": "Portrait (Video dọc)",
            "horizontal": "Landscape (Video ngang)"
        }
        filter_display = filter_display_map.get(orientation_filter, orientation_filter)
        
        message = f"Hoàn tất!\n\n"
        message += f"Tổng số: {total}\n"
        message += f"Thành công: {success}\n"
        message += f"Thất bại: {failed}\n"
        
        if filtered_count > 0:
            message += f"\nVideo bị bỏ qua do orientation filter ({filter_display}): {filtered_count}"
        
        # Cập nhật UI labels
        self.progress_label.config(text=f"Hoàn tất! Thành công: {success}/{total}")
        self.stats_label.config(text=f"Tổng: {total} | Thành công: {success} | Thất bại: {failed}")
        
        # Hiển thị danh sách video bị filter (mới)
        if filtered_count > 0:
            response = messagebox.askyesno(
                "Hoàn tất",
                message + "\n\nBạn có muốn xem danh sách video bị bỏ qua không?",
                icon='question'
            )
            
            if response:
                # Tạo window hiển thị danh sách video bị filter
                self._show_filtered_videos_list()
        else:
            messagebox.showinfo("Hoàn tất", message)
        
        # Reset filtered videos list cho lần tải tiếp theo (mới)
        self.filtered_videos = []
    
    def _show_filtered_videos_list(self):
        """Hiển thị danh sách video bị filter do orientation (mới)"""
        if not self.filtered_videos:
            return
        
        # Tạo window mới
        filtered_window = tk.Toplevel(self.root)
        filtered_window.title("Danh sách video bị bỏ qua do orientation filter")
        filtered_window.geometry("900x600")
        
        # Label
        orientation_filter = self.cookie_manager.get_setting("orientation_filter", "all")
        filter_display_map = {
            "all": "Tất cả",
            "vertical": "Portrait (Video dọc)",
            "horizontal": "Landscape (Video ngang)"
        }
        filter_display = filter_display_map.get(orientation_filter, orientation_filter)
        
        info_label = tk.Label(
            filtered_window,
            text=f"Filter đang áp dụng: {filter_display}\nTổng số video bị bỏ qua: {len(self.filtered_videos)}",
            font=("Arial", 10, "bold")
        )
        info_label.pack(pady=10)
        
        # Treeview để hiển thị danh sách
        columns = ("ID", "Video ID", "Author", "Orientation", "Size", "URL")
        tree = ttk.Treeview(filtered_window, columns=columns, show="headings", height=20)
        
        # Định nghĩa headings
        tree.heading("ID", text="STT")
        tree.heading("Video ID", text="Video ID")
        tree.heading("Author", text="Author")
        tree.heading("Orientation", text="Orientation")
        tree.heading("Size", text="Size (WxH)")
        tree.heading("URL", text="URL")
        
        # Định nghĩa column widths
        tree.column("ID", width=50)
        tree.column("Video ID", width=150)
        tree.column("Author", width=150)
        tree.column("Orientation", width=120)
        tree.column("Size", width=120)
        tree.column("URL", width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(filtered_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Thêm dữ liệu
        orientation_display_map = {
            "horizontal": "Landscape (ngang)",
            "vertical": "Portrait (dọc)",
            "square": "Square (vuông)",
            "unknown": "Unknown"
        }
        
        for idx, video in enumerate(self.filtered_videos, 1):
            orientation_display = orientation_display_map.get(video.get('orientation', 'unknown'), video.get('orientation', 'unknown'))
            size_str = f"{video.get('width', 0)}x{video.get('height', 0)}"
            if video.get('width', 0) > 0 and video.get('height', 0) > 0:
                aspect_ratio = video.get('width', 0) / video.get('height', 0)
                size_str += f" ({aspect_ratio:.2f})"
            
            url_display = video.get('url', 'N/A')
            if len(url_display) > 80:
                url_display = url_display[:80] + "..."
            
            tree.insert("", tk.END, values=(
                idx,
                video.get('video_id', 'N/A'),
                video.get('author', 'N/A'),
                orientation_display,
                size_str,
                url_display
            ))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Close button
        close_btn = ttk.Button(filtered_window, text="Đóng", command=filtered_window.destroy)
        close_btn.pack(pady=10)
    
    def _stop_download(self):
        """Dừng quá trình tải"""
        if self.logger:
            self.logger.info("User clicked: Dừng tải button")
        
        # Controllerを使用して停止
        self.download_controller.stop_download()
        
        self.progress_label.config(text="Đang dừng...")
        if self.logger:
            self.logger.info("Dừng tải - Đã gọi download_controller.stop_download()")


