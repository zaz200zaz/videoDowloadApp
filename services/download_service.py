"""
Download Service
ダウンロード管理サービス
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        complete_callback: Optional[Callable[[], None]] = None,
        timeout_settings: Optional[dict] = None
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
                      progress_callback, result_callback, complete_callback, timeout_settings),
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
        complete_callback: Optional[Callable[[], None]],
        timeout_settings: Optional[dict] = None
    ):
        """ダウンロードワーカースレッド（並行処理対応）"""
        import time
        import os
        from models.cookie_manager import CookieManager
        
        total = len(links)
        success_count = 0
        failed_count = 0
        total_download_size = 0
        start_time = time.time()
        
        # Thống kê timeout và retry (mới)
        timeout_count = 0
        retry_total_count = 0
        skipped_count = 0
        
        # Thống kê orientation filter (mới)
        filtered_by_orientation_count = 0
        filtered_videos_info = []  # Danh sách video bị filter để hiển thị cho user
        
        # Lấy max_concurrent từ config (theo System Instruction - tối ưu tốc độ tải)
        max_concurrent = 3  # Default
        try:
            cookie_manager = CookieManager()
            config = cookie_manager._load_config(use_cache=True)
            max_concurrent = config.get('settings', {}).get('max_concurrent', 3)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Không thể lấy max_concurrent từ config, sử dụng default: {max_concurrent} - {e}")
        
        # Đảm bảo download_folder là絶対パス
        download_folder = os.path.abspath(download_folder)
        
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("DownloadService._download_worker - Bắt đầu worker thread")
            self.logger.info(f"  - Tổng số video: {total}")
            self.logger.info(f"  - Download folder: {download_folder}")
            self.logger.info(f"  - Naming mode: {naming_mode}")
            self.logger.info(f"  - Video format: {video_format}")
            self.logger.info(f"  - Orientation filter: {orientation_filter}")
            self.logger.info(f"  - Max concurrent downloads: {max_concurrent} (tối ưu tốc độ tải)")
            self.logger.info(f"  - Thread ID: {threading.current_thread().ident}")
            self.logger.info("=" * 60)
        
        # Thread-safe counters cho progress tracking (theo System Instruction - logging đầy đủ)
        completed_count = 0
        completed_lock = threading.Lock()
        
        # Danh sách lưu thời gian download cho mỗi video (theo System Instruction - log thời gian từng video)
        video_times = {}  # {idx: {'start': time, 'end': time, 'duration': time, 'url': url}}
        video_times_lock = threading.Lock()
        
        def process_single_video(idx: int, link: str) -> Dict:
            """
            Process một video (được gọi từ ThreadPoolExecutor)
            
            Args:
                idx: Index của video (0-based)
                link: URL của video
                
            Returns:
                Dict kết quả với thêm idx để track
            """
            video_start_time = time.time()
            
            # Log thời gian bắt đầu (theo System Instruction - log thời gian từng video)
            if self.logger:
                with video_times_lock:
                    video_times[idx] = {
                        'start': video_start_time,
                        'url': link,
                        'status': 'processing'
                    }
                    self.logger.info("-" * 60)
                    self.logger.info(f"Processing video {idx+1}/{total}")
                    self.logger.info(f"  - URL: {link}")
                    self.logger.info(f"  - Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video_start_time))}")
                    self.logger.info(f"  - Should stop: {self.should_stop}")
            
            try:
                # Kiểm tra stop signal trước khi bắt đầu (theo System Instruction - không thay đổi chức năng gốc)
                if self.should_stop:
                    if self.logger:
                        self.logger.warning(f"Download stopped by user before processing video {idx+1}")
                    return {
                        'success': False,
                        'video_id': None,
                        'file_path': None,
                        'error': 'Stopped by user',
                        'url': link,
                        'idx': idx,
                        'download_time': 0
                    }
                
                # Gọi process_video với timeout_settings
                result = self.downloader.process_video(
                    link, download_folder, naming_mode, video_format, orientation_filter, timeout_settings
                )
                
                video_end_time = time.time()
                video_duration = video_end_time - video_start_time
                
                # Log thời gian download (theo System Instruction - log thời gian từng video)
                if self.logger:
                    with video_times_lock:
                        video_times[idx]['end'] = video_end_time
                        video_times[idx]['duration'] = video_duration
                        video_times[idx]['status'] = 'success' if result.get('success') else 'failed'
                    
                    self.logger.info(f"  - End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video_end_time))}")
                    self.logger.info(f"  - Download duration: {video_duration:.2f} seconds ({video_duration/60:.2f} minutes)")
                    if video_duration > 300:  # Nếu > 5 phút, log warning (theo System Instruction - xác định video mất thời gian bất thường)
                        self.logger.warning(f"  - ⚠️ Video {idx+1} mất thời gian bất thường: {video_duration:.2f}s ({video_duration/60:.2f} phút)")
                
                # Thêm idx và download_time vào result
                result['idx'] = idx
                result['download_time'] = video_duration
                result['url'] = link
                
                return result
                
            except Exception as e:
                video_end_time = time.time()
                video_duration = video_end_time - video_start_time
                
                # Log thời gian và lỗi (theo System Instruction - logging đầy đủ)
                if self.logger:
                    with video_times_lock:
                        video_times[idx]['end'] = video_end_time
                        video_times[idx]['duration'] = video_duration
                        video_times[idx]['status'] = 'error'
                    
                    self.logger.error(f"Exception while processing video {idx+1}: {e}", exc_info=True)
                    self.logger.error(f"  - URL: {link}")
                    self.logger.error(f"  - Duration before error: {video_duration:.2f}s")
                
                # Tạo error result
                error_result = {
                    'success': False,
                    'video_id': None,
                    'file_path': None,
                    'error': f"Exception: {str(e)}",
                    'url': link,
                    'idx': idx,
                    'download_time': video_duration
                }
                return error_result
        
        try:
            # Sử dụng ThreadPoolExecutor để tải song song (theo System Instruction - tối ưu tốc độ tải)
            if self.logger:
                self.logger.info(f"Bắt đầu tải {total} video với {max_concurrent} workers đồng thời...")
            
            # Tạo list tasks với index
            tasks = [(idx, link) for idx, link in enumerate(links)]
            
            # Sử dụng ThreadPoolExecutor để tải song song (theo System Instruction - dùng đa luồng để tối ưu tốc độ)
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                # Submit tất cả tasks
                future_to_idx = {executor.submit(process_single_video, idx, link): idx 
                                for idx, link in tasks}
                
                # Xử lý kết quả khi hoàn thành (theo System Instruction - logging đầy đủ)
                for future in as_completed(future_to_idx):
                    # Kiểm tra stop signal (theo System Instruction - không thay đổi chức năng gốc)
                    if self.should_stop:
                        if self.logger:
                            self.logger.warning("Download stopped by user - canceling remaining tasks")
                        # Cancel các tasks còn lại
                        for f in future_to_idx:
                            if not f.done():
                                f.cancel()
                        break
                    
                    idx = future_to_idx[future]
                    try:
                        result = future.result()
                        
                        # Cập nhật progress (theo System Instruction - logging đầy đủ)
                        with completed_lock:
                            completed_count += 1
                            current_progress = (completed_count / total) * 100
                            
                            # Update progress callback
                            if progress_callback:
                                try:
                                    progress_callback(current_progress, completed_count, total)
                                except Exception as e:
                                    if self.logger:
                                        self.logger.error(f"Error in progress_callback: {e}", exc_info=True)
                        
                        # Thu thập thống kê từ result
                        retry_total_count += result.get('retry_count', 0)
                        if result.get('timeout_detected'):
                            timeout_count += 1
                        if result.get('skipped'):
                            skipped_count += 1
                        
                        # Thu thập thống kê orientation filter (mới)
                        if result.get('filtered_by_orientation'):
                            filtered_by_orientation_count += 1
                            # Lưu thông tin video bị filter để hiển thị cho user
                            filtered_videos_info.append({
                                'video_id': result.get('video_id', 'N/A'),
                                'url': result.get('url', 'N/A'),
                                'author': result.get('author', 'N/A'),
                                'orientation': result.get('orientation', 'unknown'),
                                'width': result.get('width', 0),
                                'height': result.get('height', 0),
                                'error': result.get('error', 'Unknown error')
                            })
                        
                        # Log kết quả chi tiết (theo System Instruction - logging đầy đủ từng bước)
                        if self.logger:
                            if result.get('success'):
                                success_count += 1
                                file_path = result.get('file_path', '')
                                if file_path and os.path.exists(file_path):
                                    # Sử dụng file_size từ result nếu có, nếu không thì lấy từ file system
                                    file_size = result.get('file_size', 0)
                                    if file_size == 0:
                                        file_size = os.path.getsize(file_path)
                                    total_download_size += file_size
                                
                                video_idx = result.get('idx', idx) + 1
                                self.logger.info(f"  ✓ Video {video_idx} downloaded successfully")
                                self.logger.info(f"    - File path: {result.get('file_path', 'N/A')}")
                                self.logger.info(f"    - Video ID: {result.get('video_id', 'N/A')}")
                                self.logger.info(f"    - Author: {result.get('author', 'N/A')}")
                                self.logger.info(f"    - Download time: {result.get('download_time', 0):.2f}s ({result.get('download_time', 0)/60:.2f} phút)")
                                
                                # Log thống kê timeout và retry
                                if result.get('retry_count', 0) > 0:
                                    self.logger.info(f"    - Retry count: {result.get('retry_count', 0)}")
                                if result.get('timeout_detected'):
                                    self.logger.warning(f"    - Timeout detected: True (đã retry {result.get('retry_count', 0)} lần)")
                            else:
                                failed_count += 1
                                video_idx = result.get('idx', idx) + 1
                                self.logger.warning(f"  ✗ Video {video_idx} failed")
                                self.logger.warning(f"    - Error: {result.get('error', 'Unknown error')}")
                                self.logger.warning(f"    - URL: {result.get('url', 'N/A')}")
                                self.logger.warning(f"    - Download time: {result.get('download_time', 0):.2f}s ({result.get('download_time', 0)/60:.2f} phút)")
                                
                                # Log thống kê timeout và retry cho video thất bại
                                if result.get('retry_count', 0) > 0:
                                    self.logger.warning(f"    - Retry count: {result.get('retry_count', 0)}")
                                if result.get('timeout_detected'):
                                    self.logger.warning(f"    - Timeout detected: True (sau {result.get('retry_count', 0)} lần retry)")
                                if result.get('skipped'):
                                    self.logger.warning(f"    - Skipped: True (video quá lâu)")
                                # Log thống kê orientation filter cho video thất bại (mới)
                                if result.get('filtered_by_orientation'):
                                    self.logger.info(f"    - Filtered by orientation: True")
                                    self.logger.info(f"    - Video orientation: {result.get('orientation', 'unknown')}")
                                    if result.get('width', 0) > 0 and result.get('height', 0) > 0:
                                        aspect_ratio = result.get('width', 0) / result.get('height', 0)
                                        self.logger.info(f"    - Video size: {result.get('width', 0)}x{result.get('height', 0)} (aspect ratio: {aspect_ratio:.2f})")
                        
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
                            self.logger.error(f"Error getting result from future for video {idx+1}: {e}", exc_info=True)
                            self.logger.error(f"  - URL: {links[idx] if idx < len(links) else 'N/A'}")
                        
                        # エラー結果を作成
                        error_result = {
                            'success': False,
                            'video_id': None,
                            'file_path': None,
                            'error': f"Future error: {str(e)}",
                            'url': links[idx] if idx < len(links) else 'N/A',
                            'idx': idx,
                            'download_time': 0
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
                # Thống kê timeout và retry (mới)
                self.logger.info(f"  - Video bị timeout: {timeout_count}")
                self.logger.info(f"  - Video bị skip (quá lâu): {skipped_count}")
                self.logger.info(f"  - Tổng số lần retry: {retry_total_count}")
                # Thống kê orientation filter (mới)
                if orientation_filter != "all":
                    self.logger.info(f"  - Video bị bỏ qua do orientation filter ({orientation_filter}): {filtered_by_orientation_count}")
                    if filtered_videos_info:
                        self.logger.info(f"  - Danh sách video bị bỏ qua:")
                        for idx, filtered_video in enumerate(filtered_videos_info, 1):
                            self.logger.info(f"    {idx}. Video ID: {filtered_video['video_id']}")
                            self.logger.info(f"       - Author: {filtered_video['author']}")
                            self.logger.info(f"       - Orientation: {filtered_video['orientation']}")
                            if filtered_video['width'] > 0 and filtered_video['height'] > 0:
                                aspect_ratio = filtered_video['width'] / filtered_video['height']
                                self.logger.info(f"       - Size: {filtered_video['width']}x{filtered_video['height']} (aspect ratio: {aspect_ratio:.2f})")
                            self.logger.info(f"       - URL: {filtered_video['url']}")
                self.logger.info(f"  - Tổng thời gian: {total_time:.2f} giây ({total_time/60:.2f} phút)")
                if total_time > 0 and total_download_size > 0:
                    avg_speed_mbps = (total_download_size / 1024 / 1024) / total_time
                    avg_speed_kbps = (total_download_size / 1024) / total_time
                    self.logger.info(f"  - Tổng dung lượng đã tải: {total_download_size / 1024 / 1024:.2f} MB")
                    self.logger.info(f"  - Tốc độ trung bình: {avg_speed_mbps:.2f} MB/s ({avg_speed_kbps:.2f} KB/s)")
                
                # Log thống kê thời gian download từng video (theo System Instruction - log thời gian từng video)
                if 'video_times' in locals() and video_times:
                    self.logger.info("=" * 60)
                    self.logger.info("Thống kê thời gian download từng video:")
                    sorted_videos = sorted(video_times.items(), key=lambda x: x[0])
                    for vid_idx, vid_info in sorted_videos:
                        duration = vid_info.get('duration', 0)
                        url = vid_info.get('url', 'N/A')
                        status = vid_info.get('status', 'unknown')
                        status_icon = "✓" if status == 'success' else "✗" if status == 'failed' else "⚠"
                        self.logger.info(f"  {status_icon} Video {vid_idx+1}: {duration:.2f}s ({duration/60:.2f} phút) - {url[:80]}...")
                    
                    # Xác định video mất thời gian bất thường (theo System Instruction - xác định video mất thời gian bất thường)
                    if len(video_times) > 0:
                        durations = [v.get('duration', 0) for v in video_times.values() if v.get('duration', 0) > 0]
                        if durations:
                            avg_duration = sum(durations) / len(durations)
                            slow_videos = [(vid_idx, vid_info) for vid_idx, vid_info in video_times.items() 
                                         if vid_info.get('duration', 0) > avg_duration * 2]  # > 2x trung bình
                            if slow_videos:
                                self.logger.warning("=" * 60)
                                self.logger.warning("Cảnh báo: Các video mất thời gian bất thường (> 2x trung bình):")
                                for vid_idx, vid_info in slow_videos:
                                    duration = vid_info.get('duration', 0)
                                    url = vid_info.get('url', 'N/A')
                                    self.logger.warning(f"  ⚠️ Video {vid_idx+1}: {duration:.2f}s ({duration/60:.2f} phút) - {url[:80]}...")
                                self.logger.warning(f"  - Trung bình: {avg_duration:.2f}s")
                                self.logger.warning("=" * 60)
                
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

