"""
Video Downloader Module
Xử lý việc tải video từ Douyin
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
                # Sử dụng __file__ để lấy thư mục của script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                log_dir = os.path.join(script_dir, "logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = os.path.join(log_dir, f"douyin_downloader_{timestamp}.log")
            
            # Đảm bảo thư mục tồn tại
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
            
            # Tạo logger
            self.logger = logging.getLogger('VideoDownloader')
            self.logger.setLevel(logging.DEBUG)
            
            # Xóa các handler cũ
            self.logger.handlers = []
            
            # File handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
            
            self.log_file_path = log_file
            self.logger.info(f"Logging initialized. Log file: {log_file}")
            print(f"[LOG] Log file created: {log_file}")
        except Exception as e:
            # Nếu không thể tạo log file, vẫn tiếp tục nhưng không có logging
            print(f"[WARNING] Không thể tạo log file: {e}")
            # Tạo logger mặc định (chỉ console)
            self.logger = logging.getLogger('VideoDownloader')
            self.logger.setLevel(logging.INFO)
            self.logger.handlers = []
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)
            self.log_file_path = None
    
    def log(self, level: str, message: str):
        """
        Ghi log với level cụ thể
        
        Args:
            level: 'debug', 'info', 'warning', 'error', 'critical'
            message: Nội dung log
        """
        if level.lower() == 'debug':
            self.logger.debug(message)
        elif level.lower() == 'info':
            self.logger.info(message)
        elif level.lower() == 'warning':
            self.logger.warning(message)
        elif level.lower() == 'error':
            self.logger.error(message)
        elif level.lower() == 'critical':
            self.logger.critical(message)
        else:
            self.logger.info(message)
    
    def _setup_session(self):
        """Thiết lập session với headers và cookie"""
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
        if len(clean_cookie) > 0:
            self.log('info', f"Cookie đã được set (length: {len(clean_cookie)})")
            print(f"Cookie đã được set (length: {len(clean_cookie)})")
        else:
            self.log('warning', "WARNING: Cookie rỗng!")
            print("WARNING: Cookie rỗng!")
    
    def normalize_url(self, url: str) -> Optional[str]:
        """
        Chuẩn hóa URL video Douyin
        
        Args:
            url: URL gốc từ người dùng (có thể là video page URL hoặc direct video URL)
            
        Returns:
            URL đã được chuẩn hóa hoặc None nếu không hợp lệ
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        
        # Kiểm tra xem có phải direct video URL không
        is_direct_video = (url.endswith('.mp4') or '.mp4?' in url or 
                          'zjcdn.com' in url.lower() or 
                          'douyinstatic.com' in url.lower() or
                          ('/video/' in url.lower() and 'douyin.com' not in url.lower()))
        
        # Nếu là direct video URL, trả về trực tiếp (không cần normalize)
        if is_direct_video:
            self.log('info', f"Phát hiện direct video URL, bỏ qua normalize: {url[:100]}...")
            return url
        
        # Kiểm tra xem có phải link Douyin không
        if "douyin.com" not in url and "iesdouyin.com" not in url:
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
                print(f"Đã resolve short URL thành: {url}")
            except Exception as e:
                print(f"Lỗi khi resolve short URL: {e}")
                # Nếu không resolve được, trả về URL gốc và thử extract ID trực tiếp
                pass
        
        # Loại bỏ các param thừa, chỉ giữ lại link cơ bản
        try:
            parsed = urlparse(url)
            # Giữ lại scheme, netloc, path
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return normalized
        except Exception:
            return url
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Trích xuất video ID từ URL
        
        Args:
            url: URL video
            
        Returns:
            Video ID hoặc None
        """
        try:
            # Pattern cho video ID trong URL Douyin
            patterns = [
                r'/video/(\d+)',
                r'video_id=(\d+)',
                r'item_id=(\d+)',
                r'aweme_id=(\d+)',
                r'modal_id=(\d+)',  # Một số URL format khác
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    print(f"Đã tìm thấy video ID: {video_id}")
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
                # Pattern: v.douyin.com/xxxxx hoặc iesdouyin.com/xxxxx
                short_pattern = r'/([A-Za-z0-9]+)/?$'
                match = re.search(short_pattern, parsed.path)
                if match:
                    short_id = match.group(1)
                    print(f"Tìm thấy short ID: {short_id}, cần resolve URL để lấy video ID thực")
                    # Short ID này không phải video ID, cần resolve URL trước
                    # Nhưng nếu normalize_url đã resolve rồi thì sẽ có video ID ở đây
                    return None
            
            print(f"Không tìm thấy video ID trong URL: {url}")
            return None
        except Exception as e:
            print(f"Lỗi khi trích xuất video ID: {e}")
            return None
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Lấy thông tin video từ Douyin API
        
        Args:
            url: URL video (có thể là video page URL hoặc direct video URL)
            
        Returns:
            Dict chứa thông tin video hoặc None nếu lỗi
        """
        try:
            # Kiểm tra xem có phải direct video URL không
            is_direct_video = (url.endswith('.mp4') or '.mp4?' in url or 
                              'zjcdn.com' in url.lower() or 
                              'douyinstatic.com' in url.lower() or
                              ('/video/' in url.lower() and 'douyin.com' not in url.lower()))
            
            if is_direct_video:
                # Đây là direct video URL, trả về trực tiếp
                self.log('info', f"Phát hiện direct video URL: {url[:100]}...")
                self.log('warning', "Direct video URL có thể hết hạn, nhưng vẫn thử tải")
                return {
                    'video_id': None,
                    'title': 'Direct Video',
                    'author': 'Unknown',
                    'video_url': url
                }
            
            video_id = self.extract_video_id(url)
            if not video_id:
                self.log('error', f"Không thể trích xuất video ID từ URL: {url}")
                print(f"Không thể trích xuất video ID từ URL: {url}")
                return None
            
            # Thử TikVideo.App API trước (nếu có)
            print("Thử sử dụng TikVideo.App API...")
            tikvideo_result = self._get_video_info_from_tikvideo(url)
            if tikvideo_result:
                print("Đã lấy được thông tin video từ TikVideo.App API!")
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
                self.log('info', f"Đang gọi API: {api_url}")
                self.log('debug', f"Cookie length: {len(self.cookie)} characters")
                print(f"Đang gọi API: {api_url}")
                print(f"Cookie length: {len(self.cookie)} characters")
                
                try:
                    response = self.session.get(api_url, timeout=15)
                    
                    self.log('debug', f"Response status: {response.status_code}")
                    content_length = response.headers.get('Content-Length', 'unknown')
                    self.log('debug', f"Content-Length: {content_length}")
                    print(f"Response status: {response.status_code}")
                    print(f"Content-Length: {content_length}")
                    
                    if response.status_code == 200:
                        # Kiểm tra response có rỗng không
                        if len(response.text) == 0:
                            self.log('warning', f"Response rỗng từ endpoint: {api_url}")
                            self.log('warning', "Có thể cookie không hợp lệ hoặc API đã thay đổi")
                            print(f"Response rỗng từ endpoint: {api_url}")
                            print("Có thể cookie không hợp lệ hoặc API đã thay đổi")
                            continue  # Thử endpoint tiếp theo
                        
                        # Thử parse JSON
                        try:
                            data = response.json()
                            self.log('info', "Đã parse JSON thành công!")
                            print("Đã parse JSON thành công!")
                            break  # Thành công, thoát khỏi loop
                        except json.JSONDecodeError:
                            self.log('warning', f"Response không phải JSON từ endpoint: {api_url}")
                            print(f"Response không phải JSON từ endpoint: {api_url}")
                            continue
                    else:
                        self.log('warning', f"Status code không phải 200: {response.status_code}")
                        print(f"Status code không phải 200: {response.status_code}")
                        continue
                except Exception as e:
                    self.log('error', f"Lỗi khi gọi API {api_url}: {e}")
                    print(f"Lỗi khi gọi API {api_url}: {e}")
                    continue
            
            # Nếu tất cả API endpoint đều thất bại, thử lấy từ HTML page
            if data is None:
                self.log('warning', "Tất cả API endpoint đều thất bại, thử lấy từ HTML page...")
                print("Tất cả API endpoint đều thất bại, thử lấy từ HTML page...")
                return self._get_video_info_from_html(url, video_id)
            
            # Parse response để lấy link video（JavaScriptコードの方法を参考）
            if 'aweme_detail' in data:
                aweme = data['aweme_detail']
                video_info = {
                    'video_id': video_id,
                    'title': aweme.get('desc', ''),
                    'author': aweme.get('author', {}).get('nickname', ''),
                    'video_url': None
                }
                
                # JavaScriptコードの方法: video.video.play_addr.url_list[0] または video.video.download_addr.url_list[0]
                video_data = aweme.get('video', {})
                if video_data:
                    # まず play_addr を試す
                    play_addr = video_data.get('play_addr', {})
                    if play_addr:
                        url_list = play_addr.get('url_list', [])
                        if url_list and len(url_list) > 0:
                            video_url = url_list[0]
                            # HTTPをHTTPSに変換（JavaScriptコードの方法）
                            if not video_url.startswith("https"):
                                video_url = video_url.replace("http", "https")
                            video_info['video_url'] = video_url
                            print(f"Đã tìm thấy video URL từ play_addr")
                            return video_info
                    
                    # play_addrがない場合、download_addrを試す
                    download_addr = video_data.get('download_addr', {})
                    if download_addr:
                        url_list = download_addr.get('url_list', [])
                        if url_list and len(url_list) > 0:
                            video_url = url_list[0]
                            if not video_url.startswith("https"):
                                video_url = video_url.replace("http", "https")
                            video_info['video_url'] = video_url
                            print(f"Đã tìm thấy video URL từ download_addr")
                            return video_info
                    
                    print("Không tìm thấy play_addr hoặc download_addr trong video_data")
                else:
                    print("Không tìm thấy video trong aweme_detail")
                
                return video_info
            elif 'aweme_list' in data:
                # リスト形式のレスポンス（複数ビデオの場合）
                aweme_list = data['aweme_list']
                if aweme_list and len(aweme_list) > 0:
                    # 最初のビデオを取得
                    aweme = aweme_list[0]
                    video_info = {
                        'video_id': video_id,
                        'title': aweme.get('desc', ''),
                        'author': aweme.get('author', {}).get('nickname', ''),
                        'video_url': None
                    }
                    
                    video_data = aweme.get('video', {})
                    if video_data:
                        play_addr = video_data.get('play_addr', {})
                        if play_addr:
                            url_list = play_addr.get('url_list', [])
                            if url_list and len(url_list) > 0:
                                video_url = url_list[0]
                                if not video_url.startswith("https"):
                                    video_url = video_url.replace("http", "https")
                                video_info['video_url'] = video_url
                                print(f"Đã tìm thấy video URL từ aweme_list")
                                return video_info
                
                return None
            else:
                print(f"Response không chứa 'aweme_detail' hoặc 'aweme_list'. Keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
                # Thử lấy từ HTML
                return self._get_video_info_from_html(url, video_id)
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy thông tin video: {e}")
            return None
        except Exception as e:
            print(f"Lỗi không xác định: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_video_info_from_html(self, url: str, video_id: str) -> Optional[Dict]:
        """
        Lấy thông tin video từ HTML page (fallback method)
        
        Args:
            url: URL video
            video_id: Video ID đã biết
            
        Returns:
            Dict chứa thông tin video hoặc None
        """
        try:
            print(f"Đang lấy HTML từ: {url}")
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"Không thể lấy HTML. Status: {response.status_code}")
                return None
            
            html_content = response.text
            print(f"HTML length: {len(html_content)}")
            
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
            
            # Tìm trong script tags
            script_pattern = r'<script[^>]*>(.*?)</script>'
            scripts = re.findall(script_pattern, html_content, re.DOTALL)
            
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
                print("Đang tìm kiếm trong RENDER_DATA và window data...")
                render_data_patterns = [
                    r'<script[^>]*id="RENDER_DATA"[^>]*>(.+?)</script>',
                    r'window\._UNIVERSAL_DATA\s*=\s*({.+?});',
                    r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?});',
                    r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                ]
                
                for pattern in render_data_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    if matches:
                        print(f"Tìm thấy {len(matches)} match với pattern: {pattern[:50]}...")
                        for i, match in enumerate(matches):
                            print(f"Đang xử lý match {i+1}/{len(matches)}, length: {len(match)}")
                            
                            # RENDER_DATAは通常URLエンコードされている
                            try:
                                # Thử decode URL encoded JSON
                                decoded = urllib.parse.unquote(match)
                                print(f"Đã decode, length sau decode: {len(decoded)}")
                                
                                # JSONをパース
                                data = json.loads(decoded)
                                print(f"Đã parse JSON thành công! Type: {type(data)}")
                                
                                # ビデオURLを抽出
                                found_url = self._extract_video_url_from_json(data, video_id)
                                if found_url:
                                    video_url = found_url
                                    print(f"Tìm thấy video URL trong RENDER_DATA: {video_url[:150]}...")
                                    break
                                else:
                                    print("Không tìm thấy video URL trong JSON data")
                                    # Debug: JSON構造を確認
                                    if isinstance(data, dict):
                                        print(f"Top level keys: {list(data.keys())[:10]}")
                                        
                            except urllib.error.UnquoteError as e:
                                print(f"Lỗi khi decode URL: {e}")
                                try:
                                    # Thử parse trực tiếp（既にデコード済みの場合）
                                    data = json.loads(match)
                                    found_url = self._extract_video_url_from_json(data, video_id)
                                    if found_url:
                                        video_url = found_url
                                        print(f"Tìm thấy video URL trong data (không decode): {video_url[:150]}...")
                                        break
                                except json.JSONDecodeError as e2:
                                    print(f"Lỗi khi parse JSON (không decode): {str(e2)[:200]}")
                                    # 最初の100文字を表示してデバッグ
                                    print(f"Match preview: {match[:200]}...")
                            except json.JSONDecodeError as e:
                                print(f"Lỗi khi parse JSON: {str(e)[:200]}")
                                # デコード済みデータの最初の200文字を表示
                                try:
                                    decoded = urllib.parse.unquote(match)
                                    print(f"Decoded preview: {decoded[:200]}...")
                                except:
                                    print(f"Match preview: {match[:200]}...")
                            except Exception as e:
                                print(f"Lỗi không xác định khi xử lý RENDER_DATA: {type(e).__name__}: {str(e)[:200]}")
                                import traceback
                                traceback.print_exc()
                    
                    if video_url:
                        break
                
                # Nếu vẫn không tìm thấy trong RENDER_DATA, thử tìm trong toàn bộ HTML với pattern khác
                if not video_url:
                    print("Đang tìm kiếm trong toàn bộ HTML với pattern khác...")
                    # Tìm trong script tags với JSON data
                    script_pattern = r'<script[^>]*>(.*?)</script>'
                    scripts = re.findall(script_pattern, html_content, re.DOTALL)
                    print(f"Tìm thấy {len(scripts)} script tags")
                    
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
                                        print(f"Tìm thấy video URL trong script tag {i}: {video_url[:150]}...")
                                        break
                                except:
                                    pass
                            
                            if video_url:
                                break
                        
                        if video_url:
                            break
                
                # Nếu vẫn chưa tìm thấy, thử tìm tất cả URL pattern（最後の手段）
                if not video_url:
                    print("Đang tìm kiếm tất cả URL trong HTML (最後の手段)...")
                    all_urls = []
                    direct_patterns = [
                        r'https://[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                        r'https://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                    ]
                    
                    for pattern in direct_patterns:
                        matches = re.findall(pattern, html_content)
                        all_urls.extend(matches)
                    
                    print(f"Tìm thấy {len(all_urls)} URL trong HTML")
                    
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
                        print(f"Tìm thấy {len(valid_urls)} URL hợp lệ, chọn: {video_url[:150]}...")
                    else:
                        print("Không tìm thấy URL hợp lệ trong HTML (tất cả đều bị loại trừ)")
                        print("WARNING: Không thể tìm thấy video URL hợp lệ từ HTML!")
                        print("Có thể cần cookie mới hoặc video không khả dụng.")
                        # Debug: hiển thị một số URL để kiểm tra
                        if all_urls:
                            print(f"Tất cả URL tìm thấy (để debug):")
                            for i, url in enumerate(all_urls[:5]):  # Chỉ hiển thị 5 URL đầu
                                print(f"  {i+1}. {url[:100]}...")
                
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
                    print(f"URL không hợp lệ (không bắt đầu bằng http): {video_url[:100]}")
                    video_url = None
                elif len(video_url) < 20:
                    print(f"URL quá ngắn: {video_url}")
                    video_url = None
                
                if video_url:
                    print(f"Tìm thấy video URL trong HTML: {video_url[:150]}...")
                    print(f"Video URL length: {len(video_url)}")
                    
                    return {
                        'video_id': video_id,
                        'title': '',
                        'author': '',
                        'video_url': video_url
                    }
            
            # Nếu vẫn không tìm thấy, thử tìm trong window._UNIVERSAL_DATA hoặc tương tự
            if not video_url:
                print("Đang tìm kiếm trong window data...")
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
                                    print(f"Tìm thấy video URL trong window data: {video_url[:150]}...")
                                    return {
                                        'video_id': video_id,
                                        'title': '',
                                        'author': '',
                                        'video_url': video_url
                                    }
                            except Exception as e:
                                try:
                                    # Thử parse trực tiếp
                                    data = json.loads(match)
                                    video_url = self._extract_video_url_from_json(data, video_id)
                                    if video_url:
                                        print(f"Tìm thấy video URL trong window data: {video_url[:150]}...")
                                        return {
                                            'video_id': video_id,
                                            'title': '',
                                            'author': '',
                                            'video_url': video_url
                                        }
                                except Exception as e2:
                                    pass
            
            print("Không tìm thấy video URL trong HTML")
            return None
                
        except Exception as e:
            print(f"Lỗi khi lấy thông tin từ HTML: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_video_url_from_json(self, data: dict, video_id: str = None, depth: int = 0, max_depth: int = 10) -> Optional[str]:
        """Recursively tìm video URL trong JSON data"""
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
                        print(f"Tìm thấy video URL trong key '{key}' (depth {depth})")
                        return value
                    elif isinstance(value, list) and len(value) > 0:
                        for item in value:
                            if isinstance(item, str) and is_valid_video_url(item):
                                print(f"Tìm thấy video URL trong key '{key}' list (depth {depth})")
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
                            print(f"Tìm thấy video URL trong '{video_key}' (depth {depth})")
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
                        print(f"Tìm thấy video URL trong 'app' (depth {depth})")
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
                    print(f"Thử gọi TikVideo API: {api_url}")
                    
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
                            
                            print(f"TikVideo API response status: {response.status_code}")
                            
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                    print(f"TikVideo API response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
                                    
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
                                        print(f"Tìm thấy video URL từ TikVideo API: {video_url[:150]}...")
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
                                            print(f"Tìm thấy video URL từ TikVideo HTML: {video_url[:150]}...")
                                            return {
                                                'video_id': self.extract_video_id(url) or '',
                                                'title': '',
                                                'author': '',
                                                'video_url': video_url
                                            }
                                    
                        except Exception as e:
                            print(f"Lỗi khi gọi TikVideo API {api_url} với payload {payload}: {e}")
                            continue
                    
                except Exception as e:
                    print(f"Lỗi khi kết nối TikVideo API {api_url}: {e}")
                    continue
            
            print("Không thể lấy thông tin từ TikVideo.App API")
            return None
            
        except Exception as e:
            print(f"Lỗi khi gọi TikVideo API: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_videos_from_user(self, user_url: str) -> List[str]:
        """
        Lấy tất cả video URL từ user profile (giống như JavaScript code)
        
        Args:
            user_url: URL user profile (ví dụ: https://www.douyin.com/user/MS4wLjABAAAA...)
            
        Returns:
            List các video URL
        """
        video_urls = []
        
        try:
            # Extract sec_user_id từ URL
            import re
            match = re.search(r'/user/([^/?]+)', user_url)
            if not match:
                print(f"Không thể trích xuất user ID từ URL: {user_url}")
                return []
            
            sec_user_id = match.group(1)
            print(f"User ID: {sec_user_id}")
            
            has_more = 1
            max_cursor = 0
            error_count = 0
            
            while has_more == 1 and error_count < 5:
                try:
                    # API endpoint giống như JavaScript code
                    api_url = f"https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id={sec_user_id}&max_cursor={max_cursor}&count=20&version_code=170400&version_name=17.4.0"
                    
                    print(f"Đang lấy video (max_cursor={max_cursor}), đã tìm thấy {len(video_urls)} video...")
                    
                    response = self.session.get(api_url, timeout=15)
                    
                    if response.status_code != 200:
                        print(f"HTTP Error: {response.status_code}")
                        error_count += 1
                        import time
                        time.sleep(2)
                        continue
                    
                    data = response.json()
                    
                    if not data or 'aweme_list' not in data:
                        print("Không tìm thấy video data, thử lại...")
                        error_count += 1
                        import time
                        time.sleep(3)
                        continue
                    
                    error_count = 0
                    has_more = data.get('has_more', 0)
                    max_cursor = data.get('max_cursor', 0)
                    
                    # Extract video URLs
                    for video in data['aweme_list']:
                        # Lấy video ID để tạo video page URL (giống như JavaScript code)
                        aweme_id = video.get('aweme_id', '')
                        if aweme_id:
                            # Tạo video page URL thay vì direct video URL
                            # Vì direct video URL có thể hết hạn, nên dùng video page URL
                            video_page_url = f"https://www.douyin.com/video/{aweme_id}"
                            video_urls.append(video_page_url)
                            print(f"  Thêm video: {video_page_url}")
                        
                        # Nếu muốn lấy direct video URL (có thể hết hạn), uncomment phần dưới
                        # video_url = ""
                        # if video.get('video') and video['video'].get('play_addr'):
                        #     url_list = video['video']['play_addr'].get('url_list', [])
                        #     if url_list:
                        #         video_url = url_list[0]
                        # elif video.get('video') and video['video'].get('download_addr'):
                        #     url_list = video['video']['download_addr'].get('url_list', [])
                        #     if url_list:
                        #         video_url = url_list[0]
                        # 
                        # if video_url:
                        #     # HTTPをHTTPSに変換
                        #     if not video_url.startswith("https"):
                        #         video_url = video_url.replace("http", "https")
                        #     video_urls.append(video_url)
                    
                    print(f"Đã tìm thấy {len(video_urls)} video")
                    
                    # Delay giữa các request
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Lỗi khi lấy video: {e}")
                    error_count += 1
                    import time
                    time.sleep(3)
            
            print(f"Hoàn thành! Tổng cộng {len(video_urls)} video")
            return video_urls
            
        except Exception as e:
            print(f"Lỗi khi lấy video từ user: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def download_video(self, video_url: str, save_path: str) -> bool:
        """
        Tải video từ URL về máy
        
        Args:
            video_url: URL video thực tế
            save_path: Đường dẫn lưu file
            
        Returns:
            True nếu tải thành công, False nếu lỗi
        """
        try:
            response = self.session.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Tải file
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải video: {e}")
            return False
        except Exception as e:
            print(f"Lỗi không xác định khi tải: {e}")
            return False
    
    def process_video(self, url: str, download_folder: str, naming_mode: str = "video_id") -> Dict:
        """
        Xử lý một video từ URL đến file đã tải
        
        Args:
            url: URL video gốc
            download_folder: Thư mục lưu file
            naming_mode: Chế độ đặt tên ("video_id" hoặc "timestamp")
            
        Returns:
            Dict chứa kết quả: {
                'success': bool,
                'video_id': str,
                'file_path': str,
                'error': str
            }
        """
        result = {
            'success': False,
            'video_id': None,
            'file_path': None,
            'error': None,
            'url': url
        }
        
        try:
            # Bước 1: Chuẩn hóa URL (resolve short URL nếu cần)
            normalized_url = self.normalize_url(url)
            if not normalized_url:
                result['error'] = "URL không hợp lệ"
                return result
            
            print(f"URL sau khi normalize: {normalized_url}")
            
            # Bước 2: Lấy thông tin video
            video_info = self.get_video_info(normalized_url)
            if not video_info:
                # Nếu normalizeされたURLが短縮URLと異なる場合、既に解決済みなので
                # URL gốcに戻す必要はない（URL gốcは短縮URLなので）
                result['error'] = "Không thể lấy thông tin video. Có thể:\n1. Cookie không hợp lệ hoặc đã hết hạn\n2. Video không tồn tại hoặc bị chặn\n3. API Douyin đã thay đổi\n\nVui lòng kiểm tra lại cookie và thử lại."
                return result
            
            video_id = video_info.get('video_id')
            video_url = video_info.get('video_url')
            
            if not video_url:
                result['error'] = "Không tìm thấy link video"
                return result
            
            result['video_id'] = video_id
            
            # Bước 3: Tạo tên file
            if naming_mode == "video_id" and video_id:
                filename = f"{video_id}.mp4"
            else:
                # Nếu không có video_id hoặc naming_mode là timestamp, dùng timestamp
                timestamp = int(time.time())
                filename = f"video_{timestamp}.mp4"
            
            file_path = os.path.join(download_folder, filename)
            
            # Bước 4: Tải video
            if self.download_video(video_url, file_path):
                result['success'] = True
                result['file_path'] = file_path
            else:
                result['error'] = "Lỗi khi tải file"
            
        except Exception as e:
            result['error'] = f"Lỗi: {str(e)}"
        
        return result


