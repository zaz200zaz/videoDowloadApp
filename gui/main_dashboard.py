"""
Main Dashboard Screen
Màn hình chính của ứng dụng (FR-001)

Mục tiêu:
- Hiển thị các chức năng chính của ứng dụng
- Truy cập nhanh vào các màn hình con
- Responsive layout (theo FR-001)
- Logging đầy đủ theo System Instruction

Components:
- btnDownloadDouyin: Download Douyin button
- lblDownloadDouyin: Download label
- btnEditVideo: Edit Video button
- lblEditVideo: Edit label
- mainBackground: Background view

Input/Output:
- Input: User interactions (click, hover, resize)
- Output: Navigation to child screens hoặc UI updates
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import logging
import os
from utils.log_helper import get_logger
from gui.utils.ui_logger import log_ui_action, log_ui_event
from gui.components.icon_button import IconButton
from gui.components.responsive_layout import ResponsiveGridLayout
from gui.controllers.navigation_controller import NavigationController
from gui.controllers.dashboard_controller import DashboardController


class MainDashboard:
    """
    Main Dashboard Screen (FR-001)
    
    Hiển thị các chức năng chính của ứng dụng để người dùng truy cập nhanh vào các màn hình con
    
    Attributes:
        root: Tkinter root window
        frame: Main frame container
        logger: Logger instance (theo System Instruction)
        navigation_controller: NavigationController instance
        dashboard_controller: DashboardController instance
        btnDownloadDouyin: Download Douyin button (FR-001)
        lblDownloadDouyin: Download label (FR-001)
        btnEditVideo: Edit Video button (FR-001)
        lblEditVideo: Edit label (FR-001)
        mainBackground: Background view (FR-001)
        layout_manager: ResponsiveGridLayout instance
    """
    
    def __init__(self, root: tk.Tk, navigation_controller: Optional[NavigationController] = None,
                 logger: Optional[logging.Logger] = None, cookie_manager=None):
        """
        Khởi tạo Main Dashboard (theo FR-001)
        
        Args:
            root: Tkinter root window
            navigation_controller: NavigationController instance (optional)
            logger: Logger instance (theo System Instruction)
        
        Flow:
        1. Thiết lập logger (theo System Instruction)
        2. Ghi log khởi tạo (theo System Instruction)
        3. Tạo main frame
        4. Thiết lập navigation controller
        5. Thiết lập dashboard controller
        6. Tạo UI components (theo FR-001)
        7. Thiết lập responsive layout (theo FR-001)
        8. Thiết lập event handlers
        9. Ghi log hoàn thành (theo System Instruction)
        
        Exceptions:
            Exception: Lỗi khi khởi tạo UI components
        """
        function_name = "MainDashboard.__init__"
        self.logger = logger or get_logger('MainDashboard')
        self.root = root
        
        # Log khởi tạo (theo System Instruction)
        log_ui_action(self.logger, function_name, "init", "MainDashboard", "INFO",
                     "Initializing Main Dashboard")
        
        try:
            # Tạo main frame (theo FR-001: mainBackground)
            self.frame = tk.Frame(root, bg="#f0f0f0", name="mainBackground")
            self.frame.pack(fill=tk.BOTH, expand=True)
            
            # Thiết lập navigation controller
            # Nếu không có navigation_controller, tạo mới với home screen là MainDashboard (theo iOS-style navigation)
            if navigation_controller is None:
                self.navigation_controller = NavigationController(root, self.logger, home_screen_name="MainDashboard")
            else:
                self.navigation_controller = navigation_controller
            
            # Đăng ký MainDashboard vào navigation controller (theo iOS-style navigation)
            # MainDashboard là home screen (root của navigation stack)
            self.navigation_controller.screens["MainDashboard"] = self
            
            # Thiết lập dashboard controller
            # Lưu cookie_manager để truyền vào MainWindow khi mở (theo FR-001: giữ nguyên logic)
            self.cookie_manager = cookie_manager
            self.dashboard_controller = DashboardController(
                self.navigation_controller, 
                self.logger
            )
            
            # Tạo responsive layout manager (theo FR-001: responsive layout)
            self.layout_manager = ResponsiveGridLayout(
                self.frame, 
                columns=2, 
                spacing=40,
                padding=40,
                logger=self.logger
            )
            
            # Tạo title label
            title_label = tk.Label(
                self.frame,
                text="Douyin Video Downloader",
                font=("Arial", 20, "bold"),
                bg=self.frame.cget('bg')
            )
            title_label.pack(pady=20)
            
            # Tạo container cho buttons
            buttons_container = tk.Frame(self.frame, bg=self.frame.cget('bg'))
            buttons_container.pack(pady=40)
            
            # Tạo btnDownloadDouyin và lblDownloadDouyin (theo FR-001)
            self.btnDownloadDouyin = IconButton(
                buttons_container,
                label_text="Download Video Douyin",  # (theo FR-001: lblDownloadDouyin)
                click_callback=self.on_download_click,
                hover_callback=self.on_button_hover,
                button_id="btnDownloadDouyin",  # (theo FR-001)
                width=150,
                height=150,
                logger=self.logger
            )
            self.btnDownloadDouyin.grid(row=0, column=0, padx=40, pady=20)
            
            # Tạo btnEditVideo và lblEditVideo (theo FR-001)
            self.btnEditVideo = IconButton(
                buttons_container,
                label_text="Edit Video",  # (theo FR-001: lblEditVideo)
                click_callback=self.on_edit_click,
                hover_callback=self.on_button_hover,
                button_id="btnEditVideo",  # (theo FR-001)
                width=150,
                height=150,
                logger=self.logger
            )
            self.btnEditVideo.grid(row=0, column=1, padx=40, pady=20)
            
            # Bind window resize event (theo FR-001: responsive layout)
            self.root.bind("<Configure>", self.on_window_resize)
            
            # Log hoàn thành (theo System Instruction)
            log_ui_action(self.logger, function_name, "init_complete", "MainDashboard", "INFO",
                         "Main Dashboard initialized successfully")
            
        except Exception as e:
            # Log error đầy đủ (theo System Instruction)
            log_ui_action(self.logger, function_name, "init_error", "MainDashboard", "ERROR",
                         f"Error initializing Main Dashboard: {e}")
            raise
    
    def on_download_click(self):
        """
        Event handler khi click btnDownloadDouyin (theo FR-001: click -> mở MainWindow cũ, giữ nguyên logic)
        
        Flow:
        1. Ghi log click action (theo System Instruction)
        2. Gọi dashboard controller để xử lý (mở MainWindow cũ - giữ nguyên logic, layout, chức năng)
        3. Ghi log kết quả (theo System Instruction)
        
        Note:
            - Mở trực tiếp màn hình MainWindow cũ (DownloadDouyinScreen) hiện có
            - Giữ nguyên tất cả logic, layout và chức năng
            - Chỉ thêm log hành vi theo System Instruction
            - Không thay đổi module MainWindow
        """
        function_name = "MainDashboard.on_download_click"
        
        # Log click action (theo System Instruction - INFO level cho hành vi bình thường)
        log_ui_action(self.logger, function_name, "click", "btnDownloadDouyin", "INFO",
                     "User clicked Download Douyin button - opening existing MainWindow")
        
        try:
            # Gọi dashboard controller để xử lý (theo FR-001: mở MainWindow cũ - giữ nguyên logic)
            self.dashboard_controller.handle_download_click(
                from_screen="MainDashboard",
                cookie_manager=self.cookie_manager
            )
            
            # Log success theo System Instruction
            from utils.log_helper import write_log
            write_log('INFO', function_name, "Download button click handled successfully", self.logger)
            write_log('INFO', function_name, "Existing MainWindow opened with all logic, layout, and functions preserved", self.logger)
            
        except Exception as e:
            # Log error đầy đủ (theo System Instruction - ERROR level)
            log_ui_action(self.logger, function_name, "click_error", "btnDownloadDouyin", 
                         "ERROR", f"Error handling download click: {e}")
    
    def on_edit_click(self):
        """
        Event handler khi click btnEditVideo (theo FR-001: click -> mở EditVideoScreen, ghi log)
        
        Flow:
        1. Ghi log click action (theo System Instruction)
        2. Gọi dashboard controller để xử lý
        3. Ghi log kết quả (theo System Instruction)
        """
        function_name = "MainDashboard.on_edit_click"
        
        # Log click action (theo System Instruction - INFO level cho hành vi bình thường)
        log_ui_action(self.logger, function_name, "click", "btnEditVideo", "INFO",
                     "User clicked Edit Video button")
        
        try:
            # Gọi dashboard controller để xử lý (theo FR-001: mở EditVideoScreen)
            self.dashboard_controller.handle_edit_click(from_screen="MainDashboard")
            
            # Log success theo System Instruction
            from utils.log_helper import write_log
            write_log('INFO', function_name, "Edit button click handled successfully", self.logger)
            
        except Exception as e:
            # Log error đầy đủ (theo System Instruction - ERROR level)
            log_ui_action(self.logger, function_name, "click_error", "btnEditVideo", 
                         "ERROR", f"Error handling edit click: {e}")
    
    def on_button_hover(self, is_hovering: bool):
        """
        Event handler khi hover button (theo FR-001: hover effect, ghi log)
        
        Args:
            is_hovering: True nếu đang hover, False nếu không
        
        Flow:
        1. Ghi log hover event (theo System Instruction - DEBUG level cho UI interactions)
        2. Cập nhật UI nếu cần
        """
        function_name = "MainDashboard.on_button_hover"
        action = "hover_enter" if is_hovering else "hover_leave"
        
        # Log hover event (theo System Instruction - DEBUG level cho UI interactions)
        log_ui_event(self.logger, function_name, action, {"is_hovering": is_hovering}, "DEBUG")
    
    def on_window_resize(self, event):
        """
        Event handler khi resize window (theo FR-001: responsive layout)
        
        Args:
            event: Resize event
        
        Flow:
        1. Kiểm tra xem có phải main window resize không
        2. Throttle resize events để tránh log spam (theo System Instruction - tối ưu I/O)
        3. Ghi log resize event (theo System Instruction - DEBUG level)
        4. Cập nhật layout nếu cần (theo FR-001: responsive layout)
        """
        function_name = "MainDashboard.on_window_resize"
        
        # Chỉ xử lý khi là main window resize (không phải child widgets)
        if event.widget != self.root:
            return
        
        # Throttle resize events để tránh log spam (theo System Instruction - tối ưu I/O operations)
        # resizeイベントが大量に発生するため、最後のresizeイベントから0.5秒以上経過した場合のみログを記録
        import time
        if not hasattr(self, '_last_resize_log_time'):
            self._last_resize_log_time = 0
        
        current_time = time.time()
        if current_time - self._last_resize_log_time < 0.5:  # 0.5秒以内のresizeイベントはスキップ
            return
        
        self._last_resize_log_time = current_time
        
        # Log resize event (theo System Instruction - DEBUG level cho UI interactions)
        log_ui_event(self.logger, function_name, "window_resize", 
                    {"width": event.width, "height": event.height}, "DEBUG")
        
        # Cập nhật layout nếu cần (theo FR-001: responsive layout)
        # Layout manager sẽ tự động xử lý responsive layout
    
    def get_frame(self):
        """Lấy main frame để pack/grid vào parent container"""
        return self.frame
    
    def show(self):
        """Hiển thị Main Dashboard"""
        function_name = "MainDashboard.show"
        log_ui_action(self.logger, function_name, "show", "MainDashboard", "INFO",
                     "Showing Main Dashboard")
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Ẩn Main Dashboard"""
        function_name = "MainDashboard.hide"
        log_ui_action(self.logger, function_name, "hide", "MainDashboard", "INFO",
                     "Hiding Main Dashboard")
        self.frame.pack_forget()

