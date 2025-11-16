import unittest
import tkinter as tk

from gui.edit_video_screen import EditVideoScreen


class TestEditVideoScreenScrollStep(unittest.TestCase):
	def setUp(self):
		self.root = tk.Tk()
		self.root.withdraw()
	
	def tearDown(self):
		try:
			self.root.destroy()
		except Exception:
			pass
	
	def _event(self, delta):
		class E: pass
		e = E()
		e.delta = delta
		return e
	
	def test_scroll_step_affects_scale_amount(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		screen.keep_ratio_var.set(True)
		screen.force_916_var.set(True)
		screen._refresh_preview()
		# Bật tốc độ 1x để chỉ kiểm tra step
		screen.resize_speed_var.set(1)
		# Kích thước ban đầu
		w0 = int(screen.size_w_var.get())
		h0 = int(screen.size_h_var.get())
		# Step nhỏ
		screen.scroll_step_var.set(0.01)
		screen._on_wheel_resize(self._event(120))
		w_small = int(screen.size_w_var.get())
		# Reset lại
		screen._refresh_preview()
		screen.resize_speed_var.set(1)
		# Step lớn
		screen.scroll_step_var.set(0.10)
		screen._on_wheel_resize(self._event(120))
		w_big = int(screen.size_w_var.get())
		# So sánh mức tăng
		self.assertGreater(w_small, w0)
		self.assertGreater(w_big, w_small)


if __name__ == "__main__":
	unittest.main()


