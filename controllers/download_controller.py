"""
Download Controller
Quản lý các thao tác liên quan đến download từ UI layer

Mục tiêu:
- Điều phối giữa UI và DownloadService
- Khởi tạo và quản lý download process
- Xử lý user videos và delete operations

Input/Output:
- Input: Video links, user URL, download settings
- Output: Download status, video URLs, results
"""

from typing import List, Dict, Callable, Optional
import os
from models.cookie_manager import CookieManager
from services.video_downloader import VideoDownloader
from services.download_service import DownloadService
from utils.log_helper import write_log, get_logger, log_api_call


class DownloadController:
    """
    Download管理のコントローラー
    
    Chức năng chính:
    - Khởi tạo DownloadService
    - Bắt đầu/dừng download
    - Lấy video từ user
    - Xóa video đã tải
    """
    
    def __init__(self, cookie_manager: CookieManager):
        """
        Khởi tạo DownloadController
        
        Args:
            cookie_manager: CookieManager instance
            
        Flow:
        1. Lưu reference đến CookieManager
        2. Khởi tạo download_service = None (sẽ được khởi tạo khi cần)
        3. Logger sẽ được set khi initialize_downloader được gọi
        """
        function_name = "DownloadController.__init__"
        self.cookie_manager = cookie_manager
        self.download_service: Optional[DownloadService] = None
        self.logger = None  # Logger will be set when needed
        
        temp_logger = get_logger('DownloadController')
        write_log('INFO', function_name, "DownloadController đã được khởi tạo", temp_logger)
    
    def initialize_downloader(self, logger=None) -> tuple[bool, Optional[str]]:
        """
        Khởi tạo DownloadService
        
        Args:
            logger: Logger instance (optional)
            
        Returns:
            tuple: (success: bool, error_message: Optional[str])
            
        Flow:
        1. Kiểm tra cookie có tồn tại không
        2. Tạo DownloadService với cookie
        3. Lưu logger reference
        
        Exceptions:
            Exception: Lỗi khi khởi tạo DownloadService
        """
        function_name = "DownloadController.initialize_downloader"
        self.logger = logger or get_logger('DownloadController')
        
        try:
            write_log('INFO', function_name, "Bắt đầu", self.logger)
            
            # Kiểm tra cookie
            cookie = self.cookie_manager.get_cookie()
            if not cookie:
                write_log('WARNING', function_name, "Cookie not found in CookieManager", self.logger)
                return False, "Cookie chưa được lưu. Vui lòng lưu cookie trước."
            
            write_log('INFO', function_name, f"Cookie found - length: {len(cookie)} characters", self.logger)
            write_log('DEBUG', function_name, f"Cookie preview: {cookie[:100]}...", self.logger)
            
            # Tạo DownloadService
            write_log('INFO', function_name, "Đang tạo DownloadService...", self.logger)
            self.download_service = DownloadService(cookie, self.logger)
            write_log('INFO', function_name, "DownloadService created successfully", self.logger)
            
            return True, None
            
        except Exception as e:
            write_log('ERROR', function_name, f"Error: {e}", self.logger, exc_info=True)
            return False, f"Lỗi khi khởi tạo downloader: {str(e)}"
    
    def start_download(
        self,
        links: List[str],
        progress_callback: Optional[Callable[[float, int, int], None]] = None,
        result_callback: Optional[Callable[[Dict], None]] = None,
        complete_callback: Optional[Callable[[], None]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        ダウンロードを開始
        
        Args:
            links: ビデオリンクのリスト
            progress_callback: 進捗コールバック (progress, current, total)
            result_callback: 結果コールバック (result_dict)
            complete_callback: 完了コールバック
            
        Returns:
            (成功フラグ, エラーメッセージ) のタプル
        """
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("DownloadController.start_download - Bắt đầu")
            self.logger.info(f"  - Số lượng link: {len(links) if links else 0}")
        
        if not links:
            if self.logger:
                self.logger.warning("Không có link nào để tải")
            return False, "Không có link nào để tải"
        
        if not self.download_service:
            if self.logger:
                self.logger.info("DownloadService chưa được khởi tạo, đang khởi tạo...")
            success, error = self.initialize_downloader(self.logger)
            if not success:
                if self.logger:
                    self.logger.error(f"Không thể khởi tạo DownloadService: {error}")
                return False, error
        
        # 設定を取得
        download_folder = self.cookie_manager.get_download_folder()
        naming_mode = self.cookie_manager.get_setting("naming_mode", "video_id")
        video_format = self.cookie_manager.get_setting("video_format", "auto")
        orientation_filter = self.cookie_manager.get_setting("orientation_filter", "all")
        
        if self.logger:
            self.logger.info("Đã lấy cấu hình:")
            self.logger.info(f"  - Download folder: {download_folder}")
            self.logger.info(f"  - Naming mode: {naming_mode}")
            self.logger.info(f"  - Video format: {video_format}")
            self.logger.info(f"  - Orientation filter: {orientation_filter}")
            self.logger.info("Đang gọi DownloadService.start_download...")
        
        try:
            # ダウンロードを開始
            self.download_service.start_download(
                links=links,
                download_folder=download_folder,
                naming_mode=naming_mode,
                video_format=video_format,
                orientation_filter=orientation_filter,
                progress_callback=progress_callback,
                result_callback=result_callback,
                complete_callback=complete_callback
            )
            
            if self.logger:
                self.logger.info("DownloadService.start_download được gọi thành công")
                self.logger.info("=" * 60)
            
            return True, None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Lỗi khi gọi DownloadService.start_download: {e}", exc_info=True)
                self.logger.error("=" * 60)
            return False, f"Lỗi khi bắt đầu download: {str(e)}"
    
    def stop_download(self):
        """
        Dừng download process
        
        Flow:
        1. Kiểm tra DownloadService có tồn tại không
        2. Gọi DownloadService.stop_download()
        
        Note:
            Nếu DownloadService chưa được khởi tạo, chỉ log warning
        """
        function_name = "DownloadController.stop_download"
        self.logger = self.logger or get_logger('DownloadController')
        
        try:
            write_log('INFO', function_name, "Được gọi", self.logger)
            write_log('DEBUG', function_name, f"DownloadService exists: {self.download_service is not None}", self.logger)
            
            if self.download_service:
                write_log('INFO', function_name, "Đang gọi DownloadService.stop_download...", self.logger)
                self.download_service.stop_download()
                write_log('INFO', function_name, "DownloadService.stop_download đã được gọi", self.logger)
            else:
                write_log('WARNING', function_name, 
                         "DownloadService chưa được khởi tạo, không thể dừng download", 
                         self.logger)
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi stop download: {e}", self.logger, exc_info=True)
    
    def get_user_videos(self, user_url: str) -> tuple[bool, List[str], Optional[str]]:
        """
        Lấy danh sách video từ user profile
        
        Args:
            user_url: URL của user profile (ví dụ: https://www.douyin.com/user/...)
            
        Returns:
            tuple: (success: bool, video_urls: List[str], error_message: Optional[str])
            
        Flow:
        1. Kiểm tra cookie có tồn tại không
        2. Tạo VideoDownloader với cookie
        3. Gọi get_all_videos_from_user()
        
        Exceptions:
            Exception: Lỗi khi lấy video từ user
        """
        function_name = "DownloadController.get_user_videos"
        self.logger = self.logger or get_logger('DownloadController')
        
        try:
            write_log('INFO', function_name, "Bắt đầu", self.logger)
            write_log('DEBUG', function_name, f"User URL: {user_url}", self.logger)
            
            # Kiểm tra cookie
            cookie = self.cookie_manager.get_cookie()
            if not cookie:
                write_log('WARNING', function_name, "Cookie chưa được lưu", self.logger)
                return False, [], "Cookie chưa được lưu"
            
            write_log('INFO', function_name, f"Cookie found - length: {len(cookie)} characters", self.logger)
            
            # Tạo VideoDownloader
            write_log('INFO', function_name, "Đang tạo VideoDownloader...", self.logger)
            downloader = VideoDownloader(cookie)
            write_log('INFO', function_name, "VideoDownloader created, đang lấy video từ user...", self.logger)
            
            # Lấy video URLs
            video_urls = downloader.get_all_videos_from_user(user_url)
            
            write_log('INFO', function_name, f"Đã lấy được {len(video_urls)} video từ user", self.logger)
            return True, video_urls, None
            
        except Exception as e:
            write_log('ERROR', function_name, f"Lỗi khi lấy video từ user: {e}", self.logger, exc_info=True)
            return False, [], f"Lỗi khi lấy video từ user: {str(e)}"
    
    def delete_downloaded_videos(self, results: List[Dict]) -> tuple[int, int, List[str]]:
        """
        ダウンロード済みビデオを削除
        
        Args:
            results: ダウンロード結果のリスト
            
        Returns:
            (削除成功数, 削除失敗数, 失敗ファイルリスト) のタプル
        """
        import os
        
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("DownloadController.delete_downloaded_videos - Bắt đầu")
            self.logger.info(f"  - Tổng số results: {len(results)}")
        
        successful_videos = [r for r in results if r.get('success') and r.get('file_path')]
        
        if self.logger:
            self.logger.info(f"  - Số video thành công cần xóa: {len(successful_videos)}")
        
        deleted_count = 0
        failed_count = 0
        failed_files = []
        
        for idx, video_result in enumerate(successful_videos):
            file_path = video_result.get('file_path')
            if not file_path:
                if self.logger:
                    self.logger.warning(f"  Video {idx+1}: Không có file_path, bỏ qua")
                continue
            
            # 絶対パスに変換
            if not os.path.isabs(file_path):
                download_folder = self.cookie_manager.get_download_folder()
                if download_folder:
                    file_path = os.path.join(download_folder, file_path)
            
            if self.logger:
                self.logger.info(f"  Đang xóa video {idx+1}/{len(successful_videos)}: {file_path}")
            
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    # 結果を更新
                    video_result['success'] = False
                    video_result['error'] = 'Đã xóa'
                    video_result['file_path'] = None
                    
                    if self.logger:
                        self.logger.info(f"    ✓ Đã xóa thành công")
                except Exception as e:
                    failed_count += 1
                    failed_files.append(file_path)
                    if self.logger:
                        self.logger.error(f"    ✗ Lỗi khi xóa: {e}", exc_info=True)
            else:
                if self.logger:
                    self.logger.warning(f"    File không tồn tại: {file_path}")
        
        if self.logger:
            self.logger.info(f"Kết quả: Đã xóa {deleted_count}, Thất bại {failed_count}")
            self.logger.info("=" * 60)
        
        return deleted_count, failed_count, failed_files

