import os
import tempfile
import unittest
from unittest import mock

from gui.controllers.edit_controller import EditController


class TestIntegrationBatchEditor(unittest.TestCase):
	@mock.patch("services.edit_service.VideoEditor")
	def test_end_to_end_controller_to_service(self, m_editor_cls):
		with tempfile.TemporaryDirectory() as tmp:
			# Tạo input videos
			inp = os.path.join(tmp, "downloads")
			os.makedirs(inp, exist_ok=True)
			for i in range(3):
				open(os.path.join(inp, f"v{i}.mp4"), "wb").close()
			
			out = os.path.join(tmp, "edited")
			bg = os.path.join(tmp, "bg.png")
			open(bg, "wb").close()
			
			# Mock editor -> luôn trả về success
			editor_instance = mock.MagicMock()
			editor_instance.process_one.return_value = {"success": True, "input": "x", "output": "y"}
			m_editor_cls.return_value = editor_instance
			
			controller = EditController()
			
			progress_events = []
			results = []
			completed = []
			
			ok = controller.start_batch(
				background_path=bg,
				input_folder=inp,
				output_folder=out,
				config={"output_suffix": "_edited", "skip_existing": True},
				threads=2,
				progress_cb=lambda p, c, t, msg: progress_events.append((p, c, t)),
				result_cb=lambda r: results.append(r),
				complete_cb=lambda: completed.append(True)
			)
			
			self.assertTrue(ok)
			
			# Đợi xử lý xong
			import time
			for _ in range(50):
				if completed:
					break
				time.sleep(0.05)
			
			self.assertTrue(completed, "Batch không hoàn tất trong thời gian mong đợi")
			self.assertGreaterEqual(len(progress_events), 1)
			self.assertEqual(len(results), 3)


if __name__ == "__main__":
	unittest.main()


