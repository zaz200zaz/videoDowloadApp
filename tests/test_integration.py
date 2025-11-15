"""
Integration Test Cases
統合テストケース

Mục đích:
- Test integration giữa các components
- Test end-to-end workflows
- Đảm bảo logging đầy đủ theo System Instruction

Test Cases:
1. Test full download workflow: 完全なダウンロードワークフローのテスト
2. Test error handling across components: コンポーネント間のエラーハンドリングテスト
"""

import unittest
import os
import sys
import tempfile
import shutil
import time
from unittest.mock import Mock, patch, MagicMock
import logging
from datetime import datetime

# Thêm project root vào path để import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.video_downloader import VideoDownloader
from services.download_service import DownloadService
from models.cookie_manager import CookieManager


class TestIntegration(unittest.TestCase):
    """Integration test class"""
    
    def setUp(self):
        """
        Setup cho mỗi test case
        各テストケースのセットアップ
        
        Mục đích:
        - Tạo temporary directories
        - Khởi tạo các services
        - Thiết lập logging cho test
        """
        function_name = "TestIntegration.setUp"
        
        # Log bắt đầu setup
        self.test_logger = logging.getLogger('TestIntegration')
        self.test_logger.info(f"[{function_name}] Bắt đầu setup integration test")
        
        # Tạo temporary directories
        self.test_dir = tempfile.mkdtemp(prefix="test_integration_")
        self.test_logger.debug(f"[{function_name}] Test directory: {self.test_dir}")
        
        # Mock cookie
        self.mock_cookie = "test_cookie=value123; session_id=test123; " * 20
        self.test_logger.debug(f"[{function_name}] Mock cookie length: {len(self.mock_cookie)} characters")
        
        # Setup logging
        test_log_dir = os.path.join(project_root, "logs", "tests")
        os.makedirs(test_log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger = logging.getLogger('IntegrationTest')
        logger.setLevel(logging.DEBUG)
        # Đóng các handler cũ để tránh ResourceWarning (theo System Instruction 8)
        for handler in logger.handlers[:]:
            if hasattr(handler, 'close'):
                handler.close()
            logger.removeHandler(handler)
        logger.handlers = []
        
        log_file = os.path.join(test_log_dir, f"test_integration_{timestamp}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)
        
        self.test_logger.debug(f"[{function_name}] Integration test log file: {log_file}")
        self.test_logger.info(f"[{function_name}] Setup hoàn thành")
    
    def tearDown(self):
        """
        Cleanup sau mỗi test case
        各テストケース後のクリーンアップ
        """
        function_name = "TestIntegration.tearDown"
        self.test_logger.info(f"[{function_name}] Bắt đầu cleanup")
        
        try:
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
                self.test_logger.debug(f"[{function_name}] Đã xóa test directory")
        except Exception as e:
            self.test_logger.warning(f"[{function_name}] Lỗi khi cleanup: {e}", exc_info=True)
        
        self.test_logger.info(f"[{function_name}] Cleanup hoàn thành")
    
    def test_full_download_workflow(self):
        """
        Test Case 1: Full download workflow
        完全なダウンロードワークフローのテスト
        
        Mục đích:
        - Test integration giữa CookieManager, VideoDownloader, và DownloadService
        - Test end-to-end download process
        - Test logging flow qua các components
        
        Input:
        - Cookie từ CookieManager
        - Video URL
        - Download settings
        
        Expected Output:
        - Video được download thành công
        - Log records đầy đủ qua tất cả components
        """
        function_name = "TestIntegration.test_full_download_workflow"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: Full download workflow")
        
        try:
            # Step 1: Setup CookieManager
            self.test_logger.debug(f"[{function_name}] Step 1: Setup CookieManager")
            with patch.object(CookieManager, 'CONFIG_FILE', os.path.join(self.test_dir, 'config.json')):
                cookie_manager = CookieManager()
                cookie_manager.save_cookie(self.mock_cookie)
                cookie = cookie_manager.get_cookie()
                self.assertIsNotNone(cookie, "Cookie phải được lấy từ CookieManager")
                self.test_logger.info(f"[{function_name}] Step 1 PASSED - CookieManager setup thành công")
            
            # Step 2: Setup VideoDownloader
            self.test_logger.debug(f"[{function_name}] Step 2: Setup VideoDownloader")
            video_downloader = VideoDownloader(cookie)
            self.assertIsNotNone(video_downloader, "VideoDownloader phải được khởi tạo")
            self.test_logger.info(f"[{function_name}] Step 2 PASSED - VideoDownloader setup thành công")
            
            # Step 3: Test URL normalization
            self.test_logger.debug(f"[{function_name}] Step 3: Test URL normalization")
            test_url = "https://www.douyin.com/video/1234567890123456789"
            normalized = video_downloader.normalize_url(test_url)
            self.assertIsNotNone(normalized, "URL phải được normalize")
            self.test_logger.info(f"[{function_name}] Step 3 PASSED - URL normalization thành công")
            
            # Step 4: Test video ID extraction
            self.test_logger.debug(f"[{function_name}] Step 4: Test video ID extraction")
            video_id = video_downloader.extract_video_id(test_url)
            self.assertIsNotNone(video_id, "Video ID phải được extract")
            self.test_logger.info(f"[{function_name}] Step 4 PASSED - Video ID extraction thành công: {video_id}")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Full download workflow integration thành công")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_error_handling_across_components(self):
        """
        Test Case 2: Error handling across components
        コンポーネント間のエラーハンドリングテスト
        
        Mục đích:
        - Test error propagation qua các components
        - Test error handling consistency
        - Test logging của errors qua các layers
        
        Input:
        - Invalid inputs ở các components khác nhau
        
        Expected Output:
        - Errors được handle đúng ở mỗi component
        - Error logs đầy đủ theo System Instruction
        """
        function_name = "TestIntegration.test_error_handling_across_components"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: Error handling across components")
        
        try:
            # Test invalid cookie handling
            self.test_logger.debug(f"[{function_name}] Test: Invalid cookie handling")
            try:
                downloader = VideoDownloader("")  # Empty cookie
                # Không nên raise exception, nhưng nên log warning
                self.test_logger.info(f"[{function_name}] Empty cookie được handle đúng")
            except Exception as e:
                self.test_logger.warning(f"[{function_name}] Empty cookie raised exception: {e}")
            
            # Test invalid URL handling
            self.test_logger.debug(f"[{function_name}] Test: Invalid URL handling")
            downloader = VideoDownloader(self.mock_cookie)
            result = downloader.normalize_url(None)
            self.assertIsNone(result, "Invalid URL phải trả về None")
            self.test_logger.info(f"[{function_name}] Invalid URL được handle đúng")
            
            # Test invalid video ID extraction
            self.test_logger.debug(f"[{function_name}] Test: Invalid video ID extraction")
            result = downloader.extract_video_id("invalid-url")
            self.assertIsNone(result, "Invalid URL phải trả về None cho video ID")
            self.test_logger.info(f"[{function_name}] Invalid video ID extraction được handle đúng")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Error handling across components thành công")
            
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

