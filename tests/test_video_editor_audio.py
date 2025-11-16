import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from services.video_editor import VideoEditor


class TestVideoEditorAudio(unittest.TestCase):
	def setUp(self):
		self.editor = VideoEditor()
		# Tạo file giả
		self.tmpdir = tempfile.TemporaryDirectory()
		self.bg = os.path.join(self.tmpdir.name, "bg.png")
		self.iv = os.path.join(self.tmpdir.name, "in.mp4")
		self.out = os.path.join(self.tmpdir.name, "out.mp4")
		open(self.bg, "wb").close()
		open(self.iv, "wb").close()
	
	def tearDown(self):
		self.tmpdir.cleanup()
	
	@patch("services.video_editor.subprocess.run")
	def test_apply_external_audio_with_loop_and_volume(self, mrun):
		# Giả lập ffmpeg ok
		def _side_effect(*args, **kwargs):
			# Tạo file output giả như ffmpeg sinh ra
			try:
				outdir = kwargs.get("cwd") or os.getcwd()
			except Exception:
				outdir = os.getcwd()
			# output tên file nằm ở cuối cmd list (đã set cwd=workdir)
			returncode = 0
			m = MagicMock()
			m.returncode = returncode
			m.stdout = ""
			m.stderr = ""
			# Lấy tên file từ lệnh đã được tạo trước đó
			# Sau build, editor._last_cmd_list[-1] là tên file output
			try:
				outname = self.editor._last_cmd_list[-1]
				open(os.path.join(outdir, outname), "wb").close()
			except Exception:
				pass
			return m
		mrun.side_effect = _side_effect
		with patch.object(self.editor, "_ensure_ffmpeg", return_value=(True, None)), \
		     patch.object(self.editor, "_read_background_size", return_value=(360, 640)):
			cfg = {
				"position": {"x": 10, "y": 20},
				"size": {"width": 200, "height": 300},
				"keep_ratio": True,
				"pad_color": [0,0,0],
				"bitrate": "800k",
				"preset": "veryfast",
				"audio_source_path": os.path.join(self.tmpdir.name, "audio_src.mp3"),
				"audio_start_sec": 1.5,
				"audio_loop": True,
				"audio_volume_percent": 80,
			}
			open(cfg["audio_source_path"], "wb").close()
			res = self.editor.process_one(self.iv, self.bg, self.out, cfg)
			self.assertTrue(res["success"])
			cmd = self.editor._last_cmd_list
			# Kiểm tra có chèn input audio với -ss và -stream_loop
			self.assertIn("-i", cmd)
			self.assertIn(cfg["audio_source_path"], cmd)
			self.assertIn("-stream_loop", cmd)
			self.assertIn("-1", cmd)
			self.assertIn("-ss", cmd)
			self.assertIn("1.5", cmd)
			# map audio từ input 2
			self.assertIn("-map", cmd)
			self.assertIn("2:a?", cmd)
			# filter âm lượng
			self.assertIn("-filter:a", cmd)
			self.assertIn("volume=0.800", cmd)
			# cặp -filter:a và volume phải liền kề và đứng trước output
			fa_idx = cmd.index("-filter:a")
			self.assertEqual(cmd[fa_idx + 1], "volume=0.800")
			self.assertLess(fa_idx, len(cmd) - 2)
			# -shortest để dừng theo video
			self.assertIn("-shortest", cmd)
	

if __name__ == "__main__":
	unittest.main()


