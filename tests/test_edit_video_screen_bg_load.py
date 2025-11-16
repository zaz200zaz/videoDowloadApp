import unittest
import tkinter as tk
import os
import tempfile
from unittest import mock

from gui.edit_video_screen import EditVideoScreen


class TestEditVideoScreenBackgroundDiagnostics(unittest.TestCase):
	def setUp(self):
		self.root = tk.Tk()
		self.root.withdraw()

	def tearDown(self):
		try:
			self.root.destroy()
		except Exception:
			pass

	def _get_log_text(self, screen: EditVideoScreen) -> str:
		try:
			return screen.log_text.get("1.0", tk.END)
		except Exception:
			return ""

	def test_log_file_not_exist(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		screen.bg_path_var.set(os.path.join(tempfile.gettempdir(), "not_exists_abcxyz.jpg"))
		screen._refresh_preview()
		logs = self._get_log_text(screen)
		self.assertIn("File background không tồn tại", logs)
		self.assertIn("(preview)", logs)

	def test_log_pillow_missing_and_non_png(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		# Tạo file giả định .jpg rỗng
		fd, jpg_path = tempfile.mkstemp(suffix=".jpg")
		os.close(fd)
		try:
			with mock.patch.dict("sys.modules", {"PIL": None}):
				screen.bg_path_var.set(jpg_path)
				screen._refresh_preview()
				logs = self._get_log_text(screen)
				self.assertIn("Pillow không khả dụng", logs)
				self.assertIn("không phải PNG", logs)
		finally:
			try:
				os.remove(jpg_path)
			except Exception:
				pass

	def test_log_pillow_open_error(self):
		# Giả lập PIL có mặt nhưng Image.open lỗi
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		fd, img_path = tempfile.mkstemp(suffix=".jpg")
		os.close(fd)
		try:
			class FakeImage:
				def __init__(self, *a, **kw): pass
				def __enter__(self): 
					raise Exception("bad image")
				def __exit__(self, *a): return False

			class FakePILImageModule:
				@staticmethod
				def open(path):
					return FakeImage()

			class FakeImageTk:
				class PhotoImage:
					def __init__(self, *a, **kw): pass

			fake_pil_pkg = mock.MagicMock()
			fake_pil_pkg.Image = FakePILImageModule
			fake_pil_pkg.ImageTk = FakeImageTk

			with mock.patch.dict("sys.modules", {"PIL": fake_pil_pkg}):
				screen.bg_path_var.set(img_path)
				screen._refresh_preview()
				logs = self._get_log_text(screen)
				# Có thể log từ _read_bg_size_safe hoặc từ _load_preview_image tuỳ đường đi
				self.assertTrue(
					("Lỗi đọc kích thước background bằng Pillow" in logs) or
					("Lỗi mở/resize background bằng Pillow" in logs)
				)
		finally:
			try:
				os.remove(img_path)
			except Exception:
				pass


if __name__ == "__main__":
	unittest.main()


