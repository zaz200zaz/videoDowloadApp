"""
Test Cases cho DownloadService
DownloadServiceのテストケース

Mục đích:
- Test tất cả các chức năng quan trọng của DownloadService
- Test multi-threading behavior
- Test progress callbacks và result callbacks
- Đảm bảo logging đầy đủ theo System Instruction

Test Cases:
1. Test start_download: ダウンロード開始のテスト
2. Test stop_download: ダウンロード停止のテスト
3. Test progress_callback: 進捗コールバックのテスト
4. Test result_callback: 結果コールバックのテスト
5. Test complete_callback: 完了コールバックのテスト
"""

import unittest
import os
import sys
import tempfile
import shutil
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import logging
from datetime import datetime

# Thêm project root vào path để import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.download_service import DownloadService


class TestDownloadService(unittest.TestCase):
    """Test class cho DownloadService"""
    
    def setUp(self):
        """
        Setup cho mỗi test case
        各テストケースのセットアップ
        
        Mục đích:
        - Tạo temporary directory cho downloads
        - Tạo mock cookie string
        - Khởi tạo DownloadService instance
        - Thiết lập logging cho test
        """
        function_name = "TestDownloadService.setUp"
        
        # Log bắt đầu setup (theo System Instruction 4.4)
        self.test_logger = logging.getLogger('TestDownloadService')
        self.test_logger.info(f"[{function_name}] Bắt đầu setup test case")
        
        # Tạo temporary directory cho downloads
        self.test_dir = tempfile.mkdtemp(prefix="test_downloads_service_")
        self.test_logger.debug(f"[{function_name}] Test directory: {self.test_dir}")
        
        # Mock cookie string (theo System Instruction 7 - không log cookie đầy đủ)
        self.mock_cookie = "test_cookie=value123; session_id=test123; " * 20
        self.test_logger.debug(f"[{function_name}] Mock cookie length: {len(self.mock_cookie)} characters")
        
        # Tạo logger cho DownloadService
        test_log_dir = os.path.join(project_root, "logs", "tests")
        os.makedirs(test_log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        service_logger = logging.getLogger('DownloadService')
        service_logger.setLevel(logging.DEBUG)
        # Đóng các handler cũ để tránh ResourceWarning (theo System Instruction 8)
        for handler in service_logger.handlers[:]:
            if hasattr(handler, 'close'):
                handler.close()
            service_logger.removeHandler(handler)
        service_logger.handlers = []
        
        log_file = os.path.join(test_log_dir, f"test_download_service_{timestamp}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        service_logger.addHandler(file_handler)
        
        self.test_logger.debug(f"[{function_name}] Service log file: {log_file}")
        
        # Khởi tạo DownloadService instance
        try:
            self.service = DownloadService(self.mock_cookie, logger=service_logger)
            self.test_logger.info(f"[{function_name}] DownloadService initialized successfully")
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Lỗi khi khởi tạo DownloadService: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] Setup hoàn thành")
    
    def tearDown(self):
        """
        Cleanup sau mỗi test case
        各テストケース後のクリーンアップ
        
        Mục đích:
        - Stop download nếu đang chạy
        - Xóa temporary directory
        - Cleanup các file test tạo ra
        """
        function_name = "TestDownloadService.tearDown"
        self.test_logger.info(f"[{function_name}] Bắt đầu cleanup test case")
        
        try:
            # Stop download nếu đang chạy
            if self.service.is_downloading:
                self.test_logger.debug(f"[{function_name}] Đang stop download...")
                self.service.stop_download()
                # Đợi thread kết thúc
                if self.service.download_thread and self.service.download_thread.is_alive():
                    self.service.download_thread.join(timeout=5)
            
            # Xóa temporary directory
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
                self.test_logger.debug(f"[{function_name}] Đã xóa test directory: {self.test_dir}")
        except Exception as e:
            self.test_logger.warning(f"[{function_name}] Lỗi khi cleanup: {e}", exc_info=True)
        
        self.test_logger.info(f"[{function_name}] Cleanup hoàn thành")
    
    def test_start_download_empty_links(self):
        """
        Test Case 1: start_download với empty links
        空のリンクリストでのstart_downloadテスト
        
        Mục đích:
        - Test empty links listが正しく処理されることを確認
        - Test download không được開始することを確認
        
        Input:
        - Empty links list: []
        
        Expected Output:
        - Download không được started
        - is_downloading = False
        - Log records về empty links
        """
        function_name = "TestDownloadService.test_start_download_empty_links"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: start_download với empty links")
        
        # Test input
        empty_links = []
        self.test_logger.debug(f"[{function_name}] Input links: {empty_links}")
        
        try:
            # Setup callbacks
            progress_callback = Mock()
            result_callback = Mock()
            complete_callback = Mock()
            
            # Gọi function under test
            self.service.start_download(
                links=empty_links,
                download_folder=self.test_dir,
                naming_mode="video_id",
                video_format="auto",
                orientation_filter="all",
                progress_callback=progress_callback,
                result_callback=result_callback,
                complete_callback=complete_callback
            )
            
            # Đợi thread kết thúc
            if self.service.download_thread and self.service.download_thread.is_alive():
                self.service.download_thread.join(timeout=5)
            
            # Assert kết quả
            self.assertFalse(self.service.is_downloading, "Download không được started với empty links")
            
            # Complete callback phải được gọi
            complete_callback.assert_called_once()
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Empty links được xử lý đúng")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_stop_download(self):
        """
        Test Case 2: stop_download
        ダウンロード停止テスト
        
        Mục đích:
        - Test stop_downloadが正常に動作することを確認
        - Test should_stop flagが設定されることを確認
        - Test is_downloading flagが更新されることを確認
        
        Input:
        - Download đang chạy
        
        Expected Output:
        - should_stop = True
        - is_downloading = False
        - Log records về stop action
        """
        function_name = "TestDownloadService.test_stop_download"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: stop_download")
        
        try:
            # Setup initial state
            self.service.is_downloading = True
            self.service.should_stop = False
            self.test_logger.debug(f"[{function_name}] Initial state: is_downloading={self.service.is_downloading}, should_stop={self.service.should_stop}")
            
            # Gọi function under test
            self.service.stop_download()
            
            # Assert kết quả
            self.assertTrue(self.service.should_stop, "should_stop phải được set thành True")
            self.assertFalse(self.service.is_downloading, "is_downloading phải được set thành False")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Stop download thành công")
            self.test_logger.debug(f"[{function_name}] Final state: is_downloading={self.service.is_downloading}, should_stop={self.service.should_stop}")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_progress_callback(self):
        """
        Test Case 3: progress_callback
        進捗コールバックテスト
        
        Mục đích:
        - Test progress callbackが正しく呼び出されることを確認
        - Test callback parametersが正しいことを確認
        
        Input:
        - Progress callback function
        - Download links list
        
        Expected Output:
        - Progress callback được gọi với đúng parameters
        - Progress values trong range [0, 100]
        - Log records về progress updates
        """
        function_name = "TestDownloadService.test_progress_callback"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: progress_callback")
        
        try:
            # Setup mock progress callback
            progress_callback = Mock()
            progress_values = []
            
            def capture_progress(progress, current, total):
                progress_values.append((progress, current, total))
                progress_callback(progress, current, total)
            
            # Test input
            test_links = [
                "https://test.com/video1.mp4",
                "https://test.com/video2.mp4",
            ]
            self.test_logger.debug(f"[{function_name}] Input links: {test_links}")
            
            # Mock VideoDownloader để không thực sự download
            with patch('services.download_service.VideoDownloader') as mock_downloader_class:
                mock_downloader = Mock()
                mock_downloader.process_video = Mock(return_value={
                    'success': True,
                    'video_id': 'test123',
                    'file_path': os.path.join(self.test_dir, 'test.mp4'),
                    'error': None
                })
                mock_downloader_class.return_value = mock_downloader
                
                # Gọi function under test
                self.service.start_download(
                    links=test_links,
                    download_folder=self.test_dir,
                    naming_mode="video_id",
                    video_format="auto",
                    orientation_filter="all",
                    progress_callback=capture_progress,
                    result_callback=Mock(),
                    complete_callback=Mock()
                )
                
                # Đợi thread kết thúc
                if self.service.download_thread and self.service.download_thread.is_alive():
                    self.service.download_thread.join(timeout=10)
                
                # Assert kết quả
                # Progress callback phải được gọi ít nhất một lần
                self.assertGreater(len(progress_values), 0, "Progress callback phải được gọi ít nhất một lần")
                
                # Kiểm tra progress values
                for progress, current, total in progress_values:
                    self.assertGreaterEqual(progress, 0, "Progress phải >= 0")
                    self.assertLessEqual(progress, 100, "Progress phải <= 100")
                    self.assertGreaterEqual(current, 0, "Current phải >= 0")
                    self.assertLessEqual(current, total, "Current phải <= total")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - Progress callback được gọi {len(progress_values)} lần")
                self.test_logger.debug(f"[{function_name}] Progress values: {progress_values}")
                
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_result_callback(self):
        """
        Test Case 4: result_callback
        結果コールバックテスト
        
        Mục đích:
        - Test result callbackが正しく呼び出されることを確認
        - Test callback parametersが正しいことを確認
        
        Input:
        - Result callback function
        - Download links list
        
        Expected Output:
        - Result callback được gọi với đúng parameters
        - Result dict có đúng structure
        - Log records về result updates
        """
        function_name = "TestDownloadService.test_result_callback"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: result_callback")
        
        try:
            # Setup mock result callback
            result_callback = Mock()
            result_values = []
            
            def capture_result(result):
                result_values.append(result)
                result_callback(result)
            
            # Test input
            test_links = ["https://test.com/video1.mp4"]
            self.test_logger.debug(f"[{function_name}] Input links: {test_links}")
            
            # Mock VideoDownloader
            with patch('services.download_service.VideoDownloader') as mock_downloader_class:
                mock_downloader = Mock()
                mock_downloader.process_video = Mock(return_value={
                    'success': True,
                    'video_id': 'test123',
                    'file_path': os.path.join(self.test_dir, 'test.mp4'),
                    'error': None
                })
                mock_downloader_class.return_value = mock_downloader
                
                # Gọi function under test
                self.service.start_download(
                    links=test_links,
                    download_folder=self.test_dir,
                    naming_mode="video_id",
                    video_format="auto",
                    orientation_filter="all",
                    progress_callback=Mock(),
                    result_callback=capture_result,
                    complete_callback=Mock()
                )
                
                # Đợi thread kết thúc
                if self.service.download_thread and self.service.download_thread.is_alive():
                    self.service.download_thread.join(timeout=10)
                
                # Assert kết quả
                # Result callback phải được gọi
                self.assertGreater(len(result_values), 0, "Result callback phải được gọi ít nhất một lần")
                
                # Kiểm tra result structure
                for result in result_values:
                    self.assertIn('success', result, "Result phải có 'success' key")
                    self.assertIsInstance(result['success'], bool, "'success' phải là boolean")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - Result callback được gọi {len(result_values)} lần")
                self.test_logger.debug(f"[{function_name}] Result values: {result_values}")
                
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_complete_callback(self):
        """
        Test Case 5: complete_callback
        完了コールバックテスト
        
        Mục đích:
        - Test complete callbackが正しく呼び出されることを確認
        - Test callbackがdownload完了時に呼び出されることを確認
        
        Input:
        - Complete callback function
        - Download links list
        
        Expected Output:
        - Complete callback được gọi một lần khi download hoàn thành
        - Log records về completion
        """
        function_name = "TestDownloadService.test_complete_callback"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: complete_callback")
        
        try:
            # Setup mock complete callback
            complete_callback = Mock()
            
            # Test input
            test_links = ["https://test.com/video1.mp4"]
            self.test_logger.debug(f"[{function_name}] Input links: {test_links}")
            
            # Mock VideoDownloader
            with patch('services.download_service.VideoDownloader') as mock_downloader_class:
                mock_downloader = Mock()
                mock_downloader.process_video = Mock(return_value={
                    'success': True,
                    'video_id': 'test123',
                    'file_path': os.path.join(self.test_dir, 'test.mp4'),
                    'error': None
                })
                mock_downloader_class.return_value = mock_downloader
                
                # Gọi function under test
                self.service.start_download(
                    links=test_links,
                    download_folder=self.test_dir,
                    naming_mode="video_id",
                    video_format="auto",
                    orientation_filter="all",
                    progress_callback=Mock(),
                    result_callback=Mock(),
                    complete_callback=complete_callback
                )
                
                # Đợi thread kết thúc
                if self.service.download_thread and self.service.download_thread.is_alive():
                    self.service.download_thread.join(timeout=10)
                
                # Assert kết quả
                # Complete callback phải được gọi một lần
                complete_callback.assert_called_once()
                
                self.test_logger.info(f"[{function_name}] Test PASSED - Complete callback được gọi đúng")
                
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

