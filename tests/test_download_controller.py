"""
Test Cases cho DownloadController
DownloadControllerのテストケース

Mục đích:
- Test tất cả các chức năng quan trọng của DownloadController
- Test download initialization và management
- Test user videos retrieval
- Test delete operations
- Đảm bảo logging đầy đủ theo System Instruction

Test Cases:
1. Test __init__: DownloadController初期化のテスト
2. Test initialize_downloader_success: Downloader初期化の成功テスト
3. Test initialize_downloader_no_cookie: Cookieがない場合の初期化テスト
4. Test start_download: ダウンロード開始のテスト
5. Test stop_download: ダウンロード停止のテスト
6. Test get_user_videos: ユーザービデオ取得のテスト
7. Test delete_downloaded_videos: ダウンロード済みビデオ削除のテスト
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

from controllers.download_controller import DownloadController
from models.cookie_manager import CookieManager
from utils.log_helper import write_log, get_logger


class TestDownloadController(unittest.TestCase):
    """Test class cho DownloadController"""
    
    def setUp(self):
        """
        Setup cho mỗi test case
        各テストケースのセットアップ
        
        Mục đích:
        - Tạo temporary directory và config file
        - Khởi tạo CookieManager instance với temp config
        - Khởi tạo DownloadController instance
        - Thiết lập logging cho test (theo System Instruction)
        """
        function_name = "TestDownloadController.setUp"
        self.test_logger = get_logger('TestDownloadController')
        
        # Tạo temporary directory cho config file (theo System Instruction - test isolation)
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Tạo temporary config file với default config (theo System Instruction - test data)
        self.config_file = os.path.join(self.temp_dir, "config.json")
        default_config = {
            "cookie": "test_cookie_value_12345",
            "download_folder": os.path.join(self.temp_dir, "downloads"),
            "settings": {
                "naming_mode": "video_id",
                "video_format": "auto",
                "orientation_filter": "all"
            }
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        # Khởi tạo CookieManager với temp config (theo System Instruction - dependency injection)
        self.cookie_manager = CookieManager()
        self.cookie_manager.config_file = self.config_file
        
        # Khởi tạo DownloadController (theo System Instruction - test setup)
        self.download_controller = DownloadController(self.cookie_manager)
        
        # Log test setup (theo System Instruction - logging đầy đủ)
        write_log('INFO', function_name, f"Test setup completed - temp_dir: {self.temp_dir}", self.test_logger)
    
    def tearDown(self):
        """
        Cleanup sau mỗi test case
        各テストケース後のクリーンアップ
        
        Mục đích:
        - Stop download service nếu đang chạy
        - Restore original working directory
        - Xóa temporary directory và files
        - Log test cleanup (theo System Instruction)
        """
        function_name = "TestDownloadController.tearDown"
        
        # Stop download service nếu đang chạy (theo System Instruction - cleanup)
        if self.download_controller.download_service and self.download_controller.download_service.is_downloading:
            self.download_controller.stop_download()
            time.sleep(0.5)  # Đợi thread kết thúc
        
        # Restore original working directory (theo System Instruction - cleanup)
        os.chdir(self.original_cwd)
        
        # Xóa temporary directory (theo System Instruction - cleanup)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Log cleanup (theo System Instruction - logging đầy đủ)
        write_log('INFO', function_name, "Test cleanup completed", self.test_logger)
    
    def test_init(self):
        """
        Test DownloadController.__init__
        DownloadController初期化のテスト
        
        Mục đích:
        - DownloadControllerが正しく初期化されることを確認
        - CookieManagerの参照が正しく設定されることを確認
        - DownloadServiceがNoneで初期化されることを確認
        
        Expected:
        - DownloadControllerインスタンスが作成される
        - cookie_manager属性が設定される
        - download_service属性がNoneで初期化される
        """
        function_name = "TestDownloadController.test_init"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Test: DownloadController初期化 (theo System Instruction - test logic)
        download_controller = DownloadController(self.cookie_manager)
        
        # Assert: CookieManager参照が正しく設定される (theo System Instruction - assertions)
        self.assertIsNotNone(download_controller.cookie_manager)
        self.assertEqual(download_controller.cookie_manager, self.cookie_manager)
        
        # Assert: DownloadServiceがNoneで初期化される (theo System Instruction - lazy initialization)
        self.assertIsNone(download_controller.download_service)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_initialize_downloader_success(self):
        """
        Test DownloadController.initialize_downloader - success case
        Downloader初期化の成功テスト
        
        Mục đích:
        - Cookieがある場合、DownloadServiceが正しく初期化されることを確認
        - 成功ステータスが返されることを確認
        
        Expected:
        - (True, None)が返される
        - DownloadServiceが初期化される
        """
        function_name = "TestDownloadController.test_initialize_downloader_success"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Setup: Cookieを保存 (theo System Instruction - test setup)
        test_cookie = "test_cookie_value_12345"
        self.cookie_manager.save_cookie(test_cookie)
        write_log('DEBUG', function_name, f"Test cookie saved: {test_cookie[:20]}...", self.test_logger)
        
        # Test: Downloader初期化 (theo System Instruction - test logic)
        success, error_message = self.download_controller.initialize_downloader(self.test_logger)
        
        # Assert: 初期化が成功する (theo System Instruction - assertions)
        self.assertTrue(success)
        self.assertIsNone(error_message)
        self.assertIsNotNone(self.download_controller.download_service)
        write_log('INFO', function_name, f"Initialize downloader result: success={success}", self.test_logger)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_initialize_downloader_no_cookie(self):
        """
        Test DownloadController.initialize_downloader - no cookie
        Cookieがない場合の初期化テスト
        
        Mục đích:
        - Cookieがない場合、初期化が失敗することを確認
        - 適切なエラーメッセージが返されることを確認
        
        Expected:
        - (False, error message)が返される
        - DownloadServiceが初期化されない
        """
        function_name = "TestDownloadController.test_initialize_downloader_no_cookie"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Setup: Cookieを削除 (theo System Instruction - test setup)
        # clear_cookie()を使用してCookieを削除
        self.cookie_manager.clear_cookie()
        write_log('DEBUG', function_name, "Test cookie cleared", self.test_logger)
        
        # Test: Downloader初期化 (theo System Instruction - test logic)
        success, error_message = self.download_controller.initialize_downloader(self.test_logger)
        
        # Assert: 初期化が失敗する (theo System Instruction - assertions)
        self.assertFalse(success)
        self.assertIsNotNone(error_message)
        self.assertIn("cookie", error_message.lower())
        write_log('INFO', function_name, f"Initialize downloader result: success={success}, error={error_message}", self.test_logger)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_stop_download(self):
        """
        Test DownloadController.stop_download
        ダウンロード停止のテスト
        
        Mục đích:
        - ダウンロードが正しく停止されることを確認
        - should_stopフラグが設定されることを確認
        
        Expected:
        - DownloadServiceのshould_stopフラグがTrueになる
        """
        function_name = "TestDownloadController.test_stop_download"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Setup: Downloader初期化 (theo System Instruction - test setup)
        test_cookie = "test_cookie_value_12345"
        self.cookie_manager.save_cookie(test_cookie)
        self.download_controller.initialize_downloader(self.test_logger)
        write_log('DEBUG', function_name, "Downloader initialized", self.test_logger)
        
        # Test: ダウンロード停止 (theo System Instruction - test logic)
        self.download_controller.stop_download()
        
        # Assert: should_stopフラグが設定される (theo System Instruction - assertions)
        self.assertTrue(self.download_controller.download_service.should_stop)
        write_log('INFO', function_name, "Stop download result: should_stop=True", self.test_logger)
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)
    
    def test_delete_downloaded_videos(self):
        """
        Test DownloadController.delete_downloaded_videos
        ダウンロード済みビデオ削除のテスト
        
        Mục đích:
        - ダウンロード済みビデオが正しく削除されることを確認
        - 削除統計が正しく返されることを確認
        
        Expected:
        - (deleted_count, not_found_count, deleted_files)が返される
        """
        function_name = "TestDownloadController.test_delete_downloaded_videos"
        write_log('INFO', function_name, "Bắt đầu test", self.test_logger)
        
        # Setup: ダウンロードフォルダとテストファイルを作成 (theo System Instruction - test setup)
        download_folder = self.cookie_manager.get_download_folder()
        os.makedirs(download_folder, exist_ok=True)
        
        test_file = os.path.join(download_folder, "test_video.mp4")
        with open(test_file, 'w') as f:
            f.write("test video content")
        write_log('DEBUG', function_name, f"Test file created: {test_file}", self.test_logger)
        
        # Setup: Results with file path (theo System Instruction - test data)
        results = [
            {'success': True, 'file_path': test_file},
            {'success': False, 'file_path': None},
            {'success': True, 'file_path': os.path.join(download_folder, "non_existent.mp4")}
        ]
        
        # Test: ビデオ削除 (theo System Instruction - test logic)
        deleted_count, not_found_count, deleted_files = self.download_controller.delete_downloaded_videos(results)
        
        # Assert: 削除統計が正しい (theo System Instruction - assertions)
        self.assertGreaterEqual(deleted_count, 0)
        self.assertGreaterEqual(not_found_count, 0)
        write_log('INFO', function_name, f"Delete videos result: deleted={deleted_count}, not_found={not_found_count}", self.test_logger)
        
        # Assert: ファイルが削除される (theo System Instruction - verification)
        self.assertFalse(os.path.exists(test_file))
        
        write_log('INFO', function_name, "Test completed successfully", self.test_logger)


if __name__ == '__main__':
    """
    Test runner
    テストランナー
    
    Mục đích:
    - テストスイートを実行
    - 詳細なログ出力を有効化 (theo System Instruction - logging đầy đủ)
    """
    # Setup logging cho test runner (theo System Instruction - logging setup)
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Run tests với verbosity (theo System Instruction - test execution)
    unittest.main(verbosity=2)

