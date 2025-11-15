"""
Video Downloader Service
ビデオダウンロードのビジネスロジック
"""

import os
import re
import time
import requests
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs
import json
import logging
from datetime import datetime


class VideoDownloader:
    """Xử lý tải video Douyin"""
    
    # Compile regex patterns once (theo System Instruction 6 - tối ưu hiệu suất)
    # Cache regex patterns để tránh compile lại nhiều lần
    _regex_patterns = {
        'video_id_patterns': [
            re.compile(r'/video/(\d+)'),
            re.compile(r'video_id=(\d+)'),
            re.compile(r'item_id=(\d+)'),
            re.compile(r'aweme_id=(\d+)'),
            re.compile(r'modal_id=(\d+)'),
        ],
        'short_id_pattern': re.compile(r'/([A-Za-z0-9]+)/?$'),
        'script_tag_pattern': re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL),
        'user_id_pattern': re.compile(r'/user/([^/?]+)'),
        'safe_filename_pattern': re.compile(r'[<>:"/\\|?*]'),
    }
    
    def __init__(self, cookie: str, log_file: str = None):
        """
        Khởi tạo VideoDownloader
        
        Args:
            cookie: Cookie string để xác thực
            log_file: Đường dẫn file log (nếu None, sẽ tạo file log tự động)
        """
        self.cookie = cookie
        self.session = requests.Session()
        
        # Thiết lập logging
        self._setup_logging(log_file)
        
        self._setup_session()
    
    def _setup_logging(self, log_file: str = None):
        """Thiết lập logging"""
        try:
            if log_file is None:
                # Tạo file log với timestamp
                # Sử dụng __file__ để lấy thư mục của script, sau đó lên một cấp để đến project root
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # Nếu script_dir là services/, lên một cấp để đến project root
                if os.path.basename(script_dir) == 'services':
                    project_root = os.path.dirname(script_dir)
                else:
                    project_root = script_dir
                log_dir = os.path.join(project_root, "logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = os.path.join(log_dir, f"douyin_downloader_{timestamp}.log")
            
            # Đảm bảo thư mục tồn tại
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
            
            # Tạo logger
            self.logger = logging.getLogger('VideoDownloader')
            self.logger.setLevel(logging.DEBUG)
            
            # Ngăn chặn propagate đến root logger để đảm bảo format nhất quán (theo System Instruction 4.2)
            self.logger.propagate = False
            
            # Xóa các handler cũ và đóng file handlers để tránh ResourceWarning (theo System Instruction 8)
            for handler in self.logger.handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
                self.logger.removeHandler(handler)
            self.logger.handlers = []
            
            # File handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
            file_handler.setLevel(logging.DEBUG)
            # Format theo System Instruction: [timestamp] [LEVEL] [Function] Message
            # Note: write_log() hoặc log() với function name đã thêm [Function] vào message
            file_format = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            # Console format cũng theo System Instruction
            console_format = logging.Formatter('[%(levelname)s] %(message)s')
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
            
            # Tắt urllib3 DEBUG logs (theo System Instruction)
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
            
            self.log_file_path = log_file
            self.logger.info(f"[VideoDownloader._setup_logging] Logging initialized. Log file: {log_file}")
            # Không dùng print(), dùng log thay vì (theo System Instruction)
        except Exception as e:
            # Nếu không thể tạo log file, vẫn tiếp tục nhưng không có logging
            # Log lỗi này (nếu có logger cơ bản)
            # Import logging ở đây để tránh lỗi "cannot access local variable 'logging'"
            # (theo System Instruction 5 - xử lý lỗi với logging đầy đủ)
            try:
                # logging module đã được import ở đầu file, nhưng nếu có exception
                # thì có thể cần import lại trong exception handler
                import logging as logging_module
                temp_logger = logging_module.getLogger('VideoDownloader')
                temp_logger.warning(f"[VideoDownloader._setup_logging] Không thể tạo log file: {e}")
            except:
                pass
            # Tạo logger mặc định (chỉ console)
            import logging as logging_module  # Import với alias để tránh conflict
            self.logger = logging_module.getLogger('VideoDownloader')
            self.logger.setLevel(logging_module.INFO)
            self.logger.handlers = []
            console_handler = logging_module.StreamHandler()
            console_handler.setLevel(logging_module.INFO)
            self.logger.addHandler(console_handler)
            self.log_file_path = None
    
    def log(self, level: str, message: str, function: str = None, exc_info=None):
        """
        Ghi log với level cụ thể theo System Instruction format
        
        Args:
            level: 'debug', 'info', 'warning', 'error', 'critical'
            message: Nội dung log
            function: Tên function (nếu None, tự động lấy từ stack trace)
            exc_info: Nếu True, thêm exception info (stack trace)
        """
        # Lấy function name nếu không được cung cấp
        if function is None:
            import inspect
            frame = inspect.currentframe().f_back
            function = frame.f_code.co_name
            # Thêm class name nếu có
            if 'self' in frame.f_locals:
                class_name = frame.f_locals['self'].__class__.__name__
                function = f"{class_name}.{function}"
        
        # Format message theo System Instruction: [Function] Message
        formatted_message = f"[{function}] {message}"
        
        if level.lower() == 'debug':
            self.logger.debug(formatted_message, exc_info=exc_info)
        elif level.lower() == 'info':
            self.logger.info(formatted_message, exc_info=exc_info)
        elif level.lower() == 'warning':
            self.logger.warning(formatted_message, exc_info=exc_info)
        elif level.lower() == 'error':
            self.logger.error(formatted_message, exc_info=exc_info)
        elif level.lower() == 'critical':
            self.logger.critical(formatted_message, exc_info=exc_info)
        else:
            self.logger.info(formatted_message, exc_info=exc_info)
    
    def _setup_session(self):
        """Thiết lập session với headers và cookie"""
        # Tắt urllib3 DEBUG logs để giảm log file size (theo System Instruction)
        import logging
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
        
        # Làm sạch cookie (loại bỏ whitespace và ký tự không hợp lệ)
        clean_cookie = self.cookie.strip()
        # Loại bỏ newline và tab trong cookie
        clean_cookie = clean_cookie.replace('\n', '').replace('\r', '').replace('\t', ' ')
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.douyin.com/",
            "Origin": "https://www.douyin.com",
            "Cookie": clean_cookie
        }
        self.session.headers.update(headers)
        
        # Debug: kiểm tra cookie có được set đúng không
        function_name = "VideoDownloader._setup_session"
        if len(clean_cookie) > 0:
            self.log('info', f"Cookie đã được set (length: {len(clean_cookie)})", function_name)
        else:
            self.log('warning', "WARNING: Cookie rỗng!", function_name)
    
    def normalize_url(self, url: str) -> Optional[str]:
        """
        Chuẩn hóa URL video Douyin
        
        Args:
            url: URL gốc từ người dùng (có thể là video page URL hoặc direct video URL)
            
        Returns:
            URL đã được chuẩn hóa hoặc None nếu không hợp lệ
            
        Exceptions:
            Exception: Lỗi khi resolve short URL hoặc parse URL
        """
        function_name = "VideoDownloader.normalize_url"
        
        # Log bắt đầu (theo System Instruction)
        self.log('info', f"Bắt đầu normalize URL: {url[:100] if url else 'None'}...", function_name)
        
        try:
            if not url or not isinstance(url, str):
                self.log('warning', "URL không hợp lệ (None hoặc không phải string)", function_name)
                return None
            
            url = url.strip()
            
            # Kiểm tra xem có phải direct video URL không
            is_direct_video = (url.endswith('.mp4') or '.mp4?' in url or 
                              'zjcdn.com' in url.lower() or 
                              'douyinstatic.com' in url.lower() or
                              ('/video/' in url.lower() and 'douyin.com' not in url.lower()))
            
            # Nếu là direct video URL, trả về trực tiếp (không cần normalize)
            if is_direct_video:
                self.log('info', f"Phát hiện direct video URL, bỏ qua normalize: {url[:100]}...", function_name)
                self.log('info', "Normalize URL hoàn thành - direct video URL", function_name)
                return url
            
            # Kiểm tra xem có phải link Douyin không
            if "douyin.com" not in url and "iesdouyin.com" not in url:
                self.log('warning', f"URL không phải link Douyin: {url[:100]}...", function_name)
                self.log('info', "Normalize URL hoàn thành - không phải link Douyin", function_name)
                return None
            
            # Xử lý short URL (v.douyin.com) - cần resolve redirect
            if "v.douyin.com" in url or "iesdouyin.com" in url:
                try:
                    # Tạo session mới không có cookie để resolve redirect
                    # (vì cookie có thể chứa ký tự không hợp lệ)
                    temp_session = requests.Session()
                    temp_session.headers.update({
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "Referer": "https://www.douyin.com/",
                    })
                    # Follow redirect để lấy URL thực tế
                    response = temp_session.get(url, allow_redirects=True, timeout=15)
                    final_url = response.url
                    url = final_url
                    self.log('debug', f"Đã resolve short URL thành: {url}", function_name)
                except Exception as e:
                    self.log('warning', f"Lỗi khi resolve short URL: {e}", function_name, exc_info=True)
                    # Nếu không resolve được, trả về URL gốc và thử extract ID trực tiếp
                    self.log('debug', "Sử dụng URL gốc (không resolve được redirect)", function_name)
                    pass
            
            # Loại bỏ các param thừa, chỉ giữ lại link cơ bản
            try:
                parsed = urlparse(url)
                # Giữ lại scheme, netloc, path
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                self.log('info', f"Đã normalize URL thành công: {normalized[:100]}...", function_name)
                self.log('info', "Normalize URL hoàn thành thành công", function_name)
                return normalized
            except Exception as e:
                self.log('warning', f"Lỗi khi normalize URL: {e}", function_name, exc_info=True)
                self.log('info', f"Trả về URL gốc: {url[:100]}...", function_name)
                self.log('info', "Normalize URL hoàn thành - trả về URL gốc", function_name)
                return url
                
        except Exception as e:
            # Log lỗi đầy đủ theo System Instruction
            self.log('error', f"Lỗi không xác định khi normalize URL: {e}", function_name, exc_info=True)
            return None
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Trích xuất video ID từ URL
        
        Args:
            url: URL video
            
        Returns:
            Video ID hoặc None nếu không tìm thấy
            
        Exceptions:
            Exception: Lỗi khi parse URL hoặc extract ID
        """
        function_name = "VideoDownloader.extract_video_id"
        
        # Log bắt đầu (theo System Instruction)
        self.log('info', f"Bắt đầu extract video ID từ URL: {url[:100] if url else 'None'}...", function_name)
        
        try:
            # Kiểm tra URL hợp lệ trước khi search (theo System Instruction 5 - xử lý lỗi đầy đủ)
            if not url or not isinstance(url, str):
                self.log('warning', f"URL không hợp lệ (None hoặc không phải string): {url}", function_name)
                self.log('info', "Extract video ID hoàn thành - URL không hợp lệ", function_name)
                return None
            
            # Sử dụng compiled regex patterns (tối ưu hiệu suất - System Instruction 6)
            # Compile regex một lần và tái sử dụng thay vì compile lại mỗi lần
            for pattern in self._regex_patterns['video_id_patterns']:
                match = pattern.search(url)
                if match:
                    video_id = match.group(1)
                    self.log('debug', f"Đã tìm thấy video ID: {video_id}", function_name)
                    self.log('info', f"Extract video ID hoàn thành thành công: {video_id}", function_name)
                    return video_id
            
            # Nếu không tìm thấy, thử parse từ query string
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'video_id' in params:
                return params['video_id'][0]
            if 'item_id' in params:
                return params['item_id'][0]
            if 'aweme_id' in params:
                return params['aweme_id'][0]
            
            # Nếu là short URL (v.douyin.com/xxxxx), thử lấy ID từ path
            if 'v.douyin.com' in url or 'iesdouyin.com' in url:
                # Sử dụng compiled regex pattern (tối ưu hiệu suất)
                match = self._regex_patterns['short_id_pattern'].search(parsed.path)
                if match:
                    short_id = match.group(1)
                    self.log('debug', f"Tìm thấy short ID: {short_id}, cần resolve URL để lấy video ID thực", function_name)
                    # Short ID này không phải video ID, cần resolve URL trước
                    # Nhưng nếu normalize_url đã resolve rồi thì sẽ có video ID ở đây
                    return None
            
            self.log('warning', f"Không tìm thấy video ID trong URL: {url}", function_name)
            self.log('info', "Extract video ID hoàn thành - không tìm thấy", function_name)
            return None
        except Exception as e:
            # Log lỗi đầy đủ theo System Instruction
            self.log('error', f"Lỗi khi trích xuất video ID: {e}", function_name, exc_info=True)
            return None
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Lấy thông tin video từ Douyin API
        
        Args:
            url: URL video (có thể là video page URL hoặc direct video URL)
            
        Returns:
            Dict chứa thông tin video hoặc None nếu lỗi
            
        Exceptions:
            Exception: Lỗi khi gọi API, parse JSON, hoặc extract video info
        """
        function_name = "VideoDownloader.get_video_info"
        
        # Log bắt đầu (theo System Instruction)
        self.log('info', f"Bắt đầu lấy thông tin video từ URL: {url[:100] if url else 'None'}...", function_name)
        
        try:
            # Kiểm tra xem có phải audio file (MP3) không - bỏ qua
            if '.mp3' in url.lower() or 'ies-music' in url.lower() or '/music/' in url.lower():
                self.log('warning', f"Phát hiện audio file (MP3), bỏ qua: {url[:100]}...", function_name)
                self.log('info', "Get video info hoàn thành - audio file (bỏ qua)", function_name)
                return None
            
            # Kiểm tra xem có phải direct video URL không
            is_direct_video = (url.endswith('.mp4') or '.mp4?' in url or 
                              'zjcdn.com' in url.lower() or 
                              'douyinstatic.com' in url.lower() or
                              ('/video/' in url.lower() and 'douyin.com' not in url.lower()))
            
            if is_direct_video:
                # Đây là direct video URL, trả về trực tiếp
                self.log('info', f"Phát hiện direct video URL: {url[:100]}...", function_name)
                self.log('warning', "Direct video URL có thể hết hạn, nhưng vẫn thử tải", function_name)
                result = {
                    'video_id': None,
                    'title': 'Direct Video',
                    'author': 'Unknown',
                    'video_url': url
                }
                self.log('info', "Get video info hoàn thành - direct video URL", function_name)
                return result
            
            video_id = self.extract_video_id(url)
            if not video_id:
                self.log('error', f"Không thể trích xuất video ID từ URL: {url}", function_name)
                self.log('info', "Get video info hoàn thành - không thể extract video ID", function_name)
                return None
            
            # Thử TikVideo.App API trước (nếu có)
            self.log('debug', "Thử sử dụng TikVideo.App API...", function_name)
            tikvideo_result = self._get_video_info_from_tikvideo(url)
            if tikvideo_result:
                self.log('info', "Đã lấy được thông tin video từ TikVideo.App API!", function_name)
                self.log('info', "Get video info hoàn thành thành công (TikVideo.App)", function_name)
                return tikvideo_result
            
            # Thử nhiều API endpoint khác nhau（JavaScriptコードから学んだ方法を含む）
            api_endpoints = [
                # JavaScriptコードで使用されているエンドポイント（より信頼性が高い）
                f"https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={video_id}&version_code=170400&version_name=17.4.0",
                # 元のエンドポイント
                f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}",
                f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}&aid=1128&version_name=23.5.0&device_platform=web&device_id=0",
            ]
            
            data = None
            
            # Thử các API endpoint
            for api_url in api_endpoints:
                self.log('info', f"Đang gọi API: {api_url}", function_name)
                self.log('debug', f"Cookie length: {len(self.cookie)} characters", function_name)
                
                try:
                    response = self.session.get(api_url, timeout=15)
                    
                    # Log API call theo System Instruction
                    self.log('debug', f"Response status: {response.status_code}", function_name)
                    content_length = response.headers.get('Content-Length', 'unknown')
                    self.log('debug', f"Content-Length: {content_length}", function_name)
                    
                    if response.status_code == 200:
                        # Kiểm tra response có rỗng không
                        if len(response.text) == 0:
                            self.log('warning', f"Response rỗng từ endpoint: {api_url}", function_name)
                            self.log('warning', "Có thể cookie không hợp lệ hoặc API đã thay đổi", function_name)
                            continue  # Thử endpoint tiếp theo
                        
                        # Thử parse JSON
                        try:
                            data = response.json()
                            self.log('info', "Đã parse JSON thành công!", function_name)
                            break  # Thành công, thoát khỏi loop
                        except json.JSONDecodeError as je:
                            self.log('warning', f"Response không phải JSON từ endpoint: {api_url}", function_name)
                            self.log('debug', f"JSON decode error: {je}", function_name, exc_info=True)
                            continue
                    else:
                        self.log('warning', f"Status code không phải 200: {response.status_code}", function_name)
                        self.log('error', f"API call failed: {api_url} - Status {response.status_code}", function_name)
                        continue
                except Exception as e:
                    self.log('error', f"Lỗi khi gọi API {api_url}: {e}", function_name, exc_info=True)
                    continue
            
            # Nếu tất cả API endpoint đều thất bại, thử lấy từ HTML page
            if data is None:
                self.log('warning', "Tất cả API endpoint đều thất bại, thử lấy từ HTML page...", function_name)
                result = self._get_video_info_from_html(url, video_id)
                if result:
                    self.log('info', "Get video info hoàn thành thành công (HTML parsing)", function_name)
                else:
                    self.log('info', "Get video info hoàn thành - không thể lấy thông tin", function_name)
                return result
            
            # Parse response để lấy link video（JavaScriptコードの方法を参考）
            if 'aweme_detail' in data:
                aweme = data['aweme_detail']
                
                # Lấy width và height để xác định hướng video
                video_data = aweme.get('video', {})
                width = video_data.get('width', 0) if video_data else 0
                height = video_data.get('height', 0) if video_data else 0
                
                # Xác định hướng video
                # Lưu ý: Douyin API có thể trả về width và height theo hướng thực tế của video
                # Nếu height > width: video dọc (vertical/portrait)
                # Nếu width > height: video ngang (horizontal/landscape)
                orientation = 'unknown'
                if width > 0 and height > 0:
                    # Log để debug
                    self.log('info', f"Video {video_id}: width={width}, height={height}, ratio={height/width if width > 0 else 0:.2f}", function_name)
                    if height > width:
                        orientation = 'vertical'  # 縦向き (dọc)
                    elif width > height:
                        orientation = 'horizontal'  # 横向き (ngang)
                    else:
                        orientation = 'square'  # 正方形
                    self.log('info', f"Video {video_id}: orientation={orientation} (width={width}, height={height})", function_name)
                
                video_info = {
                    'video_id': video_id,
                    'title': aweme.get('desc', ''),
                    'author': aweme.get('author', {}).get('nickname', ''),
                    'width': width,
                    'height': height,
                    'orientation': orientation,
                    'video_url': None
                }
                
                # JavaScriptコードの方法: video.video.play_addr.url_list[0] または video.video.download_addr.url_list[0]
                if video_data:
                    # Lấy tất cả các URL có sẵn
                    all_urls = []
                    
                    # まず play_addr を試す
                    play_addr = video_data.get('play_addr', {})
                    if play_addr:
                        url_list = play_addr.get('url_list', [])
                        if url_list:
                            for url in url_list:
                                # HTTPをHTTPSに変換
                                if not url.startswith("https"):
                                    url = url.replace("http", "https")
                                all_urls.append({
                                    'url': url,
                                    'type': 'play',
                                    'quality': play_addr.get('height', 0)  # Lấy độ phân giải nếu có
                                })
                    
                    # download_addrを試す
                    download_addr = video_data.get('download_addr', {})
                    if download_addr:
                        url_list = download_addr.get('url_list', [])
                        if url_list:
                            for url in url_list:
                                if not url.startswith("https"):
                                    url = url.replace("http", "https")
                                all_urls.append({
                                    'url': url,
                                    'type': 'download',
                                    'quality': download_addr.get('height', 0)
                                })
                    
                    if all_urls:
                        # Sắp xếp theo quality (cao nhất trước)
                        all_urls.sort(key=lambda x: x.get('quality', 0), reverse=True)
                        video_info['video_urls'] = all_urls
                        video_info['video_url'] = all_urls[0]['url']  # Mặc định chọn chất lượng cao nhất
                        self.log('info', f"Đã tìm thấy {len(all_urls)} video URL từ play_addr/download_addr", function_name)
                        self.log('info', "Get video info hoàn thành thành công (API)", function_name)
                        return video_info
                    
                    self.log('warning', "Không tìm thấy play_addr hoặc download_addr trong video_data", function_name)
                else:
                    self.log('warning', "Không tìm thấy video trong aweme_detail", function_name)
                
                # Nếu có video_info nhưng không có video_url, thử lấy từ HTML
                if video_info and not video_info.get('video_url'):
                    self.log('warning', "Video info không có video_url, thử lấy từ HTML...", function_name)
                    html_result = self._get_video_info_from_html(url, video_id)
                    if html_result:
                        # Merge thông tin từ API và HTML
                        video_info.update(html_result)
                        self.log('info', "Get video info hoàn thành thành công (API + HTML)", function_name)
                        return video_info
                    else:
                        self.log('info', "Get video info hoàn thành - không có video URL", function_name)
                        return video_info
                
                self.log('info', "Get video info hoàn thành thành công", function_name)
                return video_info
            elif 'aweme_list' in data:
                # リスト形式のレスポンス（複数ビデオの場合）
                aweme_list = data['aweme_list']
                if aweme_list and len(aweme_list) > 0:
                    # 最初のビデオを取得
                    aweme = aweme_list[0]
                    
                    # Lấy width và height để xác định hướng video
                    video_data = aweme.get('video', {})
                    width = video_data.get('width', 0) if video_data else 0
                    height = video_data.get('height', 0) if video_data else 0
                    
                    # Xác định hướng video
                    orientation = 'unknown'
                    if width > 0 and height > 0:
                        # Log để debug
                        self.log('info', f"Video (aweme_list): width={width}, height={height}, ratio={height/width if width > 0 else 0:.2f}", function_name)
                        if height > width:
                            orientation = 'vertical'  # 縦向き (dọc)
                        elif width > height:
                            orientation = 'horizontal'  # 横向き (ngang)
                        else:
                            orientation = 'square'  # 正方形
                        self.log('info', f"Video (aweme_list): orientation={orientation} (width={width}, height={height})", function_name)
                    
                    video_info = {
                        'video_id': video_id,
                        'title': aweme.get('desc', ''),
                        'author': aweme.get('author', {}).get('nickname', ''),
                        'width': width,
                        'height': height,
                        'orientation': orientation,
                        'video_url': None
                    }
                    
                    if video_data:
                        # Lấy tất cả các URL có sẵn (giống như aweme_detail)
                        all_urls = []
                        
                        play_addr = video_data.get('play_addr', {})
                        if play_addr:
                            url_list = play_addr.get('url_list', [])
                            if url_list:
                                for url in url_list:
                                    if not url.startswith("https"):
                                        url = url.replace("http", "https")
                                    all_urls.append({
                                        'url': url,
                                        'type': 'play',
                                        'quality': play_addr.get('height', 0)
                                    })
                        
                        download_addr = video_data.get('download_addr', {})
                        if download_addr:
                            url_list = download_addr.get('url_list', [])
                            if url_list:
                                for url in url_list:
                                    if not url.startswith("https"):
                                        url = url.replace("http", "https")
                                    all_urls.append({
                                        'url': url,
                                        'type': 'download',
                                        'quality': download_addr.get('height', 0)
                                    })
                        
                        if all_urls:
                            all_urls.sort(key=lambda x: x.get('quality', 0), reverse=True)
                            video_info['video_urls'] = all_urls
                            video_info['video_url'] = all_urls[0]['url']
                            self.log('info', f"Đã tìm thấy {len(all_urls)} video URL từ aweme_list", function_name)
                            return video_info
                    
                    return None
            else:
                self.log('warning', f"Response không chứa 'aweme_detail' hoặc 'aweme_list'. Keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}", function_name)
                # Thử lấy từ HTML
                return self._get_video_info_from_html(url, video_id)
            
        except requests.exceptions.RequestException as e:
            self.log('error', f"Lỗi khi lấy thông tin video: {e}", function_name, exc_info=True)
            return None
        except Exception as e:
            self.log('error', f"Lỗi không xác định khi lấy thông tin video: {e}", function_name, exc_info=True)
            return None
    
    def _get_video_info_from_html(self, url: str, video_id: str) -> Optional[Dict]:
        """
        Lấy thông tin video từ HTML page (fallback method)
        
        Args:
            url: URL video
            video_id: Video ID đã biết
            
        Returns:
            Dict chứa thông tin video hoặc None
            
        Exceptions:
            Exception: Lỗi khi lấy HTML hoặc parse HTML
        """
        function_name = "VideoDownloader._get_video_info_from_html"
        
        # Log bắt đầu (theo System Instruction)
        self.log('info', f"Bắt đầu lấy thông tin video từ HTML: {url[:100] if url else 'None'}...", function_name)
        self.log('debug', f"Video ID: {video_id}", function_name)
        
        try:
            self.log('info', f"Đang lấy HTML từ: {url[:100]}...", function_name)
            response = self.session.get(url, timeout=15)
            
            # Log API call theo System Instruction
            self.log('debug', f"Response status: {response.status_code}", function_name)
            
            if response.status_code != 200:
                self.log('warning', f"Không thể lấy HTML. Status: {response.status_code}", function_name)
                self.log('info', "Get video info from HTML hoàn thành - status code không phải 200", function_name)
                return None
            
            html_content = response.text
            self.log('info', f"HTML length: {len(html_content)} characters", function_name)
            
            # Tìm video URL trong HTML
            # Pattern 1: Tìm trong script tag với JSON data
            import re
            import json
            import urllib.parse
            
            video_url = None
            
            # Thử tìm trong window._SSR_HYDRATED_DATA hoặc tương tự
            ssr_patterns = [
                r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?});',
                r'<script[^>]*>.*?"playAddr":\s*"([^"]+)".*?</script>',
                r'"playAddr":\s*"([^"]+)"',
                r'"play_addr":\s*"([^"]+)"',
                r'"url_list":\s*\["([^"]+)"',
            ]
            
            # Tìm trong script tags (sử dụng compiled regex pattern - tối ưu hiệu suất)
            scripts = self._regex_patterns['script_tag_pattern'].findall(html_content)
            
            for script in scripts:
                # Tìm JSON data
                for pattern in ssr_patterns:
                    matches = re.findall(pattern, script, re.DOTALL)
                    if matches:
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0] if match else ""
                            
                            # Thử parse JSON nếu có
                            if match.startswith('{'):
                                try:
                                    data = json.loads(match)
                                    # Tìm video URL trong JSON
                                    video_url = self._extract_video_url_from_json(data)
                                    if video_url:
                                        break
                                except:
                                    pass
                            elif match.startswith('http'):
                                video_url = match
                                break
                        
                        if video_url:
                            break
                
                if video_url:
                    break
            
            # Nếu vẫn chưa tìm thấy, thử tìm trực tiếp trong HTML
            if not video_url:
                # Trước tiên, thử tìm trong RENDER_DATA hoặc window data
                self.log('info', "Đang tìm kiếm trong RENDER_DATA và window data...", function_name)
                render_data_patterns = [
                    r'<script[^>]*id="RENDER_DATA"[^>]*>(.+?)</script>',
                    r'window\._UNIVERSAL_DATA\s*=\s*({.+?});',
                    r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?});',
                    r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                ]
                
                for pattern in render_data_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    if matches:
                        self.log('debug', f"Tìm thấy {len(matches)} match với pattern: {pattern[:50]}...", function_name)
                        for i, match in enumerate(matches):
                            self.log('debug', f"Đang xử lý match {i+1}/{len(matches)}, length: {len(match)}", function_name)
                            
                            # RENDER_DATAは通常URLエンコードされている
                            try:
                                # Thử decode URL encoded JSON
                                decoded = urllib.parse.unquote(match)
                                self.log('debug', f"Đã decode, length sau decode: {len(decoded)}", function_name)
                                
                                # JSONをパース
                                data = json.loads(decoded)
                                self.log('debug', f"Đã parse JSON thành công! Type: {type(data)}", function_name)
                                
                                # ビデオURLを抽出
                                found_url = self._extract_video_url_from_json(data, video_id)
                                if found_url:
                                    video_url = found_url
                                    self.log('info', f"Tìm thấy video URL trong RENDER_DATA: {video_url[:150]}...", function_name)
                                    break
                                else:
                                    self.log('debug', "Không tìm thấy video URL trong JSON data", function_name)
                                    # Debug: JSON構造を確認
                                    if isinstance(data, dict):
                                        self.log('debug', f"Top level keys: {list(data.keys())[:10]}", function_name)
                                        
                            except urllib.error.UnquoteError as e:
                                self.log('warning', f"Lỗi khi decode URL: {e}", function_name, exc_info=True)
                                try:
                                    # Thử parse trực tiếp（既にデコード済みの場合）
                                    data = json.loads(match)
                                    found_url = self._extract_video_url_from_json(data, video_id)
                                    if found_url:
                                        video_url = found_url
                                        self.log('info', f"Tìm thấy video URL trong data (không decode): {video_url[:150]}...", function_name)
                                        break
                                except json.JSONDecodeError as e2:
                                    self.log('warning', f"Lỗi khi parse JSON (không decode): {str(e2)[:200]}", function_name, exc_info=True)
                                    # Debug: Match preview
                                    self.log('debug', f"Match preview: {match[:200]}...", function_name)
                            except json.JSONDecodeError as e:
                                self.log('warning', f"Lỗi khi parse JSON: {str(e)[:200]}", function_name, exc_info=True)
                                # Decodedデータの最初の200文字を表示
                                try:
                                    decoded = urllib.parse.unquote(match)
                                    self.log('debug', f"Decoded preview: {decoded[:200]}...", function_name)
                                except:
                                    self.log('debug', f"Match preview: {match[:200]}...", function_name)
                            except Exception as e:
                                # Log lỗi đầy đủ theo System Instruction
                                self.log('error', f"Lỗi không xác định khi xử lý RENDER_DATA: {type(e).__name__}: {str(e)[:200]}", function_name, exc_info=True)
                    
                    if video_url:
                        break
                
                # Nếu vẫn không tìm thấy trong RENDER_DATA, thử tìm trong toàn bộ HTML với pattern khác
                if not video_url:
                    self.log('debug', "Đang tìm kiếm trong toàn bộ HTML với pattern khác...", function_name)
                    # Tìm trong script tags với JSON data (sử dụng compiled regex - tối ưu hiệu suất)
                    scripts = self._regex_patterns['script_tag_pattern'].findall(html_content)
                    self.log('debug', f"Tìm thấy {len(scripts)} script tags", function_name)
                    
                    for i, script in enumerate(scripts):
                        # Tìm JSON object trong script
                        json_patterns = [
                            r'\{[^{}]*"playAddr"[^{}]*\}',
                            r'\{[^{}]*"play_addr"[^{}]*\}',
                            r'\{[^{}]*"url_list"[^{}]*\}',
                        ]
                        
                        for json_pattern in json_patterns:
                            json_matches = re.findall(json_pattern, script, re.DOTALL)
                            for json_match in json_matches:
                                try:
                                    # Thử parse JSON
                                    data = json.loads(json_match)
                                    found_url = self._extract_video_url_from_json(data, video_id)
                                    if found_url:
                                        video_url = found_url
                                        self.log('info', f"Tìm thấy video URL trong script tag {i}: {video_url[:150]}...", function_name)
                                        break
                                except Exception as e:
                                    self.log('debug', f"Lỗi khi parse JSON trong script tag {i}: {e}", function_name)
                                    pass
                            
                            if video_url:
                                break
                        
                        if video_url:
                            break
                
                # Nếu vẫn chưa tìm thấy, thử tìm tất cả URL pattern（最後の手段）
                if not video_url:
                    self.log('info', "Đang tìm kiếm tất cả URL trong HTML (最後の手段)...", function_name)
                    all_urls = []
                    direct_patterns = [
                        r'https://[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                        r'https://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                    ]
                    
                    for pattern in direct_patterns:
                        matches = re.findall(pattern, html_content)
                        all_urls.extend(matches)
                    
                    self.log('info', f"Tìm thấy {len(all_urls)} URL trong HTML", function_name)
                    
                    # Loại bỏ các URL không hợp lệ
                    valid_urls = []
                    exclude_keywords = [
                        'douyin_pc_client',
                        'download/douyin',
                        'bytednsdoc',
                        'eden-cn',
                        'ild_jw',
                    ]
                    
                    for url in all_urls:
                        url_clean = url.rstrip('.,;!?\\"\'<>')
                        # Kiểm tra URL có chứa từ khóa loại trừ không
                        should_exclude = any(keyword in url_clean.lower() for keyword in exclude_keywords)
                        
                        if not should_exclude and len(url_clean) > 50:
                            # Ưu tiên URL có chứa video ID hoặc aweme
                            if str(video_id) in url_clean or 'aweme' in url_clean.lower():
                                valid_urls.insert(0, url_clean)  # Thêm vào đầu
                            else:
                                valid_urls.append(url_clean)
                    
                    if valid_urls:
                        # Lấy URL đầu tiên (ưu tiên có video ID hoặc aweme)
                        video_url = valid_urls[0]
                        self.log('info', f"Tìm thấy {len(valid_urls)} URL hợp lệ, chọn: {video_url[:150]}...", function_name)
                    else:
                        self.log('warning', "Không tìm thấy URL hợp lệ trong HTML (tất cả đều bị loại trừ)", function_name)
                        self.log('warning', "WARNING: Không thể tìm thấy video URL hợp lệ từ HTML!", function_name)
                        self.log('warning', "Có thể cần cookie mới hoặc video không khả dụng.", function_name)
                        # Debug: hiển thị một số URL để kiểm tra
                        if all_urls:
                            self.log('debug', f"Tất cả URL tìm thấy (để debug): {len(all_urls)} URLs", function_name)
                            for i, url in enumerate(all_urls[:5]):  # Chỉ hiển thị 5 URL đầu
                                self.log('debug', f"  {i+1}. {url[:100]}...", function_name)
                
                # Nếu vẫn không tìm thấy, thử tìm trong JSON string
                if not video_url:
                    # Tìm pattern với escaped URL
                    escaped_patterns = [
                        r'https://[^"\'<>\s\\\\]+\.mp4[^"\'<>\s\\\\]*',
                        r'https\\\\u002F\\\\u002F[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                    ]
                    for pattern in escaped_patterns:
                        matches = re.findall(pattern, html_content)
                        if matches:
                            video_url = max(matches, key=len)
                            # Decode escaped characters
                            video_url = video_url.replace('\\u002F', '/')
                            video_url = video_url.replace('\\/', '/')
                            video_url = video_url.replace('\\\\', '')
                            if len(video_url) > 20:
                                break
                            else:
                                video_url = None
            
            if video_url:
                # Làm sạch URL
                video_url = video_url.replace('\\u002F', '/')
                video_url = video_url.replace('\\/', '/')
                video_url = video_url.replace('\\"', '')
                video_url = video_url.replace('\\\\', '')
                video_url = video_url.replace('\\', '')
                
                # Decode URL encoding
                try:
                    video_url = urllib.parse.unquote(video_url)
                except:
                    pass
                
                # Loại bỏ các ký tự không hợp lệ ở cuối
                video_url = video_url.rstrip('.,;!?\\"\'<>')
                
                # Kiểm tra URL hợp lệ
                if not video_url.startswith('http'):
                    self.log('warning', f"URL không hợp lệ (không bắt đầu bằng http): {video_url[:100]}", function_name)
                    video_url = None
                elif len(video_url) < 20:
                    self.log('warning', f"URL quá ngắn: {video_url}", function_name)
                    video_url = None
                
                if video_url:
                    self.log('info', f"Tìm thấy video URL trong HTML: {video_url[:150]}...", function_name)
                    self.log('info', f"Video URL length: {len(video_url)}", function_name)
                    
                    # HTMLからauthor情報も取得を試みる
                    author_from_html = 'Unknown'
                    try:
                        # RENDER_DATAからauthor情報を取得
                        author_patterns = [
                            r'"nickname"\s*:\s*"([^"]+)"',
                            r'"unique_id"\s*:\s*"([^"]+)"',
                            r'"author".*?"nickname"\s*:\s*"([^"]+)"',
                        ]
                        for pattern in author_patterns:
                            match = re.search(pattern, html_content)
                            if match:
                                author_from_html = match.group(1)
                                self.log('info', f"Tìm thấy author từ HTML: {author_from_html}", function_name)
                                break
                    except Exception as e:
                        self.log('warning', f"Không thể lấy author từ HTML: {e}", function_name, exc_info=True)
                    
                    result = {
                        'video_id': video_id,
                        'title': '',
                        'author': author_from_html,
                        'video_url': video_url
                    }
                    self.log('info', "Get video info from HTML hoàn thành thành công", function_name)
                    return result
            
            # Nếu vẫn không tìm thấy, thử tìm trong window._UNIVERSAL_DATA hoặc tương tự
            if not video_url:
                self.log('info', "Đang tìm kiếm trong window data...", function_name)
                window_patterns = [
                    r'window\._UNIVERSAL_DATA\s*=\s*({.+?});',
                    r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?});',
                    r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                    r'<script[^>]*id="RENDER_DATA"[^>]*>(.+?)</script>',
                ]
                
                for pattern in window_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    if matches:
                        for match in matches:
                            try:
                                # Thử decode URL encoded JSON
                                decoded = urllib.parse.unquote(match)
                                data = json.loads(decoded)
                                video_url = self._extract_video_url_from_json(data, video_id)
                                if video_url:
                                    self.log('info', f"Tìm thấy video URL trong window data: {video_url[:150]}...", function_name)
                                    
                                    # JSONからauthor情報も取得を試みる
                                    author_from_json = 'Unknown'
                                    try:
                                        author_from_json = self._extract_author_from_json(data)
                                        if author_from_json:
                                            self.log('info', f"Tìm thấy author từ JSON: {author_from_json}", function_name)
                                    except Exception as e:
                                        self.log('warning', f"Không thể lấy author từ JSON: {e}", function_name, exc_info=True)
                                    
                                    result = {
                                        'video_id': video_id,
                                        'title': '',
                                        'author': author_from_json,
                                        'video_url': video_url
                                    }
                                    self.log('info', "Get video info from HTML hoàn thành thành công (window data)", function_name)
                                    return result
                            except Exception as e:
                                self.log('debug', f"Lỗi khi parse window data (match {i}): {e}", function_name, exc_info=True)
                                try:
                                    # Thử parse trực tiếp
                                    data = json.loads(match)
                                    video_url = self._extract_video_url_from_json(data, video_id)
                                    if video_url:
                                        self.log('info', f"Tìm thấy video URL trong window data: {video_url[:150]}...", function_name)
                                        
                                        # JSONからauthor情報も取得を試みる
                                        author_from_json = 'Unknown'
                                        try:
                                            author_from_json = self._extract_author_from_json(data)
                                            if author_from_json:
                                                self.log('info', f"Tìm thấy author từ JSON: {author_from_json}", function_name)
                                        except Exception as e:
                                            self.log('warning', f"Không thể lấy author từ JSON: {e}", function_name, exc_info=True)
                                        
                                        result = {
                                            'video_id': video_id,
                                            'title': '',
                                            'author': author_from_json,
                                            'video_url': video_url
                                        }
                                        self.log('info', "Get video info from HTML hoàn thành thành công (window data - parse trực tiếp)", function_name)
                                        return result
                                except Exception as e2:
                                    self.log('debug', f"Lỗi khi parse trực tiếp: {e2}", function_name, exc_info=True)
                                    pass
            
            self.log('warning', "Không tìm thấy video URL trong HTML", function_name)
            self.log('info', "Get video info from HTML hoàn thành - không tìm thấy video URL", function_name)
            return None
                
        except Exception as e:
            # Log lỗi đầy đủ theo System Instruction
            self.log('error', f"Lỗi khi lấy thông tin từ HTML: {e}", function_name, exc_info=True)
            self.log('info', "Get video info from HTML hoàn thành - Exception", function_name)
            return None
    
    def _extract_author_from_json(self, data: dict, depth: int = 0, max_depth: int = 5) -> Optional[str]:
        """Recursively tìm author (nickname) trong JSON data"""
        if depth > max_depth:
            return None
        
        if not isinstance(data, dict):
            return None
        
        # 優先的にチェックするキー
        priority_keys = ['author', 'user', 'nickname', 'unique_id']
        for key in priority_keys:
            if key in data:
                value = data[key]
                if isinstance(value, dict):
                    # authorオブジェクトの場合、nicknameを探す
                    if 'nickname' in value:
                        return value['nickname']
                    elif 'unique_id' in value:
                        return value['unique_id']
                    # 再帰的に探す
                    result = self._extract_author_from_json(value, depth + 1, max_depth)
                    if result:
                        return result
                elif isinstance(value, str) and value:
                    return value
        
        # すべてのキーを再帰的に探す
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                result = self._extract_author_from_json(value if isinstance(value, dict) else (value[0] if value and isinstance(value[0], dict) else {}), depth + 1, max_depth)
                if result:
                    return result
        
        return None
    
    def _extract_video_url_from_json(self, data: dict, video_id: str = None, depth: int = 0, max_depth: int = 10) -> Optional[str]:
        """Recursively tìm video URL trong JSON data"""
        function_name = "VideoDownloader._extract_video_url_from_json"
        # 深さ制限を追加（無限ループを防ぐ）
        if depth > max_depth:
            return None
        
        # URL không hợp lệ（非ビデオURL）
        exclude_patterns = [
            'chrome.google.com',
            'webstore',
            'douyin_pc_client',
            'bytednsdoc',
            'eden-cn',
            'download/douyin',
            'static',
        ]
        
        def is_valid_video_url(url: str) -> bool:
            """Kiểm tra URL có phải là video URL hợp lệ không"""
            if not url or not isinstance(url, str):
                return False
            if not url.startswith('http'):
                return False
            # Loại bỏ các URL không hợp lệ
            url_lower = url.lower()
            if any(pattern in url_lower for pattern in exclude_patterns):
                return False
            # Phải là .mp4 hoặc .m3u8
            if not ('.mp4' in url_lower or '.m3u8' in url_lower):
                return False
            # URL phải đủ dài
            if len(url) < 50:
                return False
            return True
        
        if isinstance(data, dict):
            # Ưu tiên tìm trong các key cụ thể
            priority_keys = ['playAddr', 'play_addr', 'url_list', 'video_url', 'url', 'play_url', 'playUrl', 'videoUrl']
            for key in priority_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and is_valid_video_url(value):
                        self.log('debug', f"Tìm thấy video URL trong key '{key}' (depth {depth})", function_name)
                        return value
                    elif isinstance(value, list) and len(value) > 0:
                        for item in value:
                            if isinstance(item, str) and is_valid_video_url(item):
                                self.log('debug', f"Tìm thấy video URL trong key '{key}' list (depth {depth})", function_name)
                                return item
                    elif isinstance(value, dict):
                        result = self._extract_video_url_from_json(value, video_id, depth + 1, max_depth)
                        if result:
                            return result
            
            # Tìm trong video data structure
            video_keys = ['video', 'aweme', 'aweme_detail', 'itemInfo', 'item_info']
            for video_key in video_keys:
                if video_key in data:
                    video_data = data[video_key]
                    if isinstance(video_data, dict):
                        result = self._extract_video_url_from_json(video_data, video_id, depth + 1, max_depth)
                        if result:
                            self.log('debug', f"Tìm thấy video URL trong '{video_key}' (depth {depth})", function_name)
                            return result
                    elif isinstance(video_data, list) and len(video_data) > 0:
                        for item in video_data:
                            if isinstance(item, dict):
                                result = self._extract_video_url_from_json(item, video_id, depth + 1, max_depth)
                                if result:
                                    return result
            
            # appキーの下を探索（RENDER_DATAの構造）
            if 'app' in data:
                app_data = data['app']
                if isinstance(app_data, dict):
                    result = self._extract_video_url_from_json(app_data, video_id, depth + 1, max_depth)
                    if result:
                        self.log('debug', f"Tìm thấy video URL trong 'app' (depth {depth})", function_name)
                        return result
            
            # Recursive search trong các giá trị khác
            for key, value in data.items():
                # Bỏ qua các key không liên quan（ただし、appは探索する）
                if key in ['text', 'title', 'desc', 'author', 'user', 'statistics', 'music', 'comment', 'share']:
                    continue
                
                # 深すぎる場合はスキップ
                if depth > 5 and key not in ['video', 'aweme', 'app', 'data', 'item']:
                    continue
                
                result = self._extract_video_url_from_json(value, video_id, depth + 1, max_depth)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._extract_video_url_from_json(item, video_id, depth + 1, max_depth)
                if result:
                    return result
        
        return None
    
    def _get_video_info_from_tikvideo(self, url: str) -> Optional[Dict]:
        """
        Lấy thông tin video từ TikVideo.App API
        
        Args:
            url: URL video Douyin
            
        Returns:
            Dict chứa thông tin video hoặc None nếu lỗi
        """
        function_name = "VideoDownloader._get_video_info_from_tikvideo"
        try:
            # TikVideo.AppのAPIエンドポイントを試す
            # 一般的なパターン: /api/download, /api/video, /api/parse など
            api_endpoints = [
                "https://tikvideo.app/api/download",
                "https://tikvideo.app/api/video",
                "https://tikvideo.app/api/parse",
                "https://api.tikvideo.app/download",
            ]
            
            for api_url in api_endpoints:
                try:
                    self.log('debug', f"Thử gọi TikVideo API: {api_url}", function_name)
                    
                    # POSTリクエストでURLを送信
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": "https://tikvideo.app/",
                    }
                    
                    # 異なる形式でデータを送信
                    payloads = [
                        {"url": url},
                        {"link": url},
                        {"video_url": url},
                        {"input": url},
                    ]
                    
                    for payload in payloads:
                        try:
                            response = self.session.post(
                                api_url,
                                data=payload,
                                headers=headers,
                                timeout=30
                            )
                            
                            # Log API call theo System Instruction
                            self.log('debug', f"TikVideo API response status: {response.status_code}", function_name)
                            
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                    self.log('debug', f"TikVideo API response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}", function_name)
                                    
                                    # レスポンス構造に応じてビデオURLを抽出
                                    video_url = None
                                    
                                    # 様々な可能性のあるキーを試す
                                    possible_keys = [
                                        'video_url', 'videoUrl', 'video', 'url', 'download_url',
                                        'play_url', 'playUrl', 'mp4', 'mp4_url', 'hd_url',
                                        'nwm_video_url', 'nwmVideoUrl', 'video_play_url'
                                    ]
                                    
                                    for key in possible_keys:
                                        if key in data:
                                            value = data[key]
                                            if isinstance(value, str) and value.startswith('http'):
                                                video_url = value
                                                break
                                            elif isinstance(value, dict):
                                                # ネストされた構造を探索
                                                for sub_key in possible_keys:
                                                    if sub_key in value and isinstance(value[sub_key], str) and value[sub_key].startswith('http'):
                                                        video_url = value[sub_key]
                                                        break
                                                if video_url:
                                                    break
                                    
                                    # リスト形式の場合
                                    if not video_url and isinstance(data, dict):
                                        if 'data' in data:
                                            data_obj = data['data']
                                            for key in possible_keys:
                                                if key in data_obj:
                                                    value = data_obj[key]
                                                    if isinstance(value, str) and value.startswith('http'):
                                                        video_url = value
                                                        break
                                    
                                    if video_url:
                                        self.log('info', f"Tìm thấy video URL từ TikVideo API: {video_url[:150]}...", function_name)
                                        return {
                                            'video_id': self.extract_video_id(url) or '',
                                            'title': data.get('title', data.get('desc', '')),
                                            'author': data.get('author', data.get('nickname', '')),
                                            'video_url': video_url
                                        }
                                    
                                except json.JSONDecodeError:
                                    # HTMLレスポンスの場合、ビデオURLを直接検索
                                    html_content = response.text
                                    video_url_match = re.search(r'https://[^"\'<>\s]+\.mp4[^"\'<>\s]*', html_content)
                                    if video_url_match:
                                        video_url = video_url_match.group(0)
                                        if 'douyin_pc_client' not in video_url.lower():
                                            self.log('info', f"Tìm thấy video URL từ TikVideo HTML: {video_url[:150]}...", function_name)
                                            return {
                                                'video_id': self.extract_video_id(url) or '',
                                                'title': '',
                                                'author': '',
                                                'video_url': video_url
                                            }
                                    
                        except Exception as e:
                            self.log('error', f"Lỗi khi gọi TikVideo API {api_url} với payload {payload}: {e}", function_name, exc_info=True)
                            continue
                    
                except Exception as e:
                    self.log('error', f"Lỗi khi kết nối TikVideo API {api_url}: {e}", function_name, exc_info=True)
                    continue
            
            self.log('warning', "Không thể lấy thông tin từ TikVideo.App API", function_name)
            return None
            
        except Exception as e:
            self.log('error', f"Lỗi khi gọi TikVideo API: {e}", function_name, exc_info=True)
            return None
    
    def get_all_videos_from_user(self, user_url: str, progress_callback=None) -> List[str]:
        """
        Lấy tất cả video URL từ user profile (giống như JavaScript code)
        
        Args:
            user_url: URL user profile (ví dụ: https://www.douyin.com/user/MS4wLjABAAAA...)
            progress_callback: Callback function để cập nhật tiến trình (current, total, message)
            
        Returns:
            List các video URL
        """
        function_name = "VideoDownloader.get_all_videos_from_user"
        video_urls = []
        
        try:
            # Extract sec_user_id từ URL (sử dụng compiled regex - tối ưu hiệu suất)
            match = self._regex_patterns['user_id_pattern'].search(user_url)
            if not match:
                self.log('error', f"Không thể trích xuất user ID từ URL: {user_url}", function_name)
                if progress_callback:
                    progress_callback(0, 0, f"Không thể trích xuất user ID từ URL: {user_url}")
                return []
            
            sec_user_id = match.group(1)
            self.log('info', f"User ID extracted: {sec_user_id}", function_name)
            self.log('debug', f"User ID: {sec_user_id}", function_name)
            
            if progress_callback:
                progress_callback(0, 0, f"Đang kết nối với user ID: {sec_user_id}...")
            
            has_more = 1
            max_cursor = 0
            error_count = 0
            page_count = 0
            
            while has_more == 1 and error_count < 5:
                try:
                    page_count += 1
                    # API endpoint giống như JavaScript code
                    api_url = f"https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id={sec_user_id}&max_cursor={max_cursor}&count=20&version_code=170400&version_name=17.4.0"
                    
                    message = f"Đang tải trang {page_count}... (Đã tìm thấy {len(video_urls)} video)"
                    self.log('info', message)
                    if progress_callback:
                        progress_callback(len(video_urls), 0, message)
                    
                    # Log API call theo System Instruction
                    self.log('info', f"Đang gọi API: {api_url}")
                    response = self.session.get(api_url, timeout=15)
                    
                    # Log API response theo System Instruction
                    self.log('debug', f"API response status: {response.status_code}")
                    if response.status_code != 200:
                        self.log('warning', f"HTTP Error: {response.status_code}")
                        self.log('error', f"API call failed: {api_url} - Status {response.status_code}")
                        error_count += 1
                        import time
                        time.sleep(2)
                        continue
                    
                    data = response.json()
                    
                    # Log thông tin response để debug
                    if data:
                        self.log('debug', f"API response keys: {list(data.keys())}")
                        if 'aweme_list' in data:
                            self.log('info', f"Tìm thấy {len(data['aweme_list'])} video trong trang {page_count}")
                        else:
                            self.log('warning', f"Response không có 'aweme_list', keys: {list(data.keys())}")
                    
                    if not data or 'aweme_list' not in data:
                        self.log('warning', "Không tìm thấy video data, thử lại...")
                        error_count += 1
                        import time
                        time.sleep(3)
                        continue
                    
                    error_count = 0
                    has_more = data.get('has_more', 0)
                    max_cursor = data.get('max_cursor', 0)
                    
                    self.log('info', f"Trang {page_count}: has_more={has_more}, max_cursor={max_cursor}, videos_in_page={len(data['aweme_list'])}")
                    
                    # Extract video URLs
                    videos_in_page = len(data.get('aweme_list', []))
                    for idx, video in enumerate(data['aweme_list']):
                        # Lấy video ID để tạo video page URL (giống như JavaScript code)
                        aweme_id = video.get('aweme_id', '')
                        
                        # Lấy thông tin author để xác minh
                        author_info = video.get('author', {})
                        author_nickname = author_info.get('nickname', 'Unknown')
                        author_unique_id = author_info.get('unique_id', '')
                        author_uid = author_info.get('uid', '')
                        
                        # Lấy thông tin video
                        desc = video.get('desc', '')[:50]  # Lấy 50 ký tự đầu của mô tả
                        
                        if aweme_id:
                            # Lấy width và height để xác định hướng video
                            video_data = video.get('video', {})
                            width = video_data.get('width', 0) if video_data else 0
                            height = video_data.get('height', 0) if video_data else 0
                            
                            # Xác định hướng video
                            orientation = 'unknown'
                            if width > 0 and height > 0:
                                # Log để debug
                                self.log('info', f"Video {aweme_id} (get_all_videos_from_user): width={width}, height={height}, ratio={height/width if width > 0 else 0:.2f}", function_name)
                                if height > width:
                                    orientation = 'vertical'  # 縦向き (dọc)
                                elif width > height:
                                    orientation = 'horizontal'  # 横向き (ngang)
                                else:
                                    orientation = 'square'  # 正方形
                                self.log('info', f"Video {aweme_id} (get_all_videos_from_user): orientation={orientation} (width={width}, height={height})", function_name)
                            
                            # Log thông tin video để debug
                            self.log('info', f"Video {len(video_urls)+1}: aweme_id={aweme_id}, orientation={orientation} ({width}x{height}), author={author_nickname} (@{author_unique_id}), desc={desc}", function_name)
                            
                            # Thử lấy direct video URL trước (giống như douyin-video-links1.txt)
                            video_url = None
                            
                            if video_data:
                                # Thử play_addr trước
                                play_addr = video_data.get('play_addr', {})
                                if play_addr:
                                    url_list = play_addr.get('url_list', [])
                                    if url_list:
                                        video_url = url_list[0]
                                        # HTTPをHTTPSに変換
                                        if not video_url.startswith("https"):
                                            video_url = video_url.replace("http", "https")
                                
                                # Nếu không có play_addr, thử download_addr
                                if not video_url:
                                    download_addr = video_data.get('download_addr', {})
                                    if download_addr:
                                        url_list = download_addr.get('url_list', [])
                                        if url_list:
                                            video_url = url_list[0]
                                            if not video_url.startswith("https"):
                                                video_url = video_url.replace("http", "https")
                            
                            # Nếu có direct video URL, sử dụng nó (giống như douyin-video-links1.txt)
                            if video_url:
                                self.log('info', f"Tìm thấy direct video URL cho aweme_id={aweme_id}: {video_url[:100]}...")
                                self.log('debug', f"Thêm video (direct URL): {video_url[:100]}... (Author: {author_nickname})")
                                video_urls.append(video_url)
                            else:
                                # Nếu không có direct URL, sử dụng video page URL (fallback)
                                video_page_url = f"https://www.douyin.com/video/{aweme_id}"
                                video_urls.append(video_page_url)
                                self.log('warning', f"Không tìm thấy direct video URL cho aweme_id={aweme_id}, sử dụng video page URL: {video_page_url}")
                                self.log('debug', f"Thêm video (page URL): {video_page_url} (Author: {author_nickname})")
                            
                            # Cập nhật tiến trình cho từng video
                            if progress_callback:
                                message = f"Đang xử lý video {len(video_urls)}... (Trang {page_count}, Video {idx+1}/{videos_in_page}, Author: {author_nickname})"
                                progress_callback(len(video_urls), 0, message)
                    
                    self.log('info', f"Đã tìm thấy {len(video_urls)} video")
                    
                    # Cập nhật tiến trình sau khi xử lý xong trang
                    if progress_callback:
                        message = f"Đã tải xong trang {page_count}... (Tổng: {len(video_urls)} video)"
                        progress_callback(len(video_urls), 0, message)
                    
                    # Delay giữa các request
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    error_msg = f"Lỗi khi lấy video: {e}"
                    self.log('error', error_msg, exc_info=True)
                    if progress_callback:
                        progress_callback(len(video_urls), 0, f"Lỗi: {error_msg}, đang thử lại...")
                    error_count += 1
                    import time
                    time.sleep(3)
            
            final_message = f"Hoàn thành! Tổng cộng {len(video_urls)} video"
            self.log('info', final_message)
            if progress_callback:
                progress_callback(len(video_urls), len(video_urls), final_message)
            return video_urls
            
        except Exception as e:
            self.log('error', f"Lỗi khi lấy video từ user: {e}", exc_info=True)
            return []
    
    def _select_video_url(self, video_info: Dict, video_format: str = "auto") -> Optional[str]:
        """
        Chọn video URL dựa trên format được chọn
        
        Args:
            video_info: Dict chứa thông tin video (có thể có 'video_urls' hoặc 'video_url')
            video_format: Định dạng video ("highest", "high", "medium", "low", "auto")
            
        Returns:
            Video URL được chọn hoặc None
        """
        function_name = "VideoDownloader._select_video_url"
        # Nếu có nhiều URL (video_urls), chọn dựa trên format
        if 'video_urls' in video_info and video_info['video_urls']:
            all_urls = video_info['video_urls']
            self.log('info', f"Tìm thấy {len(all_urls)} định dạng video có sẵn", function_name)
            
            if video_format == "auto" or video_format == "highest":
                # Chọn chất lượng cao nhất (đã được sắp xếp)
                selected = all_urls[0]
                self.log('info', f"Chọn định dạng: {video_format}, Quality: {selected.get('quality', 'N/A')}", function_name)
                return selected['url']
            elif video_format == "high":
                # Chọn 1/4 đầu (chất lượng cao)
                idx = max(0, len(all_urls) // 4)
                selected = all_urls[idx]
                self.log('info', f"Chọn định dạng: {video_format}, Quality: {selected.get('quality', 'N/A')}", function_name)
                return selected['url']
            elif video_format == "medium":
                # Chọn giữa (chất lượng trung bình)
                idx = len(all_urls) // 2
                selected = all_urls[idx]
                self.log('info', f"Chọn định dạng: {video_format}, Quality: {selected.get('quality', 'N/A')}", function_name)
                return selected['url']
            elif video_format == "low":
                # Chọn cuối (chất lượng thấp)
                selected = all_urls[-1]
                self.log('info', f"Chọn định dạng: {video_format}, Quality: {selected.get('quality', 'N/A')}", function_name)
                return selected['url']
            else:
                # Mặc định chọn đầu tiên
                return all_urls[0]['url']
        
        # Nếu chỉ có một URL (video_url), trả về trực tiếp
        return video_info.get('video_url')
    
    def download_video(self, video_url: str, save_path: str, timeout_settings: dict = None) -> dict:
        """
        Tải video từ URL về máy với timeout detection và retry logic
        
        Args:
            video_url: URL video thực tế
            save_path: Đường dẫn lưu file
            timeout_settings: Dict chứa các cài đặt timeout và retry (None thì dùng giá trị mặc định)
                - download_timeout_seconds: Timeout tổng (mặc định: 300s = 5 phút)
                - chunk_timeout_seconds: Timeout cho mỗi chunk (mặc định: 30s)
                - max_retries: Số lần retry tối đa (mặc định: 3)
                - retry_delay_seconds: Thời gian chờ giữa các retry (mặc định: 5s)
                - max_download_time_seconds: Thời gian tối đa (mặc định: 1800s = 30 phút)
                - enable_timeout_detection: Bật/tắt timeout detection (mặc định: True)
                - enable_auto_retry: Bật/tắt auto retry (mặc định: True)
                - enable_skip_slow_videos: Bật/tắt skip video quá lâu (mặc định: True)
                - chunk_size: Kích thước chunk (mặc định: 8192 bytes)
            
        Returns:
            Dict chứa kết quả:
                - success: True nếu thành công, False nếu thất bại
                - error: Thông điệp lỗi (nếu có)
                - retry_count: Số lần đã retry
                - timeout_detected: True nếu phát hiện timeout
                - skipped: True nếu bị skip do quá lâu
                - download_time: Thời gian tải (giây)
                - file_size: Kích thước file (bytes)
        """
        function_name = "VideoDownloader.download_video"
        
        # Sử dụng cài đặt mặc định nếu không được cung cấp
        if timeout_settings is None:
            timeout_settings = {
                'download_timeout_seconds': 300,  # 5 phút
                'chunk_timeout_seconds': 30,  # 30 giây
                'max_retries': 3,
                'retry_delay_seconds': 5,
                'max_download_time_seconds': 1800,  # 30 phút
                'enable_timeout_detection': True,
                'enable_auto_retry': True,
                'enable_skip_slow_videos': True,
                'chunk_size': 8192
            }
        
        # Log cài đặt timeout
        self.log('info', "=" * 60, function_name)
        self.log('info', f"{function_name} - Bắt đầu", function_name)
        self.log('info', f"  - Video URL: {video_url[:100]}...", function_name)
        save_path_abs = os.path.abspath(save_path)
        self.log('info', f"  - Save path: {save_path_abs}", function_name)
        self.log('debug', f"  - Timeout settings: {timeout_settings}", function_name)
        
        # Gọi download_video_with_retry để xử lý retry logic
        return self.download_video_with_retry(
            video_url, save_path, timeout_settings, retry_count=0
        )
    
    def download_video_with_retry(
        self, 
        video_url: str, 
        save_path: str, 
        timeout_settings: dict, 
        retry_count: int = 0
    ) -> dict:
        """
        Tải video với retry logic và timeout detection (internal method)
        
        Args:
            video_url: URL video
            save_path: Đường dẫn lưu file
            timeout_settings: Dict cài đặt timeout
            retry_count: Số lần đã retry (dùng cho recursive call)
            
        Returns:
            Dict kết quả (giống như download_video)
        """
        function_name = "VideoDownloader.download_video_with_retry"
        
        # Kiểm tra số lần retry
        max_retries = timeout_settings.get('max_retries', 3)
        enable_auto_retry = timeout_settings.get('enable_auto_retry', True)
        
        if retry_count > 0:
            retry_delay = timeout_settings.get('retry_delay_seconds', 5)
            self.log('info', f"Retry lần {retry_count}/{max_retries} sau {retry_delay} giây...", function_name)
            import time
            time.sleep(retry_delay)
        
        # Ghi lại thời gian bắt đầu (theo System Instruction 4.4 - log bắt đầu)
        import time
        start_time = time.time()
        self.log('debug', f"Bắt đầu tải video (retry {retry_count}/{max_retries})", function_name)
        
        # Đảm bảo save_path là絶対パス (theo System Instruction 8)
        save_path_abs = os.path.abspath(save_path)
        self.log('debug', f"Save path (absolute): {save_path_abs}", function_name)
        
        try:
            # Kiểm tra thư mục (theo System Instruction 8 - tự động tạo thư mục)
            save_dir = os.path.dirname(save_path)
            if not os.path.exists(save_dir):
                self.log('info', f"Thư mục không tồn tại, đang tạo: {save_dir}", function_name)
                os.makedirs(save_dir, exist_ok=True)
            
            # Kiểm tra timeout tổng trước khi bắt đầu
            max_download_time = timeout_settings.get('max_download_time_seconds', 1800)
            enable_skip_slow = timeout_settings.get('enable_skip_slow_videos', True)
            
            if enable_skip_slow and max_download_time > 0:
                self.log('debug', f"Max download time: {max_download_time} giây ({max_download_time/60:.1f} phút)", function_name)
            
            # Log API call theo System Instruction 4.4 - log request + status code
            self.log('info', f"Đang gửi request để tải video: {video_url[:100]}...", function_name)
            download_timeout = timeout_settings.get('download_timeout_seconds', 300)
            response = self.session.get(video_url, stream=True, timeout=download_timeout)
            response.raise_for_status()
            
            # Log API response theo System Instruction 4.4
            self.log('debug', f"Response status: {response.status_code}", function_name)
            
            # Lấy thông tin về file size nếu có (theo System Instruction 4.3 - DEBUG cho output)
            content_length = response.headers.get('Content-Length')
            if content_length:
                file_size = int(content_length)
                self.log('info', f"File size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)", function_name)
            else:
                self.log('warning', "Không thể lấy file size từ header", function_name)
                file_size = None
            
            self.log('info', "Đang tải file...", function_name)
            downloaded_size = 0
            chunk_count = 0
            
            # Cài đặt timeout detection
            enable_timeout_detection = timeout_settings.get('enable_timeout_detection', True)
            chunk_timeout = timeout_settings.get('chunk_timeout_seconds', 30)
            chunk_size = timeout_settings.get('chunk_size', 8192)
            
            # Biến để theo dõi progress và timeout
            last_progress_time = time.time()
            last_downloaded_size = 0
            
            # Tải file với timeout detection
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    # Kiểm tra stop signal (trong mỗi chunk)
                    if hasattr(self, '_service_ref') and self._service_ref and self._service_ref.should_stop:
                        self.log('warning', "Download stopped by user during file download")
                        try:
                            f.flush()
                        except Exception as e:
                            self.log('warning', f"Lỗi khi flush file: {e}")
                        # Xóa file đã tải một phần (với retry logic)
                        self._cleanup_partial_file(save_path)
                        return {
                            'success': False,
                            'error': 'Stopped by user',
                            'retry_count': retry_count,
                            'timeout_detected': False,
                            'skipped': False,
                            'download_time': time.time() - start_time,
                            'file_size': downloaded_size
                        }
                    
                    # Kiểm tra timeout tổng (max download time)
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    if enable_skip_slow and max_download_time > 0 and elapsed_time > max_download_time:
                        self.log('warning', f"Video quá lâu ({elapsed_time:.1f}s > {max_download_time}s), bỏ qua...")
                        try:
                            f.flush()
                        except Exception as e:
                            self.log('warning', f"Lỗi khi flush file: {e}")
                        self._cleanup_partial_file(save_path)
                        return {
                            'success': False,
                            'error': f'Video quá lâu (>{max_download_time}s)',
                            'retry_count': retry_count,
                            'timeout_detected': False,
                            'skipped': True,
                            'download_time': elapsed_time,
                            'file_size': downloaded_size,
                            'file_path': None  # File đã bị xóa
                        }
                    
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        chunk_count += 1
                        
                        # Timeout detection: Kiểm tra xem có progress trong chunk_timeout giây không
                        if enable_timeout_detection and chunk_timeout > 0:
                            current_chunk_time = time.time()
                            time_since_last_progress = current_chunk_time - last_progress_time
                            
                            # Nếu có progress (downloaded_size tăng), reset timer
                            if downloaded_size > last_downloaded_size:
                                last_progress_time = current_chunk_time
                                last_downloaded_size = downloaded_size
                            # Nếu không có progress trong chunk_timeout giây, phát hiện timeout
                            elif time_since_last_progress > chunk_timeout:
                                self.log('warning', f"Phát hiện timeout: Không có progress trong {time_since_last_progress:.1f}s (timeout: {chunk_timeout}s)")
                                self.log('warning', f"Downloaded size: {downloaded_size} bytes, không thay đổi trong {time_since_last_progress:.1f}s")
                                try:
                                    f.flush()
                                except Exception as e:
                                    self.log('warning', f"Lỗi khi flush file: {e}")
                                self._cleanup_partial_file(save_path)
                                
                                # Retry nếu được bật và chưa vượt quá max_retries
                                if enable_auto_retry and retry_count < max_retries:
                                    self.log('info', f"Sẽ retry download sau {timeout_settings.get('retry_delay_seconds', 5)} giây...")
                                    return self.download_video_with_retry(
                                        video_url, save_path, timeout_settings, retry_count + 1
                                    )
                                else:
                                    return {
                                        'success': False,
                                        'error': f'Timeout: Không có progress trong {time_since_last_progress:.1f}s',
                                        'retry_count': retry_count,
                                        'timeout_detected': True,
                                        'skipped': False,
                                        'download_time': elapsed_time,
                                        'file_size': downloaded_size,
                                        'file_path': None  # File có thể đã bị xóa
                                    }
                        
                        # Log tiến trình mỗi 1000 chunks hoặc mỗi 25% (giảm log spam - System Instruction 6.2)
                        # Tăng từ 500 lên 1000 chunks để giảm log I/O operations
                        if content_length:
                            progress = (downloaded_size / file_size) * 100
                            progress_int = int(progress)
                            # Log mỗi 1000 chunks hoặc mỗi 25% progress (giảm log spam)
                            if chunk_count % 1000 == 0 or (progress_int % 25 == 0 and chunk_count % 500 == 0):
                                self.log('debug', f"Đã tải: {downloaded_size} / {file_size} bytes ({progress:.1f}%)", function_name)
                        else:
                            # Không có content_length, log mỗi 1000 chunks (tăng từ 500)
                            if chunk_count % 1000 == 0:
                                self.log('debug', f"Đã tải: {downloaded_size} bytes ({chunk_count} chunks)", function_name)
            
            # Kiểm tra file đã tải
            end_time = time.time()
            download_time = end_time - start_time
            
            if os.path.exists(save_path):
                actual_size = os.path.getsize(save_path)
                
                # Tính toán tốc độ tải
                if download_time > 0:
                    download_speed_mbps = (actual_size / 1024 / 1024) / download_time
                    download_speed_kbps = (actual_size / 1024) / download_time
                    self.log('info', f"Đã tải thành công - File size: {actual_size} bytes ({actual_size / 1024 / 1024:.2f} MB)")
                    self.log('info', f"Thời gian tải: {download_time:.2f} giây ({download_time/60:.2f} phút)")
                    self.log('info', f"Tốc độ tải: {download_speed_mbps:.2f} MB/s ({download_speed_kbps:.2f} KB/s)")
                    self.log('debug', f"Retry count: {retry_count}")
                else:
                    self.log('info', f"Đã tải thành công - File size: {actual_size} bytes ({actual_size / 1024 / 1024:.2f} MB)")
                    self.log('info', f"Thời gian tải: < 0.01 giây")
                
                if content_length and actual_size != file_size:
                    self.log('warning', f"File size không khớp: expected {file_size}, actual {actual_size}")
                
                self.log('info', "=" * 60)
                return {
                    'success': True,
                    'error': None,
                    'retry_count': retry_count,
                    'timeout_detected': False,
                    'skipped': False,
                    'download_time': download_time,
                    'file_size': actual_size,
                    'file_path': save_path  # Thêm file_path vào result (theo System Instruction 4.3 - DEBUG cho output)
                }
            else:
                self.log('error', "File không tồn tại sau khi tải")
                self.log('error', "=" * 60)
                return {
                    'success': False,
                    'error': 'File không tồn tại sau khi tải',
                    'retry_count': retry_count,
                    'timeout_detected': False,
                    'skipped': False,
                    'download_time': download_time,
                    'file_size': 0,
                    'file_path': None  # File không tồn tại
                }
            
        except requests.exceptions.Timeout as e:
            self.log('error', f"Timeout khi tải video: {e}", exc_info=True)
            
            # Retry nếu được bật
            if enable_auto_retry and retry_count < max_retries:
                self.log('info', f"Sẽ retry download sau {timeout_settings.get('retry_delay_seconds', 5)} giây...")
                return self.download_video_with_retry(
                    video_url, save_path, timeout_settings, retry_count + 1
                )
            
            self.log('error', "=" * 60)
            return {
                'success': False,
                'error': f'Timeout: {str(e)}',
                'retry_count': retry_count,
                'timeout_detected': True,
                'skipped': False,
                'download_time': time.time() - start_time,
                'file_size': 0,
                'file_path': None  # File chưa được tạo hoặc đã bị xóa
            }
            
        except requests.exceptions.RequestException as e:
            self.log('error', f"Request error khi tải video: {e}", exc_info=True)
            
            # Retry nếu được bật
            if enable_auto_retry and retry_count < max_retries:
                self.log('info', f"Sẽ retry download sau {timeout_settings.get('retry_delay_seconds', 5)} giây...")
                return self.download_video_with_retry(
                    video_url, save_path, timeout_settings, retry_count + 1
                )
            
            self.log('error', "=" * 60)
            return {
                'success': False,
                'error': f'Request error: {str(e)}',
                'retry_count': retry_count,
                'timeout_detected': False,
                'skipped': False,
                'download_time': time.time() - start_time,
                'file_size': 0,
                'file_path': None  # File chưa được tạo hoặc đã bị xóa
            }
            
        except Exception as e:
            self.log('error', f"Lỗi không xác định khi tải: {e}", exc_info=True)
            
            # Retry nếu được bật (chỉ cho một số lỗi cụ thể)
            if enable_auto_retry and retry_count < max_retries and isinstance(e, (IOError, OSError)):
                self.log('info', f"Sẽ retry download sau {timeout_settings.get('retry_delay_seconds', 5)} giây...")
                return self.download_video_with_retry(
                    video_url, save_path, timeout_settings, retry_count + 1
                )
            
            self.log('error', "=" * 60)
            return {
                'success': False,
                'error': f'Lỗi không xác định: {str(e)}',
                'retry_count': retry_count,
                'timeout_detected': False,
                'skipped': False,
                'download_time': time.time() - start_time,
                'file_size': 0,
                'file_path': None  # File chưa được tạo hoặc đã bị xóa
            }
    
    def _cleanup_partial_file(self, save_path: str):
        """
        Xóa file đã tải một phần (với retry logic để tránh PermissionError trên Windows)
        
        Args:
            save_path: Đường dẫn file cần xóa
        """
        function_name = "VideoDownloader._cleanup_partial_file"
        
        try:
            import time
            time.sleep(0.2)  # Đợi file handle đóng
            
            if os.path.exists(save_path):
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        os.remove(save_path)
                        self.log('info', f"Đã xóa file đã tải một phần (thử lần {retry+1})")
                        return
                    except PermissionError as pe:
                        if retry < max_retries - 1:
                            self.log('debug', f"File đang được sử dụng, đợi 0.5 giây rồi thử lại... (thử lần {retry+1}/{max_retries})")
                            time.sleep(0.5)
                        else:
                            self.log('warning', f"Không thể xóa file đã tải một phần sau {max_retries} lần thử: {pe}")
                            self.log('warning', f"File sẽ được giữ lại: {os.path.abspath(save_path)}")
                    except Exception as e:
                        self.log('error', f"Lỗi khi xóa file đã tải một phần: {e}", exc_info=True)
                        break
        except Exception as e:
            self.log('error', f"Lỗi khi cleanup file: {e}", exc_info=True)
    
    def _get_video_orientation_from_file(self, file_path: str) -> str:
        """
        ビデオファイルのメタデータから向きを取得
        
        Args:
            file_path: ビデオファイルのパス
            
        Returns:
            'vertical', 'horizontal', 'square', または 'unknown'
        """
        function_name = "VideoDownloader._get_video_orientation_from_file"
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                self.log('warning', f"Không thể mở video file: {file_path}", function_name)
                return 'unknown'
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            if width > 0 and height > 0:
                # Log để debug
                self.log('info', f"Video file {file_path}: width={width}, height={height}, ratio={height/width if width > 0 else 0:.2f}", function_name)
                if height > width:
                    orientation = 'vertical'  # 縦向き (dọc)
                elif width > height:
                    orientation = 'horizontal'  # 横向き (ngang)
                else:
                    orientation = 'square'  # 正方形
                self.log('info', f"Video file {file_path}: orientation={orientation} (width={width}, height={height})", function_name)
                return orientation
            else:
                return 'unknown'
        except ImportError:
            self.log('warning', "opencv-python chưa được cài đặt, không thể lấy metadata từ file", function_name)
            return 'unknown'
        except Exception as e:
            self.log('error', f"Lỗi khi lấy metadata từ file {file_path}: {e}", function_name, exc_info=True)
            return 'unknown'
    
    def process_video(self, url: str, download_folder: str, naming_mode: str = "video_id", video_format: str = "auto", orientation_filter: str = "all", timeout_settings: dict = None) -> Dict:
        """
        Xử lý một video từ URL đến file đã tải
        
        Args:
            url: URL video gốc
            download_folder: Thư mục lưu file
            naming_mode: Chế độ đặt tên ("video_id" hoặc "timestamp")
            video_format: Định dạng video ("highest", "high", "medium", "low", "auto")
            orientation_filter: Lọc theo hướng video ("all", "vertical", "horizontal")
            
        Returns:
            Dict chứa kết quả: {
                'success': bool,
                'video_id': str,
                'file_path': str,
                'error': str
            }
        """
        function_name = "VideoDownloader.process_video"
        self.log('info', "=" * 60, function_name)
        self.log('info', "VideoDownloader.process_video - Bắt đầu xử lý video", function_name)
        self.log('info', f"  - URL: {url}", function_name)
        # Đảm bảo download_folder là絶対パスで表示
        download_folder_abs = os.path.abspath(download_folder)
        self.log('info', f"  - Download folder: {download_folder_abs}", function_name)
        self.log('info', f"  - Naming mode: {naming_mode}", function_name)
        self.log('info', f"  - Video format: {video_format}", function_name)
        self.log('info', f"  - Orientation filter: {orientation_filter}", function_name)
        
        result = {
            'success': False,
            'video_id': None,
            'file_path': None,
            'error': None,
            'url': url,
            # Thống kê timeout và retry (mới)
            'retry_count': 0,
            'timeout_detected': False,
            'skipped': False,
            'download_time': 0,
            'file_size': 0,
            # Thống kê orientation filter (mới)
            'filtered_by_orientation': False,
            'orientation': None,
            'width': 0,
            'height': 0
        }
        
        try:
            # Bước 1: Chuẩn hóa URL (resolve short URL nếu cần)
            normalized_url = self.normalize_url(url)
            if not normalized_url:
                result['error'] = "URL không hợp lệ"
                self.log('warning', "URL không hợp lệ sau khi normalize", function_name)
                self.log('info', "Process video hoàn thành - URL không hợp lệ", function_name)
                return result
            
            self.log('debug', f"URL sau khi normalize: {normalized_url[:100]}...", function_name)
            
            # Bước 2: Lấy thông tin video
            self.log('info', f"Đang lấy thông tin video từ URL: {normalized_url[:100]}...", function_name)
            video_info = self.get_video_info(normalized_url)
            if not video_info:
                # Nếu normalizeされたURLが短縮URLと異なる場合、既に解決済みなので
                # URL gốcに戻す必要はない（URL gốcは短縮URLなので）
                error_msg = "Không thể lấy thông tin video. Có thể:\n1. Cookie không hợp lệ hoặc đã hết hạn\n2. Video không tồn tại hoặc bị chặn\n3. API Douyin đã thay đổi\n\nVui lòng kiểm tra lại cookie và thử lại."
                result['error'] = error_msg
                self.log('error', error_msg, function_name)
                self.log('info', "Process video hoàn thành - không thể lấy thông tin video", function_name)
                return result
            
            video_id = video_info.get('video_id')
            author = video_info.get('author', 'Unknown')
            title = video_info.get('title', 'N/A')
            orientation = video_info.get('orientation', 'unknown')
            width = video_info.get('width', 0)
            height = video_info.get('height', 0)
            
            # Cập nhật result với thông tin orientation (mới)
            result['orientation'] = orientation
            result['width'] = width
            result['height'] = height
            
            # Tính tỷ lệ khung hình (aspect ratio) để log chi tiết (mới)
            aspect_ratio = 0
            if width > 0 and height > 0:
                aspect_ratio = width / height
                orientation_detailed = "landscape" if width > height else ("portrait" if height > width else "square")
            else:
                orientation_detailed = "unknown"
            
            # Log thông tin video để debug (theo System Instruction 4.3 - DEBUG cho input/output)
            self.log('debug', f"Video info retrieved - video_id={video_id}, author={author}, orientation={orientation} ({orientation_detailed}), size={width}x{height}, aspect_ratio={aspect_ratio:.2f}, title={title[:50] if title else 'N/A'}", function_name)
            self.log('debug', f"Video info keys: {list(video_info.keys())}", function_name)
            
            # Kiểm tra orientation filter (cải thiện logging)
            # 直接ビデオURLの場合、orientationはunknownになるが、ダウンロード後に判定する
            # そのため、直接ビデオURLの場合は、ここではフィルタをスキップし、ダウンロード後に判定する
            is_direct_video_url = (video_info.get('video_id') is None and 
                                  video_info.get('title') == 'Direct Video')
            
            if orientation_filter != "all":
                # Log filter đang được áp dụng (theo System Instruction 4.4 - log các bước chính)
                filter_name_map = {
                    "horizontal": "Landscape (ngang)",
                    "vertical": "Portrait (dọc)",
                    "all": "Tất cả"
                }
                filter_display_name = filter_name_map.get(orientation_filter, orientation_filter)
                self.log('info', f"Đang áp dụng orientation filter: {filter_display_name}", function_name)
                
                if orientation != "unknown":
                    # APIから取得したorientationがある場合、ここでフィルタを適用
                    # Tính toán orientation dựa trên width/height nếu cần (mới)
                    if width > 0 and height > 0:
                        calculated_orientation = "horizontal" if width > height else ("vertical" if height > width else "square")
                        if calculated_orientation != orientation and orientation != "square":
                            self.log('debug', f"Orientation từ API ({orientation}) không khớp với tính toán ({calculated_orientation}), sử dụng orientation từ API", function_name)
                    
                    if orientation != orientation_filter:
                        result['error'] = f"Video orientation ({orientation} - {orientation_detailed}) không khớp với filter ({orientation_filter} - {filter_display_name})"
                        result['filtered_by_orientation'] = True  # Đánh dấu là bị filter
                        # Log chi tiết về lý do filter (theo System Instruction 4.3 - WARNING cho cảnh báo)
                        self.log('warning', f"Bỏ qua video {video_id} - Lý do: orientation không khớp", function_name)
                        self.log('debug', f"  - Video orientation: {orientation} ({orientation_detailed})", function_name)
                        self.log('debug', f"  - Video size: {width}x{height} (aspect ratio: {aspect_ratio:.2f})", function_name)
                        self.log('debug', f"  - Filter yêu cầu: {orientation_filter} ({filter_display_name})", function_name)
                        self.log('debug', f"  - Video ID: {video_id}", function_name)
                        self.log('debug', f"  - Author: {author}", function_name)
                        self.log('debug', f"  - Title: {title[:100] if title else 'N/A'}", function_name)
                        self.log('info', "Process video hoàn thành - bị filter bởi orientation", function_name)
                        return result
                    else:
                        self.log('debug', f"Video {video_id} phù hợp với orientation filter: {orientation_filter} ({filter_display_name})", function_name)
                        self.log('debug', f"  - Video size: {width}x{height} (aspect ratio: {aspect_ratio:.2f})", function_name)
                elif is_direct_video_url:
                    # 直接ビデオURLの場合、ダウンロード後に判定する
                    self.log('info', f"Video {video_id} là direct video URL, sẽ kiểm tra orientation sau khi tải (filter: {filter_display_name})", function_name)
                else:
                    # orientationがunknownで、直接ビデオURLでもない場合
                    self.log('warning', f"Video {video_id} có orientation=unknown, không thể áp dụng filter ({filter_display_name})", function_name)
                    self.log('debug', f"  - Video size: {width}x{height} (aspect ratio: {aspect_ratio:.2f})", function_name)
            else:
                # Không có filter, log để debug (theo System Instruction 4.3 - DEBUG cho input/output)
                self.log('debug', f"Không có orientation filter, tải tất cả video (orientation: {orientation}, size: {width}x{height})", function_name)
            
            # Chọn video URL dựa trên format được chọn
            self.log('debug', f"Đang chọn video URL với format: {video_format}", function_name)
            video_url = self._select_video_url(video_info, video_format)
            
            if not video_url:
                result['error'] = "Không tìm thấy link video"
                self.log('error', "Không tìm thấy link video", function_name)
                self.log('info', "Process video hoàn thành - không tìm thấy link video", function_name)
                return result
            
            self.log('debug', f"Đã chọn video URL: {video_url[:100]}...", function_name)
            
            result['video_id'] = video_id
            result['author'] = author
            
            # Bước 3: Kiểm tra orientation filter (nếu orientation là unknown で、direct video URLの場合)
            # 直接ビデオURLの場合、ダウンロード後にメタデータから向きを判定する必要がある
            # フィルタが設定されている場合、ダウンロード後に判定して、一致しない場合は削除する
            is_direct_video_url = (video_info.get('video_id') is None and 
                                  video_info.get('title') == 'Direct Video')
            needs_orientation_check_after_download = (orientation == 'unknown' and 
                                                      is_direct_video_url and
                                                      orientation_filter != "all")
            
            if needs_orientation_check_after_download:
                self.log('info', f"Video là direct URL, sẽ kiểm tra orientation sau khi tải (filter: {orientation_filter})", function_name)
            
            # Bước 4: Tạo thư mục theo tên người dùng
            # Làm sạch tên người dùng (loại bỏ ký tự không hợp lệ cho tên thư mục)
            # Sử dụng compiled regex pattern (tối ưu hiệu suất)
            safe_author = self._regex_patterns['safe_filename_pattern'].sub('_', author.strip())
            if not safe_author or safe_author == '':
                safe_author = 'Unknown'
            
            # Tạo thư mục con theo tên người dùng (theo System Instruction 8 - tự động tạo thư mục)
            user_folder = os.path.join(download_folder, safe_author)
            # Đảm bảo thư mục là絶対パス (theo System Instruction 8)
            user_folder = os.path.abspath(user_folder)
            os.makedirs(user_folder, exist_ok=True)
            self.log('info', f"Lưu video vào thư mục: {user_folder}", function_name)
            
            # Bước 4: Tạo tên file
            if naming_mode == "video_id" and video_id:
                filename = f"{video_id}.mp4"
            else:
                # Nếu không có video_id hoặc naming_mode là timestamp, dùng timestamp
                # Sử dụng timestamp với microsecond để tránh trùng lặp
                timestamp = int(time.time() * 1000000)  # Microsecond precision
                filename = f"video_{timestamp}.mp4"
            
            file_path = os.path.join(user_folder, filename)
            # Đảm bảo file_path là絶対パス
            file_path = os.path.abspath(file_path)
            
            # Kiểm tra file đã tồn tại chưa, nếu có thì thêm số thứ tự
            if os.path.exists(file_path):
                base_name = filename.rsplit('.', 1)[0]  # Tên file không có extension
                extension = filename.rsplit('.', 1)[1] if '.' in filename else 'mp4'
                counter = 1
                while os.path.exists(file_path):
                    new_filename = f"{base_name}_{counter}.{extension}"
                    file_path = os.path.join(user_folder, new_filename)
                    file_path = os.path.abspath(file_path)
                    counter += 1
                self.log('info', f"File đã tồn tại, đổi tên thành: {os.path.basename(file_path)}", function_name)
            
            # Bước 5: Tải video với timeout settings
            # Sử dụng timeout_settings từ parameter, hoặc lấy từ config nếu không có
            if timeout_settings is None:
                # Nếu không có timeout_settings, sử dụng giá trị mặc định
                # (trong tương lai có thể lấy từ CookieManager nếu cần)
                timeout_settings = {
                    'download_timeout_seconds': 300,  # 5 phút
                    'chunk_timeout_seconds': 30,  # 30 giây
                    'max_retries': 3,
                    'retry_delay_seconds': 5,
                    'max_download_time_seconds': 1800,  # 30 phút
                    'enable_timeout_detection': True,
                    'enable_auto_retry': True,
                    'enable_skip_slow_videos': True,
                    'chunk_size': 8192
                }
                self.log('debug', f"Sử dụng timeout settings mặc định: {timeout_settings}", function_name)
            
            self.log('info', f"Bắt đầu tải video với timeout settings: enable_timeout_detection={timeout_settings.get('enable_timeout_detection')}, enable_auto_retry={timeout_settings.get('enable_auto_retry')}, enable_skip_slow_videos={timeout_settings.get('enable_skip_slow_videos')}", function_name)
            
            # Tải video với retry logic và timeout detection
            download_result = self.download_video(video_url, file_path, timeout_settings)
            
            # Cập nhật result với thông tin từ download_result
            result['success'] = download_result.get('success', False)
            result['retry_count'] = download_result.get('retry_count', 0)
            result['timeout_detected'] = download_result.get('timeout_detected', False)
            result['skipped'] = download_result.get('skipped', False)
            result['download_time'] = download_result.get('download_time', 0)
            result['file_size'] = download_result.get('file_size', 0)
            
            if not download_result.get('success', False):
                error_msg = download_result.get('error', 'Unknown error')
                result['error'] = error_msg
                
                # Log chi tiết về lỗi (theo System Instruction 4.3 - ERROR cho chi tiết lỗi)
                if download_result.get('timeout_detected'):
                    self.log('warning', f"Video bị timeout sau {download_result.get('retry_count', 0)} lần retry", function_name)
                elif download_result.get('skipped'):
                    self.log('warning', f"Video bị skip do quá lâu (> {timeout_settings.get('max_download_time_seconds', 1800)}s)", function_name)
                else:
                    self.log('error', f"Video tải thất bại: {error_msg}", function_name)
                
                # Nếu bị skip hoặc timeout, không cần kiểm tra orientation filter
                if download_result.get('skipped') or download_result.get('timeout_detected'):
                    self.log('info', "Process video hoàn thành - bị skip hoặc timeout", function_name)
                    return result
            
            # Bước 6: Kiểm tra orientation filter (nếu cần) - CHUYỂN SAU KHI TẢI XONG
            if download_result.get('success', False):
                # 直接ビデオURLの場合、ダウンロード後にメタデータから向きを判定する
                if needs_orientation_check_after_download:
                    actual_orientation = self._get_video_orientation_from_file(file_path)
                    self.log('info', f"Video {file_path} - actual_orientation={actual_orientation}, filter={orientation_filter}", function_name)
                    if actual_orientation != 'unknown' and actual_orientation != orientation_filter:
                        # フィルタに一致しない場合は削除 (cải thiện logging)
                        filter_name_map = {
                            "horizontal": "Landscape (ngang)",
                            "vertical": "Portrait (dọc)",
                            "all": "Tất cả"
                        }
                        filter_display_name = filter_name_map.get(orientation_filter, orientation_filter)
                        orientation_display_map = {
                            "horizontal": "Landscape (ngang)",
                            "vertical": "Portrait (dọc)",
                            "square": "Square (vuông)",
                            "unknown": "Unknown"
                        }
                        actual_orientation_display = orientation_display_map.get(actual_orientation, actual_orientation)
                        
                        try:
                            os.remove(file_path)
                            self.log('info', f"Đã xóa video {os.path.basename(file_path)} vì orientation không khớp với filter", function_name)
                            self.log('debug', f"  - Video orientation: {actual_orientation} ({actual_orientation_display})", function_name)
                            self.log('debug', f"  - Filter yêu cầu: {orientation_filter} ({filter_display_name})", function_name)
                            self.log('debug', f"  - Video ID: {result.get('video_id', 'N/A')}", function_name)
                            self.log('debug', f"  - Author: {result.get('author', 'N/A')}", function_name)
                        except Exception as e:
                            self.log('error', f"Không thể xóa file: {e}", function_name, exc_info=True)
                        result['error'] = f"Video orientation ({actual_orientation} - {actual_orientation_display}) không khớp với filter ({orientation_filter} - {filter_display_name})"
                        result['filtered_by_orientation'] = True  # Đánh dấu là bị filter
                        result['success'] = False
                        result['orientation'] = actual_orientation  # Cập nhật orientation
                        self.log('info', "Process video hoàn thành - bị filter bởi orientation (sau khi tải)", function_name)
                        return result
                    elif actual_orientation != 'unknown':
                        # フィルタに一致する場合は、orientationを更新 (cải thiện logging)
                        orientation = actual_orientation
                        result['orientation'] = actual_orientation  # Cập nhật orientation
                        orientation_display_map = {
                            "horizontal": "Landscape (ngang)",
                            "vertical": "Portrait (dọc)",
                            "square": "Square (vuông)",
                            "unknown": "Unknown"
                        }
                        orientation_display = orientation_display_map.get(orientation, orientation)
                        self.log('debug', f"Video {os.path.basename(file_path)} có orientation: {orientation} ({orientation_display}) - phù hợp với filter ({orientation_filter})", function_name)
                    else:
                        self.log('warning', f"Không thể xác định orientation từ file {os.path.basename(file_path)}, giữ lại file", function_name)
                
                # result['success'] đã được cập nhật từ download_result
                result['file_path'] = file_path
            
        except Exception as e:
            # Log lỗi đầy đủ theo System Instruction 5 - exc_info=True
            self.log('error', f"Exception trong process_video: {e}", function_name, exc_info=True)
            result['error'] = f"Lỗi: {str(e)}"
            self.log('info', "Process video hoàn thành - Exception", function_name)
        
        # Log kết quả cuối cùng (theo System Instruction 4.4 - log bắt đầu & kết thúc)
        if result.get('success'):
            self.log('info', "Process video hoàn thành thành công", function_name)
            self.log('debug', f"  - Video ID: {result.get('video_id', 'N/A')}", function_name)
            # Đảm bảo file_path là絶対パスで表示 (theo System Instruction 8)
            file_path_log = result.get('file_path', 'N/A')
            if file_path_log != 'N/A':
                file_path_log = os.path.abspath(file_path_log)
            self.log('info', f"  - File path: {file_path_log}", function_name)
            self.log('debug', f"  - Author: {result.get('author', 'N/A')}", function_name)
            # Log thống kê timeout và retry (theo System Instruction 4.3 - DEBUG cho output)
            if result.get('retry_count', 0) > 0:
                self.log('debug', f"  - Retry count: {result.get('retry_count', 0)}", function_name)
            if result.get('download_time', 0) > 0:
                self.log('debug', f"  - Download time: {result.get('download_time', 0):.2f}s ({result.get('download_time', 0)/60:.2f} phút)", function_name)
            if result.get('file_size', 0) > 0:
                self.log('debug', f"  - File size: {result.get('file_size', 0)} bytes ({result.get('file_size', 0)/1024/1024:.2f} MB)", function_name)
        else:
            self.log('warning', "Process video hoàn thành - thất bại", function_name)
            self.log('error', f"  - Error: {result.get('error', 'Unknown error')}", function_name)
            # Log thống kê timeout và retry (theo System Instruction 4.3 - WARNING cho cảnh báo)
            if result.get('retry_count', 0) > 0:
                self.log('warning', f"  - Retry count: {result.get('retry_count', 0)}", function_name)
            if result.get('timeout_detected'):
                self.log('warning', f"  - Timeout detected: True", function_name)
            if result.get('skipped'):
                self.log('warning', f"  - Skipped: True (video quá lâu)", function_name)
        
        self.log('info', "=" * 60, function_name)
        return result


