import os
import tempfile
import unittest
from unittest import mock

from services.edit_service import EditService


class TestEditService(unittest.TestCase):
	def _make_dummy_files(self, folder: str, n: int = 3):
		os.makedirs(folder, exist_ok=True)
		paths = []
		for i in range(n):
			p = os.path.join(folder, f"v{i}.mp4")
			open(p, "wb").close()
			paths.append(p)
		return paths
	
	@mock.patch("services.edit_service.VideoEditor")
	def test_run_success_and_skip(self, m_editor_cls):
		with tempfile.TemporaryDirectory() as tmp:
			inp = os.path.join(tmp, "downloads")
			out = os.path.join(tmp, "edited")
			self._make_dummy_files(inp, 3)
			
			# Tạo sẵn 1 output để skip
			os.makedirs(out, exist_ok=True)
			open(os.path.join(out, "v1_edited.mp4"), "wb").close()
			
			# mock process_one trả success
			editor_instance = mock.MagicMock()
			editor_instance.process_one.return_value = {"success": True, "input": "x", "output": "y"}
			m_editor_cls.return_value = editor_instance
			
			progress_calls = []
			result_calls = []
			service = EditService(
				background_path=os.path.join(tmp, "bg.png"),
				input_folder=inp,
				output_folder=out,
				config={"output_suffix": "_edited", "skip_existing": True},
				threads=2,
				progress_cb=lambda p, c, t, msg: progress_calls.append((p, c, t)),
				result_cb=lambda r: result_calls.append(r),
				complete_cb=None
			)
			
			summary = service.run()
			self.assertEqual(summary["total"], 3)
			# 1 file skip, 2 file xử lý thành công
			self.assertEqual(summary["skipped"], 1)
			self.assertEqual(summary["success"], 2)
			self.assertEqual(summary["failed"], 0)
			
			self.assertTrue(len(progress_calls) >= 2)  # Có cập nhật progress
			self.assertEqual(len(result_calls), 3)     # Có 3 kết quả được bắn ra
	
	@mock.patch("services.edit_service.VideoEditor")
	def test_stop_flag(self, m_editor_cls):
		with tempfile.TemporaryDirectory() as tmp:
			inp = os.path.join(tmp, "downloads")
			out = os.path.join(tmp, "edited")
			self._make_dummy_files(inp, 5)
			
			editor_instance = mock.MagicMock()
			# Giả lập xử lý chậm để stop giữa chừng
			def slow_process(*args, **kwargs):
				import time; time.sleep(0.05)
				return {"success": True, "input": "x", "output": "y"}
			editor_instance.process_one.side_effect = slow_process
			m_editor_cls.return_value = editor_instance
			
			service = EditService(
				background_path=os.path.join(tmp, "bg.png"),
				input_folder=inp,
				output_folder=out,
				config={"output_suffix": "_edited", "skip_existing": False},
				threads=2
			)
			# Gửi stop trước khi chạy
			service.stop()
			summary = service.run()
			# Có thể vẫn xử lý 0 hoặc 1 vài file (tùy thread), nhưng không được lỗi hệ thống
			self.assertIn("total", summary)
			self.assertIn("success", summary)


if __name__ == "__main__":
	unittest.main()


