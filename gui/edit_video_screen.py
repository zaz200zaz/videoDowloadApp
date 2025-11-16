"""
Edit Video Screen
Màn hình chỉnh sửa video (Placeholder cho FR-001)

Mục tiêu:
- Placeholder screen cho navigation testing
- Basic screen structure
- Navigation back to Main Dashboard
- Logging integration (theo System Instruction)

Input/Output:
- Input: User interactions
- Output: Navigation commands
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import logging
from utils.log_helper import get_logger
from gui.utils.ui_logger import log_ui_action, log_screen_navigation


class EditVideoScreen:
    """
    Edit Video Screen (Placeholder)
    
    Placeholder screen cho navigation testing (theo FR-001)
    """
    
    def __init__(self, parent, logger: Optional[logging.Logger] = None, **kwargs):
        """
        Khởi tạo EditVideoScreen
        
        Args:
            parent: Parent window
            logger: Logger instance (theo System Instruction)
            **kwargs: Additional parameters (có thể chứa navigation_controller)
        """
        function_name = "EditVideoScreen.__init__"
        self.logger = logger or get_logger('EditVideoScreen')
        # Lưu navigation_controller để hỗ trợ back navigation (iOS-style)
        # Nếu có trong kwargs, lưu lại để sử dụng trong back button
        self.navigation_controller = kwargs.get('navigation_controller', None)
        
        # Log khởi tạo (theo System Instruction)
        log_ui_action(self.logger, function_name, "init", "EditVideoScreen", "INFO",
                     "Initializing Edit Video Screen")
        
        try:
            # Chế độ nhúng (frame-based) nếu parent là Frame (mobile_mode) → không mở cửa sổ mới
            self._embedded_mode = isinstance(parent, tk.Frame)
            self.root = parent
            
            if self._embedded_mode:
                # Tạo main frame ngay trong parent (nhúng trong content_container của NavigationController)
                self.frame = tk.Frame(self.root, bg="#ffffff")
                self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            else:
                # Fallback: tạo Toplevel nếu không có frame container (giữ tương thích cũ)
                self.window = tk.Toplevel(parent)
                self.window.title("Edit Video")
                self.window.geometry("800x600")
                self.frame = tk.Frame(self.window, bg="#ffffff")
                self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Back button frame (iOS-style navigation)
            back_frame = tk.Frame(self.frame, bg=self.frame.cget('bg'))
            back_frame.pack(fill=tk.X, pady=10)
            
            # Back button (iOS-style)
            back_button = tk.Button(
                back_frame,
                text="← Back to Home",
                command=self.on_back_click,
                width=20,
                height=2,
                bg="#f0f0f0",
                relief=tk.FLAT,
                cursor="hand2"
            )
            back_button.pack(side=tk.LEFT, padx=10)
            
            # Title label
            title_label = tk.Label(
                self.frame,
                text="Edit Video",
                font=("Arial", 18, "bold"),
                bg=self.frame.cget('bg')
            )
            title_label.pack(pady=20)
            
            # ========== CẤU HÌNH BATCH VIDEO EDITOR ==========
            config_frame = tk.LabelFrame(self.frame, text="Cấu hình Batch Video Editor", bg=self.frame.cget('bg'))
            config_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Hàng 1: Background + Input Folder + Output Folder
            row1 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row1.pack(fill=tk.X, pady=5)
            tk.Label(row1, text="Background (PNG/JPG):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.bg_path_var = tk.StringVar()
            self.bg_entry = tk.Entry(row1, textvariable=self.bg_path_var, width=50)
            self.bg_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(row1, text="Chọn...", command=self._choose_background).pack(side=tk.LEFT, padx=5)
            
            row2 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row2.pack(fill=tk.X, pady=5)
            tk.Label(row2, text="Thư mục nguồn:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.input_folder_var = tk.StringVar(value="downloads")
            tk.Entry(row2, textvariable=self.input_folder_var, width=40).pack(side=tk.LEFT, padx=5)
            tk.Button(row2, text="Chọn...", command=self._choose_input_folder).pack(side=tk.LEFT, padx=5)
            
            row3 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row3.pack(fill=tk.X, pady=5)
            tk.Label(row3, text="Thư mục output:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.output_folder_var = tk.StringVar(value="downloads/edited")
            tk.Entry(row3, textvariable=self.output_folder_var, width=40).pack(side=tk.LEFT, padx=5)
            tk.Button(row3, text="Chọn...", command=self._choose_output_folder).pack(side=tk.LEFT, padx=5)
            
            # Hàng 4: Position & Size
            row4 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row4.pack(fill=tk.X, pady=5)
            tk.Label(row4, text="Vị trí (x,y):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.pos_x_var = tk.IntVar(value=100)
            self.pos_y_var = tk.IntVar(value=200)
            tk.Entry(row4, textvariable=self.pos_x_var, width=6).pack(side=tk.LEFT, padx=2)
            tk.Entry(row4, textvariable=self.pos_y_var, width=6).pack(side=tk.LEFT, padx=2)
            
            tk.Label(row4, text="Kích thước (w,h):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)
            self.size_w_var = tk.IntVar(value=720)
            self.size_h_var = tk.IntVar(value=1280)
            tk.Entry(row4, textvariable=self.size_w_var, width=6).pack(side=tk.LEFT, padx=2)
            tk.Entry(row4, textvariable=self.size_h_var, width=6).pack(side=tk.LEFT, padx=2)
            
            self.keep_ratio_var = tk.BooleanVar(value=True)
            tk.Checkbutton(row4, text="Giữ tỉ lệ", variable=self.keep_ratio_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)
            
            # Hàng 5: Threads, bitrate, preset, suffix, skip
            row5 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row5.pack(fill=tk.X, pady=5)
            tk.Label(row5, text="Số luồng:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.threads_var = tk.IntVar(value=4)
            tk.Scale(row5, from_=1, to=8, orient=tk.HORIZONTAL, variable=self.threads_var, length=150).pack(side=tk.LEFT, padx=5)
            
            tk.Label(row5, text="Bitrate:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)
            self.bitrate_var = tk.StringVar(value="2500k")
            tk.Entry(row5, textvariable=self.bitrate_var, width=8).pack(side=tk.LEFT, padx=2)
            
            tk.Label(row5, text="Preset:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)
            self.preset_var = tk.StringVar(value="medium")
            ttk.Combobox(row5, textvariable=self.preset_var, values=["ultrafast","superfast","veryfast","faster","fast","medium","slow","slower","veryslow"], width=10, state="readonly").pack(side=tk.LEFT, padx=2)
            
            tk.Label(row5, text="Hậu tố:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)
            self.suffix_var = tk.StringVar(value="_edited")
            tk.Entry(row5, textvariable=self.suffix_var, width=10).pack(side=tk.LEFT, padx=2)
            
            self.skip_existing_var = tk.BooleanVar(value=True)
            tk.Checkbutton(row5, text="Skip file đã tồn tại", variable=self.skip_existing_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)
            
            # Hàng 6: Nút Start/Stop + Progress + Log
            row6 = tk.Frame(self.frame, bg=self.frame.cget('bg'))
            row6.pack(fill=tk.X, pady=10)
            tk.Button(row6, text="Start Batch Edit", command=self._start_batch).pack(side=tk.LEFT, padx=10)
            tk.Button(row6, text="Stop", command=self._stop_batch).pack(side=tk.LEFT, padx=5)
            
            self.progress_var = tk.DoubleVar(value=0)
            self.progress_bar = ttk.Progressbar(row6, variable=self.progress_var, maximum=100, length=300)
            self.progress_bar.pack(side=tk.LEFT, padx=15)
            
            # Log view
            log_frame = tk.LabelFrame(self.frame, text="Log", bg=self.frame.cget('bg'))
            log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.log_text = tk.Text(log_frame, height=12)
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Close button
            close_button = tk.Button(
                self.frame,
                text="Close",
                command=self.on_close,
                width=20,
                height=2
            )
            close_button.pack(pady=20)
            
            # Bind close event nếu ở chế độ window
            if hasattr(self, "window"):
                self.window.protocol("WM_DELETE_WINDOW", self.on_close)
            
            # Log hoàn thành (theo System Instruction)
            log_ui_action(self.logger, function_name, "init_complete", 
                         "EditVideoScreen", "INFO",
                         "Edit Video Screen initialized successfully")
            
        except Exception as e:
            # Log error đầy đủ (theo System Instruction)
            log_ui_action(self.logger, function_name, "init_error", 
                         "EditVideoScreen", "ERROR",
                         f"Error initializing Edit Video Screen: {e}")
            raise
    
    def on_back_click(self):
        """
        Event handler cho back button (iOS-style navigation)
        
        Mục đích:
        - Quay lại Home Screen (Main Dashboard) khi nhấn back button
        - Sử dụng navigation_controller để điều hướng back
        
        Flow:
        1. Ghi log back action (theo System Instruction)
        2. Gọi navigation_controller.go_back() để quay lại screen trước
        3. Ghi log kết quả (theo System Instruction)
        """
        function_name = "EditVideoScreen.on_back_click"
        
        if not self.navigation_controller:
            # Nếu không có navigation_controller, sử dụng close behavior cũ
            log_ui_action(self.logger, function_name, "back_no_nav", "EditVideoScreen", "WARNING",
                         "NavigationController not available, using close behavior")
            self.on_close()
            return
        
        try:
            # Log back action (theo System Instruction)
            log_ui_action(self.logger, function_name, "back", "EditVideoScreen", "INFO",
                         "User clicked back button - navigating back to Home Screen")
            
            # Gọi navigation_controller.go_back() để quay lại screen trước (iOS-style)
            success = self.navigation_controller.go_back()
            
            if success:
                log_ui_action(self.logger, function_name, "back_success", "EditVideoScreen", "INFO",
                             "Successfully navigated back to Home Screen")
                # Log navigation (theo System Instruction)
                log_screen_navigation(self.logger, function_name, "EditVideoScreen", 
                                    "MainDashboard", success=True, action="back")
            else:
                log_ui_action(self.logger, function_name, "back_failed", "EditVideoScreen", "WARNING",
                             "Cannot go back: already at home screen")
                
        except Exception as e:
            # Log error đầy đủ (theo System Instruction)
            log_ui_action(self.logger, function_name, "back_error", "EditVideoScreen", "ERROR",
                         f"Error during back navigation: {e}")
    
    def on_close(self):
        """Event handler khi close screen"""
        function_name = "EditVideoScreen.on_close"
        log_ui_action(self.logger, function_name, "close", "EditVideoScreen", "INFO",
                     "Closing Edit Video Screen")
        
        # Log navigation (theo System Instruction)
        log_screen_navigation(self.logger, function_name, "EditVideoScreen", 
                            "MainDashboard", success=True)
        
        # Hủy theo chế độ hiển thị
        try:
            if self._embedded_mode:
                # Nhúng: chỉ destroy frame
                if hasattr(self, "frame"):
                    self.frame.destroy()
                # Yêu cầu NavigationController back nếu có
                if self.navigation_controller and hasattr(self.navigation_controller, "go_back"):
                    self.navigation_controller.go_back()
            else:
                if hasattr(self, "window"):
                    self.window.destroy()
        except Exception:
            pass
    
    # ========== EVENT HANDLERS ==========
    def _choose_background(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="Chọn background", filetypes=[("Image files","*.png;*.jpg;*.jpeg")])
        if path:
            self.bg_path_var.set(path)
    
    def _choose_input_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Chọn thư mục nguồn", initialdir="downloads")
        if path:
            self.input_folder_var.set(path)
    
    def _choose_output_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Chọn thư mục output", initialdir="downloads/edited")
        if path:
            self.output_folder_var.set(path)
    
    def _append_log(self, message: str):
        try:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        except Exception:
            pass
    
    def _start_batch(self):
        """Khởi chạy batch edit qua EditController"""
        from gui.controllers.edit_controller import EditController
        import os
        
        self._append_log("Bắt đầu batch...")
        
        bg = self.bg_path_var.get().strip()
        inp = self.input_folder_var.get().strip() or "downloads"
        out = self.output_folder_var.get().strip() or os.path.join("downloads","edited")
        threads = int(self.threads_var.get())
        
        config = {
            "position": {"x": int(self.pos_x_var.get()), "y": int(self.pos_y_var.get())},
            "size": {"width": int(self.size_w_var.get()), "height": int(self.size_h_var.get())},
            "keep_ratio": bool(self.keep_ratio_var.get()),
            "pad_color": [0,0,0],
            "bitrate": self.bitrate_var.get().strip() or "2500k",
            "preset": self.preset_var.get().strip() or "medium",
            "output_suffix": self.suffix_var.get(),
            "skip_existing": bool(self.skip_existing_var.get())
        }
        
        if not hasattr(self, "_controller"):
            self._controller = EditController()
        
        def on_progress(progress: float, current: int, total: int, message: str):
            self.window.after(0, lambda: self._on_progress_ui(progress, current, total, message))
        
        def on_result(res: dict):
            msg = f"{'✓' if res.get('success') else '✗'} {os.path.basename(res.get('input',''))} -> {res.get('output') or res.get('error')}"
            self.window.after(0, lambda: self._append_log(msg))
        
        def on_complete():
            self.window.after(0, lambda: self._append_log("Hoàn tất batch!"))
        
        ok = self._controller.start_batch(
            background_path=bg, input_folder=inp, output_folder=out,
            config=config, threads=threads,
            progress_cb=on_progress, result_cb=on_result, complete_cb=on_complete
        )
        if not ok:
            self._append_log("✗ Không thể khởi chạy batch (kiểm tra cấu hình).")
    
    def _on_progress_ui(self, progress: float, current: int, total: int, message: str):
        try:
            self.progress_var.set(progress)
            self._append_log(f"{message} ({progress:.1f}%)")
        except Exception:
            pass
    
    def _stop_batch(self):
        if hasattr(self, "_controller"):
            self._controller.stop_batch()
            self._append_log("Đã gửi tín hiệu dừng batch.")

