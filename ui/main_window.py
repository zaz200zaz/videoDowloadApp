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


class MainWindow:
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self, root: tk.Tk, cookie_manager, downloader_class):
        """
        Khởi tạo MainWindow
        
        Args:
            root: Tkinter root window
            cookie_manager: CookieManager instance
            downloader_class: VideoDownloader class
        """
        self.root = root
        self.cookie_manager = cookie_manager
        self.downloader_class = downloader_class
        self.downloader = None
        
        # Trạng thái
        self.is_downloading = False
        self.should_stop = False
        self.download_queue = queue.Queue()
        self.results = []
        
        # Thiết lập giao diện
        self._setup_ui()
        self._load_saved_cookie()
    
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
        
        # Nút reset
        reset_buttons = ttk.Frame(status_frame)
        reset_buttons.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.reset_btn = ttk.Button(reset_buttons, text="Reset App", command=self._reset_app)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
    
    def _load_saved_cookie(self):
        """Tải cookie đã lưu vào ô nhập"""
        cookie = self.cookie_manager.get_cookie()
        if cookie:
            self.cookie_text.insert('1.0', cookie)
            self.cookie_status_label.config(text="✓ Đã tải cookie đã lưu", foreground="green")
    
    def _load_cookie_from_file(self):
        """Tải cookie từ file"""
        file_path = filedialog.askopenfilename(
            title="Chọn file Cookie",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                messagebox.showwarning("Cảnh báo", "File rỗng!")
                return
            
            cookie_value = content
            
            # Kiểm tra nếu là Netscape cookie format
            if content.startswith('# Netscape HTTP Cookie File') or ('\t' in content and len(content.split('\t')) >= 7):
                # Parse Netscape format
                cookie_value = self.cookie_manager.parse_netscape_cookie_file(content)
                if not cookie_value:
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
                messagebox.showerror("Lỗi", f"Không thể đọc file với encoding khác: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")
    
    def _save_cookie(self):
        """Lưu cookie"""
        cookie = self.cookie_text.get('1.0', tk.END).strip()
        
        if not cookie:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập cookie!")
            return
        
        # Kiểm tra nếu là Netscape format, tự động convert
        # Header String format (key1=value1; key2=value2; ...) không cần xử lý đặc biệt
        if cookie.startswith('# Netscape HTTP Cookie File') or ('\t' in cookie and len(cookie.split('\t')) >= 7):
            cookie = self.cookie_manager.parse_netscape_cookie_file(cookie)
            if not cookie:
                messagebox.showerror("Lỗi", "Không thể parse Netscape cookie file!")
                return
            # Cập nhật lại text box với cookie đã convert
            self.cookie_text.delete('1.0', tk.END)
            self.cookie_text.insert('1.0', cookie)
        
        # Header String format đã sẵn sàng để sử dụng (key1=value1; key2=value2; ...)
        # Không cần xử lý thêm
        
        if not self.cookie_manager.validate_cookie(cookie):
            result = messagebox.askyesno(
                "Cảnh báo",
                "Cookie có vẻ không hợp lệ. Bạn có muốn tiếp tục lưu không?"
            )
            if not result:
                return
        
        if self.cookie_manager.save_cookie(cookie):
            self.cookie_status_label.config(text="✓ Cookie đã được lưu", foreground="green")
            messagebox.showinfo("Thành công", "Cookie đã được lưu thành công!")
        else:
            self.cookie_status_label.config(text="✗ Lỗi khi lưu cookie", foreground="red")
            messagebox.showerror("Lỗi", "Không thể lưu cookie!")
    
    def _import_links(self):
        """Import danh sách link từ file .txt"""
        file_path = filedialog.askopenfilename(
            title="Chọn file .txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.links_text.insert('1.0', content)
                messagebox.showinfo("Thành công", f"Đã import {len(content.splitlines())} link!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")
    
    def _clear_links(self):
        """Xóa tất cả link"""
        self.links_text.config(state=tk.NORMAL)
        self.links_text.delete('1.0', tk.END)
    
    def _clear_cookie(self):
        """Xóa cookie đã lưu"""
        result = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa cookie đã lưu không?"
        )
        
        if result:
            if self.cookie_manager.clear_cookie():
                # Xóa cookie trong text box
                self.cookie_text.delete('1.0', tk.END)
                self.cookie_status_label.config(text="✓ Cookie đã được xóa", foreground="green")
                messagebox.showinfo("Thành công", "Cookie đã được xóa!")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa cookie!")
    
    def _reset_app(self):
        """Reset toàn bộ app về trạng thái ban đầu"""
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
        folder = filedialog.askdirectory(title="Chọn thư mục lưu video")
        if folder:
            self.cookie_manager.set_download_folder(folder)
            messagebox.showinfo("Thành công", f"Đã chọn thư mục: {folder}")
    
    def _get_links(self) -> List[str]:
        """Lấy danh sách link từ text box"""
        content = self.links_text.get('1.0', tk.END).strip()
        if not content:
            return []
        
        links = []
        for line in content.split('\n'):
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
                links.append(url)
            elif 'douyin.com' in line.lower() or 'v.douyin.com' in line.lower():
                # Nếu dòng chứa douyin nhưng không match pattern, thử lấy toàn bộ
                links.append(line)
        
        return links
    
    def _start_download(self):
        """Bắt đầu tải video"""
        # Kiểm tra cookie
        cookie = self.cookie_manager.get_cookie()
        if not cookie:
            messagebox.showerror("Lỗi", "Vui lòng nhập và lưu cookie trước!")
            return
        
        # Lấy danh sách link
        links = self._get_links()
        if not links:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ít nhất một link video!")
            return
        
        # Khởi tạo downloader
        self.downloader = self.downloader_class(cookie)
        
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
            result = self.downloader.process_video(link, download_folder, naming_mode)
            self.results.append(result)
            
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
        self.is_downloading = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        # Thống kê
        total = len(self.results)
        success = sum(1 for r in self.results if r['success'])
        failed = total - success
        
        self.progress_label.config(text=f"Hoàn tất! Thành công: {success}/{total}")
        self.stats_label.config(text=f"Tổng: {total} | Thành công: {success} | Thất bại: {failed}")
        
        # Hiển thị thông báo
        download_folder = self.cookie_manager.get_download_folder()
        messagebox.showinfo(
            "Hoàn tất",
            f"Đã tải xong {total} video!\n\n"
            f"Thành công: {success}\n"
            f"Thất bại: {failed}\n\n"
            f"Thư mục: {download_folder}"
        )
    
    def _stop_download(self):
        """Dừng quá trình tải"""
        self.should_stop = True
        self.progress_label.config(text="Đang dừng...")


