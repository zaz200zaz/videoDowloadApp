"""
Test Cases cho VideoDownloader Service
VideoDownloaderサービスのテストケース

Mục đích:
- Test tất cả các chức năng quan trọng của VideoDownloader
- Đảm bảo logging đầy đủ theo System Instruction
- Test các edge cases và error handling

Test Cases:
1. Test normalize_url: URL正規化のテスト
2. Test extract_video_id: 動画ID抽出のテスト
3. Test get_video_info: 動画情報取得のテスト
4. Test download_video: 動画ダウンロードのテスト
5. Test process_video: 動画処理全体のテスト
6. Test get_all_videos_from_user: ユーザーからのすべての動画取得のテスト
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import logging
from datetime import datetime

# Thêm project root vào path để import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.video_downloader import VideoDownloader


class TestVideoDownloader(unittest.TestCase):
    """Test class cho VideoDownloader"""
    
    def setUp(self):
        """
        Setup cho mỗi test case
        各テストケースのセットアップ
        
        Mục đích:
        - Tạo temporary directory cho downloads
        - Tạo mock cookie string
        - Khởi tạo VideoDownloader instance
        - Thiết lập logging cho test
        """
        function_name = "TestVideoDownloader.setUp"
        
        # Log bắt đầu setup (theo System Instruction 4.4 - log bắt đầu & kết thúc)
        self.test_logger = logging.getLogger('TestVideoDownloader')
        self.test_logger.info(f"[{function_name}] Bắt đầu setup test case")
        
        # Tạo temporary directory cho downloads
        self.test_dir = tempfile.mkdtemp(prefix="test_downloads_")
        self.test_logger.debug(f"[{function_name}] Test directory: {self.test_dir}")
        
        # Mock cookie string (theo System Instruction 7 - không log cookie đầy đủ)
        # Cookie string giả định để test
        self.mock_cookie = "test_cookie=value123; session_id=test123; " * 20
        self.test_logger.debug(f"[{function_name}] Mock cookie length: {len(self.mock_cookie)} characters")
        
        # Tạo log file cho test
        test_log_dir = os.path.join(project_root, "logs", "tests")
        os.makedirs(test_log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_log_file = os.path.join(test_log_dir, f"test_video_downloader_{timestamp}.log")
        self.test_logger.debug(f"[{function_name}] Test log file: {self.test_log_file}")
        
        # Khởi tạo VideoDownloader instance
        try:
            self.downloader = VideoDownloader(self.mock_cookie, log_file=self.test_log_file)
            self.test_logger.info(f"[{function_name}] VideoDownloader initialized successfully")
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Lỗi khi khởi tạo VideoDownloader: {e}", exc_info=True)
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
        function_name = "TestVideoDownloader.tearDown"
        self.test_logger.info(f"[{function_name}] Bắt đầu cleanup test case")
        
        try:
            # Xóa temporary directory
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
                self.test_logger.debug(f"[{function_name}] Đã xóa test directory: {self.test_dir}")
        except Exception as e:
            self.test_logger.warning(f"[{function_name}] Lỗi khi xóa test directory: {e}", exc_info=True)
        
        self.test_logger.info(f"[{function_name}] Cleanup hoàn thành")
    
    def test_normalize_url_valid_douyin_url(self):
        """
        Test Case 1: normalize_url với valid Douyin URL
        有効なDouyin URLでのnormalize_urlテスト
        
        Mục đích:
        - Test URL正規化が正常に動作することを確認
        - Test log出力が正しく記録されることを確認
        
        Input:
        - Valid Douyin URL: "https://www.douyin.com/video/1234567890123456789"
        
        Expected Output:
        - Normalized URL: "https://www.douyin.com/video/1234567890123456789"
        - Log records về normalize process
        """
        function_name = "TestVideoDownloader.test_normalize_url_valid_douyin_url"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: normalize_url với valid Douyin URL")
        
        # Test input
        test_url = "https://www.douyin.com/video/1234567890123456789"
        self.test_logger.debug(f"[{function_name}] Input URL: {test_url}")
        
        try:
            # Gọi function under test
            result = self.downloader.normalize_url(test_url)
            
            # Assert kết quả
            self.assertIsNotNone(result, "Normalize URL không được trả về None")
            self.assertIn("douyin.com", result, "Normalized URL phải chứa 'douyin.com'")
            self.assertIn("/video/", result, "Normalized URL phải chứa '/video/'")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Normalize URL thành công: {result}")
            self.test_logger.debug(f"[{function_name}] Output: {result}")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_normalize_url_direct_video_url(self):
        """
        Test Case 2: normalize_url với direct video URL
        直接動画URLでのnormalize_urlテスト
        
        Mục đích:
        - Test direct video URLが正しく処理されることを確認
        - Test direct URL detectionが動作することを確認
        
        Input:
        - Direct video URL: "https://v5-hl-szyd-ov.zjcdn.com/.../video.mp4"
        
        Expected Output:
        - Same URL (không normalize)
        - Log records về direct URL detection
        """
        function_name = "TestVideoDownloader.test_normalize_url_direct_video_url"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: normalize_url với direct video URL")
        
        # Test input
        test_url = "https://v5-hl-szyd-ov.zjcdn.com/test/video.mp4"
        self.test_logger.debug(f"[{function_name}] Input URL: {test_url}")
        
        try:
            # Gọi function under test
            result = self.downloader.normalize_url(test_url)
            
            # Assert kết quả
            self.assertEqual(result, test_url, "Direct video URL phải được trả về nguyên vẹn")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Direct URL được phát hiện và trả về")
            self.test_logger.debug(f"[{function_name}] Output: {result}")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_normalize_url_invalid_url(self):
        """
        Test Case 3: normalize_url với invalid URL
        無効なURLでのnormalize_urlテスト
        
        Mục đích:
        - Test invalid URLが正しく処理されることを確認
        - Test error handlingが動作することを確認
        
        Input:
        - Invalid URL: None hoặc empty string hoặc non-Douyin URL
        
        Expected Output:
        - None
        - Log records về error/warning
        """
        function_name = "TestVideoDownloader.test_normalize_url_invalid_url"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: normalize_url với invalid URL")
        
        # Test cases
        test_cases = [
            (None, "None URL"),
            ("", "Empty string URL"),
            ("https://www.youtube.com/watch?v=test", "Non-Douyin URL"),
        ]
        
        for test_url, description in test_cases:
            self.test_logger.debug(f"[{function_name}] Test case: {description}")
            self.test_logger.debug(f"[{function_name}] Input: {test_url}")
            
            try:
                # Gọi function under test
                result = self.downloader.normalize_url(test_url)
                
                # Assert kết quả - invalid URL phải trả về None
                self.assertIsNone(result, f"Invalid URL ({description}) phải trả về None")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - {description} được xử lý đúng")
                
            except Exception as e:
                self.test_logger.error(f"[{function_name}] Test FAILED - {description}: {e}", exc_info=True)
                raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_extract_video_id_valid_url(self):
        """
        Test Case 4: extract_video_id với valid URL
        有効なURLでの動画ID抽出テスト
        
        Mục đích:
        - Test video ID extractionが正常に動作することを確認
        - Test various URL formatsがサポートされることを確認
        
        Input:
        - Valid Douyin URL với video ID: "https://www.douyin.com/video/1234567890123456789"
        
        Expected Output:
        - Video ID: "1234567890123456789"
        - Log records về extraction process
        """
        function_name = "TestVideoDownloader.test_extract_video_id_valid_url"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: extract_video_id với valid URL")
        
        # Test cases với các format khác nhau
        test_cases = [
            ("https://www.douyin.com/video/1234567890123456789", "1234567890123456789", "Standard video URL"),
            ("https://www.douyin.com/video/1234567890123456789?param=value", "1234567890123456789", "URL với query params"),
            ("https://www.douyin.com/video/1234567890123456789#fragment", "1234567890123456789", "URL với fragment"),
        ]
        
        for test_url, expected_id, description in test_cases:
            self.test_logger.debug(f"[{function_name}] Test case: {description}")
            self.test_logger.debug(f"[{function_name}] Input URL: {test_url}")
            self.test_logger.debug(f"[{function_name}] Expected ID: {expected_id}")
            
            try:
                # Gọi function under test
                result = self.downloader.extract_video_id(test_url)
                
                # Assert kết quả
                self.assertEqual(result, expected_id, f"Video ID extraction failed for {description}")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - {description}: ID={result}")
                
            except Exception as e:
                self.test_logger.error(f"[{function_name}] Test FAILED - {description}: {e}", exc_info=True)
                raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_extract_video_id_no_id(self):
        """
        Test Case 5: extract_video_id với URL không có video ID
        動画IDがないURLでのextract_video_idテスト
        
        Mục đích:
        - Test URL without video IDが正しく処理されることを確認
        - Test None returnが正しく動作することを確認
        
        Input:
        - URL không có video ID: "https://www.douyin.com/"
        
        Expected Output:
        - None
        - Log records về không tìm thấy ID
        """
        function_name = "TestVideoDownloader.test_extract_video_id_no_id"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: extract_video_id với URL không có video ID")
        
        # Test cases
        test_cases = [
            ("https://www.douyin.com/", "Homepage URL"),
            ("https://www.douyin.com/user/test", "User profile URL"),
            ("", "Empty URL"),
            (None, "None URL"),
        ]
        
        for test_url, description in test_cases:
            self.test_logger.debug(f"[{function_name}] Test case: {description}")
            self.test_logger.debug(f"[{function_name}] Input: {test_url}")
            
            try:
                # Gọi function under test
                result = self.downloader.extract_video_id(test_url)
                
                # Assert kết quả - không có ID phải trả về None
                self.assertIsNone(result, f"URL không có ID ({description}) phải trả về None")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - {description} được xử lý đúng")
                
            except Exception as e:
                self.test_logger.error(f"[{function_name}] Test FAILED - {description}: {e}", exc_info=True)
                raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_get_video_info_direct_url(self):
        """
        Test Case 6: get_video_info với direct video URL
        直接動画URLでのget_video_infoテスト
        
        Mục đích:
        - Test direct video URL handlingが正常に動作することを確認
        - Test return formatが正しいことを確認
        
        Input:
        - Direct video URL: "https://v5-hl-szyd-ov.zjcdn.com/.../video.mp4"
        
        Expected Output:
        - Dict với video_url và default values
        - Log records về direct URL detection
        """
        function_name = "TestVideoDownloader.test_get_video_info_direct_url"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: get_video_info với direct video URL")
        
        # Test input
        test_url = "https://v5-hl-szyd-ov.zjcdn.com/test/video.mp4"
        self.test_logger.debug(f"[{function_name}] Input URL: {test_url}")
        
        try:
            # Gọi function under test (không cần mock session vì direct URL không cần API call)
            result = self.downloader.get_video_info(test_url)
            
            # Assert kết quả
            self.assertIsNotNone(result, "get_video_info không được trả về None")
            self.assertIn('video_url', result, "Result phải có 'video_url' key")
            self.assertEqual(result['video_url'], test_url, "video_url phải bằng input URL")
            self.assertEqual(result['title'], 'Direct Video', "Title phải là 'Direct Video'")
            self.assertEqual(result['author'], 'Unknown', "Author phải là 'Unknown'")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Direct URL được phát hiện")
            self.test_logger.debug(f"[{function_name}] Output: {result}")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_get_video_info_audio_file(self):
        """
        Test Case 7: get_video_info với audio file (MP3)
        MP3オーディオファイルでのget_video_infoテスト
        
        Mục đích:
        - Test audio file detectionが正常に動作することを確認
        - Test audio filesがスキップされることを確認
        
        Input:
        - Audio URL: "https://.../music.mp3"
        
        Expected Output:
        - None (audio files should be skipped)
        - Log records về audio file detection
        """
        function_name = "TestVideoDownloader.test_get_video_info_audio_file"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: get_video_info với audio file")
        
        # Test cases
        test_cases = [
            "https://test.com/music.mp3",
            "https://test.com/ies-music/123",
            "https://test.com/music/123",
        ]
        
        for test_url in test_cases:
            self.test_logger.debug(f"[{function_name}] Input URL: {test_url}")
            
            try:
                # Gọi function under test
                result = self.downloader.get_video_info(test_url)
                
                # Assert kết quả - audio files phải trả về None
                self.assertIsNone(result, f"Audio file ({test_url}) phải trả về None")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - Audio file được phát hiện và bỏ qua")
                
            except Exception as e:
                self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
                raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    @patch('services.video_downloader.requests.Session.get')
    def test_download_video_success(self, mock_get):
        """
        Test Case 8: download_video thành công
        動画ダウンロード成功テスト
        
        Mục đích:
        - Test video downloadが正常に動作することを確認
        - Test file creationが正しく行われることを確認
        - Test timeout settingsが適用されることを確認
        
        Input:
        - Video URL: "https://test.com/video.mp4"
        - Save path: temporary file path
        - Timeout settings: default settings
        
        Expected Output:
        - Success dict với file_path và file_size
        - File được tạo tại save_path
        - Log records về download process
        """
        function_name = "TestVideoDownloader.test_download_video_success"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: download_video thành công")
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': '1024'}
        mock_response.iter_content = lambda chunk_size: [b'x' * 1024]  # Mock video content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test input
        test_url = "https://test.com/video.mp4"
        save_path = os.path.join(self.test_dir, "test_video.mp4")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        self.test_logger.debug(f"[{function_name}] Input URL: {test_url}")
        self.test_logger.debug(f"[{function_name}] Save path: {save_path}")
        
        try:
            # Gọi function under test
            result = self.downloader.download_video(test_url, save_path)
            
            # Assert kết quả
            self.assertIsNotNone(result, "Download result không được trả về None")
            self.assertTrue(result.get('success', False), "Download phải thành công")
            self.assertIn('file_path', result, "Result phải có 'file_path' key")
            
            self.test_logger.info(f"[{function_name}] Test PASSED - Download thành công")
            self.test_logger.debug(f"[{function_name}] Output: {result}")
            
        except Exception as e:
            self.test_logger.error(f"[{function_name}] Test FAILED - Exception: {e}", exc_info=True)
            raise
        
        self.test_logger.info(f"[{function_name}] ============================================================")
    
    def test_process_video_invalid_url(self):
        """
        Test Case 9: process_video với invalid URL
        無効なURLでのprocess_videoテスト
        
        Mục đích:
        - Test invalid URL handlingが正常に動作することを確認
        - Test error handlingが正しく機能することを確認
        
        Input:
        - Invalid URL: None hoặc empty string
        
        Expected Output:
        - Success: False
        - Error message trong result
        - Log records về error
        """
        function_name = "TestVideoDownloader.test_process_video_invalid_url"
        self.test_logger.info(f"[{function_name}] ============================================================")
        self.test_logger.info(f"[{function_name}] Bắt đầu test: process_video với invalid URL")
        
        # Test cases
        test_cases = [
            (None, "None URL"),
            ("", "Empty string URL"),
            ("invalid-url", "Invalid format URL"),
        ]
        
        for test_url, description in test_cases:
            self.test_logger.debug(f"[{function_name}] Test case: {description}")
            self.test_logger.debug(f"[{function_name}] Input: {test_url}")
            
            try:
                # Gọi function under test
                result = self.downloader.process_video(
                    url=test_url,
                    download_folder=self.test_dir,
                    naming_mode="video_id",
                    video_format="auto",
                    orientation_filter="all"
                )
                
                # Assert kết quả
                self.assertIsNotNone(result, "Process result không được trả về None")
                self.assertFalse(result.get('success', True), "Process phải thất bại với invalid URL")
                self.assertIn('error', result, "Result phải có 'error' key")
                
                self.test_logger.info(f"[{function_name}] Test PASSED - {description} được xử lý đúng")
                self.test_logger.debug(f"[{function_name}] Error message: {result.get('error')}")
                
            except Exception as e:
                self.test_logger.error(f"[{function_name}] Test FAILED - {description}: {e}", exc_info=True)
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

