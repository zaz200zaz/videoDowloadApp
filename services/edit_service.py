"""
Edit Service
Quản lý xử lý hàng loạt video: scan, đa luồng, gọi VideoEditor, progress & logging.
"""

import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List, Optional
from utils.log_helper import get_logger, write_log
from services.video_editor import VideoEditor


class EditService:
	"""
	Quản lý batch edit video.
	
	Args:
		background_path: Đường dẫn ảnh nền
		input_folder: Thư mục nguồn chứa các .mp4
		output_folder: Thư mục output
		config: Cấu hình xử lý (position, size, keep_ratio, pad_color, bitrate, preset, skip_existing, output_suffix)
		threads: Số luồng xử lý song song
		progress_cb: callback(progress_float, current, total, message)
		result_cb: callback(result_dict)
		complete_cb: callback()
	"""
	
	def __init__(
		self,
		background_path: str,
		input_folder: str,
		output_folder: str,
		config: Dict,
		threads: int = 4,
		progress_cb: Optional[Callable[[float, int, int, str], None]] = None,
		result_cb: Optional[Callable[[Dict], None]] = None,
		complete_cb: Optional[Callable[[], None]] = None,
	):
		self.logger = get_logger("EditService")
		self.background_path = background_path
		self.input_folder = input_folder
		self.output_folder = output_folder
		self.config = config or {}
		self.threads = max(1, min(int(threads or 1), 8))
		self.progress_cb = progress_cb
		self.result_cb = result_cb
		self.complete_cb = complete_cb
		self._should_stop = False
	
	def stop(self):
		"""Yêu cầu dừng (không hủy job đang chạy, ngăn job mới)."""
		self._should_stop = True
	
	def _make_output_path(self, src_path: str) -> str:
		"""
		Tạo output path từ file nguồn, thêm hậu tố nếu cấu hình.
		"""
		suffix = self.config.get("output_suffix", "_edited") or ""
		base = os.path.splitext(os.path.basename(src_path))[0]
		filename = f"{base}{suffix}.mp4" if suffix else f"{base}.mp4"
		return os.path.join(self.output_folder, filename)
	
	def run(self) -> Dict:
		"""
		Chạy batch edit. Trả về thống kê tổng hợp.
		"""
		function = "EditService.run"
		try:
			# Giới hạn threads theo CPU để tránh quá tải
			try:
				cpu_cap = max(1, (os.cpu_count() or 2) - 1)
				orig = self.threads
				self.threads = max(1, min(self.threads, cpu_cap))
				if self.threads != orig:
					write_log("INFO", function, f"Điều chỉnh threads: yêu cầu={orig}, theo CPU={cpu_cap}, sử dụng={self.threads}", self.logger)
			except Exception:
				pass

			write_log("INFO", function, "Bắt đầu batch edit", self.logger)
			# Ghi cấu hình tổng quan để dễ debug
			try:
				write_log("DEBUG", function, f"Config: keep_ratio={self.config.get('keep_ratio', True)}, "
				         f"size={self.config.get('size')}, position={self.config.get('position')}, "
				         f"bitrate={self.config.get('bitrate')}, preset={self.config.get('preset')}, "
				         f"suffix={self.config.get('output_suffix', '_edited')}, "
				         f"skip_existing={self.config.get('skip_existing', True)}", self.logger)
				write_log("DEBUG", function, f"Paths: background={os.path.abspath(self.background_path)}, "
				         f"input={os.path.abspath(self.input_folder)}, output={os.path.abspath(self.output_folder)}", self.logger)
				write_log("DEBUG", function, f"Threads: {self.threads}", self.logger)
			except Exception:
				pass
			
			# Pre-check: background tồn tại (cảnh báo nhưng vẫn tiếp tục để không phá test/mocking)
			if not os.path.exists(self.background_path):
				write_log("WARNING", function, f"Background không tồn tại (tiếp tục chạy): {self.background_path}", self.logger)
			# Pre-check: input_folder
			if not os.path.isdir(self.input_folder):
				write_log("ERROR", function, f"Thư mục nguồn không hợp lệ: {self.input_folder}", self.logger)
				return {"total": 0, "success": 0, "failed": 0, "skipped": 0, "error": "invalid_input_folder"}
			
			# Scan input files
			pattern = os.path.join(self.input_folder, "**", "*.mp4")
			files = glob.glob(pattern, recursive=True)
			files = [f for f in files if os.path.isfile(f)]
			# Chuẩn hoá tuyệt đối để không phụ thuộc working directory khi gọi FFmpeg
			files = [os.path.abspath(f) for f in files]
			write_log("INFO", function, f"Đã quét file .mp4: {len(files)}", self.logger)
			try:
				head = [os.path.basename(p) for p in files[:5]]
				if head:
					write_log("DEBUG", function, f"Mẫu files: {head}", self.logger)
			except Exception:
				pass
			
			total = len(files)
			if total == 0:
				write_log("WARNING", function, f"Không tìm thấy file .mp4 trong: {self.input_folder}", self.logger)
				return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
			
			os.makedirs(self.output_folder, exist_ok=True)
			
			editor = VideoEditor()
			# Chuẩn hoá đường dẫn nền tuyệt đối
			background_abs = os.path.abspath(self.background_path)
			# Chuẩn bị nguồn audio nếu có
			audio_source_path = self.config.get("audio_source_path") or ""
			audio_library_dir = self.config.get("audio_library_dir") or os.path.join(self.output_folder, "..", "..", "assets", "audio")
			audio_extract_when_video = bool(self.config.get("audio_extract_when_video", True))
			audio_delete_source_after_extract = bool(self.config.get("audio_delete_source_after_extract", True))
			prepared_audio_path = ""
			if audio_source_path:
				try:
					ext = os.path.splitext(audio_source_path)[1].lower()
					audio_exts = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
					if ext in audio_exts:
						prepared_audio_path = os.path.abspath(audio_source_path)
						write_log("INFO", function, f"Dùng audio trực tiếp: {prepared_audio_path}", self.logger)
					else:
						if audio_extract_when_video:
							base = os.path.splitext(os.path.basename(audio_source_path))[0]
							ok, err, out_audio = editor.extract_audio(audio_source_path, os.path.abspath(audio_library_dir), base_name=base)
							if ok and out_audio:
								prepared_audio_path = out_audio
								write_log("INFO", function, f"Đã tách audio vào kho: {prepared_audio_path}", self.logger)
								# Ghi nhớ đường dẫn này để tái sử dụng (ghi luôn vào config để các file dùng chung)
								self.config["audio_source_path"] = prepared_audio_path
								if audio_delete_source_after_extract:
                                    # Xoá video nguồn tách âm nếu được yêu cầu
									try:
										os.remove(audio_source_path)
										write_log("INFO", function, f"Đã xoá file nguồn sau khi tách audio: {audio_source_path}", self.logger)
									except Exception as _e_rm:
										write_log("WARNING", function, f"Không thể xoá file nguồn: {_e_rm}", self.logger)
							else:
								write_log("WARNING", function, f"Tách audio thất bại, dùng nguồn audio gốc nếu có: {err}", self.logger)
						else:
							write_log("INFO", function, "Không bật tách audio từ video, dùng trực tiếp media như input audio.", self.logger)
							prepared_audio_path = os.path.abspath(audio_source_path)
				except Exception as e:
					write_log("ERROR", function, f"Lỗi chuẩn bị audio: {e}", self.logger, exc_info=True)
			success = 0
			failed = 0
			skipped = 0
			done = 0
			
			def process_one(src: str) -> Dict:
				try:
					if self._should_stop:
						return {"success": False, "error": "Stopped", "input": src, "output": None}
					
					dst = self._make_output_path(src)
					if os.path.exists(dst) and self.config.get("skip_existing", True):
						write_log("INFO", function, f"Skip (đã tồn tại): {dst}", self.logger)
						return {"success": True, "skipped": True, "input": src, "output": dst}
					
					# Gộp config: truyền audio đã chuẩn bị (nếu có)
					cfg = dict(self.config)
					if prepared_audio_path:
						cfg["audio_source_path"] = prepared_audio_path
					result = editor.process_one(
						input_video=src,
						background_path=background_abs,
						output_path=dst,
						config=cfg
					)
					return result
				except Exception as e:
					write_log("ERROR", function, f"Lỗi khi xử lý {src}: {e}", self.logger, exc_info=True)
					return {"success": False, "error": str(e), "input": src, "output": None}
			
			with ThreadPoolExecutor(max_workers=self.threads) as ex:
				future_map = {ex.submit(process_one, f): f for f in files}
				for fut in as_completed(future_map):
					src = future_map[fut]
					try:
						res = fut.result()
					except Exception as e:
						write_log("ERROR", function, f"Worker lỗi: {e}", self.logger, exc_info=True)
						res = {"success": False, "error": str(e), "input": src, "output": None}
					
					done += 1
					if res.get("success"):
						if res.get("skipped"):
							skipped += 1
						else:
							success += 1
					else:
						failed += 1
					
					if self.result_cb:
						try:
							self.result_cb(res)
						except Exception as e:
							write_log("ERROR", function, f"result_cb error: {e}", self.logger, exc_info=True)
					
					progress = (done / total) * 100.0
					msg = f"Đang xử lý {done}/{total}"
					if self.progress_cb:
						try:
							self.progress_cb(progress, done, total, msg)
						except Exception as e:
							write_log("ERROR", function, f"progress_cb error: {e}", self.logger, exc_info=True)
			
			summary = {"total": total, "success": success, "failed": failed, "skipped": skipped}
			write_log("INFO", function, f"Hoàn tất batch: {summary}", self.logger)
			
			if self.complete_cb:
				try:
					self.complete_cb()
				except Exception as e:
					write_log("ERROR", function, f"complete_cb error: {e}", self.logger, exc_info=True)
			
			return summary
		
		except Exception as e:
			write_log("ERROR", function, f"Lỗi batch: {e}", self.logger, exc_info=True)
			return {"total": 0, "success": 0, "failed": 0, "skipped": 0, "error": str(e)}


