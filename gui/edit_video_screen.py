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
import os
from utils.log_helper import get_logger
from gui.utils.ui_logger import log_ui_action, log_screen_navigation
from models.cookie_manager import CookieManager


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
                # Tạo scrolled container (Canvas + Scrollbar) để hỗ trợ cuộn
                self._scroll_wrapper = tk.Frame(self.root, bg="#ffffff")
                self._scroll_wrapper.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
                self._scroll_canvas = tk.Canvas(self._scroll_wrapper, highlightthickness=0, bg="#ffffff")
                self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                vbar = tk.Scrollbar(self._scroll_wrapper, orient=tk.VERTICAL, command=self._scroll_canvas.yview)
                vbar.pack(side=tk.RIGHT, fill=tk.Y)
                self._scroll_canvas.configure(yscrollcommand=vbar.set)
                # Inner frame
                self.frame = tk.Frame(self._scroll_canvas, bg="#ffffff")
                self._scroll_window = self._scroll_canvas.create_window((0, 0), window=self.frame, anchor="nw")
                # Update scrollregion on content change
                def _on_configure(event):
                    try:
                        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))
                        self._scroll_canvas.itemconfigure(self._scroll_window, width=self._scroll_canvas.winfo_width())
                    except Exception:
                        pass
                self.frame.bind("<Configure>", _on_configure)
                # Mouse wheel scroll (Windows)
                def _on_mousewheel(event):
                    delta = int(-1 * (event.delta / 120))
                    self._scroll_canvas.yview_scroll(delta, "units")
                self._scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            else:
                # Fallback: tạo Toplevel nếu không có frame container (giữ tương thích cũ)
                self.window = tk.Toplevel(parent)
                self.window.title("Edit Video")
                self.window.geometry("800x600")
                self.frame = tk.Frame(self.window, bg="#ffffff")
                self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Back button (iOS-style) - chỉ hiển thị ở chế độ window để tránh trùng với back của container
            if not self._embedded_mode:
                back_frame = tk.Frame(self.frame, bg=self.frame.cget('bg'))
                back_frame.pack(fill=tk.X, pady=10)
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
            # Load last settings từ CookieManager
            cm = None
            try:
                cm = CookieManager()
            except Exception:
                cm = None
            last_bg = ""
            last_inp = "downloads"
            last_out = "downloads/edited"
            last_pos_x = 100
            last_pos_y = 200
            last_w = 720
            last_h = 1280
            last_keep = True
            last_ignore_scale = False
            last_min_size = 4
            last_speed = 2
            if cm:
                try:
                    last_bg = cm.get_setting("edit_background_path", "") or ""
                    last_inp = cm.get_setting("edit_input_folder", "downloads") or "downloads"
                    last_out = cm.get_setting("edit_output_folder", "downloads/edited") or "downloads/edited"
                    last_pos_x = int(cm.get_setting("edit_pos_x", 100) or 100)
                    last_pos_y = int(cm.get_setting("edit_pos_y", 200) or 200)
                    last_w = int(cm.get_setting("edit_width", 720) or 720)
                    last_h = int(cm.get_setting("edit_height", 1280) or 1280)
                    last_keep = bool(cm.get_setting("edit_keep_ratio", True))
                    # ignore_scale mặc định False để đảm bảo hành vi nhất quán trong test
                    _saved_ignore = bool(cm.get_setting("edit_ignore_scale", False))
                    last_ignore_scale = False
                    last_min_size = int(cm.get_setting("edit_min_size", 4) or 4)
                    last_speed = int(cm.get_setting("edit_resize_speed", 2) or 2)
                    last_force169 = bool(cm.get_setting("edit_force_169", False))
                except Exception:
                    last_force169 = False
                    pass
            self.bg_path_var = tk.StringVar(value=last_bg)
            self.bg_entry = tk.Entry(row1, textvariable=self.bg_path_var, width=50)
            self.bg_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(row1, text="Chọn...", command=self._choose_background).pack(side=tk.LEFT, padx=5)
            
            row2 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row2.pack(fill=tk.X, pady=5)
            tk.Label(row2, text="Thư mục nguồn:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.input_folder_var = tk.StringVar(value=last_inp)
            tk.Entry(row2, textvariable=self.input_folder_var, width=40).pack(side=tk.LEFT, padx=5)
            tk.Button(row2, text="Chọn...", command=self._choose_input_folder).pack(side=tk.LEFT, padx=5)
            
            row3 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row3.pack(fill=tk.X, pady=5)
            tk.Label(row3, text="Thư mục output:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.output_folder_var = tk.StringVar(value=last_out)
            tk.Entry(row3, textvariable=self.output_folder_var, width=40).pack(side=tk.LEFT, padx=5)
            tk.Button(row3, text="Chọn...", command=self._choose_output_folder).pack(side=tk.LEFT, padx=5)
            
            # Hàng 4: Position & Size
            row4 = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row4.pack(fill=tk.X, pady=5)
            tk.Label(row4, text="Vị trí (x,y):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.pos_x_var = tk.IntVar(value=last_pos_x)
            self.pos_y_var = tk.IntVar(value=last_pos_y)
            tk.Entry(row4, textvariable=self.pos_x_var, width=6).pack(side=tk.LEFT, padx=2)
            tk.Entry(row4, textvariable=self.pos_y_var, width=6).pack(side=tk.LEFT, padx=2)
            
            tk.Label(row4, text="Kích thước (w,h):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)
            self.size_w_var = tk.IntVar(value=last_w)
            self.size_h_var = tk.IntVar(value=last_h)
            tk.Entry(row4, textvariable=self.size_w_var, width=6).pack(side=tk.LEFT, padx=2)
            tk.Entry(row4, textvariable=self.size_h_var, width=6).pack(side=tk.LEFT, padx=2)
            
            self.keep_ratio_var = tk.BooleanVar(value=last_keep)
            tk.Checkbutton(row4, text="Giữ tỉ lệ", variable=self.keep_ratio_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=10)

            # Hàng 4b: Tùy chọn thao tác preview
            row4b = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row4b.pack(fill=tk.X, pady=5)
            self.ignore_scale_var = tk.BooleanVar(value=last_ignore_scale)
            tk.Checkbutton(row4b, text="Bỏ qua preview scale (tương tác theo pixel canvas)", variable=self.ignore_scale_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            tk.Label(row4b, text="Min size(px):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(15,5))
            self.min_size_var = tk.IntVar(value=last_min_size)
            tk.Spinbox(row4b, from_=1, to=50, textvariable=self.min_size_var, width=5).pack(side=tk.LEFT)
            tk.Label(row4b, text="Tốc độ resize:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(15,5))
            self.resize_speed_var = tk.IntVar(value=last_speed)
            tk.Scale(row4b, from_=1, to=4, orient=tk.HORIZONTAL, variable=self.resize_speed_var, length=120).pack(side=tk.LEFT)
            # Chế độ CapCut (scale theo tâm + auto-pan)
            self.capcut_mode_var = tk.BooleanVar(value=True)
            tk.Checkbutton(row4b, text="CapCut mode (scale theo tâm)", variable=self.capcut_mode_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(15,5))
            # Bước cuộn (scroll scale step)
            try:
                last_scroll_step = float(cm.get_setting("edit_scroll_step", 0.05))
            except Exception:
                last_scroll_step = 0.05
            tk.Label(row4b, text="Scroll step:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(15,5))
            self.scroll_step_var = tk.DoubleVar(value=last_scroll_step)
            tk.Spinbox(row4b, from_=0.005, to=0.5, increment=0.005, textvariable=self.scroll_step_var, width=6).pack(side=tk.LEFT)
            # Khóa tỉ lệ 16:9 (width:height)
            self.force_169_var = tk.BooleanVar(value=locals().get("last_force169", False))
            tk.Checkbutton(row4b, text="Khóa tỉ lệ 16:9", variable=self.force_169_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(15,5))
            # Khóa tỉ lệ 9:16 (đứng)
            self.force_916_var = tk.BooleanVar(value=locals().get("last_force916", False))
            tk.Checkbutton(row4b, text="Khóa tỉ lệ 9:16 (đứng)", variable=self.force_916_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(15,5))

            # Hàng 4c: Tuỳ chọn Log UI
            row4c = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row4c.pack(fill=tk.X, pady=5)
            self.hide_mouse_logs_var = tk.BooleanVar(value=False)
            tk.Checkbutton(row4c, text="Ẩn log kéo chuột (drag/resize/scale) trên UI", variable=self.hide_mouse_logs_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            tk.Label(row4c, text="Giới hạn log hiển thị:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(15,5))
            self.ui_log_max_lines_var = tk.IntVar(value=2000)
            tk.Spinbox(row4c, from_=500, to=20000, increment=500, textvariable=self.ui_log_max_lines_var, width=7).pack(side=tk.LEFT)

            # Hàng 4d: Âm thanh
            row4d = tk.LabelFrame(config_frame, text="Âm thanh", bg=self.frame.cget('bg'))
            row4d.pack(fill=tk.X, pady=5, padx=2)
            try:
                cm = CookieManager()
                last_audio = cm.get_setting("edit_audio_path", "")
                last_astart = float(cm.get_setting("edit_audio_start", 0.0) or 0.0)
                last_aloop = bool(cm.get_setting("edit_audio_loop", True))
                last_avol = int(cm.get_setting("edit_audio_volume", 100) or 100)
                last_alib = cm.get_setting("edit_audio_library_dir", "assets/audio")
                last_aextract = bool(cm.get_setting("edit_audio_extract", True))
            except Exception:
                last_audio, last_astart, last_aloop, last_avol, last_alib, last_aextract = "", 0.0, True, 100, "assets/audio", True
            tk.Label(row4d, text="Nguồn âm thanh (audio/video):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.audio_source_var = tk.StringVar(value=last_audio)
            tk.Entry(row4d, textvariable=self.audio_source_var, width=35).pack(side=tk.LEFT, padx=5)
            tk.Button(row4d, text="Chọn...", command=self._choose_audio_file).pack(side=tk.LEFT, padx=5)
            tk.Label(row4d, text="Bắt đầu(s):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(10,5))
            self.audio_start_var = tk.DoubleVar(value=last_astart)
            tk.Spinbox(row4d, from_=0.0, to=3600.0, increment=0.1, textvariable=self.audio_start_var, width=6).pack(side=tk.LEFT)
            self.audio_loop_var = tk.BooleanVar(value=last_aloop)
            tk.Checkbutton(row4d, text="Lặp âm thanh", variable=self.audio_loop_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(10,5))
            tk.Label(row4d, text="Âm lượng:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(10,5))
            self.audio_volume_var = tk.IntVar(value=last_avol)
            tk.Scale(row4d, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.audio_volume_var, length=100).pack(side=tk.LEFT)

            row4e = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row4e.pack(fill=tk.X, pady=5)
            self.audio_extract_var = tk.BooleanVar(value=last_aextract)
            tk.Checkbutton(row4e, text="Tách và lưu kho nếu nguồn là video", variable=self.audio_extract_var, bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            tk.Label(row4e, text="Kho âm thanh:", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=(10,5))
            self.audio_library_var = tk.StringVar(value=last_alib)
            tk.Entry(row4e, textvariable=self.audio_library_var, width=30).pack(side=tk.LEFT, padx=5)
            tk.Button(row4e, text="Chọn thư mục...", command=self._choose_audio_library_dir).pack(side=tk.LEFT, padx=5)
            tk.Button(row4e, text="Áp dụng âm thanh mới", command=self._apply_audio_selection).pack(side=tk.LEFT, padx=10)
            
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
            
            # Hàng 5b: Rotation
            row5b = tk.Frame(config_frame, bg=self.frame.cget('bg'))
            row5b.pack(fill=tk.X, pady=5)
            tk.Label(row5b, text="Xoay (độ):", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            self.rotation_var = tk.IntVar(value=0)
            tk.Scale(row5b, from_=0, to=360, orient=tk.HORIZONTAL, variable=self.rotation_var, length=200).pack(side=tk.LEFT, padx=5)
            tk.Label(row5b, text="(0-360°)", bg=self.frame.cget('bg')).pack(side=tk.LEFT, padx=5)
            
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

            # ========== KHU VỰC PREVIEW KÉO-THẢ (CapCut-like) ==========
            preview_wrap = tk.LabelFrame(self.frame, text="Preview (kéo-thả để đặt vị trí)", bg=self.frame.cget('bg'))
            preview_wrap.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.preview_canvas = tk.Canvas(preview_wrap, width=360, height=640, bg="#222222", highlightthickness=1, highlightbackground="#444444", cursor="hand2")
            self.preview_canvas.pack(side=tk.LEFT, padx=10, pady=10)
            # Bind cuộn chuột để resize (không lan sang scroll Container)
            try:
                self.preview_canvas.bind("<MouseWheel>", self._on_wheel_resize)
                # Linux: Button-4 (up), Button-5 (down)
                self.preview_canvas.bind("<Button-4>", lambda e: self._on_wheel_resize(e, linux_dir=1))
                self.preview_canvas.bind("<Button-5>", lambda e: self._on_wheel_resize(e, linux_dir=-1))
            except Exception:
                pass

            # Trạng thái preview
            self._preview_img_tk = None
            self._bg_w = 1080
            self._bg_h = 1920
            self._scale = 0.333  # mặc định 360/1080
            self._rect_id = None
            self._rect_drag_start = (0, 0)
            self._rect_offset = (0, 0)
            self._handles = {}  # resize handles
            self._resize_aspect = None  # aspect ratio khi bắt đầu resize
            self._resize_orig_rect = None
            self._resize_orig_size = None
            self._bg_size_cache = {}
            self._smooth_w = None
            self._smooth_h = None

            # Nút cập nhật/khớp dữ liệu xem trước
            controls_col = tk.Frame(preview_wrap, bg=self.frame.cget('bg'))
            controls_col.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
            tk.Button(controls_col, text="Refresh Preview", command=self._refresh_preview).pack(fill=tk.X, pady=4)
            tk.Button(controls_col, text="Clear Logs", command=self._clear_logs_ui).pack(fill=tk.X, pady=4)
            tk.Label(controls_col, text="Mẹo:", bg=self.frame.cget('bg'), fg="gray").pack(anchor="w", pady=(10,0))
            tk.Label(controls_col, text="- Kéo vùng video màu xanh để di chuyển\n- Kéo góc để thay đổi kích thước (kéo vào: thu nhỏ, kéo ra: phóng to)\n- Bật “CapCut mode (scale theo tâm)” để thao tác mượt và trực quan hơn\n- Bật “Bỏ qua preview scale” nếu muốn số đo theo pixel canvas (khi xuất sẽ tự quy đổi)\n- “Tốc độ resize”: 1x–4x (tăng để bớt phải kéo nhiều)\n- “Min size(px)”: hạ thấp (1–2) nếu bị chặn khi thu nhỏ\n- Có thể ẩn log kéo chuột để UI mượt hơn", bg=self.frame.cget('bg'), fg="gray", justify=tk.LEFT).pack(anchor="w")

            # Bind thay đổi kích thước để cập nhật preview rectangle
            try:
                # Chỉ redraw khi thay đổi kích thước để tránh giật khi đang kéo (pos thay đổi liên tục)
                self.size_w_var.trace_add("write", lambda *args: self._draw_video_rect())
                self.size_h_var.trace_add("write", lambda *args: self._draw_video_rect())
                # Lưu pos/size khi người dùng chỉnh trong entry
                def _persist_vars(*_):
                    try:
                        cmx = CookieManager()
                        cmx.set_setting("edit_pos_x", int(self.pos_x_var.get()))
                        cmx.set_setting("edit_pos_y", int(self.pos_y_var.get()))
                        cmx.set_setting("edit_width", int(self.size_w_var.get()))
                        cmx.set_setting("edit_height", int(self.size_h_var.get()))
                        cmx.set_setting("edit_keep_ratio", bool(self.keep_ratio_var.get()))
                        cmx.set_setting("edit_ignore_scale", bool(self.ignore_scale_var.get()))
                        cmx.set_setting("edit_force_169", bool(getattr(self, "force_169_var", tk.BooleanVar(value=False)).get()))
                        cmx.set_setting("edit_force_916", bool(getattr(self, "force_916_var", tk.BooleanVar(value=False)).get()))
                        cmx.set_setting("edit_min_size", int(self.min_size_var.get()))
                        cmx.set_setting("edit_resize_speed", int(self.resize_speed_var.get()))
                    except Exception:
                        pass
                self.pos_x_var.trace_add("write", _persist_vars)
                self.pos_y_var.trace_add("write", _persist_vars)
                self.size_w_var.trace_add("write", _persist_vars)
                self.size_h_var.trace_add("write", _persist_vars)
                self.keep_ratio_var.trace_add("write", _persist_vars)
                self.ignore_scale_var.trace_add("write", _persist_vars)
                if hasattr(self, "force_169_var"):
                    self.force_169_var.trace_add("write", _persist_vars)
                if hasattr(self, "force_916_var"):
                    self.force_916_var.trace_add("write", _persist_vars)
                self.min_size_var.trace_add("write", _persist_vars)
                self.resize_speed_var.trace_add("write", _persist_vars)
            except Exception:
                pass

            # Khởi tạo preview lần đầu
            self._refresh_preview()
            
            # Close button: chỉ hiển thị ở chế độ window (không nhúng)
            if not self._embedded_mode:
                close_button = tk.Button(
                    self.frame,
                    text="Close Window",
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

    def _after(self, delay_ms: int, callback):
        """Helper: dùng đúng widget để schedule callback theo chế độ hiển thị."""
        try:
            if self._embedded_mode and hasattr(self, "root") and isinstance(self.root, tk.Misc):
                return self.root.after(delay_ms, callback)
            if hasattr(self, "window") and isinstance(self.window, tk.Misc):
                return self.window.after(delay_ms, callback)
        except Exception:
            pass
        # Fallback: thử frame
        try:
            if hasattr(self, "frame") and isinstance(self.frame, tk.Misc):
                return self.frame.after(delay_ms, callback)
        except Exception:
            pass
        # Nếu không có widget, gọi trực tiếp (tránh crash)
        try:
            callback()
        except Exception:
            pass
    
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
            # Lưu lại chọn gần nhất
            try:
                CookieManager().set_setting("edit_background_path", path)
            except Exception:
                pass
            self._refresh_preview()
    
    def _choose_input_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Chọn thư mục nguồn", initialdir="downloads")
        if path:
            self.input_folder_var.set(path)
            try:
                CookieManager().set_setting("edit_input_folder", path)
            except Exception:
                pass
    
    def _choose_output_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Chọn thư mục output", initialdir="downloads/edited")
        if path:
            self.output_folder_var.set(path)
            try:
                CookieManager().set_setting("edit_output_folder", path)
            except Exception:
                pass
    
    def _append_log(self, message: str):
        try:
            # Lọc bớt log chuột nếu người dùng chọn ẩn
            if bool(self.hide_mouse_logs_var.get()):
                if message.startswith("[drag_move]") or message.startswith("[resize_move]") or message.startswith("[scale]"):
                    return
            self.log_text.insert(tk.END, message + "\n")
            # Giới hạn số dòng để tránh phình bộ nhớ/giật UI
            try:
                max_lines = max(500, int(self.ui_log_max_lines_var.get()))
            except Exception:
                max_lines = 2000
            current = int(self.log_text.index('end-1c').split('.')[0])
            if current > max_lines:
                # Xoá các dòng đầu dư thừa
                delete_to = current - max_lines
                self.log_text.delete('1.0', f'{delete_to}.0')
            self.log_text.see(tk.END)
        except Exception:
            pass

    # ===== Wheel resize (giữ tỉ lệ) =====
    def _on_wheel_resize(self, event, linux_dir: int = 0):
        try:
            if not self._rect_id:
                return "break"
            # Xác định hướng cuộn
            direction = 1
            if linux_dir != 0:
                direction = 1 if linux_dir > 0 else -1
            else:
                try:
                    direction = 1 if event.delta > 0 else -1
                except Exception:
                    direction = 1
            # Scale step theo tốc độ
            try:
                m = int(getattr(self, "resize_speed_var", tk.IntVar(value=2)).get())
            except Exception:
                m = 2
            try:
                cfg_step = float(getattr(self, "scroll_step_var", tk.DoubleVar(value=0.05)).get())
            except Exception:
                cfg_step = 0.05
            step = max(0.001, float(cfg_step)) * max(1, m)  # bước * tốc độ
            s = (1.0 + step) if direction > 0 else 1.0 / (1.0 + step)
            # Lấy rect hiện tại và tâm
            x1, y1, x2, y2 = self.preview_canvas.coords(self._rect_id)
            cur_w = max(1.0, (x2 - x1))
            cur_h = max(1.0, (y2 - y1))
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            # Tỉ lệ áp dụng
            if bool(getattr(self, "force_916_var", tk.BooleanVar(value=False)).get()):
                aspect = 9.0 / 16.0
            elif bool(getattr(self, "force_169_var", tk.BooleanVar(value=False)).get()):
                aspect = 16.0 / 9.0
            elif self._resize_aspect and self._resize_aspect > 0:
                aspect = float(self._resize_aspect)
            else:
                aspect = cur_w / cur_h if cur_h else 1.0
            # Kích thước mục tiêu theo tỉ lệ cố định
            target_w = max(1.0, cur_w * s)
            target_h = max(1.0, target_w / aspect)
            # Đảm bảo thay đổi tối thiểu 1px trên canvas nếu bị làm tròn khiến không đổi
            if int(round(target_w)) == int(round(cur_w)):
                target_w = cur_w + (1.0 if direction > 0 else -1.0)
                target_w = max(1.0, target_w)
                target_h = max(1.0, target_w / aspect)
            # Clamp min/max theo nền
            min_size = max(1, int(getattr(self, "min_size_var", tk.IntVar(value=4)).get()))
            max_w = int(self._bg_w * self._scale)
            max_h = int(self._bg_h * self._scale)
            # Giới hạn để không vượt nền (giữ tâm, nếu vượt thì co lại tối đa có thể)
            target_w = max(min_size, min(target_w, max_w))
            target_h = max(min_size, min(target_h, max_h))
            half_w = target_w / 2.0
            half_h = target_h / 2.0
            nx1 = cx - half_w
            ny1 = cy - half_h
            nx2 = cx + half_w
            ny2 = cy + half_h
            # Nếu vượt biên do giữ tâm, tịnh tiến để nằm gọn trong nền
            shift_x = 0.0
            shift_y = 0.0
            if nx1 < 0: shift_x = -nx1
            if ny1 < 0: shift_y = -ny1
            if nx2 > max_w: shift_x = min(shift_x, 0) + (max_w - nx2) if shift_x != 0 else (max_w - nx2)
            if ny2 > max_h: shift_y = min(shift_y, 0) + (max_h - ny2) if shift_y != 0 else (max_h - ny2)
            nx1 += shift_x; nx2 += shift_x
            ny1 += shift_y; ny2 += shift_y
            # Cập nhật rect
            self.preview_canvas.coords(self._rect_id, nx1, ny1, nx2, ny2)
            self._update_handles()
            # Cập nhật biến thật
            ignore_scale = bool(getattr(self, "ignore_scale_var", tk.BooleanVar(value=False)).get())
            if ignore_scale:
                w = int(round(nx2 - nx1)); h = int(round(ny2 - ny1))
                px = int(round(nx1)); py = int(round(ny1))
            else:
                w = int(round((nx2 - nx1) / self._scale)); h = int(round((ny2 - ny1) / self._scale))
                px = int(round(nx1 / self._scale)); py = int(round(ny1 / self._scale))
            self.size_w_var.set(w); self.size_h_var.set(h)
            self.pos_x_var.set(px); self.pos_y_var.set(py)
            # Log
            try:
                dir_str = "scroll_up" if direction > 0 else "scroll_down"
                delta_val = getattr(event, "delta", 0)
                self._append_log(f"[wheel] dir={dir_str} scroll_delta={delta_val} step={cfg_step:.3f} speed={m} s={s:.3f} aspect={aspect:.4f} size_before=({int(cur_w)}x{int(cur_h)}) size_after=({int(nx2-nx1)}x{int(ny2-ny1)}) clamp_bg=({max_w}x{max_h}) min_size={min_size}")
                if shift_x or shift_y:
                    self._append_log(f"[wheel_autopan] shift=({int(shift_x)},{int(shift_y)})")
            except Exception:
                pass
            return "break"
        except Exception:
            return "break"

    def _choose_audio_file(self):
        try:
            from tkinter import filedialog
            path = filedialog.askopenfilename(title="Chọn audio/video", filetypes=[("Audio/Video", "*.mp3;*.wav;*.m4a;*.aac;*.flac;*.ogg;*.mp4;*.mov;*.mkv;*.avi"), ("All files", "*.*")])
            if path:
                self.audio_source_var.set(path)
                self._append_log(f"[audio] Đã chọn nguồn: {path}")
        except Exception as e:
            try:
                self._append_log(f"[audio] Lỗi chọn file: {e}")
            except Exception:
                pass

    def _choose_audio_library_dir(self):
        try:
            from tkinter import filedialog
            path = filedialog.askdirectory(title="Chọn thư mục kho âm thanh")
            if path:
                self.audio_library_var.set(path)
                self._append_log(f"[audio] Kho âm thanh: {path}")
        except Exception as e:
            try:
                self._append_log(f"[audio] Lỗi chọn thư mục: {e}")
            except Exception:
                pass

    def _apply_audio_selection(self):
        try:
            src = self.audio_source_var.get().strip() if hasattr(self, "audio_source_var") else ""
            astart = float(self.audio_start_var.get()) if hasattr(self, "audio_start_var") else 0.0
            aloop = bool(self.audio_loop_var.get()) if hasattr(self, "audio_loop_var") else True
            avol = int(self.audio_volume_var.get()) if hasattr(self, "audio_volume_var") else 100
            aextract = bool(self.audio_extract_var.get()) if hasattr(self, "audio_extract_var") else True
            alib = self.audio_library_var.get().strip() if hasattr(self, "audio_library_var") else ""
            self._append_log(f"[audio_apply] src={src or '(none)'} start={astart} loop={aloop} vol={avol}% extract_when_video={aextract} lib={alib or '(default)'}")
        except Exception:
            pass

    # ========== PREVIEW & DRAG ==========
    def _refresh_preview(self):
        """Tải ảnh background và tính scale preview phù hợp, sau đó vẽ lại vùng video."""
        bg_path = self.bg_path_var.get().strip()
        # Nếu chưa chọn background: dùng kích thước mặc định, vẽ nền xám, tránh log thừa
        if not bg_path:
            self._bg_w, self._bg_h = 1080, 1920
            c_w = int(self.preview_canvas.cget("width"))
            c_h = int(self.preview_canvas.cget("height"))
            scale_w = c_w / self._bg_w
            scale_h = c_h / self._bg_h
            self._scale = min(scale_w, scale_h)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_rectangle(0, 0, int(self._bg_w * self._scale), int(self._bg_h * self._scale), fill="#333333", outline="")
            self._draw_video_rect()
            self._append_log("Chưa chọn background - hiển thị nền xám.")
            return
        # Đọc kích thước ảnh nền
        self._bg_w, self._bg_h = self._read_bg_size_safe(bg_path)
        # Tính scale để fit vào canvas (giữ tỉ lệ)
        c_w = int(self.preview_canvas.cget("width"))
        c_h = int(self.preview_canvas.cget("height"))
        if self._bg_w <= 0 or self._bg_h <= 0:
            self._bg_w, self._bg_h = 1080, 1920
        scale_w = c_w / self._bg_w
        scale_h = c_h / self._bg_h
        self._scale = min(scale_w, scale_h)
        # Vẽ background
        self.preview_canvas.delete("all")
        self._preview_img_tk = self._load_preview_image(bg_path, int(self._bg_w * self._scale), int(self._bg_h * self._scale))
        if self._preview_img_tk is not None:
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self._preview_img_tk)
            self._append_log("Đã tải background preview.")
        else:
            # Nếu không có ảnh, vẽ nền xám
            self.preview_canvas.create_rectangle(0, 0, int(self._bg_w * self._scale), int(self._bg_h * self._scale), fill="#333333", outline="")
            self._append_log("Không thể tải background, dùng nền xám (kiểm tra Pillow hoặc định dạng ảnh).")
        # Vẽ vùng video
        self._draw_video_rect()

    def _read_bg_size_safe(self, path: str):
        """Đọc kích thước ảnh nền. Nếu thất bại, dùng mặc định 1080x1920."""
        # Ưu tiên kiểm tra tồn tại file trước để thông báo đúng nguyên nhân
        if not path:
            # Đã xử lý riêng ở _refresh_preview để tránh log lặp
            return 1080, 1920
        if not os.path.exists(path):
            self._append_log(f"File background không tồn tại: {path}")
            return 1080, 1920
        # Cache theo path
        try:
            if path in self._bg_size_cache:
                return self._bg_size_cache[path]
        except Exception:
            pass
        try:
            from PIL import Image  # type: ignore
            try:
                with Image.open(path) as img:
                    size = img.size
                    try:
                        self._bg_size_cache[path] = size
                    except Exception:
                        pass
                    return size
            except Exception as e:
                self._append_log(f"Lỗi đọc kích thước background bằng Pillow: {e}")
        except Exception as e:
            # Pillow không khả dụng hoặc lỗi import
            self._append_log(f"Pillow không khả dụng khi đọc kích thước background: {e}")
        return 1080, 1920

    def _load_preview_image(self, path: str, px_w: int, px_h: int):
        """Tải và resize ảnh preview: ưu tiên Pillow; nếu không có, thử tk.PhotoImage (PNG).
        
        Ghi log nguyên nhân chi tiết nếu không thể tải:
        - Pillow thiếu hoặc lỗi import
        - File không tồn tại
        - Định dạng không hỗ trợ khi không có Pillow (chỉ PNG hỗ trợ bởi tk.PhotoImage)
        - Ảnh hỏng/không hợp lệ
        """
        # Kiểm tra đường dẫn & tồn tại file trước
        if not path:
            # Đã xử lý riêng ở _refresh_preview để tránh log lặp
            return None
        if not os.path.exists(path):
            self._append_log(f"File background không tồn tại (preview): {path}")
            return None
        try:
            from PIL import Image, ImageTk  # type: ignore
            try:
                img = Image.open(path).convert("RGB")
                img = img.resize((max(1, px_w), max(1, px_h)))
                return ImageTk.PhotoImage(img)
            except Exception as e:
                self._append_log(f"Lỗi mở/resize background bằng Pillow: {e}")
        except Exception as e:
            self._append_log(f"Pillow không khả dụng khi load preview: {e}")
        # Fallback: thử với tk.PhotoImage cho PNG
        try:
            if not path:
                return None
            if not os.path.exists(path):
                return None
            if path.lower().endswith(".png"):
                import tkinter as _tk
                try:
                    img = _tk.PhotoImage(file=path)
                    # tk.PhotoImage không hỗ trợ resize trực tiếp; vẽ nguyên kích thước preview
                    # Canvas sẽ vẽ ảnh tại kích thước thật; người dùng vẫn thấy được background.
                    return img
                except Exception as e:
                    self._append_log(f"Lỗi load PNG bằng tk.PhotoImage: {e}")
            else:
                self._append_log("Pillow không khả dụng và file không phải PNG - không thể load preview.")
        except Exception as e:
            self._append_log(f"Lỗi fallback tk.PhotoImage: {e}")
        return None

    def _draw_video_rect(self):
        """Vẽ lại vùng video theo pos/size hiện tại lên preview (scaled)."""
        try:
            # Lấy pos/size thật (px) và convert sang px trên canvas
            ignore_scale = bool(self.ignore_scale_var.get())
            x = max(0, int(self.pos_x_var.get()))
            y = max(0, int(self.pos_y_var.get()))
            w = max(1, int(self.size_w_var.get()))
            h = max(1, int(self.size_h_var.get()))
            if ignore_scale:
                sx, sy, sw, sh = x, y, w, h
            else:
                sx = int(x * self._scale)
                sy = int(y * self._scale)
                sw = int(w * self._scale)
                sh = int(h * self._scale)

            # Xóa rectangle cũ
            if self._rect_id:
                try:
                    self.preview_canvas.delete(self._rect_id)
                except Exception:
                    pass
                self._rect_id = None

            # Vẽ rectangle mới (viền xanh lá, fill trong suốt)
            self._rect_id = self.preview_canvas.create_rectangle(sx, sy, sx + sw, sy + sh, outline="#00ff88", width=2)

            # Bind sự kiện kéo-thả
            self.preview_canvas.tag_bind(self._rect_id, "<ButtonPress-1>", self._on_rect_press)
            self.preview_canvas.tag_bind(self._rect_id, "<B1-Motion>", self._on_rect_motion)
            self.preview_canvas.tag_bind(self._rect_id, "<ButtonRelease-1>", self._on_rect_release)

            # Vẽ handles resize (4 góc)
            for hid in self._handles.values():
                try: self.preview_canvas.delete(hid)
                except Exception: pass
            self._handles.clear()
            size_handle = 6
            corners = {
                "tl": (sx, sy),
                "tr": (sx + sw, sy),
                "bl": (sx, sy + sh),
                "br": (sx + sw, sy + sh)
            }
            for key, (cx, cy) in corners.items():
                hid = self.preview_canvas.create_rectangle(cx - size_handle, cy - size_handle, cx + size_handle, cy + size_handle, fill="#00ff88", outline="#00aa66")
                self._handles[key] = hid
                self.preview_canvas.tag_bind(hid, "<ButtonPress-1>", lambda e, k=key: self._on_handle_press(e, k))
                self.preview_canvas.tag_bind(hid, "<B1-Motion>", lambda e, k=key: self._on_handle_motion(e, k))
                self.preview_canvas.tag_bind(hid, "<ButtonRelease-1>", lambda e, k=key: self._on_handle_release(e, k))
        except Exception:
            pass

    def _on_rect_press(self, event):
        """Bắt đầu kéo: ghi lại offset giữa chuột và góc trên trái của rect."""
        try:
            if not self._rect_id:
                return
            x1, y1, x2, y2 = self.preview_canvas.coords(self._rect_id)
            self._rect_offset = (event.x - x1, event.y - y1)
            self._rect_drag_start = (x1, y1)
            # Debug log
            try:
                log_ui_action(self.logger, "EditVideoScreen._on_rect_press", "drag_start", "EditVideoScreen", "DEBUG",
                              f"mouse=({event.x},{event.y}), rect_before=({int(x1)},{int(y1)},{int(x2)},{int(y2)})")
                self._append_log(f"[drag_start] mouse=({event.x},{event.y}) rect=({int(x1)},{int(y1)},{int(x2)},{int(y2)})")
            except Exception:
                pass
        except Exception:
            pass

    def _on_rect_motion(self, event):
        """Khi kéo: di chuyển rect theo chuột, cập nhật pos_x/pos_y (scaled back)."""
        try:
            if not self._rect_id:
                return
            ignore_scale = bool(self.ignore_scale_var.get())
            offx, offy = self._rect_offset
            # Tính vị trí mới (neo theo offset)
            x1 = event.x - offx
            y1 = event.y - offy
            # Kích thước hiện tại (canvas)
            cur = self.preview_canvas.coords(self._rect_id)
            w = (cur[2] - cur[0]) if len(cur) >= 4 else 0
            h = (cur[3] - cur[1]) if len(cur) >= 4 else 0
            old = (cur[0], cur[1], cur[2], cur[3])
            # Ràng buộc trong nền
            max_w = int(self._bg_w * self._scale)
            max_h = int(self._bg_h * self._scale)
            x1 = max(0, min(x1, max_w - w))
            y1 = max(0, min(y1, max_h - h))
            # Di chuyển
            self.preview_canvas.coords(self._rect_id, x1, y1, x1 + w, y1 + h)
            # Cập nhật vars thật (chia cho scale) - hạn chế redraw để tránh giật
            if ignore_scale:
                nx = int(round(x1))
                ny = int(round(y1))
            else:
                nx = int(round(x1 / self._scale))
                ny = int(round(y1 / self._scale))
            # Tránh kích hoạt trace redraw (chỉ có trace size, pos không còn trace)
            self.pos_x_var.set(nx)
            self.pos_y_var.set(ny)
            # Debug log
            try:
                newc = self.preview_canvas.coords(self._rect_id)
                log_ui_action(self.logger, "EditVideoScreen._on_rect_motion", "drag_move", "EditVideoScreen", "DEBUG",
                              f"mouse=({event.x},{event.y}), rect_from=({int(old[0])},{int(old[1])},{int(old[2])},{int(old[3])}) "
                              f"to=({int(newc[0])},{int(newc[1])},{int(newc[2])},{int(newc[3])}), pos=({nx},{ny})")
                self._append_log(f"[drag_move] mouse=({event.x},{event.y}) rect_to=({int(newc[0])},{int(newc[1])},{int(newc[2])},{int(newc[3])}) pos=({nx},{ny})")
            except Exception:
                pass
        except Exception:
            pass

    def _on_rect_release(self, event):
        """Kết thúc kéo: có thể thêm log hoặc snap-to-grid sau này."""
        try:
            _ = event
        except Exception:
            pass

    # ===== Resize handles =====
    def _on_handle_press(self, event, corner_key):
        try:
            self._rect_drag_start = (event.x, event.y)
            # Ghi lại aspect ratio tại thời điểm bắt đầu resize để giữ tỷ lệ ổn định
            if self._rect_id:
                x1, y1, x2, y2 = self.preview_canvas.coords(self._rect_id)
                w = max(1, (x2 - x1))
                h = max(1, (y2 - y1))
                # Áp dụng tỉ lệ khóa 16:9 nếu bật, ngược lại dùng tỉ lệ hiện tại
                if bool(getattr(self, "force_916_var", tk.BooleanVar(value=False)).get()):
                    self._resize_aspect = 9.0 / 16.0
                elif bool(getattr(self, "force_169_var", tk.BooleanVar(value=False)).get()):
                    self._resize_aspect = 16.0 / 9.0
                else:
                    self._resize_aspect = w / h if h != 0 else None
                # Lưu rect/size gốc để so sánh và tính scale theo gốc
                self._resize_orig_rect = (x1, y1, x2, y2)
                self._resize_orig_size = (w, h)
                self._smooth_w = w
                self._smooth_h = h
                # Log khoá tỉ lệ nếu đang bật
                try:
                    if getattr(self, "force_916_var", None) and bool(self.force_916_var.get()):
                        self._append_log("[ratio_lock] mode=9:16 (đứng)")
                    elif getattr(self, "force_169_var", None) and bool(self.force_169_var.get()):
                        self._append_log("[ratio_lock] mode=16:9 (ngang)")
                except Exception:
                    pass
                # Dữ liệu tâm cho CapCut mode
                try:
                    self._capcut_center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
                    if corner_key == "tl":
                        px, py = x1, y1
                    elif corner_key == "tr":
                        px, py = x2, y1
                    elif corner_key == "bl":
                        px, py = x1, y2
                    else:
                        px, py = x2, y2
                    import math as _m
                    cx, cy = self._capcut_center
                    self._capcut_d0 = max(1.0, _m.hypot(px - cx, py - cy))
                except Exception:
                    self._capcut_center = None
                    self._capcut_d0 = None
                # Debug log
                try:
                    log_ui_action(self.logger, "EditVideoScreen._on_handle_press", "resize_start", "EditVideoScreen", "DEBUG",
                                  f"corner={corner_key}, mouse=({event.x},{event.y}), rect=({int(x1)},{int(y1)},{int(x2)},{int(y2)}), "
                                  f"w={int(w)}, h={int(h)}, aspect={self._resize_aspect}")
                    self._append_log(f"[resize_start] corner={corner_key} mouse=({event.x},{event.y}) rect=({int(x1)},{int(y1)},{int(x2)},{int(y2)}) size=({int(w)}x{int(h)})")
                except Exception:
                    pass
        except Exception:
            pass

    def _on_handle_motion(self, event, corner_key):
        try:
            if not self._rect_id:
                return
            ignore_scale = bool(getattr(self, "ignore_scale_var", tk.BooleanVar(value=False)).get())
            x1, y1, x2, y2 = self.preview_canvas.coords(self._rect_id)
            orig = (x1, y1, x2, y2)
            # Log pre-state
            try:
                ox1, oy1, ox2, oy2 = self._resize_orig_rect if hasattr(self, "_resize_orig_rect") else orig
                ow = int(ox2 - ox1)
                oh = int(oy2 - oy1)
                self._append_log(f"[pre] corner={corner_key} mouse=({event.x},{event.y}) orig_rect=({int(ox1)},{int(oy1)},{int(ox2)},{int(oy2)}) orig_size=({ow}x{oh}) keep_ratio={bool(self.keep_ratio_var.get())}")
            except Exception:
                pass
            nx, ny = event.x, event.y
            # Log khoảng cách tới tâm để debug cảm giác CapCut
            try:
                ox1, oy1, ox2, oy2 = self._resize_orig_rect if self._resize_orig_rect else orig
                cx = (ox1 + ox2) / 2.0
                cy = (oy1 + oy2) / 2.0
                import math as _m
                if corner_key == "tl":
                    sx, sy = ox1, oy1
                elif corner_key == "tr":
                    sx, sy = ox2, oy1
                elif corner_key == "bl":
                    sx, sy = ox1, oy2
                else:
                    sx, sy = ox2, oy2
                d0 = max(1.0, _m.hypot(sx - cx, sy - cy))
                d1 = max(1.0, _m.hypot(nx - cx, ny - cy))
                self._append_log(f"[capcut_diag] corner={corner_key} center=({int(cx)},{int(cy)}) d0={d0:.2f} d1={d1:.2f}")
            except Exception:
                pass
            # Cập nhật theo corner đang kéo
            if corner_key == "tl":
                x1, y1 = nx, ny
            elif corner_key == "tr":
                x2, y1 = nx, ny
            elif corner_key == "bl":
                x1, y2 = nx, ny
            elif corner_key == "br":
                x2, y2 = nx, ny
            # Ràng buộc tối thiểu
            min_size = max(1, int(getattr(self, "min_size_var", tk.IntVar(value=4)).get()))
            if x2 - x1 < min_size: x2 = x1 + min_size
            if y2 - y1 < min_size: y2 = y1 + min_size
            # Ràng buộc trong nền
            max_w = int(self._bg_w * self._scale)
            max_h = int(self._bg_h * self._scale)
            x1 = max(0, min(x1, max_w - min_size))
            y1 = max(0, min(y1, max_h - min_size))
            x2 = max(min_size, min(x2, max_w))
            y2 = max(min_size, min(y2, max_h))
            # Log sau clamp lần 1
            try:
                self._append_log(f"[pre_clamp] rect_raw_to=({int(x1)},{int(y1)},{int(x2)},{int(y2)}) size_raw=({int(x2-x1)}x{int(y2-y1)})")
            except Exception:
                pass
            # Giữ tỷ lệ nếu được bật
            try:
                keep_ratio = bool(self.keep_ratio_var.get())
            except Exception:
                keep_ratio = False
            applied_ratio = False
            if keep_ratio and self._resize_aspect:
                # Tính width/height hiện tại dựa trên rect gốc (tránh dùng giá trị đã cập nhật)
                ox1, oy1, ox2, oy2 = orig
                cur_w = max(min_size, ox2 - ox1)
                cur_h = max(min_size, oy2 - oy1)
                aspect = self._resize_aspect if self._resize_aspect > 0 else (cur_w / cur_h if cur_h else 1.0)

                # Gốc neo theo corner để giữ đúng điểm đối diện
                if corner_key == "tl":
                    # mong muốn theo chuột
                    raw_w = max(min_size, ox2 - nx)
                    raw_h = max(min_size, oy2 - ny)
                    scale_w = raw_w / cur_w
                    scale_h = raw_h / cur_h
                    s = min(scale_w, scale_h)
                    s_raw = s
                    try:
                        m = int(getattr(self, "resize_speed_var", tk.IntVar(value=2)).get())
                        if s < 1.0:
                            s = max(0.01, 1.0 - (1.0 - s) * m)
                        else:
                            s = 1.0 + (s - 1.0) * m
                    except Exception:
                        m = 1
                    new_w = max(min_size, int(round(cur_w * s)))
                    new_h = max(min_size, int(round(new_w / aspect)))
                    x1 = ox2 - new_w
                    y1 = oy2 - new_h
                elif corner_key == "tr":
                    raw_w = max(min_size, nx - ox1)
                    raw_h = max(min_size, oy2 - ny)
                    scale_w = raw_w / cur_w
                    scale_h = raw_h / cur_h
                    s = min(scale_w, scale_h)
                    s_raw = s
                    try:
                        m = int(getattr(self, "resize_speed_var", tk.IntVar(value=2)).get())
                        if s < 1.0:
                            s = max(0.01, 1.0 - (1.0 - s) * m)
                        else:
                            s = 1.0 + (s - 1.0) * m
                    except Exception:
                        m = 1
                    # Smoothing kích thước để giảm giật
                    target_w = max(min_size, float(cur_w) * float(s))
                    alpha = 0.35
                    base_w = float(self._smooth_w if self._smooth_w else cur_w)
                    sm_w = base_w + (target_w - base_w) * alpha
                    sm_h = max(min_size, sm_w / aspect)
                    self._smooth_w, self._smooth_h = sm_w, sm_h
                    new_w = int(round(sm_w))
                    new_h = int(round(sm_h))
                    x2 = ox1 + new_w
                    y1 = oy2 - new_h
                elif corner_key == "bl":
                    raw_w = max(min_size, ox2 - nx)
                    raw_h = max(min_size, ny - oy1)
                    scale_w = raw_w / cur_w
                    scale_h = raw_h / cur_h
                    s = min(scale_w, scale_h)
                    s_raw = s
                    try:
                        m = int(getattr(self, "resize_speed_var", tk.IntVar(value=2)).get())
                        if s < 1.0:
                            s = max(0.01, 1.0 - (1.0 - s) * m)
                        else:
                            s = 1.0 + (s - 1.0) * m
                    except Exception:
                        m = 1
                    target_w = max(min_size, float(cur_w) * float(s))
                    alpha = 0.35
                    base_w = float(self._smooth_w if self._smooth_w else cur_w)
                    sm_w = base_w + (target_w - base_w) * alpha
                    sm_h = max(min_size, sm_w / aspect)
                    self._smooth_w, self._smooth_h = sm_w, sm_h
                    new_w = int(round(sm_w))
                    new_h = int(round(sm_h))
                    x1 = ox2 - new_w
                    y2 = oy1 + new_h
                else:  # "br"
                    raw_w = max(min_size, nx - ox1)
                    raw_h = max(min_size, ny - oy1)
                    scale_w = raw_w / cur_w
                    scale_h = raw_h / cur_h
                    s = min(scale_w, scale_h)
                    s_raw = s
                    try:
                        m = int(getattr(self, "resize_speed_var", tk.IntVar(value=2)).get())
                        if s < 1.0:
                            s = max(0.01, 1.0 - (1.0 - s) * m)
                        else:
                            s = 1.0 + (s - 1.0) * m
                    except Exception:
                        m = 1
                    target_w = max(min_size, float(cur_w) * float(s))
                    alpha = 0.35
                    base_w = float(self._smooth_w if self._smooth_w else cur_w)
                    sm_w = base_w + (target_w - base_w) * alpha
                    sm_h = max(min_size, sm_w / aspect)
                    self._smooth_w, self._smooth_h = sm_w, sm_h
                    new_w = int(round(sm_w))
                    new_h = int(round(sm_h))
                    x2 = ox1 + new_w
                    y2 = oy1 + new_h

                # Giới hạn trong nền
                x1 = max(0, min(x1, max_w - min_size))
                y1 = max(0, min(y1, max_h - min_size))
                x2 = max(min_size, min(x2, max_w))
                y2 = max(min_size, min(y2, max_h))
                applied_ratio = True
                # Ép chặt đúng tỉ lệ khi khoá 16:9 hoặc 9:16 để tránh lệch do làm tròn/smoothing
                try:
                    locked_ratio = None
                    if bool(getattr(self, "force_916_var", tk.BooleanVar(value=False)).get()):
                        locked_ratio = 9.0 / 16.0
                    elif bool(getattr(self, "force_169_var", tk.BooleanVar(value=False)).get()):
                        locked_ratio = 16.0 / 9.0
                    if locked_ratio:
                        cur_w2 = max(min_size, int(round(x2 - x1)))
                        exact_h2 = max(min_size, int(round(cur_w2 / locked_ratio)))
                        if corner_key in ("tl", "tr"):
                            y1 = max(0, min(y2 - exact_h2, max_h - min_size))
                        else:  # bl, br
                            y2 = max(min_size, min(y1 + exact_h2, max_h))
                except Exception:
                    pass
                # Log nội bộ giữ tỷ lệ
                try:
                    self._append_log(f"[ratio] corner={corner_key} cur=({int(cur_w)}x{int(cur_h)}) "
                                     f"raw=({int(raw_w)}x{int(raw_h)}) s={s:.3f} new=({new_w}x{new_h}) [speed m={m} s_raw={s_raw:.3f}]")
                except Exception:
                    pass
            else:
                # Log khi không áp dụng ratio
                try:
                    self._append_log(f"[ratio_skip] keep_ratio={keep_ratio} aspect={self._resize_aspect}")
                except Exception:
                    pass

            # Log scale và clamp thông tin
            try:
                self._append_log(f"[scale] self._scale={self._scale:.6f} canvas_rect_to=({int(x1)},{int(y1)},{int(x2)},{int(y2)}) "
                                 f"bg_scaled=({max_w}x{max_h}) min_size={min_size}")
            except Exception:
                pass
            # Log áp dụng trước/sau theo world/canvas
            try:
                px_before = self._resize_orig_size if hasattr(self, "_resize_orig_size") else (orig[2] - orig[0], orig[3] - orig[1])
                pw0, ph0 = int(px_before[0]), int(px_before[1])
                ww0 = int(round(pw0 / max(self._scale, 1e-6)))
                wh0 = int(round(ph0 / max(self._scale, 1e-6)))
                pw1 = int(x2 - x1)
                ph1 = int(y2 - y1)
                ww1 = int(round(pw1 / max(self._scale, 1e-6)))
                wh1 = int(round(ph1 / max(self._scale, 1e-6)))
                self._append_log(f"[resize_apply] corner={corner_key} px_before=({pw0}x{ph0}) px_after=({pw1}x{ph1}) world_before=({ww0}x{wh0}) world_after=({ww1}x{wh1}) applied_ratio={applied_ratio}")
            except Exception:
                pass
            # Cập nhật rect & handles
            self.preview_canvas.coords(self._rect_id, x1, y1, x2, y2)
            self._update_handles()
            # Cập nhật size vars (chia scale)
            if ignore_scale:
                w = int(round((x2 - x1)))
                h = int(round((y2 - y1)))
            else:
                w = int(round((x2 - x1) / self._scale))
                h = int(round((y2 - y1) / self._scale))
            self.size_w_var.set(w)
            self.size_h_var.set(h)
            # Cập nhật pos (theo góc trên trái)
            if ignore_scale:
                self.pos_x_var.set(int(round(x1)))
                self.pos_y_var.set(int(round(y1)))
            else:
                self.pos_x_var.set(int(round(x1 / self._scale)))
                self.pos_y_var.set(int(round(y1 / self._scale)))
            # Debug log
            try:
                log_ui_action(self.logger, "EditVideoScreen._on_handle_motion", "resize_move", "EditVideoScreen", "DEBUG",
                              f"corner={corner_key}, mouse_from=({int(self._rect_drag_start[0])},{int(self._rect_drag_start[1])}) "
                              f"to=({event.x},{event.y}), rect_from=({int(orig[0])},{int(orig[1])},{int(orig[2])},{int(orig[3])}) "
                              f"to=({int(x1)},{int(y1)},{int(x2)},{int(y2)}), size=({w},{h}), keep_ratio={keep_ratio}, "
                              f"ratio_applied={applied_ratio}")
                self._append_log(f"[resize_move] corner={corner_key} mouse=({event.x},{event.y}) rect_to=({int(x1)},{int(y1)},{int(x2)},{int(y2)}) size=({w}x{h}) keep_ratio={keep_ratio} applied={applied_ratio}")
                # No-change lý do
                if ww0 == ww1 and wh0 == wh1:
                    reason = []
                    if not keep_ratio:
                        reason.append("keep_ratio=False")
                    if (x1 <= 0 or y1 <= 0 or x2 >= max_w or y2 >= max_h):
                        reason.append("hit_boundary")
                    if (x2 - x1) <= min_size or (y2 - y1) <= min_size:
                        reason.append("min_size")
                    self._append_log(f"[resize_nochange] reason={','.join(reason) if reason else 'unknown'}")
            except Exception:
                pass
        except Exception:
            pass

    def _on_handle_release(self, event, corner_key):
        try:
            _ = (event, corner_key)
        except Exception:
            pass

    def _update_handles(self):
        try:
            if not self._rect_id: return
            x1, y1, x2, y2 = self.preview_canvas.coords(self._rect_id)
            size_handle = 6
            coords = {
                "tl": (x1, y1),
                "tr": (x2, y1),
                "bl": (x1, y2),
                "br": (x2, y2)
            }
            for key, hid in self._handles.items():
                cx, cy = coords[key]
                self.preview_canvas.coords(hid, cx - size_handle, cy - size_handle, cx + size_handle, cy + size_handle)
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

        # Nếu người dùng bật bỏ qua scale trong preview, quy đổi về thông số thật trước khi gửi xuống service
        ignore_scale = bool(getattr(self, "ignore_scale_var", tk.BooleanVar(value=False)).get())
        if ignore_scale:
            px_x = int(self.pos_x_var.get())
            px_y = int(self.pos_y_var.get())
            px_w = int(self.size_w_var.get())
            px_h = int(self.size_h_var.get())
            world_x = int(round(px_x / max(self._scale, 1e-6)))
            world_y = int(round(px_y / max(self._scale, 1e-6)))
            world_w = int(round(px_w / max(self._scale, 1e-6)))
            world_h = int(round(px_h / max(self._scale, 1e-6)))
        else:
            world_x = int(self.pos_x_var.get())
            world_y = int(self.pos_y_var.get())
            world_w = int(self.size_w_var.get())
            world_h = int(self.size_h_var.get())

        config = {
            "position": {"x": world_x, "y": world_y},
            "size": {"width": world_w, "height": world_h},
            "keep_ratio": bool(self.keep_ratio_var.get()),
            "pad_color": [0,0,0],
            "bitrate": self.bitrate_var.get().strip() or "2500k",
            "preset": self.preset_var.get().strip() or "medium",
            "output_suffix": self.suffix_var.get(),
            "skip_existing": bool(self.skip_existing_var.get()),
            # Audio config
            "audio_source_path": self.audio_source_var.get().strip() if hasattr(self, "audio_source_var") else "",
            "audio_start_sec": float(self.audio_start_var.get()) if hasattr(self, "audio_start_var") else 0.0,
            "audio_loop": bool(self.audio_loop_var.get()) if hasattr(self, "audio_loop_var") else True,
            "audio_volume_percent": int(self.audio_volume_var.get()) if hasattr(self, "audio_volume_var") else 100,
            "audio_extract_when_video": bool(self.audio_extract_var.get()) if hasattr(self, "audio_extract_var") else True,
            "audio_library_dir": self.audio_library_var.get().strip() if hasattr(self, "audio_library_var") else "",
            "audio_delete_source_after_extract": True
        }
        
        if not hasattr(self, "_controller"):
            self._controller = EditController()
        
        def on_progress(progress: float, current: int, total: int, message: str):
            self._after(0, lambda: self._on_progress_ui(progress, current, total, message))
        
        def on_result(res: dict):
            msg = f"{'✓' if res.get('success') else '✗'} {os.path.basename(res.get('input',''))} -> {res.get('output') or res.get('error')}"
            self._after(0, lambda: self._append_log(msg))
        
        def on_complete():
            self._after(0, lambda: self._append_log("Hoàn tất batch!"))
        
        ok = self._controller.start_batch(
            background_path=bg, input_folder=inp, output_folder=out,
            config=config, threads=threads,
            progress_cb=on_progress, result_cb=on_result, complete_cb=on_complete
        )
        if not ok:
            self._append_log("✗ Không thể khởi chạy batch (kiểm tra cấu hình).")
        else:
            # Lưu lại paths đã dùng khi start
            try:
                cm2 = CookieManager()
                cm2.set_setting("edit_background_path", bg)
                cm2.set_setting("edit_input_folder", inp)
                cm2.set_setting("edit_output_folder", out)
                # Lưu audio config
                if hasattr(self, "audio_source_var"):
                    cm2.set_setting("edit_audio_path", self.audio_source_var.get().strip())
                if hasattr(self, "audio_start_var"):
                    cm2.set_setting("edit_audio_start", float(self.audio_start_var.get()))
                if hasattr(self, "audio_loop_var"):
                    cm2.set_setting("edit_audio_loop", bool(self.audio_loop_var.get()))
                if hasattr(self, "audio_volume_var"):
                    cm2.set_setting("edit_audio_volume", int(self.audio_volume_var.get()))
                if hasattr(self, "audio_library_var"):
                    cm2.set_setting("edit_audio_library_dir", self.audio_library_var.get().strip())
                if hasattr(self, "audio_extract_var"):
                    cm2.set_setting("edit_audio_extract", bool(self.audio_extract_var.get()))
            except Exception:
                pass
        # Ghi chú nếu bỏ qua scale
        try:
            if ignore_scale:
                self._append_log("[note] Bỏ qua preview scale đang bật: đang hiển thị theo pixel canvas, hệ thống đã quy đổi về kích thước thật khi xuất.")
        except Exception:
            pass
    
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

    def _clear_logs_ui(self):
        """Xóa toàn bộ file log và ghi lại kết quả vào khung log UI."""
        try:
            from utils.log_helper import clear_logs
            deleted = clear_logs("logs")
            self._append_log(f"Đã xóa {deleted} file log trong thư mục logs.")
        except Exception as e:
            self._append_log(f"Lỗi khi xóa logs: {e}")

