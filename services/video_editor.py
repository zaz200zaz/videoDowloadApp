"""
Video Editor
Xử lý một video: resize, chèn vào background, overlay, xuất MP4 bằng FFmpeg.

Yêu cầu kỹ thuật:
- Dùng FFmpeg qua subprocess
- Pillow để đọc kích thước background, hỗ trợ tính toán vị trí

Logging: sử dụng utils.log_helper.write_log/get_logger theo chuẩn.
"""

import os
import shlex
import shutil
import subprocess
from typing import Dict, Optional, Tuple
from typing import Tuple as _TupleAlias
try:
	from PIL import Image  # type: ignore
	_HAS_PIL = True
except Exception:
	Image = None  # type: ignore
	_HAS_PIL = False
from utils.log_helper import get_logger, write_log


class VideoEditor:
	"""
	Xử lý một video với FFmpeg theo cấu hình.
	
	Parameters:
	- background_path: Đường dẫn ảnh nền (PNG/JPG)
	- position: dict {x, y} vị trí overlay video trên background
	- size: dict {width, height} kích thước mục tiêu của video trong khung
	- keep_ratio: bool, giữ tỉ lệ khi resize (pad vào phần dư)
	- pad_color: [r, g, b] màu pad nếu keep_ratio
	- bitrate: str, ví dụ "2500k"
	- preset: str, ví dụ "medium"
	
	Returns:
	- Tuple(success: bool, error: Optional[str])
	"""
	
	def __init__(self):
		self.logger = get_logger("VideoEditor")
	
	def _ensure_ffmpeg(self) -> Tuple[bool, Optional[str]]:
		"""
		Kiểm tra ffmpeg có sẵn trong PATH.
		"""
		function = "VideoEditor._ensure_ffmpeg"
		try:
			path = shutil.which("ffmpeg")
			if path:
				write_log("DEBUG", function, f"ffmpeg found: {path}", self.logger)
				return True, None
			write_log("ERROR", function, "ffmpeg không tìm thấy trong PATH", self.logger)
			return False, "ffmpeg không tìm thấy trong PATH"
		except Exception as e:
			write_log("ERROR", function, f"Lỗi khi kiểm tra ffmpeg: {e}", self.logger, exc_info=True)
			return False, str(e)
	
	def _read_background_size(self, background_path: str) -> Tuple[int, int]:
		"""
		Đọc kích thước background từ file ảnh.
		"""
		function = "VideoEditor._read_background_size"
		# Ưu tiên dùng Pillow nếu có
		if _HAS_PIL and Image is not None:
			with Image.open(background_path) as img:
				w, h = img.size
				write_log("DEBUG", function, f"Background size (PIL): {w}x{h}", self.logger)
				return w, h
		# Fallback: parse nhanh PNG/JPEG header để lấy kích thước (không cần PIL)
		try:
			with open(background_path, "rb") as f:
				sig = f.read(24)
				# PNG
				if sig.startswith(b"\x89PNG\r\n\x1a\n") and sig[12:16] == b"IHDR":
					w = int.from_bytes(sig[16:20], "big")
					h = int.from_bytes(sig[20:24], "big")
					write_log("DEBUG", function, f"Background size (PNG header): {w}x{h}", self.logger)
					return w, h
				# JPEG - tìm SOFn
				f.seek(0)
				data = f.read()
				i = 0
				while i < len(data) - 9:
					if data[i] == 0xFF and 0xC0 <= data[i+1] <= 0xC3:
						# SOF0..SOF3
						block_len = data[i+2] << 8 | data[i+3]
						h = data[i+5] << 8 | data[i+6]
						w = data[i+7] << 8 | data[i+8]
						write_log("DEBUG", function, f"Background size (JPEG header): {w}x{h}", self.logger)
						return w, h
					i += 1
		except Exception as e:
			write_log("WARNING", function, f"Không thể đọc kích thước background: {e}, dùng mặc định 1080x1920", self.logger)
		# Mặc định an toàn nếu không đọc được
		return 1080, 1920
	
	def build_ffmpeg_command(
		self,
		input_video: str,
		background_path: str,
		output_path: str,
		position: Dict[str, int],
		size: Dict[str, int],
		keep_ratio: bool,
		pad_color: Tuple[int, int, int],
		bitrate: str,
		preset: str
	) -> Tuple[str, str]:
		"""
		Tạo lệnh FFmpeg (filter_complex) để:
		1) Đọc background làm layer nền
		2) Scale video vào kích thước mục tiêu (giữ tỉ lệ -> pad)
		3) Overlay lên background tại (x, y)
		4) Encode H.264/AAC với bitrate/preset
		
		Returns:
			(cmd_str, working_dir)
		"""
		function = "VideoEditor.build_ffmpeg_command"
		
		bg_w, bg_h = self._read_background_size(background_path)
		target_w = max(1, int(size.get("width", bg_w)))
		target_h = max(1, int(size.get("height", bg_h)))
		x = max(0, int(position.get("x", 0)))
		y = max(0, int(position.get("y", 0)))
		pr = max(0, int(pad_color[0]))
		pg = max(0, int(pad_color[1]))
		pb = max(0, int(pad_color[2]))
		
		# Filter để scale và pad video đến kích thước mục tiêu
		# Nếu keep_ratio: dùng scale với force_original_aspect_ratio=decrease, sau đó pad đến target_w/target_h
		# Nếu không: scale trực tiếp về target_w x target_h
		if keep_ratio:
			scale_filter = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease"
			pad_filter = f",pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:color=#{pr:02x}{pg:02x}{pb:02x}"
			video_chain = f"[1:v]{scale_filter}{pad_filter}[vid]"
		else:
			video_chain = f"[1:v]scale={target_w}:{target_h}:flags=bicubic[vid]"
		
		# Overlay video đã scale/pad lên background tại (x,y)
		# Input #0: background ảnh (loop), Input #1: video
		filter_complex = f"{video_chain};[0:v][vid]overlay={x}:{y}:shortest=1[outv]"
		
		# Lệnh ffmpeg
		# -loop 1 để phát background ảnh, -shortest dừng khi video kết thúc
		# -map [outv] -map 1:a? để audio từ video nguồn (nếu có)
		cmd = [
			"ffmpeg",
			"-y",
			"-loop", "1",
			"-i", background_path,
			"-i", input_video,
			"-filter_complex", filter_complex,
			"-map", "[outv]",
			"-map", "1:a?",
			"-c:v", "libx264",
			"-preset", preset,
			"-b:v", bitrate,
			"-pix_fmt", "yuv420p",
			"-c:a", "aac",
			"-shortest",
			output_path
		]
		
		cmd_str = " ".join(shlex.quote(part) for part in cmd)
		write_log("DEBUG", function, f"FFmpeg command: {cmd_str}", self.logger)
		return cmd_str, os.path.dirname(os.path.abspath(output_path))
	
	def process_one(
		self,
		input_video: str,
		background_path: str,
		output_path: str,
		config: Dict
	) -> Dict:
		"""
		Xử lý một video theo config.
		
		Returns:
			result dict: {success, error, input, output}
		"""
		function = "VideoEditor.process_one"
		try:
			write_log("INFO", function, f"Bắt đầu xử lý: {input_video}", self.logger)
			
			ok, err = self._ensure_ffmpeg()
			if not ok:
				return {"success": False, "error": err, "input": input_video, "output": None}
			
			position = config.get("position", {"x": 0, "y": 0})
			size = config.get("size", {"width": 720, "height": 1280})
			keep_ratio = bool(config.get("keep_ratio", True))
			pad_color = tuple(config.get("pad_color", [0, 0, 0]))  # [r,g,b]
			bitrate = config.get("bitrate", "2500k")
			preset = config.get("preset", "medium")
			
			cmd_str, workdir = self.build_ffmpeg_command(
				input_video, background_path, output_path,
				position, size, keep_ratio, pad_color, bitrate, preset
			)
			
			os.makedirs(os.path.dirname(output_path), exist_ok=True)
			
			# Thực thi FFmpeg
			proc = subprocess.run(
				cmd_str, shell=True, cwd=workdir,
				stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore"
			)
			if proc.returncode != 0:
				# Ghi snippet stderr để debug
				stderr_snippet = (proc.stderr or "")[-400:]
				write_log("ERROR", function, f"FFmpeg failed (code={proc.returncode}). Stderr: {stderr_snippet}", self.logger)
				# Retry một lần theo yêu cầu
				proc2 = subprocess.run(
					cmd_str, shell=True, cwd=workdir,
					stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore"
				)
				if proc2.returncode != 0:
					stderr_snippet2 = (proc2.stderr or "")[-400:]
					write_log("ERROR", function, f"FFmpeg retry failed (code={proc2.returncode}). Stderr: {stderr_snippet2}", self.logger)
					return {"success": False, "error": "FFmpeg failed", "input": input_video, "output": None}
			
			if not os.path.exists(output_path):
				write_log("ERROR", function, "Output file không tồn tại sau khi FFmpeg chạy", self.logger)
				return {"success": False, "error": "No output generated", "input": input_video, "output": None}
			
			write_log("INFO", function, f"Hoàn tất: {output_path}", self.logger)
			return {"success": True, "error": None, "input": input_video, "output": output_path}
		
		except Exception as e:
			write_log("ERROR", function, f"Lỗi xử lý video: {e}", self.logger, exc_info=True)
			return {"success": False, "error": str(e), "input": input_video, "output": None}


