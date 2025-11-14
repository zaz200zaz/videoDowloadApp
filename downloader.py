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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.douyin.com/",
            "Cookie": self.cookie
        }
        self.session.headers.update(headers)
    
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
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # Nếu không tìm thấy, thử parse từ query string
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'video_id' in params:
                return params['video_id'][0]
            if 'item_id' in params:
                return params['item_id'][0]
            
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
                return None
            
            # API endpoint để lấy thông tin video
            # Lưu ý: API này có thể thay đổi, cần cập nhật theo thời gian
            api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}"
            
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response để lấy link video
                # Cấu trúc response có thể thay đổi
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
                    
                    return video_info
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy thông tin video: {e}")
            return None
        except Exception as e:
            print(f"Lỗi không xác định: {e}")
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
            # Bước 1: Chuẩn hóa URL
            normalized_url = self.normalize_url(url)
            if not normalized_url:
                result['error'] = "URL không hợp lệ"
                return result
            
            # Bước 2: Lấy thông tin video
            video_info = self.get_video_info(normalized_url)
            if not video_info:
                result['error'] = "Không thể lấy thông tin video"
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


