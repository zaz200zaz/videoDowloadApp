"""
Dashboard Controller
Controller xử lý Main Dashboard business logic

Mục tiêu:
- Xử lý Main Dashboard business logic
- Coordinate với navigation controller
- Logging đầy đủ theo System Instruction

Input/Output:
- Input: User actions (click, hover, resize)
- Output: Navigation commands hoặc state changes
"""

import tkinter as tk
from typing import Optional, Callable
import logging
from utils.log_helper import get_logger, write_log
from gui.utils.ui_logger import log_ui_action
from gui.controllers.navigation_controller import NavigationController


class DashboardController:
    """
    Dashboard Controller cho Main Dashboard
    
    Attributes:
        navigation_controller: NavigationController instance
        logger: Logger instance (theo System Instruction)
    """
    
    def __init__(self, navigation_controller: NavigationController, 
                 logger: Optional[logging.Logger] = None):
        """
        Khởi tạo DashboardController
        
        Args:
            navigation_controller: NavigationController instance
            logger: Logger instance (theo System Instruction)
        
        Flow:
        1. Thiết lập logger (theo System Instruction)
        2. Ghi log khởi tạo (theo System Instruction)
        3. Lưu navigation controller
        """
        function_name = "DashboardController.__init__"
        self.logger = logger or get_logger('DashboardController')
        self.navigation_controller = navigation_controller
        
        # Log initialization theo System Instruction
        write_log('INFO', function_name, "DashboardController initialized", self.logger)
    
    def handle_download_click(self, from_screen: str = "MainDashboard", cookie_manager=None):
        """
        Xử lý click btnDownloadDouyin (theo FR-001: click -> mở MainWindow cũ, giữ nguyên logic)
        
        Args:
            from_screen: Tên screen hiện tại (default: "MainDashboard")
            cookie_manager: CookieManager instance (cần cho MainWindow)
        
        Flow:
        1. Ghi log click action (theo System Instruction)
        2. Mở MainWindow cũ qua navigation controller (theo FR-001: giữ nguyên logic, layout, chức năng)
        3. Ghi log kết quả (theo System Instruction)
        
        Note:
            - Mở trực tiếp màn hình DownloadDouyinScreen cũ (MainWindow) hiện có
            - Giữ nguyên tất cả logic, layout và chức năng
            - Chỉ thêm log hành vi theo System Instruction
            - Không thay đổi module MainWindow
        """
        function_name = "DashboardController.handle_download_click"
        
        # Log click action (theo System Instruction - INFO level cho hành vi bình thường)
        log_ui_action(self.logger, function_name, "click", "btnDownloadDouyin", "INFO",
                     "User clicked Download Douyin button - opening existing MainWindow")
        
        try:
            # Mở MainWindow cũ (theo FR-001: mở trực tiếp màn hình cũ, giữ nguyên logic)
            # MainWindowは既存のui/main_window.pyから（変更しない）
            if cookie_manager is None:
                error_msg = "CookieManager is required to open MainWindow"
                write_log('ERROR', function_name, error_msg, self.logger)
                log_ui_action(self.logger, function_name, "click_error", "btnDownloadDouyin", 
                             "ERROR", error_msg)
                return
            
            # MainWindowを開く（既存のロジック、レイアウト、機能を保持）
            # Truyền navigation_controller để hỗ trợ back navigation (iOS-style)
            screen = self.navigation_controller.open_screen(
                "MainWindow", 
                from_screen=from_screen,
                cookie_manager=cookie_manager,
                navigation_controller=self.navigation_controller
            )
            
            if screen:
                write_log('INFO', function_name, "MainWindow (DownloadDouyinScreen) opened successfully", self.logger)
                write_log('INFO', function_name, "Existing logic, layout, and functions are preserved", self.logger)
            else:
                write_log('WARNING', function_name, "Failed to open MainWindow (DownloadDouyinScreen)", self.logger)
                
        except Exception as e:
            # Log error đầy đủ (theo System Instruction - ERROR level)
            log_ui_action(self.logger, function_name, "click_error", "btnDownloadDouyin", 
                         "ERROR", f"Error opening MainWindow (DownloadDouyinScreen): {e}")
    
    def handle_edit_click(self, from_screen: str = "MainDashboard"):
        """
        Xử lý click btnEditVideo (theo FR-001: click -> mở EditVideoScreen, ghi log)
        
        Args:
            from_screen: Tên screen hiện tại (default: "MainDashboard")
        
        Flow:
        1. Ghi log click action (theo System Instruction)
        2. Mở EditVideoScreen qua navigation controller
        3. Ghi log kết quả (theo System Instruction)
        """
        function_name = "DashboardController.handle_edit_click"
        
        # Log click action (theo System Instruction - INFO level cho hành vi bình thường)
        log_ui_action(self.logger, function_name, "click", "btnEditVideo", "INFO",
                     "User clicked Edit Video button")
        
        try:
            # Mở EditVideoScreen (theo FR-001)
            # Truyền navigation_controller để hỗ trợ back navigation (iOS-style)
            screen = self.navigation_controller.open_screen(
                "EditVideoScreen", 
                from_screen=from_screen,
                navigation_controller=self.navigation_controller
            )
            
            if screen:
                write_log('INFO', function_name, "EditVideoScreen opened successfully", self.logger)
            else:
                write_log('WARNING', function_name, "Failed to open EditVideoScreen", self.logger)
                
        except Exception as e:
            # Log error đầy đủ (theo System Instruction - ERROR level)
            log_ui_action(self.logger, function_name, "click_error", "btnEditVideo", 
                         "ERROR", f"Error opening EditVideoScreen: {e}")

