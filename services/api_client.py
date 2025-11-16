"""
API Client Module
Chuẩn hóa gọi HTTP với timeout, retry, headers và logging theo System Instruction PRO.
"""

import logging
from typing import Any, Dict, Optional, Union

import requests
from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.log_helper import write_log, get_logger


class ApiClient:
	"""
	API Client chuẩn hóa cho HTTP requests.
	
	Mục tiêu:
	- Thống nhất timeout/retry
	- Gắn cookie và headers
	- Ghi log theo chuẩn: [timestamp] [LEVEL] [Function] Message
	
	Sử dụng:
		client = ApiClient(cookie="xxx", logger=get_logger('Api'))
		resp = client.get("https://example.com/api", params={"q": "test"})
		if resp and resp.ok:
			data = resp.json()
	"""
	
	def __init__(
		self,
		cookie: Optional[str] = None,
		timeout_seconds: float = 30.0,
		max_retries: int = 3,
		backoff_factor: float = 0.5,
		logger: Optional[logging.Logger] = None,
	):
		self.logger = logger or get_logger('ApiClient')
		self.cookie = self._normalize_cookie(cookie or "")
		self.timeout_seconds = timeout_seconds
		self.session = self._build_session(max_retries, backoff_factor)
		
		# Thiết lập headers mặc định
		self.session.headers.update({
			"User-Agent": (
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
				"AppleWebKit/537.36 (KHTML, like Gecko) "
				"Chrome/120.0.0.0 Safari/537.36"
			),
			# Ưu tiên JSON; vẫn cho phép text/plain hoặc fallback
			"Accept": "application/json, text/plain, */*",
			# Tăng khả năng tương thích với web CN (Douyin)
			"Accept-Language": "zh-CN,zh;q=0.9,en-US,en;q=0.8"
		})
		if self.cookie:
			self.session.headers.update({"Cookie": self.cookie})
			try:
				write_log('DEBUG', "ApiClient.__init__", f"Cookie set (length={len(self.cookie)})", self.logger)
			except Exception:
				pass
	
	def _build_session(self, max_retries: int, backoff_factor: float) -> Session:
		"""
		Tạo Session với Retry (idempotent methods) và pool adapter.
		"""
		function_name = "ApiClient._build_session"
		try:
			session = requests.Session()
			
			retry = Retry(
				total=max_retries,
				read=max_retries,
				connect=max_retries,
				backoff_factor=backoff_factor,
				status_forcelist=(429, 500, 502, 503, 504),
				allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
				respect_retry_after_header=True,
			)
			
			adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=50)
			session.mount("http://", adapter)
			session.mount("https://", adapter)
			
			return session
		except Exception as e:
			write_log('ERROR', function_name, f"Lỗi khi tạo session: {e}", self.logger, exc_info=True)
			return requests.Session()
	
	def set_cookie(self, cookie: str):
		"""Cập nhật Cookie header an toàn."""
		self.cookie = self._normalize_cookie(cookie or "")
		if self.cookie:
			self.session.headers.update({"Cookie": self.cookie})
		else:
			self.session.headers.pop("Cookie", None)
		try:
			write_log('DEBUG', "ApiClient.set_cookie", f"Cookie updated (length={len(self.cookie)})", self.logger)
		except Exception:
			pass

	def _normalize_cookie(self, cookie: str) -> str:
		"""
		Chuẩn hóa cookie lấy ở dạng 'Header String'.
		- Loại bỏ tiền tố 'Cookie:' hoặc 'cookie:' nếu có.
		- Trim khoảng trắng dư.
		- Loại bỏ xuống dòng.
		"""
		try:
			c = cookie.strip()
			# Remove optional "Cookie:" prefix
			if c.lower().startswith("cookie:"):
				c = c[len("cookie:"):].strip()
			# Collapse newlines/tabs
			c = " ".join(c.split())
			return c
		except Exception:
			return cookie
	
	def _request(
		self,
		method: str,
		url: str,
		*,
		params: Optional[Dict[str, Any]] = None,
		data: Optional[Union[Dict[str, Any], str]] = None,
		json: Optional[Dict[str, Any]] = None,
		headers: Optional[Dict[str, str]] = None,
		timeout: Optional[float] = None,
		stream: bool = False,
	) -> Optional[Response]:
		"""
		Thực thi HTTP request với logging/timeout.
		"""
		function_name = f"ApiClient.{method.upper()}"
		try:
			req_headers = {}
			if headers:
				req_headers.update(headers)
			
			write_log('INFO', function_name, f"API Call: {method.upper()} {url[:120]}...", self.logger)
			if self.logger.isEnabledFor(logging.DEBUG):
				write_log('DEBUG', function_name, f"Params: {params}", self.logger)
				if data:
					write_log('DEBUG', function_name, f"Data length: {len(str(data))}", self.logger)
				if json:
					write_log('DEBUG', function_name, f"JSON keys: {list(json.keys())}", self.logger)
			
			resp = self.session.request(
				method=method.upper(),
				url=url,
				params=params,
				data=data,
				json=json,
				headers=req_headers or None,
				timeout=timeout or self.timeout_seconds,
				stream=stream,
			)
			
			write_log('INFO', function_name, f"Status: {resp.status_code}", self.logger)
			if not resp.ok:
				write_log('WARNING', function_name, f"Response not OK, reason: {resp.reason}", self.logger)
			
			return resp
		
		except requests.Timeout as e:
			write_log('ERROR', function_name, f"Timeout: {e}", self.logger, exc_info=True)
			return None
		except requests.RequestException as e:
			write_log('ERROR', function_name, f"RequestException: {e}", self.logger, exc_info=True)
			return None
		except Exception as e:
			write_log('ERROR', function_name, f"Unexpected error: {e}", self.logger, exc_info=True)
			return None
	
	def get(self, url: str, **kwargs) -> Optional[Response]:
		return self._request("GET", url, **kwargs)
	
	def head(self, url: str, **kwargs) -> Optional[Response]:
		return self._request("HEAD", url, **kwargs)
	
	def options(self, url: str, **kwargs) -> Optional[Response]:
		return self._request("OPTIONS", url, **kwargs)
	
	def post(self, url: str, **kwargs) -> Optional[Response]:
		# Lưu ý: POST có thể không idempotent – retry đã hạn chế ở allowed_methods
		return self._request("POST", url, **kwargs)


