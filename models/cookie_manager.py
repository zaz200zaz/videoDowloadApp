"""
Cookie Manager Module
Quản lý việc lưu và đọc cookie từ file config.json

Mục tiêu:
- Quản lý cookie Douyin và cấu hình ứng dụng
- Lưu trữ và đọc từ file config.json
- Cache config để tối ưu I/O operations

Input/Output:
- Input: Cookie string, settings, download folder path
- Output: Cookie string, settings values, config dict
"""

import json
import os
import logging
from typing import Optional
from utils.log_helper import write_log, get_logger


class CookieManager:
    """
    Quản lý cookie Douyin và cấu hình ứng dụng
    
    Chức năng chính:
    - Lưu và đọc cookie từ config.json
    - Quản lý download folder
    - Quản lý settings (naming_mode, video_format, etc.)
    - Cache config để giảm I/O operations
    """
    
    CONFIG_FILE = "config.json"
    
    def __init__(self):
        """
        Khởi tạo CookieManager
        
        Flow:
        1. Thiết lập logger
        2. Khởi tạo cache
        3. Đảm bảo config file tồn tại
        
        Exceptions:
            Exception: Lỗi khi tạo config file
        """
        function_name = "CookieManager.__init__"
        self.config_file = self.CONFIG_FILE
        self.logger = get_logger('CookieManager')
        self._config_cache = None  # Cache config để giảm I/O
        self._config_cache_time = None  # Thời gian cache
        
        write_log('INFO', function_name, "Bắt đầu khởi tạo CookieManager", self.logger)
        try:
            self._ensure_config_exists()
            write_log('INFO', function_name, "CookieManager đã được khởi tạo thành công", self.logger)
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi khởi tạo CookieManager: {e}", self.logger, exc_info=True)
            raise
    
    def _ensure_config_exists(self):
        """
        Đảm bảo file config.json tồn tại
        
        Flow:
        1. Kiểm tra file có tồn tại không
        2. Nếu không, tạo file với config mặc định
        3. Nếu có, log thông tin
        
        Exceptions:
            Exception: Lỗi khi tạo hoặc đọc config file
        """
        function_name = "CookieManager._ensure_config_exists"
        
        try:
            if not os.path.exists(self.config_file):
                write_log('INFO', function_name, 
                         f"Config file không tồn tại, đang tạo file mặc định: {self.config_file}", 
                         self.logger)
                
                default_config = {
                    "cookie": "",
                    "download_folder": "./downloads",
                    "settings": {
                        "naming_mode": "video_id",  # "video_id" hoặc "timestamp"
                        "max_concurrent": 3,
                        "video_format": "auto",  # "highest", "high", "medium", "low", "auto"
                        "orientation_filter": "all",  # "all", "vertical", "horizontal"
                        "orientation_swap": False,  # True nếu width/height bị đảo ngược trong API response
                        # Timeout và Retry settings (theo System Instruction)
                        "download_timeout_seconds": 300,  # Timeout tổng cho mỗi video (5 phút)
                        "chunk_timeout_seconds": 30,  # Timeout cho mỗi chunk (30 giây) - nếu không có progress trong 30 giây thì coi như bị treo
                        "max_retries": 3,  # Số lần retry tối đa khi timeout hoặc lỗi
                        "retry_delay_seconds": 5,  # Thời gian chờ giữa các lần retry (5 giây)
                        "max_download_time_seconds": 1800,  # Thời gian tối đa cho mỗi video (30 phút) - nếu vượt quá sẽ skip
                        "enable_timeout_detection": True,  # Bật/tắt phát hiện timeout
                        "enable_auto_retry": True,  # Bật/tắt tự động retry
                        "enable_skip_slow_videos": True,  # Bật/tắt skip video quá lâu
                        "chunk_size": 8192  # Kích thước chunk (bytes) - 8KB mặc định
                    }
                }
                self._save_config(default_config)
                write_log('INFO', function_name, "Đã tạo config file mặc định thành công", self.logger)
            else:
                write_log('DEBUG', function_name, f"Config file đã tồn tại: {self.config_file}", self.logger)
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi đảm bảo config file tồn tại: {e}", self.logger, exc_info=True)
            raise
    
    def _load_config(self, use_cache: bool = True) -> dict:
        """
        Đọc cấu hình từ file (với cache để giảm I/O)
        
        Args:
            use_cache: Có sử dụng cache không (mặc định: True)
            
        Returns:
            dict: Config dictionary hoặc {} nếu lỗi
            
        Exceptions:
            FileNotFoundError: Config file không tồn tại
            json.JSONDecodeError: Lỗi khi parse JSON
            Exception: Các lỗi khác
        """
        function_name = "CookieManager._load_config"
        import time
        
        try:
            # Kiểm tra cache (cache trong 1 giây để tránh đọc quá nhiều lần)
            if use_cache and self._config_cache is not None and self._config_cache_time is not None:
                if time.time() - self._config_cache_time < 1.0:  # Cache 1 giây
                    write_log('DEBUG', function_name, "Sử dụng cache config", self.logger)
                    return self._config_cache
            
            # Chỉ log khi không dùng cache hoặc cache hết hạn
            if not use_cache or self._config_cache is None:
                write_log('DEBUG', function_name, f"Đang đọc config từ file: {self.config_file}", self.logger)
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Cập nhật cache
            cache_updated = self._config_cache is None
            self._config_cache = config
            self._config_cache_time = time.time()
            
            if not use_cache or cache_updated:
                write_log('DEBUG', function_name, f"Đã đọc config thành công, keys: {list(config.keys())}", self.logger)
            
            return config
            
        except FileNotFoundError:
            write_log('WARNING', function_name, f"Config file không tồn tại: {self.config_file}", self.logger)
            return {}
        except json.JSONDecodeError as e:
            write_log('ERROR', function_name, f"Lỗi khi parse JSON từ config file: {e}", self.logger, exc_info=True)
            return {}
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi không xác định khi đọc config: {e}", self.logger, exc_info=True)
            return {}
    
    def _save_config(self, config: dict):
        """
        Lưu cấu hình vào file
        
        Args:
            config: Dictionary chứa config cần lưu
            
        Exceptions:
            Exception: Lỗi khi ghi file hoặc parse JSON
        """
        function_name = "CookieManager._save_config"
        import time
        
        try:
            write_log('DEBUG', function_name, f"Đang lưu config vào file: {self.config_file}", self.logger)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # Cập nhật cache sau khi lưu
            self._config_cache = config
            self._config_cache_time = time.time()
            
            write_log('DEBUG', function_name, "Đã lưu config thành công", self.logger)
            
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi lưu config: {e}", self.logger, exc_info=True)
            # Xóa cache nếu lưu thất bại
            self._config_cache = None
            self._config_cache_time = None
            raise
    
    def save_cookie(self, cookie: str) -> bool:
        """
        Lưu cookie vào config.json
        
        Args:
            cookie: Cookie string từ người dùng
            
        Returns:
            True nếu lưu thành công, False nếu có lỗi
            
        Exceptions:
            Exception: Lỗi khi đọc/ghi config file
        """
        function_name = "CookieManager.save_cookie"
        
        try:
            write_log('INFO', function_name, "Bắt đầu", self.logger)
            
            # Kiểm tra cookie có hợp lệ không
            if not cookie or not cookie.strip():
                write_log('WARNING', function_name, "Cookie rỗng, không thể lưu", self.logger)
                return False
            
            cookie_length = len(cookie.strip())
            write_log('INFO', function_name, f"Đang lưu cookie - length: {cookie_length} characters", self.logger)
            # Log preview (theo System Instruction: chỉ log preview, không log toàn bộ)
            write_log('DEBUG', function_name, f"Cookie preview: {cookie[:100]}...", self.logger)
            
            # Lưu cookie vào config
            config = self._load_config()
            config["cookie"] = cookie.strip()
            self._save_config(config)
            
            write_log('INFO', function_name, "Đã lưu cookie thành công", self.logger)
            return True
            
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi lưu cookie: {e}", self.logger, exc_info=True)
            print(f"Lỗi khi lưu cookie: {e}")
            return False
    
    def get_cookie(self) -> Optional[str]:
        """
        Lấy cookie từ config.json
        
        Returns:
            Cookie string hoặc None nếu không có
            
        Exceptions:
            Exception: Lỗi khi đọc config file
        """
        function_name = "CookieManager.get_cookie"
        
        try:
            write_log('DEBUG', function_name, "Đang đọc cookie", self.logger)
            config = self._load_config()
            cookie = config.get("cookie", "")
            
            if cookie:
                write_log('DEBUG', function_name, f"Cookie found - length: {len(cookie)} characters", self.logger)
                return cookie
            else:
                write_log('DEBUG', function_name, "Cookie không tồn tại hoặc rỗng", self.logger)
                return None
                
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi đọc cookie: {e}", self.logger, exc_info=True)
            print(f"Lỗi khi đọc cookie: {e}")
            return None
    
    def validate_cookie(self, cookie: str) -> bool:
        """
        Kiểm tra định dạng cookie cơ bản
        
        Args:
            cookie: Cookie string cần kiểm tra
            
        Returns:
            True nếu cookie có vẻ hợp lệ, False nếu không
            
        Logic:
        1. Kiểm tra độ dài cookie (phải >= 10)
        2. Kiểm tra cookie có chứa các key thông thường của Douyin không
           (sessionid, sid_guard, uid_tt, sid_tt)
        """
        function_name = "CookieManager.validate_cookie"
        
        try:
            write_log('DEBUG', function_name, "Đang kiểm tra cookie", self.logger)
            
            # Kiểm tra độ dài
            if not cookie or len(cookie.strip()) < 10:
                cookie_length = len(cookie.strip()) if cookie else 0
                write_log('WARNING', function_name, 
                         f"Cookie quá ngắn hoặc rỗng - length: {cookie_length}", 
                         self.logger)
                return False
            
            # Kiểm tra cookie có chứa các key thông thường của Douyin
            common_keys = ["sessionid", "sid_guard", "uid_tt", "sid_tt"]
            cookie_lower = cookie.lower()
            found_keys = [key for key in common_keys if key in cookie_lower]
            
            if found_keys:
                write_log('DEBUG', function_name, f"Cookie hợp lệ - tìm thấy keys: {found_keys}", self.logger)
                return True
            else:
                write_log('WARNING', function_name, 
                         "Cookie không chứa các key thông thường của Douyin", 
                         self.logger)
                return False
                
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi validate cookie: {e}", self.logger, exc_info=True)
            return False
    
    def parse_netscape_cookie_file(self, cookie_file_content: str) -> str:
        """
        Parse Netscape format cookie file thành cookie string
        
        Args:
            cookie_file_content: Nội dung file cookie Netscape format
            
        Returns:
            str: Cookie string dạng "key1=value1; key2=value2; ..."
            
        Logic:
        - Netscape format: domain, flag, path, secure, expiration, name, value (tab-separated)
        - Bỏ qua comment lines (bắt đầu với #)
        - Bỏ qua dòng trống
        
        Exceptions:
            Exception: Lỗi khi parse cookie file
        """
        function_name = "CookieManager.parse_netscape_cookie_file"
        
        try:
            write_log('INFO', function_name, "Bắt đầu parse Netscape cookie file", self.logger)
            write_log('DEBUG', function_name, f"Content length: {len(cookie_file_content)} characters", self.logger)
            
            cookies = []
            lines = cookie_file_content.strip().split('\n')
            
            for idx, line in enumerate(lines):
                line = line.strip()
                # Bỏ qua comment và dòng trống
                if not line or line.startswith('#'):
                    continue
                
                # Netscape format: domain, flag, path, secure, expiration, name, value
                parts = line.split('\t')
                if len(parts) >= 7:
                    name = parts[5]
                    value = parts[6]
                    if name and value:
                        cookies.append(f"{name}={value}")
            
            result = "; ".join(cookies)
            write_log('INFO', function_name, f"Đã parse thành công - {len(cookies)} cookies", self.logger)
            write_log('DEBUG', function_name, f"Result length: {len(result)} characters", self.logger)
            
            return result
            
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi parse Netscape cookie file: {e}", self.logger, exc_info=True)
            return ""
    
    def get_download_folder(self) -> str:
        """
        Lấy thư mục tải về
        
        Returns:
            str: Đường dẫn thư mục download (absolute path)
            
        Note:
            Tự động tạo thư mục nếu chưa tồn tại (theo System Instruction)
        """
        function_name = "CookieManager.get_download_folder"
        
        try:
            write_log('DEBUG', function_name, "Đang lấy download folder", self.logger)
            config = self._load_config()
            folder = config.get("download_folder", "./downloads")
            
            # Tạo thư mục nếu chưa tồn tại (theo System Instruction)
            os.makedirs(folder, exist_ok=True)
            
            # Convert to absolute path để log rõ ràng
            folder_abs = os.path.abspath(folder)
            write_log('DEBUG', function_name, f"Download folder: {folder_abs}", self.logger)
            
            return folder_abs
            
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi lấy download folder: {e}", self.logger, exc_info=True)
            # Fallback to default
            default_folder = os.path.abspath("./downloads")
            os.makedirs(default_folder, exist_ok=True)
            return default_folder
    
    def set_download_folder(self, folder: str):
        """
        Thiết lập thư mục tải về
        
        Args:
            folder: Đường dẫn thư mục download
            
        Exceptions:
            Exception: Lỗi khi lưu config
        """
        function_name = "CookieManager.set_download_folder"
        
        try:
            write_log('INFO', function_name, f"Đang thiết lập download folder: {folder}", self.logger)
            config = self._load_config()
            config["download_folder"] = folder
            self._save_config(config)
            write_log('INFO', function_name, "Đã thiết lập download folder thành công", self.logger)
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi thiết lập download folder: {e}", self.logger, exc_info=True)
            raise
    
    def get_setting(self, key: str, default=None):
        """
        Lấy một setting cụ thể
        
        Args:
            key: Tên setting cần lấy
            default: Giá trị mặc định nếu không tìm thấy
            
        Returns:
            Giá trị setting hoặc default
        """
        function_name = "CookieManager.get_setting"
        
        try:
            write_log('DEBUG', function_name, f"Đang lấy setting: {key}", self.logger)
            config = self._load_config()
            value = config.get("settings", {}).get(key, default)
            write_log('DEBUG', function_name, f"Setting {key} = {value}", self.logger)
            return value
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi lấy setting {key}: {e}", self.logger, exc_info=True)
            return default
    
    def set_setting(self, key: str, value):
        """
        Thiết lập một setting
        
        Args:
            key: Tên setting
            value: Giá trị setting
            
        Exceptions:
            Exception: Lỗi khi lưu config
        """
        function_name = "CookieManager.set_setting"
        
        try:
            write_log('INFO', function_name, f"Đang thiết lập setting: {key} = {value}", self.logger)
            config = self._load_config()
            if "settings" not in config:
                config["settings"] = {}
            config["settings"][key] = value
            self._save_config(config)
            write_log('INFO', function_name, f"Đã thiết lập setting {key} thành công", self.logger)
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi thiết lập setting {key}: {e}", self.logger, exc_info=True)
            raise
    
    def clear_cookie(self) -> bool:
        """
        Xóa cookie đã lưu
        
        Returns:
            bool: True nếu xóa thành công, False nếu có lỗi
            
        Exceptions:
            Exception: Lỗi khi đọc/ghi config file
        """
        function_name = "CookieManager.clear_cookie"
        
        try:
            write_log('INFO', function_name, "Bắt đầu xóa cookie", self.logger)
            config = self._load_config()
            config["cookie"] = ""
            self._save_config(config)
            write_log('INFO', function_name, "Đã xóa cookie thành công", self.logger)
            return True
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi xóa cookie: {e}", self.logger, exc_info=True)
            print(f"Lỗi khi xóa cookie: {e}")
            return False
    
    def reset_all(self) -> bool:
        """
        Reset tất cả dữ liệu về trạng thái ban đầu
        
        Returns:
            bool: True nếu reset thành công, False nếu có lỗi
            
        Exceptions:
            Exception: Lỗi khi lưu config file
        """
        function_name = "CookieManager.reset_all"
        
        try:
            write_log('INFO', function_name, "Bắt đầu reset tất cả cấu hình", self.logger)
            
            default_config = {
                "cookie": "",
                "download_folder": "./downloads",
                "settings": {
                    "naming_mode": "video_id",
                    "max_concurrent": 3,
                    "video_format": "auto",
                    "orientation_filter": "all",
                    "orientation_swap": False
                }
            }
            self._save_config(default_config)
            
            # Xóa cache để đảm bảo đọc lại từ file
            self._config_cache = None
            self._config_cache_time = None
            
            write_log('INFO', function_name, "Đã reset cấu hình thành công", self.logger)
            return True
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi reset: {e}", self.logger, exc_info=True)
            print(f"Lỗi khi reset: {e}")
            return False

