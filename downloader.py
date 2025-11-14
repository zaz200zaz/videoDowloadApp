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


class VideoDownloader:
    """Xử lý tải video Douyin"""
    
    def __init__(self, cookie: str):
        """
        Khởi tạo VideoDownloader
        
        Args:
            cookie: Cookie string để xác thực
        """
        self.cookie = cookie
        self.session = requests.Session()
        self._setup_session()
    
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
            print(f"Cookie đã được set (length: {len(clean_cookie)})")
        else:
            print("WARNING: Cookie rỗng!")
    
    def normalize_url(self, url: str) -> Optional[str]:
        """
        Chuẩn hóa URL video Douyin
        
        Args:
            url: URL gốc từ người dùng
            
        Returns:
            URL đã được chuẩn hóa hoặc None nếu không hợp lệ
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        
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
            url: URL video
            
        Returns:
            Dict chứa thông tin video hoặc None nếu lỗi
        """
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                print(f"Không thể trích xuất video ID từ URL: {url}")
                return None
            
            # Thử nhiều API endpoint khác nhau
            api_endpoints = [
                f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}",
                f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}&aid=1128&version_name=23.5.0&device_platform=web&device_id=0",
            ]
            
            data = None
            
            # Thử các API endpoint
            for api_url in api_endpoints:
                print(f"Đang gọi API: {api_url}")
                print(f"Cookie length: {len(self.cookie)} characters")
                
                try:
                    response = self.session.get(api_url, timeout=15)
                    
                    print(f"Response status: {response.status_code}")
                    content_length = response.headers.get('Content-Length', 'unknown')
                    print(f"Content-Length: {content_length}")
                    
                    if response.status_code == 200:
                        # Kiểm tra response có rỗng không
                        if len(response.text) == 0:
                            print(f"Response rỗng từ endpoint: {api_url}")
                            print("Có thể cookie không hợp lệ hoặc API đã thay đổi")
                            continue  # Thử endpoint tiếp theo
                        
                        # Thử parse JSON
                        try:
                            data = response.json()
                            print("Đã parse JSON thành công!")
                            break  # Thành công, thoát khỏi loop
                        except json.JSONDecodeError:
                            print(f"Response không phải JSON từ endpoint: {api_url}")
                            continue
                    else:
                        print(f"Status code không phải 200: {response.status_code}")
                        continue
                except Exception as e:
                    print(f"Lỗi khi gọi API {api_url}: {e}")
                    continue
            
            # Nếu tất cả API endpoint đều thất bại, thử lấy từ HTML page
            if data is None:
                print("Tất cả API endpoint đều thất bại, thử lấy từ HTML page...")
                return self._get_video_info_from_html(url, video_id)
            
            # Parse response để lấy link video
            if 'aweme_detail' in data:
                aweme = data['aweme_detail']
                video_info = {
                    'video_id': video_id,
                    'title': aweme.get('desc', ''),
                    'author': aweme.get('author', {}).get('nickname', ''),
                    'video_url': None
                }
                
                # Tìm link video trong response
                video_data = aweme.get('video', {})
                if video_data:
                    play_addr = video_data.get('play_addr', {})
                    if play_addr:
                        url_list = play_addr.get('url_list', [])
                        if url_list:
                            video_info['video_url'] = url_list[0]
                            print(f"Đã tìm thấy video URL")
                        else:
                            print("Không tìm thấy url_list trong play_addr")
                    else:
                        print("Không tìm thấy play_addr trong video_data")
                else:
                    print("Không tìm thấy video trong aweme_detail")
                
                return video_info
            else:
                print(f"Response không chứa 'aweme_detail'. Keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
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
                # Tìm URL pattern với full URL
                direct_patterns = [
                    r'https://[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                    r'https://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                    r'https://[^"\'<>\s]*aweme[^"\'<>\s]*\.mp4[^"\'<>\s]*',
                    r'https://[^"\'<>\s]*douyin[^"\'<>\s]*\.mp4[^"\'<>\s]*',
                    r'https://[^"\'<>\s]*bytednsdoc[^"\'<>\s]*\.mp4[^"\'<>\s]*',
                    r'https://[^"\'<>\s]*\.mp4\?[^"\'<>\s]*',
                ]
                
                for pattern in direct_patterns:
                    matches = re.findall(pattern, html_content)
                    if matches:
                        # Lấy URL dài nhất（通常は完全なURL）
                        video_url = max(matches, key=len)
                        # Loại bỏ các ký tự không hợp lệ ở cuối
                        video_url = video_url.rstrip('.,;!?\\"\'<>')
                        if len(video_url) > 20:  # Đảm bảo là URL hợp lệ
                            break
                        else:
                            video_url = None
                
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
                ]
                
                for pattern in window_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    if matches:
                        try:
                            data = json.loads(matches[0])
                            video_url = self._extract_video_url_from_json(data)
                            if video_url and video_url.startswith('http') and len(video_url) > 20:
                                print(f"Tìm thấy video URL trong window data: {video_url[:150]}...")
                                return {
                                    'video_id': video_id,
                                    'title': '',
                                    'author': '',
                                    'video_url': video_url
                                }
                        except:
                            pass
            
            print("Không tìm thấy video URL trong HTML")
            return None
                
        except Exception as e:
            print(f"Lỗi khi lấy thông tin từ HTML: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_video_url_from_json(self, data: dict) -> Optional[str]:
        """Recursively tìm video URL trong JSON data"""
        if isinstance(data, dict):
            # Tìm các key có thể chứa video URL
            for key in ['playAddr', 'play_addr', 'url_list', 'video_url', 'url']:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and value.startswith('http'):
                        return value
                    elif isinstance(value, list) and len(value) > 0:
                        if isinstance(value[0], str) and value[0].startswith('http'):
                            return value[0]
                    elif isinstance(value, dict):
                        result = self._extract_video_url_from_json(value)
                        if result:
                            return result
            
            # Recursive search
            for value in data.values():
                result = self._extract_video_url_from_json(value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._extract_video_url_from_json(item)
                if result:
                    return result
        
        return None
    
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
            if naming_mode == "video_id":
                filename = f"{video_id}.mp4"
            else:
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


