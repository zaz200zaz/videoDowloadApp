"""
Download Controller
ダウンロード管理のコントローラー
"""

from typing import List, Dict, Callable, Optional
from models.cookie_manager import CookieManager
from services.video_downloader import VideoDownloader
from services.download_service import DownloadService


class DownloadController:
    """ダウンロード管理のコントローラー"""
    
    def __init__(self, cookie_manager: CookieManager):
        """
        初期化
        
        Args:
            cookie_manager: CookieManagerインスタンス
        """
        self.cookie_manager = cookie_manager
        self.download_service: Optional[DownloadService] = None
    
    def initialize_downloader(self, logger=None) -> tuple[bool, Optional[str]]:
        """
        ダウンローダーを初期化
        
        Args:
            logger: ロガーインスタンス（オプション）
            
        Returns:
            (成功フラグ, エラーメッセージ) のタプル
        """
        cookie = self.cookie_manager.get_cookie()
        if not cookie:
            if logger:
                logger.warning("DownloadController.initialize_downloader - Cookie not found")
            return False, "Cookie chưa được lưu. Vui lòng lưu cookie trước."
        
        try:
            # DownloadServiceを作成
            self.download_service = DownloadService(cookie, logger)
            if logger:
                logger.info("DownloadController.initialize_downloader - DownloadService created successfully")
            return True, None
        except Exception as e:
            if logger:
                logger.error(f"DownloadController.initialize_downloader - Error: {e}", exc_info=True)
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
        if not links:
            return False, "Không có link nào để tải"
        
        if not self.download_service:
            success, error = self.initialize_downloader()
            if not success:
                return False, error
        
        # 設定を取得
        download_folder = self.cookie_manager.get_download_folder()
        naming_mode = self.cookie_manager.get_setting("naming_mode", "video_id")
        video_format = self.cookie_manager.get_setting("video_format", "auto")
        orientation_filter = self.cookie_manager.get_setting("orientation_filter", "all")
        
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
        
        return True, None
    
    def stop_download(self):
        """ダウンロードを停止"""
        if self.download_service:
            if hasattr(self.download_service, 'logger') and self.download_service.logger:
                self.download_service.logger.info("DownloadController.stop_download called - stopping download_service")
            self.download_service.stop_download()
        else:
            # DownloadServiceが初期化されていない場合
            # これは通常、ダウンロードが開始されていないか、既に完了していることを意味します
            # ログに記録するだけ
            pass
    
    def get_user_videos(self, user_url: str) -> tuple[bool, List[str], Optional[str]]:
        """
        ユーザーのビデオリストを取得
        
        Args:
            user_url: ユーザーURL
            
        Returns:
            (成功フラグ, ビデオリンクリスト, エラーメッセージ) のタプル
        """
        cookie = self.cookie_manager.get_cookie()
        if not cookie:
            return False, [], "Cookie chưa được lưu"
        
        try:
            downloader = VideoDownloader(cookie)
            video_urls = downloader.get_all_videos_from_user(user_url)
            return True, video_urls, None
        except Exception as e:
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
        
        successful_videos = [r for r in results if r.get('success') and r.get('file_path')]
        
        deleted_count = 0
        failed_count = 0
        failed_files = []
        
        for video_result in successful_videos:
            file_path = video_result.get('file_path')
            if not file_path:
                continue
            
            # 絶対パスに変換
            if not os.path.isabs(file_path):
                download_folder = self.cookie_manager.get_download_folder()
                if download_folder:
                    file_path = os.path.join(download_folder, file_path)
            
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    # 結果を更新
                    video_result['success'] = False
                    video_result['error'] = 'Đã xóa'
                    video_result['file_path'] = None
                except Exception as e:
                    failed_count += 1
                    failed_files.append(file_path)
        
        return deleted_count, failed_count, failed_files

