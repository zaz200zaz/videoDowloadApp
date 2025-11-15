"""
Cookie Controller
Quản lý các thao tác liên quan đến cookie từ UI layer

Mục tiêu:
- Điều phối giữa UI và CookieManager
- Xử lý cookie từ file (Netscape format, plain text)
- Validate và lưu cookie

Input/Output:
- Input: Cookie string, file path
- Output: Success status, messages, cookie string
"""

import logging
import os
from typing import Optional
from models.cookie_manager import CookieManager
from utils.log_helper import write_log, get_logger


class CookieController:
    """
    Cookie管理のコントローラー
    
    Chức năng chính:
    - Lưu cookie từ UI
    - Đọc cookie từ file
    - Validate cookie
    - Xóa cookie
    """
    
    def __init__(self, cookie_manager: CookieManager):
        """
        Khởi tạo CookieController
        
        Args:
            cookie_manager: CookieManager instance
            
        Flow:
        1. Lưu reference đến CookieManager
        2. Thiết lập logger
        """
        function_name = "CookieController.__init__"
        self.cookie_manager = cookie_manager
        self.logger = get_logger('CookieController')
        
        write_log('INFO', function_name, "CookieController đã được khởi tạo", self.logger)
    
    def save_cookie(self, cookie: str) -> tuple[bool, str]:
        """
        Lưu cookie từ UI
        
        Args:
            cookie: Cookie string từ người dùng
            
        Returns:
            tuple: (success: bool, message: str)
            
        Flow:
        1. Kiểm tra cookie có rỗng không
        2. Nếu là Netscape format, chuyển đổi
        3. Validate cookie
        4. Lưu cookie vào CookieManager
        
        Exceptions:
            Exception: Lỗi khi lưu cookie
        """
        function_name = "CookieController.save_cookie"
        
        try:
            write_log('INFO', function_name, "Bắt đầu", self.logger)
            write_log('DEBUG', function_name, f"Cookie length: {len(cookie) if cookie else 0} characters", self.logger)
            
            # Kiểm tra cookie có rỗng không
            if not cookie or not cookie.strip():
                write_log('WARNING', function_name, "Cookie rỗng hoặc không hợp lệ", self.logger)
                return False, "Cookie không được để trống"
            
            # Netscape形式の場合は変換
            if cookie.startswith("# Netscape"):
                write_log('INFO', function_name, "Phát hiện Netscape format cookie, đang chuyển đổi...", self.logger)
                cookie = self.cookie_manager.parse_netscape_cookie_file(cookie)
                write_log('INFO', function_name, f"Đã chuyển đổi - length: {len(cookie)} characters", self.logger)
            
            # Validate cookie
            write_log('INFO', function_name, "Đang kiểm tra tính hợp lệ của cookie...", self.logger)
            if not self.cookie_manager.validate_cookie(cookie):
                write_log('WARNING', function_name, "Cookie không hợp lệ", self.logger)
                return False, "Cookie không hợp lệ. Vui lòng kiểm tra lại."
            
            # Lưu cookie
            write_log('INFO', function_name, "Cookie hợp lệ, đang lưu...", self.logger)
            if self.cookie_manager.save_cookie(cookie):
                write_log('INFO', function_name, "Đã lưu cookie thành công", self.logger)
                return True, "Cookie đã được lưu thành công!"
            else:
                write_log('ERROR', function_name, "Lỗi khi lưu cookie", self.logger)
                return False, "Lỗi khi lưu cookie"
                
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi save cookie: {e}", self.logger, exc_info=True)
            return False, f"Lỗi khi lưu cookie: {str(e)}"
    
    def load_cookie(self) -> Optional[str]:
        """
        保存されたCookieを読み込む
        
        Returns:
            Cookie文字列またはNone
        """
        return self.cookie_manager.get_cookie()
    
    def clear_cookie(self) -> bool:
        """
        Cookieをクリア
        
        Returns:
            成功フラグ
        """
        return self.cookie_manager.clear_cookie()
    
    def load_cookie_from_file(self, file_path: str) -> tuple[bool, str, Optional[str]]:
        """
        Đọc cookie từ file
        
        Args:
            file_path: Đường dẫn file cookie
            
        Returns:
            tuple: (success: bool, message: str, cookie: Optional[str])
            
        Flow:
        1. Kiểm tra file có tồn tại không
        2. Thử đọc với nhiều encoding (utf-8, latin-1, cp1252)
        3. Phát hiện format (Netscape hoặc plain text)
        4. Parse và trả về cookie string
        
        Exceptions:
            FileNotFoundError: File không tồn tại
            UnicodeDecodeError: Không thể đọc file với bất kỳ encoding nào
            Exception: Các lỗi khác
        """
        function_name = "CookieController.load_cookie_from_file"
        
        try:
            write_log('INFO', function_name, "Bắt đầu", self.logger)
            write_log('DEBUG', function_name, f"File path: {file_path}", self.logger)
            
            # Kiểm tra file có tồn tại không
            if not os.path.exists(file_path):
                write_log('ERROR', function_name, f"File không tồn tại: {file_path}", self.logger)
                return False, f"File không tồn tại: {file_path}", None
            
            file_size = os.path.getsize(file_path)
            write_log('DEBUG', function_name, f"File size: {file_size} bytes", self.logger)
            
            # Thử đọc với nhiều encoding (theo System Instruction: log input)
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    write_log('DEBUG', function_name, f"Thử đọc với encoding: {encoding}", self.logger)
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    used_encoding = encoding
                    write_log('INFO', function_name, f"Đã đọc file thành công với encoding: {encoding}", self.logger)
                    break
                except UnicodeDecodeError as e:
                    write_log('DEBUG', function_name, f"Encoding {encoding} thất bại: {e}", self.logger)
                    continue
            
            if content is None:
                write_log('ERROR', function_name, "Không thể đọc file với bất kỳ encoding nào", self.logger)
                return False, "Không thể đọc file. Vui lòng kiểm tra encoding.", None
            
            write_log('DEBUG', function_name, f"Content length: {len(content)} characters", self.logger)
            
            # Phát hiện format và parse
            if content.startswith("# Netscape"):
                write_log('INFO', function_name, "Phát hiện Netscape format cookie, đang chuyển đổi...", self.logger)
                cookie = self.cookie_manager.parse_netscape_cookie_file(content)
                write_log('INFO', function_name, f"Đã chuyển đổi - cookie length: {len(cookie)} characters", self.logger)
            else:
                write_log('INFO', function_name, "Cookie format: Plain text hoặc JSON", self.logger)
                cookie = content.strip()
            
            write_log('INFO', function_name, f"Cookie loaded successfully - length: {len(cookie)} characters", self.logger)
            return True, "Đã tải cookie từ file", cookie
            
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi đọc file: {e}", self.logger, exc_info=True)
            return False, f"Lỗi khi đọc file: {str(e)}", None

