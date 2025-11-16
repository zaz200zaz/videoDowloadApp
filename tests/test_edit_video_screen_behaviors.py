import unittest
import tkinter as tk

from gui.edit_video_screen import EditVideoScreen


class TestEditVideoScreenBehaviors(unittest.TestCase):
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
	
	def test_drag_changes_position_and_logs(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		screen._refresh_preview()
		self.assertIsNotNone(screen._rect_id)
		# Lấy rect hiện tại
		x1, y1, x2, y2 = screen.preview_canvas.coords(screen._rect_id)
		# ấn gần góc trái trên rồi kéo +10,+6
		screen._on_rect_press(self._make_event(int(x1)+1, int(y1)+1))
		screen._on_rect_motion(self._make_event(int(x1)+11, int(y1)+7))
		# pos (thực) phải thay đổi >= 0
		self.assertGreaterEqual(int(screen.pos_x_var.get()), 0)
		self.assertGreaterEqual(int(screen.pos_y_var.get()), 0)
		# log phải có drag_start và drag_move
		logs = screen.log_text.get("1.0", tk.END)
		self.assertIn("[drag_start]", logs)
		self.assertIn("[drag_move]", logs)
	
	def test_resize_keeps_ratio_and_logs(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		screen.keep_ratio_var.set(True)
		screen.size_w_var.set(240)
		screen.size_h_var.set(120)  # tỉ lệ 2.0
		screen._refresh_preview()
		x1, y1, x2, y2 = screen.preview_canvas.coords(screen._rect_id)
		# ấn vào góc br, kéo tăng kích thước
		screen._on_handle_press(self._make_event(int(x2), int(y2)), "br")
		screen._on_handle_motion(self._make_event(int(x2)+30, int(y2)+15), "br")
		# kiểm tra size thay đổi và gần giữ tỉ lệ
		new_w = int(screen.size_w_var.get())
		new_h = int(screen.size_h_var.get())
		self.assertGreater(new_w, 0)
		self.assertGreater(new_h, 0)
		self.assertAlmostEqual(new_w / new_h, 2.0, delta=0.2)
		# log phải có resize_start, ratio, resize_move
		logs = screen.log_text.get("1.0", tk.END)
		self.assertIn("[resize_start]", logs)
		self.assertIn("[ratio]", logs)
		self.assertIn("[resize_move]", logs)

	def test_resize_top_left_shrink_changes_size_and_logs_reasons(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		screen.keep_ratio_var.set(True)
		screen.size_w_var.set(200)
		screen.size_h_var.set(100)  # 2:1
		screen._refresh_preview()
		x1, y1, x2, y2 = screen.preview_canvas.coords(screen._rect_id)
		# nhấn góc TL rồi kéo vào trong để thu nhỏ
		screen._on_handle_press(self._make_event(int(x1), int(y1)), "tl")
		screen._on_handle_motion(self._make_event(int(x1)+20, int(y1)+10), "tl")
		w_after = int(screen.size_w_var.get())
		h_after = int(screen.size_h_var.get())
		self.assertLess(w_after, 200)
		self.assertLess(h_after, 100)
		# Log phong phú
		logs = screen.log_text.get("1.0", tk.END)
		self.assertIn("[pre]", logs)
		self.assertIn("[pre_clamp]", logs)
		self.assertIn("[resize_apply]", logs)
	
	def test_preview_coords_match_scale(self):
		container = tk.Frame(self.root)
		container.pack()
		screen = EditVideoScreen(container, logger=None, navigation_controller=None)
		# Đặt pos/size cụ thể, refresh và kiểm tra coords theo scale
		screen.pos_x_var.set(100)
		screen.pos_y_var.set(150)
		screen.size_w_var.set(200)
		screen.size_h_var.set(300)
		screen._refresh_preview()
		x1, y1, x2, y2 = screen.preview_canvas.coords(screen._rect_id)
		sw = x2 - x1
		sh = y2 - y1
		# Tỉ lệ sai số nhỏ do làm tròn
		self.assertAlmostEqual(sw, int(200 * screen._scale), delta=2.0)
		self.assertAlmostEqual(sh, int(300 * screen._scale), delta=2.0)


if __name__ == "__main__":
	unittest.main()


