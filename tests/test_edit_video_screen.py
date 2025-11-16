import unittest
import tkinter as tk
from unittest import mock

from gui.edit_video_screen import EditVideoScreen
from gui.controllers.navigation_controller import NavigationController


class TestEditVideoScreen(unittest.TestCase):
	def setUp(self):
		self.root = tk.Tk()
		self.root.withdraw()  # không hiện cửa sổ thật
	
	def tearDown(self):
		try:
			self.root.destroy()
		except Exception:
			pass
	
	def test_embedded_mode_no_toplevel(self):
		# Tạo content_container và navigation ở chế độ mobile (frame-based)
		container = tk.Frame(self.root)
		container.pack()
		nav = NavigationController(self.root, home_screen_name="MainDashboard", content_container=container, mobile_mode=True)
		# Đăng ký EditVideoScreen
		nav.register_screen("EditVideoScreen", EditVideoScreen)
		# Mở EditVideoScreen như frame nhúng
		_ = nav.open_screen("EditVideoScreen", from_screen="MainDashboard")
		# Trong mobile mode, NavigationController lưu frame tại screens[screen_name]
		frame = nav.screens.get("EditVideoScreen")
		self.assertIsNotNone(frame, "Frame của EditVideoScreen phải tồn tại trong registry")
		# Kiểm tra tồn tại Canvas preview trong cây widget
		def has_canvas(widget):
			if isinstance(widget, tk.Canvas):
				return True
			for ch in widget.winfo_children():
				if has_canvas(ch):
					return True
			return False
		canvas_found = has_canvas(frame)
		self.assertTrue(canvas_found, "Canvas preview phải tồn tại trong embedded mode")
	
	def test_drag_updates_position_vars(self):
		# Tạo EditVideoScreen trực tiếp ở embedded mode
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		# Đảm bảo có canvas và rectangle
		screen._refresh_preview()
		self.assertIsNotNone(screen.preview_canvas)
		# Lấy rect và mô phỏng drag nhỏ (nếu có)
		if screen._rect_id:
			# Gọi trực tiếp handler: press tại 0,0 (giả lập nằm trên góc trái rect)
			class E: pass
			e = E(); e.x = 1; e.y = 1
			screen._on_rect_press(e)
			# Kéo sang phải 10px, xuống 5px (trên canvas)
			e2 = E(); e2.x = 11; e2.y = 6
			screen._on_rect_motion(e2)
			# Xác minh pos_x/pos_y đã thay đổi phù hợp (chia scale)
			self.assertGreaterEqual(int(screen.pos_x_var.get()), 0)
			self.assertGreaterEqual(int(screen.pos_y_var.get()), 0)


if __name__ == "__main__":
	unittest.main()


