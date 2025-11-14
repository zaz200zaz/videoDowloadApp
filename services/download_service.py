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
        if self.is_downloading:
            if self.logger:
                self.logger.warning("Download already in progress")
            return
        
        # ダウンローダーを初期化
        self.downloader = VideoDownloader(self.cookie, log_file=None)
        # DownloadServiceの参照を渡して、停止フラグをチェックできるようにする
        self.downloader._service_ref = self
        if self.logger:
            self.logger.info(f"DownloadService initialized, should_stop={self.should_stop}")
        
        # 状態をリセット
        self.is_downloading = True
        self.should_stop = False
        
        # ダウンロードスレッドを開始
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(links, download_folder, naming_mode, video_format, 
                  progress_callback, result_callback, complete_callback),
            daemon=True
        )
        self.download_thread.start()
    
    def _download_worker(
        self,
        links: List[str],
        download_folder: str,
        naming_mode: str,
        video_format: str,
        progress_callback: Optional[Callable[[float, int, int], None]],
        result_callback: Optional[Callable[[Dict], None]],
        complete_callback: Optional[Callable[[], None]]
    ):
        """ダウンロードワーカースレッド"""
        total = len(links)
        
        if self.logger:
            self.logger.info(f"Starting download of {total} videos")
            self.logger.info(f"Video format: {video_format}")
        
        for idx, link in enumerate(links):
            # 停止シグナルをチェック（各ビデオの処理前）
            if self.should_stop:
                if self.logger:
                    self.logger.info("Download stopped by user - breaking loop")
                break
            
            # 進捗を更新
            if progress_callback:
                progress = (idx / total) * 100
                progress_callback(progress, idx, total)
            
            # ビデオを処理
            if self.logger:
                self.logger.info(f"Processing video {idx+1}/{total}: {link}")
            
            # 停止シグナルを再度チェック
            if self.should_stop:
                if self.logger:
                    self.logger.info("Download stopped by user - before processing video")
                break
            
            result = self.downloader.process_video(
                link, download_folder, naming_mode, video_format
            )
            
            # 処理後に再度停止シグナルをチェック
            if self.should_stop:
                if self.logger:
                    self.logger.info("Download stopped by user - after processing video")
                break
            
            # 結果をコールバック
            if result_callback:
                result_callback(result)
        
        # 完了
        self.is_downloading = False
        if complete_callback:
            complete_callback()
        
        if self.logger:
            self.logger.info("Download completed")
    
    def stop_download(self):
        """ダウンロードを停止"""
        if self.logger:
            self.logger.info(f"stop_download called - current should_stop={self.should_stop}, is_downloading={self.is_downloading}")
        self.should_stop = True
        self.is_downloading = False
        if self.logger:
            self.logger.info(f"Stop signal sent - should_stop={self.should_stop}, is_downloading={self.is_downloading}")

