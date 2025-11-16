import unittest
import tkinter as tk

from gui.edit_video_screen import EditVideoScreen


class TestEditVideoScreenScroll(unittest.TestCase):
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
	
	def test_scroll_resize_keeps_ratio(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		screen.keep_ratio_var.set(True)
		# Bật khoá 9:16 để kiểm tra đứng
		screen.force_916_var.set(True)
		screen._refresh_preview()
		w0 = int(screen.size_w_var.get())
		h0 = int(screen.size_h_var.get())
		# Scroll up -> phóng to
		screen._on_wheel_resize(self._event(120))
		w1 = int(screen.size_w_var.get())
		h1 = int(screen.size_h_var.get())
		self.assertGreater(w1, w0)
		self.assertGreater(h1, h0)
		self.assertAlmostEqual(w1 / h1, 9/16, delta=0.03)
		# Scroll down -> thu nhỏ
		screen._on_wheel_resize(self._event(-120))
		w2 = int(screen.size_w_var.get())
		h2 = int(screen.size_h_var.get())
		self.assertLess(w2, w1)
		self.assertLess(h2, h1)
		self.assertAlmostEqual(w2 / h2, 9/16, delta=0.03)


if __name__ == "__main__":
	unittest.main()


