"""
Icon Button Component
Component button có icon và label text

Mục tiêu:
- Tạo button có icon và label text phía dưới
- Hỗ trợ hover effect
- Logging đầy đủ theo System Instruction
- Dễ dàng tái sử dụng

Input/Output:
- Input: Icon path/image, label text, click callback, hover callback (optional)
- Output: Tkinter button widget với icon và label
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import os
import logging
from utils.log_helper import get_logger
from gui.utils.ui_logger import log_ui_action, log_ui_event

# PIL (Pillow) is optional - if not available, will use text-only buttons
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class IconButton:
    """
    Icon Button Component với label text
    
    Attributes:
        parent: Parent container (Tkinter widget)
        icon_path: Đường dẫn đến icon file (optional)
        icon_image: Icon image object (optional)
        label_text: Text hiển thị dưới icon
        click_callback: Callback function khi click (optional)
        hover_callback: Callback function khi hover (optional)
        button_id: ID của button (theo FR-001: btnDownloadDouyin, btnEditVideo, etc.)
        logger: Logger instance (theo System Instruction)
        frame: Tkinter Frame chứa button và label
        button: Tkinter Button widget
        label: Tkinter Label widget
        default_bg: Background color mặc định
        hover_bg: Background color khi hover
    """
    
    def __init__(self, parent, icon_path: Optional[str] = None, 
                 icon_image: Optional[Image.Image] = None,
                 label_text: str = "", 
                 click_callback: Optional[Callable] = None,
                 hover_callback: Optional[Callable] = None,
                 button_id: str = "",
                 width: int = 100,
                 height: int = 100,
                 logger: Optional[logging.Logger] = None):
        """
        Khởi tạo IconButton
        
        Args:
            parent: Parent container (Tkinter widget)
            icon_path: Đường dẫn đến icon file (optional, ưu tiên icon_image)
            icon_image: Icon image object (optional)
            label_text: Text hiển thị dưới icon
            click_callback: Callback function khi click (optional)
            hover_callback: Callback function khi hover (optional)
            button_id: ID của button (theo FR-001)
            width: Chiều rộng button (default: 100)
            height: Chiều cao button (default: 100)
            logger: Logger instance (theo System Instruction)
        
        Flow:
        1. Thiết lập logger (theo System Instruction)
        2. Ghi log khởi tạo (theo System Instruction)
        3. Tạo frame container
        4. Load và resize icon
        5. Tạo button với icon
        6. Tạo label text
        7. Thiết lập event handlers (click, hover)
        8. Ghi log hoàn thành (theo System Instruction)
        
        Exceptions:
            Exception: Lỗi khi load icon hoặc tạo widget
        """
        function_name = "IconButton.__init__"
        self.logger = logger or get_logger('IconButton')
        self.button_id = button_id
        self.label_text = label_text
        self.click_callback = click_callback
        self.hover_callback = hover_callback
        
        # Log khởi tạo (theo System Instruction)
        log_ui_action(self.logger, function_name, "init", button_id, "INFO",
                     f"Creating icon button with label: {label_text}")
        
        try:
            # Tạo frame container
            self.frame = tk.Frame(parent)
            
            # Thiết lập màu sắc (theo FR-001: hỗ trợ hover effect)
            self.default_bg = self.frame.cget('bg')
            self.hover_bg = "#e0e0e0"  # Light gray khi hover
            
            # Load icon (PIL is optional)
            self.icon_photo = None
            if PIL_AVAILABLE:
                if icon_image:
                    # Sử dụng icon_image nếu có
                    try:
                        icon_img = icon_image.copy()
                        icon_img = icon_img.resize((width - 20, height - 40), Image.Resampling.LANCZOS)
                        self.icon_photo = ImageTk.PhotoImage(icon_img)
                    except Exception as e:
                        # Log warning theo System Instruction
                        from utils.log_helper import write_log
                        write_log('WARNING', function_name, f"Không thể resize icon image: {e}", self.logger)
                        self.icon_photo = None
                elif icon_path and os.path.exists(icon_path):
                    # Load từ file nếu có
                    try:
                        icon_img = Image.open(icon_path)
                        icon_img = icon_img.resize((width - 20, height - 40), Image.Resampling.LANCZOS)
                        self.icon_photo = ImageTk.PhotoImage(icon_img)
                    except Exception as e:
                        # Log warning theo System Instruction
                        from utils.log_helper import write_log
                        write_log('WARNING', function_name, f"Không thể load icon từ {icon_path}: {e}", self.logger)
                        # Sử dụng text icon nếu không load được
                        self.icon_photo = None
                else:
                    # Không có icon, sẽ sử dụng text
                    self.icon_photo = None
            else:
                # PIL không available, sử dụng text-only button
                self.icon_photo = None
                if logger:
                    logger.debug(f"[{function_name}] PIL (Pillow) not available, using text-only button")
            
            # Tạo button
            # Nếu có icon, sử dụng icon; nếu không, hiển thị text label (2 ký tự đầu hoặc "Icon")
            button_text = ""
            if not self.icon_photo:
                if label_text:
                    button_text = label_text[:2].upper()  # Hiển thị 2 ký tự đầu nếu không có icon
                else:
                    button_text = "Icon"  # Default text nếu không có label
            
            self.button = tk.Button(
                self.frame,
                image=self.icon_photo if self.icon_photo else None,
                text=button_text if not self.icon_photo else "",
                width=width // 10,  # Tkinter width is in character units
                height=height // 20,  # Tkinter height is in character units
                command=self._on_click,
                relief=tk.FLAT,
                bg=self.default_bg,
                cursor="hand2",
                font=("Arial", 14, "bold") if not self.icon_photo else ("Arial", 10)
            )
            
            # Bind hover events (theo FR-001: hỗ trợ hover effect)
            self.button.bind("<Enter>", self._on_enter)
            self.button.bind("<Leave>", self._on_leave)
            
            # Pack button
            self.button.pack(pady=(0, 5))
            
            # Tạo label text (theo FR-001: icon có label text bên dưới)
            if label_text:
                self.label = tk.Label(
                    self.frame,
                    text=label_text,
                    font=("Arial", 10),
                    bg=self.frame.cget('bg')
                )
                self.label.pack()
            else:
                self.label = None
            
            # Log hoàn thành (theo System Instruction)
            log_ui_action(self.logger, function_name, "init_complete", button_id, "INFO",
                         f"Icon button created successfully")
            
        except Exception as e:
            # Log lỗi đầy đủ (theo System Instruction)
            log_ui_action(self.logger, function_name, "init_error", button_id, "ERROR",
                         f"Error creating icon button: {e}")
            raise
    
    def _on_click(self):
        """
        Event handler khi click button (theo FR-001: ghi log hành vi click)
        
        Flow:
        1. Ghi log click action (theo System Instruction)
        2. Gọi click_callback nếu có
        3. Ghi log kết quả (theo System Instruction)
        """
        function_name = "IconButton._on_click"
        
        # Log click action (theo System Instruction - INFO level cho hành vi bình thường)
        log_ui_action(self.logger, function_name, "click", self.button_id, "INFO",
                     f"User clicked button: {self.button_id}")
        
        try:
            # Gọi callback nếu có
            if self.click_callback:
                self.click_callback()
                log_ui_action(self.logger, function_name, "click_callback_executed", 
                            self.button_id, "DEBUG", "Callback executed successfully")
        except Exception as e:
            # Log lỗi (theo System Instruction - ERROR level)
            log_ui_action(self.logger, function_name, "click_error", self.button_id, "ERROR",
                         f"Error in click callback: {e}")
    
    def _on_enter(self, event):
        """
        Event handler khi mouse enter button (theo FR-001: hover effect)
        
        Flow:
        1. Ghi log hover event (theo System Instruction - DEBUG level cho UI interactions)
        2. Thay đổi background color (hover effect)
        3. Gọi hover_callback nếu có
        """
        function_name = "IconButton._on_enter"
        
        # Log hover event (theo System Instruction - DEBUG level cho UI interactions)
        log_ui_event(self.logger, function_name, "hover_enter", {"component_id": self.button_id}, "DEBUG")
        
        try:
            # Hover effect: highlight icon (theo FR-001)
            self.button.config(bg=self.hover_bg, relief=tk.RAISED)
            if self.label:
                self.label.config(bg=self.hover_bg)
            
            # Gọi hover callback nếu có
            if self.hover_callback:
                self.hover_callback(True)
        except Exception as e:
            log_ui_action(self.logger, function_name, "hover_error", self.button_id, "ERROR",
                         f"Error in hover callback: {e}")
    
    def _on_leave(self, event):
        """
        Event handler khi mouse leave button (theo FR-001: hover effect)
        
        Flow:
        1. Ghi log hover event (theo System Instruction - DEBUG level)
        2. Khôi phục background color mặc định
        3. Gọi hover_callback nếu có
        """
        function_name = "IconButton._on_leave"
        
        # Log hover event (theo System Instruction - DEBUG level)
        log_ui_event(self.logger, function_name, "hover_leave", {"component_id": self.button_id}, "DEBUG")
        
        try:
            # Khôi phục màu sắc mặc định
            self.button.config(bg=self.default_bg, relief=tk.FLAT)
            if self.label:
                self.label.config(bg=self.default_bg)
            
            # Gọi hover callback nếu có
            if self.hover_callback:
                self.hover_callback(False)
        except Exception as e:
            log_ui_action(self.logger, function_name, "hover_error", self.button_id, "ERROR",
                         f"Error in hover callback: {e}")
    
    def pack(self, **kwargs):
        """Pack frame vào parent container"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid frame vào parent container"""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs):
        """Place frame vào parent container"""
        self.frame.place(**kwargs)
    
    def get_widget(self):
        """Lấy frame widget để customize thêm"""
        return self.frame
    
    def set_enabled(self, enabled: bool):
        """
        Bật/tắt button
        
        Args:
            enabled: True để bật, False để tắt
        """
        function_name = "IconButton.set_enabled"
        state = "enabled" if enabled else "disabled"
        
        log_ui_action(self.logger, function_name, "set_state", self.button_id, "DEBUG",
                     f"Setting button state to: {state}")
        
        self.button.config(state=tk.NORMAL if enabled else tk.DISABLED)

