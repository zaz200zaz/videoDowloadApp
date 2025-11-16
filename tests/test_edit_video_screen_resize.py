import unittest
import tkinter as tk

from gui.edit_video_screen import EditVideoScreen


class TestEditVideoScreenResize(unittest.TestCase):
	def setUp(self):
		self.root = tk.Tk()
		self.root.withdraw()
	
	def tearDown(self):
		try:
			self.root.destroy()
		except Exception:
			pass
	
	def test_resize_keeps_aspect_when_enabled(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		# Kích thước ban đầu (w,h)
		screen.size_w_var.set(200)
		screen.size_h_var.set(100)
		screen.keep_ratio_var.set(True)
		screen._refresh_preview()
		self.assertIsNotNone(screen._rect_id)
		# Bắt đầu resize tại góc br
		class E: pass
		# giả lập press vào br handle: lấy toạ độ hiện tại
		x1, y1, x2, y2 = screen.preview_canvas.coords(screen._rect_id)
		e_press = E(); e_press.x = x2; e_press.y = y2
		screen._on_handle_press(e_press, "br")
		# Kéo br theo hướng tăng width và height
		e_move = E(); e_move.x = x2 + 40; e_move.y = y2 + 20
		screen._on_handle_motion(e_move, "br")
		# Lấy size thực sau khi resize
		new_w = int(screen.size_w_var.get())
		new_h = int(screen.size_h_var.get())
		# Tỷ lệ gần bằng 2.0 (200/100)
		self.assertGreater(new_w, 0)
		self.assertGreater(new_h, 0)
		self.assertAlmostEqual(new_w / new_h, 2.0, delta=0.15)
	

if __name__ == "__main__":
	unittest.main()


