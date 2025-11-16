import unittest
import tkinter as tk

from gui.edit_video_screen import EditVideoScreen


class TestEditVideoScreen916(unittest.TestCase):
	def setUp(self):
		self.root = tk.Tk()
		self.root.withdraw()
	
	def tearDown(self):
		try:
			self.root.destroy()
		except Exception:
			pass
	
	def _make_event(self, x, y):
		class E: pass
		e = E()
		e.x = x
		e.y = y
		return e
	
	def test_resize_strict_916_lock(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		# Bật khoá 9:16
		screen.force_916_var.set(True)
		screen.keep_ratio_var.set(True)
		screen._refresh_preview()
		# Lấy rect và kéo góc br để phóng to
		x1, y1, x2, y2 = screen.preview_canvas.coords(screen._rect_id)
		screen._on_handle_press(self._make_event(int(x2), int(y2)), "br")
		screen._on_handle_motion(self._make_event(int(x2)+40, int(y2)+70), "br")
		new_w = int(screen.size_w_var.get())
		new_h = int(screen.size_h_var.get())
		# Tỉ lệ 9:16 ~ 0.5625
		self.assertGreater(new_w, 0)
		self.assertGreater(new_h, 0)
		self.assertAlmostEqual(new_w / new_h, 9/16, delta=0.03)
		# Log phải thể hiện ratio_lock
		logs = screen.log_text.get("1.0", tk.END)
		self.assertIn("[ratio_lock] mode=9:16", logs)


if __name__ == "__main__":
	unittest.main()


