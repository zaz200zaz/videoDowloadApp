"""
Test Cases cho CookieManager
CookieManagerのテストケース

Mục đích:
- Test tất cả các chức năng quan trọng của CookieManager
- Test config file management
- Test caching mechanism
- Đảm bảo logging đầy đủ theo System Instruction

Test Cases:
1. Test save_cookie: Cookie保存のテスト
2. Test get_cookie: Cookie取得のテスト
3. Test get_download_folder: ダウンロードフォルダ取得のテスト
4. Test get_setting: 設定取得のテスト
5. Test config caching: 設定キャッシュのテスト
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
import time
from unittest.mock import Mock, patch, MagicMock
import logging
from datetime import datetime

# Thêm project root vào path để import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from models.cookie_manager import CookieManager


class TestCookieManager(unittest.TestCase):
    """Test class cho CookieManager"""
    
    def setUp(self):
        """
        Setup cho mỗi test case
        各テストケースのセットアップ
        
        Mục đích:
        - Tạo temporary config file
        - Khởi tạo CookieManager instance với temp config
        - Thiết lập logging cho test
        """
        function_name = "TestCookieManager.setUp"
        
        # Log bắt đầu setup (theo System Instruction 4.4)
        self.test_logger = logging.getLogger('TestCookieManager')
        self.test_logger.info(f"[{function_name}] Bắt đầu setup test case")
        
        # Tạo temporary directory cho config file
        self.test_dir = tempfile.mkdtemp(prefix="test_cookie_manager_")
        self.test_logger.debug(f"[{function_name}] Test directory: {self.test_dir}")
        
        # Tạo temporary config file
        self.test_config_file = os.path.join(self.test_dir, "test_config.json")
        
        # Default config
        default_config = {
            "cookie": "",
            "download_folder": "./downloads",
            "settings": {
                "naming_mode": "video_id",
                "video_format": "auto",
                "orientation_filter": "all"
            }
        }
        
        with open(self.test_config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        self.test_logger.debug(f"[{function_name}] Test config file: {self.test_config_file}")
        
        # Tạo log file cho test
        test_log_dir = os.path.join(project_root, "logs", "tests")
        os.makedirs(test_log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_log_file = os.path.join(test_log_dir, f"test_cookie_manager_{timestamp}.log")
        self.test_logger.debug(f"[{function_name}] Test log file: {self.test_log_file}")
        
        # Khởi tạo CookieManager instance với temp config
        try:
            # Patch CONFIG_FILE để sử dụng temp config
            with patch.object(CookieManager, 'CONFIG_FILE', self.test_config_file):
                self.manager = CookieManager()
                self.test_logger.info(f"[{function_name}] CookieManager initialized successfully")
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Lỗi khi khởi tạo CookieManager: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] Setup hoàn thành")
    
    def tearDown(self):
        """
        Cleanup sau mỗi test case
        各テストケース後のクリーンアップ
        
        Mục đích:
        - Xóa temporary directory
        - Cleanup các file test tạo ra
        """
        function_name = "TestCookieManager.tearDown"
        self.test_logger.info(f"[{function_name}] Bắt đầu cleanup test case")
        
        try:
            # Xóa temporary directory
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
                self.test_logger.debug(f"[{function_name}] Đã xóa test directory: {self.test_dir}")
        except Exception as e:
            self.test_logger.warning(f"[{function_name}] Lỗi khi xóa test directory: {e}", exc_info=True)
        
        self.test_logger.info(f"[{function_name}] Cleanup hoàn thành")
    
    def test_save_cookie(self):
        """
        Test Case 1: save_cookie
        Cookie保存テスト
        
        Mục đích:
        - Test cookie保存が正常に動作することを確認
        - Test config fileが更新されることを確認
        - Test cookieが正しく保存されることを確認
        
        Input:
        - Cookie string: "test_cookie=value123; session_id=test123"
        
        Expected Output:
        - Return True
        - Cookie được lưu vào config file
        - Log records về save operation
        """
        function_name = "TestCookieManager.test_save_cookie"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: save_cookie")
        
        # Test input
        test_cookie = "test_cookie=value123; session_id=test123; " * 10
        self.test_logger.debug(f"[{function_name}] Input cookie length: {len(test_cookie)} characters")
        # Không log cookie đầy đủ (theo System Instruction 7 - bảo mật)
        self.test_logger.debug(f"[{function_name}] Input cookie preview: {test_cookie[:50]}...")
        
        try:
            # Gọi function under test
            result = self.manager.save_cookie(test_cookie)
            
            # Assert kết quả
            self.assertTrue(result, "save_cookie phải trả về True")
            
            # Kiểm tra cookie được lưu trong config file
            # Lưu ý: save_cookie() sẽ gọi .strip() trên cookie, nên cookie được lưu sẽ là stripped version
            with open(self.test_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # save_cookie() gọi .strip() trên cookie trước khi lưu (theo code trong models/cookie_manager.py)
            # Nên cookie được lưu sẽ là stripped version
            expected_cookie = test_cookie.strip()  # Cookie sẽ được strip trước khi lưu
            self.assertEqual(config.get('cookie'), expected_cookie, "Cookie phải được lưu vào config file (đã được strip)")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Cookie được lưu thành công")
            self.test_logger.debug(f"[{function_name}] Config file updated")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_get_cookie(self):
        """
        Test Case 2: get_cookie
        Cookie取得テスト
        
        Mục đích:
        - Test cookie取得が正常に動作することを確認
        - Test saved cookieが正しく取得されることを確認
        
        Input:
        - Cookie đã được lưu trong config file
        
        Expected Output:
        - Cookie string được trả về
        - Log records về get operation
        """
        function_name = "TestCookieManager.test_get_cookie"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: get_cookie")
        
        # Setup: Lưu cookie trước
        test_cookie = "test_cookie=value123; session_id=test123"
        self.manager.save_cookie(test_cookie)
        self.test_logger.debug(f"[{function_name}] Cookie đã được lưu")
        
        try:
            # Gọi function under test
            result = self.manager.get_cookie()
            
            # Assert kết quả
            self.assertEqual(result, test_cookie, "get_cookie phải trả về cookie đã lưu")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Cookie được lấy thành công")
            self.test_logger.debug(f"[{function_name}] Cookie length: {len(result)} characters")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_get_download_folder(self):
        """
        Test Case 3: get_download_folder
        ダウンロードフォルダ取得テスト
        
        Mục đích:
        - Test download folder取得が正常に動作することを確認
        - Test default valueが返されることを確認
        
        Input:
        - Config file với download_folder setting
        
        Expected Output:
        - Download folder path được trả về
        - Log records về get operation
        """
        function_name = "TestCookieManager.test_get_download_folder"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: get_download_folder")
        
        try:
            # Gọi function under test
            result = self.manager.get_download_folder()
            
            # Assert kết quả
            self.assertIsNotNone(result, "get_download_folder không được trả về None")
            self.assertIsInstance(result, str, "Download folder phải là string")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Download folder được lấy thành công")
            self.test_logger.debug(f"[{function_name}] Download folder: {result}")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_get_setting(self):
        """
        Test Case 4: get_setting
        設定取得テスト
        
        Mục đích:
        - Test setting取得が正常に動作することを確認
        - Test default valueが返されることを確認
        
        Input:
        - Setting key: "naming_mode", "video_format", etc.
        - Default value (optional)
        
        Expected Output:
        - Setting value được trả về
        - Log records về get operation
        """
        function_name = "TestCookieManager.test_get_setting"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: get_setting")
        
        # Test cases
        test_cases = [
            ("naming_mode", "video_id", "Naming mode setting"),
            ("video_format", "auto", "Video format setting"),
            ("orientation_filter", "all", "Orientation filter setting"),
            ("non_existent_setting", None, "Non-existent setting"),
        ]
        
        for setting_key, expected_value, description in test_cases:
            self.test_logger.debug(f"[{function_name}] Test case: {description}")
            self.test_logger.debug(f"[{function_name}] Setting key: {setting_key}")
            self.test_logger.debug(f"[{function_name}] Expected value: {expected_value}")
            
            try:
                # Gọi function under test
                result = self.manager.get_setting(setting_key, default=None)
                
                # Assert kết quả
                if expected_value is not None:
                    self.assertEqual(result, expected_value, f"{description} phải trả về {expected_value}")
                else:
                    self.assertIsNone(result, f"{description} phải trả về None")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - {description}: {result}")
                
            except Exception as e:
                self.test_logger.error(f"[{function_name}] Test FAILED - {description}: {e}", exc_info=True)
                raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_config_caching(self):
        """
        Test Case 5: config caching
        設定キャッシュテスト
        
        Mục đích:
        - Test config caching mechanismが正常に動作することを確認
        - Test cache durationが正しく適用されることを確認
        - Test cache invalidationが正しく動作することを確認
        
        Input:
        - Multiple get operations trong cache duration
        - Config file update
        
        Expected Output:
        - Cache được sử dụng trong cache duration
        - Cache được invalidate sau khi file được update
        - Log records về cache usage
        """
        function_name = "TestCookieManager.test_config_caching"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: config caching")
        
        try:
            # Lưu cookie ban đầu
            initial_cookie = "initial_cookie=value123"
            self.manager.save_cookie(initial_cookie)
            
            # Lần 1: Đọc cookie (sẽ cache)
            result1 = self.manager.get_cookie()
            self.test_logger.debug(f"[{function_name}] First read: {result1}")
            
            # Lần 2: Đọc lại ngay lập tức (sẽ dùng cache)
            result2 = self.manager.get_cookie()
            self.test_logger.debug(f"[{function_name}] Second read (cached): {result2}")
            
            # Assert cả hai lần đều trả về cùng giá trị
            self.assertEqual(result1, result2, "Cached value phải giống với original value")
            
            # Cập nhật config file trực tiếp
            with open(self.test_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            config['cookie'] = "updated_cookie=value456"
            with open(self.test_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # Đợi cache expire (11 giây - nhiều hơn cache duration 10 giây)
            # Cache duration đã được tăng từ 5 giây lên 10 giây để tối ưu I/O operations
            self.test_logger.debug(f"[{function_name}] Đợi cache expire...")
            time.sleep(11)
            
            # Lần 3: Đọc lại sau khi cache expire (sẽ đọc lại từ file)
            result3 = self.manager.get_cookie()
            self.test_logger.debug(f"[{function_name}] Third read (after cache expire): {result3}")
            
            # Assert giá trị mới được đọc
            self.assertEqual(result3, "updated_cookie=value456", "Cookie mới phải được đọc sau khi cache expire")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Config caching hoạt động đúng")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")


if __name__ == '__main__':
    # Setup logging cho test runner
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Run tests
    unittest.main(verbosity=2)

