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
        
        self.cookie_status_label = ttk.Label(cookie_frame, text="", foreground="gray")
        self.cookie_status_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # ========== PHẦN 2: LINK VIDEO ==========
        links_frame = ttk.LabelFrame(main_frame, text="2. Danh sách Link Video", padding="10")
        links_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        links_frame.columnconfigure(0, weight=1)
        links_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        links_buttons = ttk.Frame(links_frame)
        links_buttons.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.import_btn = ttk.Button(links_buttons, text="Import từ file .txt", command=self._import_links)
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_links_btn = ttk.Button(links_buttons, text="Xóa tất cả", command=self._clear_links)
        self.clear_links_btn.pack(side=tk.LEFT, padx=5)
        
        self.links_text = scrolledtext.ScrolledText(links_frame, height=8, wrap=tk.WORD)
        self.links_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        ttk.Label(links_frame, text="Mỗi dòng một link video Douyin", foreground="gray").grid(
            row=2, column=0, sticky=tk.W, pady=2
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
            
            # Thử parse JSON nếu là file JSON
            cookie_value = content
            if file_path.lower().endswith('.json'):
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
                self.cookie_text.delete('1.0', tk.END)
                self.cookie_text.insert('1.0', content)
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
        self.links_text.delete('1.0', tk.END)
    
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
        
        links = [line.strip() for line in content.split('\n') if line.strip()]
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


