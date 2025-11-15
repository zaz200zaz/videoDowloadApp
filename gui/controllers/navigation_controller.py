"""
Navigation Controller
Controller quản lý navigation giữa các screens

Mục tiêu:
- Quản lý screen navigation
- Multi-screen support (theo FR-001)
- Logging đầy đủ theo System Instruction

Input/Output:
- Input: Screen name, action (open, close, switch)
- Output: Screen instance hoặc None
"""

import tkinter as tk
from typing import Dict, Optional, Type, List
import logging
from utils.log_helper import get_logger, write_log
from gui.utils.ui_logger import log_screen_navigation


class NavigationController:
    """
    Navigation Controller cho screen management với iOS-style navigation stack
    
    Mục tiêu:
    - Quản lý screen navigation với navigation stack (iOS-style)
    - Hỗ trợ back navigation (quay lại màn hình trước)
    - Quản lý screen instances (không tạo lại hay ghi đè màn hình cũ)
    - Logging đầy đủ theo System Instruction
    
    Attributes:
        root: Tkinter root window
        current_screen: Tên screen hiện tại
        navigation_stack: List lưu trữ navigation history (iOS-style stack) - [screen_name1, screen_name2, ...]
        screens: Dict lưu trữ screen instances {screen_name: screen_instance}
        screen_classes: Dict lưu trữ screen classes {screen_name: screen_class}
        home_screen_name: Tên home screen (root của navigation stack) - mặc định "MainDashboard"
        logger: Logger instance (theo System Instruction)
    """
    
    def __init__(self, root: tk.Tk, logger: Optional[logging.Logger] = None, home_screen_name: str = "MainDashboard"):
        """
        Khởi tạo NavigationController với iOS-style navigation stack
        
        Args:
            root: Tkinter root window
            logger: Logger instance (theo System Instruction)
            home_screen_name: Tên home screen (root của navigation stack) - mặc định "MainDashboard"
        
        Flow:
        1. Thiết lập logger (theo System Instruction)
        2. Ghi log khởi tạo (theo System Instruction)
        3. Khởi tạo screen registry
        4. Khởi tạo navigation stack với home screen (theo iOS-style navigation)
        """
        function_name = "NavigationController.__init__"
        self.logger = logger or get_logger('NavigationController')
        self.root = root
        self.current_screen = None
        # Navigation stack để quản lý navigation history (iOS-style)
        # Stack chứa tên các screens theo thứ tự: [home_screen, screen1, screen2, ...]
        # Khi back, pop stack để quay lại screen trước
        self.navigation_stack: List[str] = []
        self.home_screen_name = home_screen_name
        
        # Lưu trữ screen instances - có thể là Toplevel hoặc MainWindow instance
        # (theo FR-001: MainWindow là class, không phải Toplevel)
        # Không tạo lại hay ghi đè màn hình cũ, chỉ liên kết điều hướng tới màn hình đã tồn tại
        self.screens: Dict[str, any] = {}  # Changed from Dict[str, tk.Toplevel] to support MainWindow
        self.screen_classes: Dict[str, Type] = {}
        
        # Khởi tạo navigation stack với home screen (theo iOS-style navigation)
        # Home screen là root của navigation stack
        self.navigation_stack.append(home_screen_name)
        self.current_screen = home_screen_name
        
        # Log initialization theo System Instruction
        write_log('INFO', function_name, f"NavigationController initialized with home screen: {home_screen_name}", self.logger)
        write_log('DEBUG', function_name, f"Navigation stack initialized: {self.navigation_stack}", self.logger)
    
    def register_screen(self, screen_name: str, screen_class: Type):
        """
        Đăng ký screen class (theo FR-001: hệ thống dễ dàng mở rộng)
        
        Args:
            screen_name: Tên screen
            screen_class: Screen class
        
        Flow:
        1. Ghi log registration (theo System Instruction)
        2. Lưu screen class vào registry
        """
        function_name = "NavigationController.register_screen"
        
        self.screen_classes[screen_name] = screen_class
        # Log registration theo System Instruction
        write_log('INFO', function_name, f"Registered screen: {screen_name}", self.logger)
    
    def open_screen(self, screen_name: str, from_screen: Optional[str] = None,
                   **kwargs) -> Optional:
        """
        Mở screen (theo FR-001: click icon -> mở screen, ghi log hành vi)
        
        Args:
            screen_name: Tên screen cần mở
            from_screen: Tên screen hiện tại (optional, để log navigation)
            **kwargs: Parameters truyền vào screen constructor
        
        Returns:
            Screen instance hoặc None nếu lỗi
        
        Flow:
        1. Ghi log navigation (theo System Instruction)
        2. Kiểm tra screen đã tồn tại chưa
        3. Nếu chưa, tạo screen instance mới
        4. Hiển thị screen
        5. Ghi log kết quả (theo System Instruction)
        
        Exceptions:
            Exception: Lỗi khi mở screen
        """
        function_name = "NavigationController.open_screen"
        from_screen_name = from_screen or self.current_screen or "MainDashboard"
        
        # Log navigation start (theo System Instruction)
        log_screen_navigation(self.logger, function_name, from_screen_name, 
                            screen_name, success=True)
        
        try:
            # Kiểm tra screen đã tồn tại chưa (theo FR-001: multi-screen support)
            if screen_name in self.screens:
                screen = self.screens[screen_name]
                # Đưa screen lên front (theo FR-001: Main Dashboard luôn hiển thị)
                if isinstance(screen, tk.Toplevel):
                    screen.lift()
                    screen.focus_force()
                elif hasattr(screen, 'root'):
                    # MainWindowのような場合は、rootウィンドウを前面に
                    # (theo FR-001: Main Dashboard luôn hiển thị)
                    root_window = screen.root
                    if isinstance(root_window, tk.Toplevel):
                        root_window.lift()
                        root_window.focus_force()
                    elif isinstance(root_window, tk.Tk):
                        root_window.lift()
                        root_window.focus_force()
                elif hasattr(screen, '_top_level') and screen._top_level:
                    # MainWindowがToplevelウィンドウで開かれた場合
                    screen._top_level.lift()
                    screen._top_level.focus_force()
                elif hasattr(screen, 'window') and isinstance(screen.window, tk.Toplevel):
                    # EditVideoScreenやDownloadDouyinScreenの場合
                    screen.window.lift()
                    screen.window.focus_force()
                # Log screen already exists theo System Instruction
                write_log('INFO', function_name, f"Screen {screen_name} already exists, bringing to front", self.logger)
                return screen
            
            # Kiểm tra screen class đã đăng ký chưa
            if screen_name not in self.screen_classes:
                error_msg = f"Screen class {screen_name} not registered"
                # Log warning theo System Instruction
                write_log('WARNING', function_name, error_msg, self.logger)
                log_screen_navigation(self.logger, function_name, from_screen_name, 
                                    screen_name, success=False, error=error_msg)
                return None
            
            # Tạo screen instance mới
            screen_class = self.screen_classes[screen_name]
            
            # MainWindowの場合は特別な処理（既存のrootウィンドウを使用）
            # MainWindowを検出する際は、クラス名を使用（theo System Instruction - code quality）
            is_mainwindow = (screen_name == "MainWindow" or 
                           screen_class.__name__ == "MainWindow" or
                           "MainWindow" in screen_class.__name__)
            
            if is_mainwindow:
                # MainWindowの場合、新しいToplevelウィンドウを作成
                # (theo FR-001: mở trực tiếp màn hình cũ, giữ nguyên logic)
                top_level = tk.Toplevel(self.root)
                top_level.title("Douyin Video Downloader - Download Screen")
                top_level.geometry("800x700")
                
                # MainWindowインスタンスを作成（既存のロジックを保持）
                # Lưu cả top_level và screen instance để close_screenで使用
                screen = screen_class(top_level, logger=self.logger, **kwargs)
                # Lưu top_level reference để destroy時に使用（theo System Instruction - logging đầy đủ）
                screen._top_level = top_level  # Store reference to Toplevel window
            else:
                # その他の画面は通常通り
                screen = screen_class(self.root, logger=self.logger, **kwargs)
            
            # Lưu screen instance (theo FR-001: multi-screen support)
            # Không tạo lại hay ghi đè màn hình cũ, chỉ liên kết điều hướng tới màn hình đã tồn tại
            self.screens[screen_name] = screen
            
            # Cập nhật navigation stack (iOS-style)
            # Nếu screen chưa có trong stack, thêm vào stack (push)
            # Nếu screen đã có trong stack, không thêm lại (tránh duplicate)
            if screen_name not in self.navigation_stack:
                self.navigation_stack.append(screen_name)
                write_log('DEBUG', function_name, f"Screen {screen_name} added to navigation stack", self.logger)
            else:
                write_log('DEBUG', function_name, f"Screen {screen_name} already in navigation stack, bringing to front", self.logger)
            
            # Cập nhật current screen
            self.current_screen = screen_name
            
            # Log success (theo System Instruction)
            write_log('INFO', function_name, f"Screen {screen_name} opened successfully", self.logger)
            write_log('DEBUG', function_name, f"Navigation stack: {self.navigation_stack}", self.logger)
            log_screen_navigation(self.logger, function_name, from_screen_name, 
                                screen_name, success=True)
            
            return screen
            
        except Exception as e:
            # Log error đầy đủ (theo System Instruction)
            error_msg = str(e)
            write_log('ERROR', function_name, f"Error opening screen {screen_name}: {e}", 
                     self.logger, exc_info=True)
            log_screen_navigation(self.logger, function_name, from_screen_name, 
                                screen_name, success=False, error=error_msg)
            return None
    
    def close_screen(self, screen_name: str):
        """
        Đóng screen (theo System Instruction - logging đầy đủ)
        
        Args:
            screen_name: Tên screen cần đóng
        
        Flow:
        1. Ghi log close action (theo System Instruction)
        2. Destroy screen (MainWindowの場合は特別な処理)
        3. Xóa khỏi registry
        4. Ghi log kết quả (theo System Instruction)
        """
        function_name = "NavigationController.close_screen"
        
        # Log close action (theo System Instruction)
        write_log('INFO', function_name, f"Closing screen: {screen_name}", self.logger)
        
        if screen_name in self.screens:
            try:
                screen = self.screens[screen_name]
                
                # MainWindowの場合は特別な処理（theo FR-001: giữ nguyên logic）
                # MainWindowは_root属性または_top_level属性を持つ
                if hasattr(screen, '_top_level') and screen._top_level:
                    # MainWindowがToplevelウィンドウで開かれた場合
                    top_level = screen._top_level
                    top_level.destroy()
                    write_log('DEBUG', function_name, "MainWindow Toplevel window destroyed", self.logger)
                elif isinstance(screen, tk.Toplevel):
                    # Toplevelウィンドウの場合
                    screen.destroy()
                    write_log('DEBUG', function_name, "Toplevel window destroyed", self.logger)
                elif hasattr(screen, 'root') and isinstance(screen.root, tk.Toplevel):
                    # MainWindowインスタンスで、rootがToplevelの場合
                    screen.root.destroy()
                    write_log('DEBUG', function_name, "MainWindow root (Toplevel) destroyed", self.logger)
                elif hasattr(screen, 'window') and isinstance(screen.window, tk.Toplevel):
                    # EditVideoScreenやDownloadDouyinScreenの場合
                    screen.window.destroy()
                    write_log('DEBUG', function_name, "Screen window (Toplevel) destroyed", self.logger)
                else:
                    # その他の場合、destroy()を試みる
                    if hasattr(screen, 'destroy'):
                        screen.destroy()
                        write_log('DEBUG', function_name, "Screen destroyed using destroy() method", self.logger)
                    else:
                        write_log('WARNING', function_name, f"Cannot destroy screen {screen_name}: no destroy method found", self.logger)
                
                # Xóa khỏi registry
                del self.screens[screen_name]
                
                # Xóa khỏi navigation stack (iOS-style)
                if screen_name in self.navigation_stack:
                    self.navigation_stack.remove(screen_name)
                    write_log('DEBUG', function_name, f"Screen {screen_name} removed from navigation stack", self.logger)
                
                # Reset current screen nếu đang là screen này
                if self.current_screen == screen_name:
                    # Nếu còn screens trong stack, set current screen là screen cuối cùng
                    if self.navigation_stack:
                        self.current_screen = self.navigation_stack[-1]
                        write_log('DEBUG', function_name, f"Current screen set to: {self.current_screen}", self.logger)
                    else:
                        # Nếu stack rỗng, set về home screen
                        self.current_screen = self.home_screen_name
                        self.navigation_stack.append(self.home_screen_name)
                        write_log('DEBUG', function_name, f"Navigation stack empty, reset to home screen: {self.home_screen_name}", self.logger)
                
                # Log success (theo System Instruction)
                write_log('INFO', function_name, f"Screen {screen_name} closed successfully", self.logger)
                write_log('DEBUG', function_name, f"Navigation stack: {self.navigation_stack}", self.logger)
                
            except Exception as e:
                # Log error đầy đủ (theo System Instruction - ERROR level)
                write_log('ERROR', function_name, f"Error closing screen {screen_name}: {e}", 
                         self.logger, exc_info=True)
        else:
            # Screen not found in registry
            write_log('WARNING', function_name, f"Screen {screen_name} not found in registry", self.logger)
    
    def go_back(self) -> bool:
        """
        Quay lại màn hình trước đó (iOS-style back navigation)
        
        Mục đích:
        - Pop navigation stack để quay lại screen trước đó
        - Ẩn current screen và hiển thị previous screen
        - Không destroy screen, chỉ hide/show để giữ nguyên state
        
        Returns:
            True nếu back thành công, False nếu không thể back (đã ở home screen)
        
        Flow:
        1. Kiểm tra có thể back không (stack phải có > 1 screen)
        2. Pop current screen khỏi stack
        3. Ẩn current screen
        4. Hiển thị previous screen (screen cuối cùng trong stack)
        5. Ghi log navigation (theo System Instruction)
        
        Exceptions:
            Exception: Lỗi khi back navigation
        """
        function_name = "NavigationController.go_back"
        
        # Kiểm tra có thể back không (theo iOS-style: không back khỏi home screen)
        if len(self.navigation_stack) <= 1:
            write_log('WARNING', function_name, "Cannot go back: already at home screen", self.logger)
            return False
        
        try:
            # Pop current screen khỏi stack (theo iOS-style navigation)
            current = self.navigation_stack.pop()
            previous = self.navigation_stack[-1] if self.navigation_stack else self.home_screen_name
            
            write_log('INFO', function_name, f"Navigating back from {current} to {previous}", self.logger)
            
            # Ẩn current screen (không destroy để giữ nguyên state)
            if current in self.screens:
                screen = self.screens[current]
                # Hide screen (không destroy)
                if isinstance(screen, tk.Toplevel):
                    screen.withdraw()  # Hide window thay vì destroy
                elif hasattr(screen, '_top_level') and screen._top_level:
                    screen._top_level.withdraw()
                elif hasattr(screen, 'window') and isinstance(screen.window, tk.Toplevel):
                    screen.window.withdraw()
                elif hasattr(screen, 'hide'):
                    screen.hide()  # Sử dụng hide method nếu có
                write_log('DEBUG', function_name, f"Hidden screen: {current}", self.logger)
            
            # Hiển thị previous screen
            if previous in self.screens:
                screen = self.screens[previous]
                # Show screen
                if isinstance(screen, tk.Toplevel):
                    screen.deiconify()  # Show window
                    screen.lift()
                    screen.focus_force()
                elif hasattr(screen, '_top_level') and screen._top_level:
                    screen._top_level.deiconify()
                    screen._top_level.lift()
                    screen._top_level.focus_force()
                elif hasattr(screen, 'window') and isinstance(screen.window, tk.Toplevel):
                    screen.window.deiconify()
                    screen.window.lift()
                    screen.window.focus_force()
                elif hasattr(screen, 'show'):
                    screen.show()  # Sử dụng show method nếu có
                write_log('DEBUG', function_name, f"Shown screen: {previous}", self.logger)
            
            # Cập nhật current screen
            self.current_screen = previous
            
            # Log navigation (theo System Instruction)
            write_log('INFO', function_name, f"Successfully navigated back to {previous}", self.logger)
            write_log('DEBUG', function_name, f"Navigation stack: {self.navigation_stack}", self.logger)
            log_screen_navigation(self.logger, function_name, current, previous, success=True, action="back")
            
            return True
            
        except Exception as e:
            # Log error đầy đủ (theo System Instruction)
            write_log('ERROR', function_name, f"Error during back navigation: {e}", self.logger, exc_info=True)
            return False
    
    def can_go_back(self) -> bool:
        """
        Kiểm tra có thể back không (theo iOS-style: không back khỏi home screen)
        
        Returns:
            True nếu có thể back, False nếu không thể (đã ở home screen)
        """
        function_name = "NavigationController.can_go_back"
        can_back = len(self.navigation_stack) > 1
        write_log('DEBUG', function_name, f"Can go back: {can_back} (stack size: {len(self.navigation_stack)})", self.logger)
        return can_back
    
    def get_navigation_stack(self) -> List[str]:
        """
        Lấy navigation stack (theo System Instruction - logging đầy đủ)
        
        Returns:
            List tên các screens trong navigation stack
        """
        function_name = "NavigationController.get_navigation_stack"
        write_log('DEBUG', function_name, f"Navigation stack: {self.navigation_stack}", self.logger)
        return self.navigation_stack.copy()

