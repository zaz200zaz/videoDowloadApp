"""
Cookie Controller
Cookie管理のコントローラー
"""

from typing import Optional
from models.cookie_manager import CookieManager


class CookieController:
    """Cookie管理のコントローラー"""
    
    def __init__(self, cookie_manager: CookieManager):
        """
        初期化
        
        Args:
            cookie_manager: CookieManagerインスタンス
        """
        self.cookie_manager = cookie_manager
    
    def save_cookie(self, cookie: str) -> tuple[bool, str]:
        """
        Cookieを保存
        
        Args:
            cookie: Cookie文字列
            
        Returns:
            (成功フラグ, メッセージ) のタプル
        """
        if not cookie or not cookie.strip():
            return False, "Cookie không được để trống"
        
        # Netscape形式の場合は変換
        if cookie.startswith("# Netscape"):
            cookie = self.cookie_manager.parse_netscape_cookie_file(cookie)
        
        # バリデーション
        if not self.cookie_manager.validate_cookie(cookie):
            return False, "Cookie không hợp lệ. Vui lòng kiểm tra lại."
        
        # 保存
        if self.cookie_manager.save_cookie(cookie):
            return True, "Cookie đã được lưu thành công!"
        else:
            return False, "Lỗi khi lưu cookie"
    
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
        ファイルからCookieを読み込む
        
        Args:
            file_path: ファイルパス
            
        Returns:
            (成功フラグ, メッセージ, Cookie文字列) のタプル
        """
        try:
            # エンコーディングを試行
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return False, "Không thể đọc file. Vui lòng kiểm tra encoding.", None
            
            # Netscape形式の場合は変換
            if content.startswith("# Netscape"):
                cookie = self.cookie_manager.parse_netscape_cookie_file(content)
            else:
                # JSON形式またはプレーンテキスト
                cookie = content.strip()
            
            return True, "Đã tải cookie từ file", cookie
            
        except Exception as e:
            return False, f"Lỗi khi đọc file: {str(e)}", None

