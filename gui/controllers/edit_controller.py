"""
Edit Controller
Kết nối GUI với EditService (batch video editor)
"""

from typing import Dict, Optional, Callable
from utils.log_helper import get_logger, write_log
from services.edit_service import EditService


class EditController:
	"""
	Điều phối giữa GUI và EditService.
	"""
	
	def __init__(self):
		self.logger = get_logger("EditController")
		self._service: Optional[EditService] = None
	
	def start_batch(
		self,
		background_path: str,
		input_folder: str,
		output_folder: str,
		config: Dict,
		threads: int,
		progress_cb: Optional[Callable[[float, int, int, str], None]] = None,
		result_cb: Optional[Callable[[Dict], None]] = None,
		complete_cb: Optional[Callable[[], None]] = None,
	) -> bool:
		"""
		Khởi chạy batch edit.
		
		Returns:
			bool: True nếu khởi chạy được, False nếu lỗi
		"""
		function = "EditController.start_batch"
		try:
			write_log("INFO", function, "Bắt đầu", self.logger)
			
			if not background_path:
				write_log("ERROR", function, "Thiếu background_path", self.logger)
				return False
			
			if not input_folder:
				write_log("ERROR", function, "Thiếu input_folder", self.logger)
				return False
			
			if not output_folder:
				write_log("ERROR", function, "Thiếu output_folder", self.logger)
				return False
			
			self._service = EditService(
				background_path=background_path,
				input_folder=input_folder,
				output_folder=output_folder,
				config=config,
				threads=threads,
				progress_cb=progress_cb,
				result_cb=result_cb,
				complete_cb=complete_cb
			)
			
			# Chạy trong thread riêng (để không block UI) - do EditService.run tự dùng ThreadPoolExecutor bên trong,
			# ở đây chỉ cần gọi trong 1 thread nền đơn giản.
			import threading
			t = threading.Thread(target=self._service.run, daemon=True)
			t.start()
			
			write_log("INFO", function, "Đã khởi chạy batch", self.logger)
			return True
		except Exception as e:
			write_log("ERROR", function, f"Lỗi khi start batch: {e}", self.logger, exc_info=True)
			return False
	
	def stop_batch(self):
		"""Yêu cầu dừng batch (không hủy job đang chạy)."""
		function = "EditController.stop_batch"
		try:
			if self._service:
				self._service.stop()
				write_log("INFO", function, "Đã gửi tín hiệu dừng", self.logger)
		except Exception as e:
			write_log("ERROR", function, f"Lỗi khi stop batch: {e}", self.logger, exc_info=True)


