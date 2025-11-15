"""
Download Service
ダウンロード管理サービス
"""

import threading
from typing import List, Dict, Callable, Optional
from services.video_downloader import VideoDownloader


class DownloadService:
    """ダウンロード管理サービス"""
    
    def __init__(self, cookie: str, logger=None):
        """
        初期化
        
        Args:
            cookie: Cookie文字列
            logger: ロガーインスタンス（オプション）
        """
        self.cookie = cookie
        self.logger = logger
        self.downloader: Optional[VideoDownloader] = None
        self.is_downloading = False
        self.should_stop = False
        self.download_thread: Optional[threading.Thread] = None
        # DownloadServiceのインスタンスをVideoDownloaderに渡すための参照
        self._service_ref = None
    
    def start_download(
        self,
        links: List[str],
        download_folder: str,
        naming_mode: str = "video_id",
        video_format: str = "auto",
        orientation_filter: str = "all",
        progress_callback: Optional[Callable[[float, int, int], None]] = None,
        result_callback: Optional[Callable[[Dict], None]] = None,
        complete_callback: Optional[Callable[[], None]] = None
    ):
        """
        ダウンロードを開始
        
        Args:
            links: ビデオリンクのリスト
            download_folder: ダウンロードフォルダ
            naming_mode: ファイル名モード
            video_format: ビデオフォーマット
            progress_callback: 進捗コールバック
            result_callback: 結果コールバック
            complete_callback: 完了コールバック
        """
        # Đảm bảo download_folder là絶対パス
        import os
        download_folder = os.path.abspath(download_folder)
        
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("DownloadService.start_download - Bắt đầu")
            self.logger.info(f"  - Số lượng link: {len(links)}")
            self.logger.info(f"  - Download folder: {download_folder}")
            self.logger.info(f"  - Naming mode: {naming_mode}")
            self.logger.info(f"  - Video format: {video_format}")
            self.logger.info(f"  - Orientation filter: {orientation_filter}")
            self.logger.info(f"  - Current is_downloading: {self.is_downloading}")
            self.logger.info(f"  - Current should_stop: {self.should_stop}")
        
        if self.is_downloading:
            if self.logger:
                self.logger.warning("Download already in progress - cannot start new download")
            return
        
        try:
            # ダウンローダーを初期化
            if self.logger:
                self.logger.info("Đang khởi tạo VideoDownloader...")
                self.logger.debug(f"Cookie length: {len(self.cookie) if self.cookie else 0} characters")
            
            self.downloader = VideoDownloader(self.cookie, log_file=None)
            # DownloadServiceの参照を渡して、停止フラグをチェックできるようにする
            self.downloader._service_ref = self
            
            if self.logger:
                self.logger.info("VideoDownloader initialized successfully")
                self.logger.info(f"DownloadService initialized, should_stop={self.should_stop}")
            
            # 状態をリセット
            self.is_downloading = True
            self.should_stop = False
            
            if self.logger:
                self.logger.info("Đang tạo download thread...")
            
            # ダウンロードスレッドを開始
            self.download_thread = threading.Thread(
                target=self._download_worker,
                args=(links, download_folder, naming_mode, video_format, orientation_filter,
                      progress_callback, result_callback, complete_callback),
                daemon=True
            )
            self.download_thread.start()
            
            if self.logger:
                self.logger.info(f"Download thread started - Thread ID: {self.download_thread.ident}")
                self.logger.info("=" * 60)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Lỗi khi khởi tạo download: {e}", exc_info=True)
            self.is_downloading = False
            self.should_stop = False
            raise
    
    def _download_worker(
        self,
        links: List[str],
        download_folder: str,
        naming_mode: str,
        video_format: str,
        orientation_filter: str,
        progress_callback: Optional[Callable[[float, int, int], None]],
        result_callback: Optional[Callable[[Dict], None]],
        complete_callback: Optional[Callable[[], None]]
    ):
        """ダウンロードワーカースレッド"""
        import time
        total = len(links)
        success_count = 0
        failed_count = 0
        total_download_size = 0
        start_time = time.time()
        
        # Đảm bảo download_folder là絶対パス
        import os
        download_folder = os.path.abspath(download_folder)
        
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("DownloadService._download_worker - Bắt đầu worker thread")
            self.logger.info(f"  - Tổng số video: {total}")
            self.logger.info(f"  - Download folder: {download_folder}")
            self.logger.info(f"  - Naming mode: {naming_mode}")
            self.logger.info(f"  - Video format: {video_format}")
            self.logger.info(f"  - Orientation filter: {orientation_filter}")
            self.logger.info(f"  - Thread ID: {threading.current_thread().ident}")
            self.logger.info("=" * 60)
        
        try:
            for idx, link in enumerate(links):
                # 停止シグナルをチェック（各ビデオの処理前）
                if self.should_stop:
                    if self.logger:
                        self.logger.warning(f"Download stopped by user at video {idx+1}/{total} - breaking loop")
                    break
                
                # 進捗を更新
                if progress_callback:
                    progress = (idx / total) * 100
                    progress_callback(progress, idx, total)
                
                # ビデオを処理
                if self.logger:
                    self.logger.info("-" * 60)
                    self.logger.info(f"Processing video {idx+1}/{total}")
                    self.logger.info(f"  - URL: {link}")
                    self.logger.info(f"  - Should stop: {self.should_stop}")
                
                # 停止シグナルを再度チェック
                if self.should_stop:
                    if self.logger:
                        self.logger.warning("Download stopped by user - before processing video")
                    break
                
                try:
                    result = self.downloader.process_video(
                        link, download_folder, naming_mode, video_format, orientation_filter
                    )
                    
                    # 結果をログに記録
                    if self.logger:
                        if result.get('success'):
                            success_count += 1
                            file_path = result.get('file_path', '')
                            if file_path and os.path.exists(file_path):
                                file_size = os.path.getsize(file_path)
                                total_download_size += file_size
                            self.logger.info(f"  ✓ Video {idx+1} downloaded successfully")
                            self.logger.info(f"    - File path: {result.get('file_path', 'N/A')}")
                            self.logger.info(f"    - Video ID: {result.get('video_id', 'N/A')}")
                            self.logger.info(f"    - Author: {result.get('author', 'N/A')}")
                        else:
                            failed_count += 1
                            self.logger.warning(f"  ✗ Video {idx+1} failed")
                            self.logger.warning(f"    - Error: {result.get('error', 'Unknown error')}")
                            self.logger.warning(f"    - URL: {link}")
                    
                    # 処理後に再度停止シグナルをチェック
                    if self.should_stop:
                        if self.logger:
                            self.logger.warning("Download stopped by user - after processing video")
                        break
                    
                    # 結果をコールバック
                    if result_callback:
                        try:
                            result_callback(result)
                        except Exception as e:
                            if self.logger:
                                self.logger.error(f"Error in result_callback: {e}", exc_info=True)
                
                except Exception as e:
                    failed_count += 1
                    if self.logger:
                        self.logger.error(f"Exception while processing video {idx+1}: {e}", exc_info=True)
                        self.logger.error(f"  - URL: {link}")
                    
                    # エラー結果を作成
                    error_result = {
                        'success': False,
                        'video_id': None,
                        'file_path': None,
                        'error': f"Exception: {str(e)}",
                        'url': link
                    }
                    if result_callback:
                        try:
                            result_callback(error_result)
                        except Exception as e2:
                            if self.logger:
                                self.logger.error(f"Error in result_callback for error result: {e2}", exc_info=True)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Fatal error in download worker: {e}", exc_info=True)
        finally:
            # 完了
            self.is_downloading = False
            end_time = time.time()
            total_time = end_time - start_time
            
            if self.logger:
                self.logger.info("=" * 60)
                self.logger.info("DownloadService._download_worker - Hoàn thành")
                self.logger.info(f"  - Tổng số video: {total}")
                self.logger.info(f"  - Thành công: {success_count}")
                self.logger.info(f"  - Thất bại: {failed_count}")
                self.logger.info(f"  - Tỷ lệ thành công: {(success_count/total*100):.1f}%" if total > 0 else "  - Tỷ lệ thành công: N/A")
                self.logger.info(f"  - Tổng thời gian: {total_time:.2f} giây ({total_time/60:.2f} phút)")
                if total_time > 0 and total_download_size > 0:
                    avg_speed_mbps = (total_download_size / 1024 / 1024) / total_time
                    avg_speed_kbps = (total_download_size / 1024) / total_time
                    self.logger.info(f"  - Tổng dung lượng đã tải: {total_download_size / 1024 / 1024:.2f} MB")
                    self.logger.info(f"  - Tốc độ trung bình: {avg_speed_mbps:.2f} MB/s ({avg_speed_kbps:.2f} KB/s)")
                self.logger.info(f"  - Should stop: {self.should_stop}")
                self.logger.info("=" * 60)
            
            if complete_callback:
                try:
                    complete_callback()
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error in complete_callback: {e}", exc_info=True)
    
    def stop_download(self):
        """ダウンロードを停止"""
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("DownloadService.stop_download - Được gọi")
            self.logger.info(f"  - Current should_stop: {self.should_stop}")
            self.logger.info(f"  - Current is_downloading: {self.is_downloading}")
            self.logger.info(f"  - Download thread: {self.download_thread.ident if self.download_thread else 'None'}")
            self.logger.info(f"  - Download thread alive: {self.download_thread.is_alive() if self.download_thread else 'N/A'}")
        
        self.should_stop = True
        self.is_downloading = False
        
        if self.logger:
            self.logger.info(f"Stop signal sent - should_stop={self.should_stop}, is_downloading={self.is_downloading}")
            self.logger.info("=" * 60)

