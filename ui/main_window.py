"""
Main Window UI Module
Giao diện chính của ứng dụng sử dụng Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from typing import List, Callable, Optional
import queue
import logging


class MainWindow:
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self, root: tk.Tk, cookie_manager, downloader_class, logger=None):
        """
        Khởi tạo MainWindow
        
        Args:
            root: Tkinter root window
            cookie_manager: CookieManager instance
            downloader_class: VideoDownloader class
            logger: Logger instance (optional)
        """
        self.root = root
        self.cookie_manager = cookie_manager
        self.downloader_class = downloader_class
        self.downloader = None
        self.logger = logger or logging.getLogger('MainWindow')
        
        if self.logger:
            self.logger.info("MainWindow.__init__ - Bắt đầu khởi tạo UI")
        
        # Trạng thái
        self.is_downloading = False
        self.should_stop = False
        self.download_queue = queue.Queue()
        self.results = []
        
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
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(download_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(download_frame, text="Sẵn sàng")
        self.progress_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
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
        
        # Nút reset và log
        reset_buttons = ttk.Frame(status_frame)
        reset_buttons.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.reset_btn = ttk.Button(reset_buttons, text="Reset App", command=self._reset_app)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_log_btn = ttk.Button(reset_buttons, text="Mở thư mục Log", command=self._open_log_folder)
        self.open_log_btn.pack(side=tk.LEFT, padx=5)
    
    def _load_saved_cookie(self):
        """Tải cookie đã lưu vào ô nhập"""
        cookie = self.cookie_manager.get_cookie()
        if cookie:
            self.cookie_text.insert('1.0', cookie)
            self.cookie_status_label.config(text="✓ Đã tải cookie đã lưu", foreground="green")
    
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
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                if self.logger:
                    self.logger.warning("Chọn file Cookie - File rỗng, hiển thị cảnh báo")
                messagebox.showwarning("Cảnh báo", "File rỗng!")
                return
            
            cookie_value = content
            
            # Kiểm tra nếu là Netscape cookie format
            if content.startswith('# Netscape HTTP Cookie File') or ('\t' in content and len(content.split('\t')) >= 7):
                # Parse Netscape format
                cookie_value = self.cookie_manager.parse_netscape_cookie_file(content)
                if not cookie_value:
                    if self.logger:
                        self.logger.warning("Chọn file Cookie - Không thể parse Netscape cookie file, hiển thị cảnh báo")
                    messagebox.showwarning("Cảnh báo", "Không thể parse Netscape cookie file!")
                    return
            
            # Thử parse JSON nếu là file JSON
            elif file_path.lower().endswith('.json'):
                try:
                    import json
                    data = json.loads(content)
                    # Thử các key phổ biến
                    if isinstance(data, dict):
                        cookie_value = data.get('cookie', data.get('Cookie', data.get('COOKIE', content)))
                        if cookie_value == content:
                            # Nếu không tìm thấy key 'cookie', thử lấy toàn bộ dict và convert thành string
                            cookie_value = str(data)
                except json.JSONDecodeError:
                    # Không phải JSON hợp lệ, dùng content gốc
                    pass
            
            # Nếu không phải Netscape hoặc JSON, giả sử là Header String format (key1=value1; key2=value2; ...)
            # Header String format không cần xử lý đặc biệt, dùng trực tiếp
            
            # Xóa nội dung cũ và thêm cookie mới
            self.cookie_text.delete('1.0', tk.END)
            self.cookie_text.insert('1.0', cookie_value)
            
            self.cookie_status_label.config(
                text=f"✓ Đã tải cookie từ file: {os.path.basename(file_path)}",
                foreground="green"
            )
            if self.logger:
                self.logger.info(f"Chọn file Cookie - Thành công, đã tải cookie từ file: {os.path.basename(file_path)}")
            messagebox.showinfo("Thành công", f"Đã tải cookie từ file!\n\nFile: {os.path.basename(file_path)}")
            
        except UnicodeDecodeError:
            # Thử với encoding khác
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read().strip()
                
                # Kiểm tra Netscape format
                if content.startswith('# Netscape HTTP Cookie File') or ('\t' in content and len(content.split('\t')) >= 7):
                    cookie_value = self.cookie_manager.parse_netscape_cookie_file(content)
                else:
                    # Header String format hoặc plain text
                    cookie_value = content
                
                self.cookie_text.delete('1.0', tk.END)
                self.cookie_text.insert('1.0', cookie_value)
                self.cookie_status_label.config(
                    text=f"✓ Đã tải cookie từ file: {os.path.basename(file_path)}",
                    foreground="green"
                )
                messagebox.showinfo("Thành công", f"Đã tải cookie từ file!")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Chọn file Cookie - Lỗi khi đọc file với encoding khác: {e}")
                messagebox.showerror("Lỗi", f"Không thể đọc file với encoding khác: {e}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Chọn file Cookie - Lỗi khi đọc file: {e}")
            messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")
    
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
        
        # Kiểm tra nếu là Netscape format, tự động convert
        # Header String format (key1=value1; key2=value2; ...) không cần xử lý đặc biệt
        if cookie.startswith('# Netscape HTTP Cookie File') or ('\t' in cookie and len(cookie.split('\t')) >= 7):
            cookie = self.cookie_manager.parse_netscape_cookie_file(cookie)
            if not cookie:
                if self.logger:
                    self.logger.error("Lưu Cookie - Không thể parse Netscape cookie file")
                messagebox.showerror("Lỗi", "Không thể parse Netscape cookie file!")
                return
            # Cập nhật lại text box với cookie đã convert
            self.cookie_text.delete('1.0', tk.END)
            self.cookie_text.insert('1.0', cookie)
        
        # Header String format đã sẵn sàng để sử dụng (key1=value1; key2=value2; ...)
        # Không cần xử lý thêm
        
        if not self.cookie_manager.validate_cookie(cookie):
            if self.logger:
                self.logger.warning("Lưu Cookie - Cookie có vẻ không hợp lệ, hiển thị cảnh báo")
            result = messagebox.askyesno(
                "Cảnh báo",
                "Cookie có vẻ không hợp lệ. Bạn có muốn tiếp tục lưu không?"
            )
            if not result:
                if self.logger:
                    self.logger.info("Lưu Cookie - Người dùng đã hủy do cookie không hợp lệ")
                return
            if self.logger:
                self.logger.info("Lưu Cookie - Người dùng đã xác nhận lưu cookie không hợp lệ")
        
        if self.cookie_manager.save_cookie(cookie):
            if self.logger:
                self.logger.info(f"Lưu Cookie - Thành công (length: {len(cookie)})")
            self.cookie_status_label.config(text="✓ Cookie đã được lưu", foreground="green")
            messagebox.showinfo("Thành công", "Cookie đã được lưu thành công!")
        else:
            if self.logger:
                self.logger.error("Lưu Cookie - Lỗi khi lưu cookie")
            self.cookie_status_label.config(text="✗ Lỗi khi lưu cookie", foreground="red")
            messagebox.showerror("Lỗi", "Không thể lưu cookie!")
    
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
                        self.logger.error(f"Import links - Lỗi khi đọc file với encoding khác: {e}")
                    messagebox.showerror("Lỗi", f"Không thể đọc file với encoding khác: {e}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Import links - Lỗi khi đọc file: {e}")
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
        
        # Lấy video URLs
        try:
            from downloader import VideoDownloader
            import os
            from datetime import datetime
            
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
            self.get_user_videos_btn.config(state=tk.DISABLED)
            self.progress_label.config(text="Đang lấy video từ user...")
            self.root.update()
            
            video_urls = downloader.get_all_videos_from_user(user_url)
            
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
                            self.logger.error(f"Lấy video từ user - Lỗi khi lưu file: {e}")
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
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Lấy video từ user - Lỗi: {e}", exc_info=True)
            messagebox.showerror("Lỗi", f"Lỗi khi lấy video: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Enable button lại
            self.get_user_videos_btn.config(state=tk.NORMAL)
            self.progress_label.config(text="Sẵn sàng")
    
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
    
    def _select_folder(self):
        """Chọn thư mục lưu video"""
        if self.logger:
            self.logger.info("User clicked: Chọn thư mục button")
        folder = filedialog.askdirectory(title="Chọn thư mục lưu video")
        if folder:
            if self.logger:
                self.logger.info(f"Chọn thư mục - Thư mục được chọn: {folder}")
            self.cookie_manager.set_download_folder(folder)
            messagebox.showinfo("Thành công", f"Đã chọn thư mục: {folder}")
        else:
            if self.logger:
                self.logger.info("Chọn thư mục - Người dùng đã hủy")
    
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
            messagebox.showerror("Lỗi", f"Không thể mở thư mục log: {e}\n\nThư mục log: {log_dir}")
    
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
                # Nếu là direct video URL (.mp4), cần chuyển đổi thành video page URL
                if url.endswith('.mp4') or '.mp4?' in url:
                    # Đây là direct video URL, cần extract video ID từ URL hoặc bỏ qua
                    # Vì direct video URL có thể hết hạn, nên chỉ chấp nhận video page URL
                    if self.logger:
                        self.logger.debug(f"_get_links - Dòng {idx+1}: Bỏ qua direct video URL (có thể hết hạn): {url[:100]}...")
                    continue
                
                # Chỉ chấp nhận video page URL hoặc short URL
                if 'douyin.com' in url.lower() or 'v.douyin.com' in url.lower() or 'iesdouyin.com' in url.lower():
                    links.append(url)
                    if self.logger:
                        self.logger.debug(f"_get_links - Dòng {idx+1}: Thêm link hợp lệ: {url[:100]}...")
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
        
        # Khởi tạo downloader với logging
        import os
        from datetime import datetime
        
        # Tạo thư mục logs nếu chưa có (sử dụng script directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Nếu script_dir là ui/, lên một cấp
        if os.path.basename(script_dir) == 'ui':
            script_dir = os.path.dirname(script_dir)
        log_dir = os.path.join(script_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"download_{timestamp}.log")
        
        self.downloader = self.downloader_class(cookie, log_file)
        
        # Hiển thị thông tin log file
        self.downloader.log('info', f"Bắt đầu tải {len(links)} video")
        self.downloader.log('info', f"Log file: {log_file}")
        
        # Hiển thị thông báo cho người dùng
        messagebox.showinfo(
            "Log File",
            f"Log file đã được tạo:\n{log_file}\n\n"
            f"Tất cả hoạt động sẽ được ghi vào file này."
        )
        
        # Reset trạng thái
        self.is_downloading = True
        self.should_stop = False
        self.results = []
        self.status_tree.delete(*self.status_tree.get_children())
        
        # Cập nhật UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.progress_label.config(text=f"Đang tải 0/{len(links)}...")
        
        # Thêm các link vào treeview
        for link in links:
            self.status_tree.insert('', tk.END, values=(link, 'Đang chờ...', ''))
        
        # Chạy download trong thread riêng
        thread = threading.Thread(target=self._download_worker, args=(links,), daemon=True)
        thread.start()
    
    def _download_worker(self, links: List[str]):
        """Worker thread để tải video"""
        total = len(links)
        download_folder = self.cookie_manager.get_download_folder()
        naming_mode = self.cookie_manager.get_setting("naming_mode", "video_id")
        
        for idx, link in enumerate(links):
            if self.should_stop:
                break
            
            # Cập nhật progress
            progress = (idx / total) * 100
            self.root.after(0, lambda p=progress, i=idx, t=total: self._update_progress(p, i, t))
            
            # Xử lý video
            if self.logger:
                self.logger.info(f"Đang xử lý video {idx+1}/{total}: {link}")
            result = self.downloader.process_video(link, download_folder, naming_mode)
            self.results.append(result)
            
            # Log kết quả
            if result['success']:
                if self.logger:
                    self.logger.info(f"Video {idx+1}/{total} - Thành công: {result.get('file_path', '')}")
            else:
                if self.logger:
                    self.logger.error(f"Video {idx+1}/{total} - Thất bại: {result.get('error', 'Lỗi không xác định')}")
            
            # Cập nhật trạng thái trong treeview
            status = "✓ Thành công" if result['success'] else f"✗ {result.get('error', 'Lỗi')}"
            file_path = result.get('file_path', '')
            
            # Tìm item trong treeview và cập nhật
            items = self.status_tree.get_children()
            if idx < len(items):
                item = items[idx]
                self.root.after(0, lambda i=item, s=status, f=file_path: 
                               self.status_tree.item(i, values=(link, s, os.path.basename(f) if f else '')))
        
        # Hoàn tất
        self.root.after(0, self._download_complete)
    
    def _update_progress(self, progress: float, current: int, total: int):
        """Cập nhật progress bar"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"Đang tải {current}/{total}...")
    
    def _download_complete(self):
        """Hoàn tất quá trình tải"""
        if self.logger:
            self.logger.info("Download - Quá trình tải đã hoàn tất")
        
        self.is_downloading = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        # Thống kê
        total = len(self.results)
        success = sum(1 for r in self.results if r['success'])
        failed = total - success
        
        if self.logger:
            self.logger.info(f"Download - Thống kê: Tổng={total}, Thành công={success}, Thất bại={failed}")
        
        self.progress_label.config(text=f"Hoàn tất! Thành công: {success}/{total}")
        self.stats_label.config(text=f"Tổng: {total} | Thành công: {success} | Thất bại: {failed}")
        
        # Hiển thị thông báo
        download_folder = self.cookie_manager.get_download_folder()
        if self.logger:
            self.logger.info(f"Download - Hiển thị thông báo hoàn tất: {total} video, {success} thành công, {failed} thất bại")
        messagebox.showinfo(
            "Hoàn tất",
            f"Đã tải xong {total} video!\n\n"
            f"Thành công: {success}\n"
            f"Thất bại: {failed}\n\n"
            f"Thư mục: {download_folder}"
        )
    
    def _stop_download(self):
        """Dừng quá trình tải"""
        if self.logger:
            self.logger.info("User clicked: Dừng tải button")
        self.should_stop = True
        self.progress_label.config(text="Đang dừng...")
        if self.logger:
            self.logger.info("Dừng tải - Đã dừng quá trình tải")


