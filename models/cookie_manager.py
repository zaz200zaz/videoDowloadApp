"""
Cookie Manager Module
Quản lý việc lưu và đọc cookie từ file config.json
"""

import json
import os
from typing import Optional


class CookieManager:
    """Quản lý cookie Douyin"""
    
    CONFIG_FILE = "config.json"
    
    def __init__(self):
        """Khởi tạo CookieManager"""
        self.config_file = self.CONFIG_FILE
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Đảm bảo file config.json tồn tại"""
        if not os.path.exists(self.config_file):
            default_config = {
                "cookie": "",
                "download_folder": "./downloads",
                "settings": {
                    "naming_mode": "video_id",  # "video_id" hoặc "timestamp"
                    "max_concurrent": 3,
                    "video_format": "auto",  # "highest", "high", "medium", "low", "auto"
                    "orientation_filter": "all",  # "all", "vertical", "horizontal"
                    "orientation_swap": False  # True nếu width/height bị đảo ngược trong API response
                }
            }
            self._save_config(default_config)
    
    def _load_config(self) -> dict:
        """Đọc cấu hình từ file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_config(self, config: dict):
        """Lưu cấu hình vào file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def save_cookie(self, cookie: str) -> bool:
        """
        Lưu cookie vào config.json
        
        Args:
            cookie: Cookie string từ người dùng
            
        Returns:
            True nếu lưu thành công, False nếu có lỗi
        """
        try:
            if not cookie or not cookie.strip():
                return False
            
            config = self._load_config()
            config["cookie"] = cookie.strip()
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu cookie: {e}")
            return False
    
    def get_cookie(self) -> Optional[str]:
        """
        Lấy cookie từ config.json
        
        Returns:
            Cookie string hoặc None nếu không có
        """
        try:
            config = self._load_config()
            cookie = config.get("cookie", "")
            return cookie if cookie else None
        except Exception as e:
            print(f"Lỗi khi đọc cookie: {e}")
            return None
    
    def validate_cookie(self, cookie: str) -> bool:
        """
        Kiểm tra định dạng cookie cơ bản
        
        Args:
            cookie: Cookie string cần kiểm tra
            
        Returns:
            True nếu cookie có vẻ hợp lệ
        """
        if not cookie or len(cookie.strip()) < 10:
            return False
        
        # Kiểm tra cookie có chứa các key thông thường của Douyin
        common_keys = ["sessionid", "sid_guard", "uid_tt", "sid_tt"]
        cookie_lower = cookie.lower()
        return any(key in cookie_lower for key in common_keys)
    
    def parse_netscape_cookie_file(self, cookie_file_content: str) -> str:
        """
        Parse Netscape format cookie file thành cookie string
        
        Args:
            cookie_file_content: Nội dung file cookie Netscape format
            
        Returns:
            Cookie string dạng "key1=value1; key2=value2; ..."
        """
        cookies = []
        lines = cookie_file_content.strip().split('\n')
        
        for line in lines:
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
        
        return "; ".join(cookies)
    
    def get_download_folder(self) -> str:
        """Lấy thư mục tải về"""
        config = self._load_config()
        folder = config.get("download_folder", "./downloads")
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(folder, exist_ok=True)
        return folder
    
    def set_download_folder(self, folder: str):
        """Thiết lập thư mục tải về"""
        config = self._load_config()
        config["download_folder"] = folder
        self._save_config(config)
    
    def get_setting(self, key: str, default=None):
        """Lấy một setting cụ thể"""
        config = self._load_config()
        return config.get("settings", {}).get(key, default)
    
    def set_setting(self, key: str, value):
        """Thiết lập một setting"""
        config = self._load_config()
        if "settings" not in config:
            config["settings"] = {}
        config["settings"][key] = value
        self._save_config(config)
    
    def clear_cookie(self) -> bool:
        """
        Xóa cookie đã lưu
        
        Returns:
            True nếu xóa thành công
        """
        try:
            config = self._load_config()
            config["cookie"] = ""
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Lỗi khi xóa cookie: {e}")
            return False
    
    def reset_all(self) -> bool:
        """
        Reset tất cả dữ liệu về trạng thái ban đầu
        
        Returns:
            True nếu reset thành công
        """
        try:
            default_config = {
                "cookie": "",
                "download_folder": "./downloads",
                "settings": {
                    "naming_mode": "video_id",
                    "max_concurrent": 3,
                    "video_format": "auto",
                    "orientation_filter": "all"
                }
            }
            self._save_config(default_config)
            return True
        except Exception as e:
            print(f"Lỗi khi reset: {e}")
            return False

