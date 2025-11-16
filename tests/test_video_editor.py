import os
import tempfile
import unittest
from unittest import mock
try:
	from PIL import Image
	_HAS_PIL = True
except Exception:
	Image = None
	_HAS_PIL = False

from services.video_editor import VideoEditor


class TestVideoEditor(unittest.TestCase):
	def setUp(self):
		self.editor = VideoEditor()
	
	@mock.patch("shutil.which", return_value="C:/ffmpeg/bin/ffmpeg.exe")
	def test_ensure_ffmpeg_ok(self, m_which):
		ok, err = self.editor._ensure_ffmpeg()
		self.assertTrue(ok)
		self.assertIsNone(err)
	
	@mock.patch("shutil.which", return_value=None)
	def test_ensure_ffmpeg_missing(self, m_which):
		ok, err = self.editor._ensure_ffmpeg()
		self.assertFalse(ok)
		self.assertIn("ffmpeg", err or "")
	
	@unittest.skipUnless(_HAS_PIL, "Pillow không có sẵn trong môi trường test")
	def test_read_background_size(self):
		with tempfile.TemporaryDirectory() as tmp:
			bg = os.path.join(tmp, "bg.png")
			Image.new("RGB", (800, 600), color=(0, 0, 0)).save(bg)
			w, h = self.editor._read_background_size(bg)
			self.assertEqual((w, h), (800, 600))
	
	@mock.patch.object(VideoEditor, "_read_background_size", return_value=(1080, 1920))
	def test_build_ffmpeg_command_keep_ratio(self, m_bgsize):
		cmd, wd = self.editor.build_ffmpeg_command(
			input_video="in.mp4",
			background_path="bg.png",
			output_path="out.mp4",
			position={"x": 100, "y": 200},
			size={"width": 720, "height": 1280},
			keep_ratio=True,
			pad_color=(0, 0, 0),
			bitrate="2500k",
			preset="medium"
		)
		self.assertIn("ffmpeg", cmd)
		self.assertIn("-filter_complex", cmd)
		self.assertIn("overlay=100:200", cmd)
		self.assertTrue(wd.endswith(os.path.dirname(os.path.abspath("out.mp4"))))
	
	@mock.patch.object(VideoEditor, "_read_background_size", return_value=(1080, 1920))
	@mock.patch.object(VideoEditor, "_ensure_ffmpeg", return_value=(True, None))
	@mock.patch("subprocess.run")
	def test_process_one_success(self, m_run, m_ffmpeg_ok, m_bgsize):
		# Giả lập FFmpeg tạo output thành công
		class Proc: returncode = 0; stderr = ""; stdout = ""
		m_run.return_value = Proc()
		
		with tempfile.TemporaryDirectory() as tmp:
			bg = os.path.join(tmp, "bg.png")
			if _HAS_PIL and Image is not None:
				Image.new("RGB", (1080, 1920), color=(0, 0, 0)).save(bg)
			else:
				# Tạo file rỗng; _read_background_size đã mock nên không cần nội dung thật
				open(bg, "wb").close()
			
			# Tạo file out giả để kiểm tra branch tồn tại sau khi ffmpeg chạy
			out_path = os.path.join(tmp, "out.mp4")
			
			def run_side_effect(*args, **kwargs):
				# tạo file output
				open(out_path, "wb").close()
				return Proc()
			m_run.side_effect = run_side_effect
			
			res = self.editor.process_one(
				input_video=os.path.join(tmp, "in.mp4"),
				background_path=bg,
				output_path=out_path,
				config={
					"position": {"x": 0, "y": 0},
					"size": {"width": 720, "height": 1280},
					"keep_ratio": True,
					"pad_color": [0, 0, 0],
					"bitrate": "2500k",
					"preset": "medium"
				}
			)
			self.assertTrue(res.get("success"))
			self.assertEqual(res.get("output"), out_path)
	
	@mock.patch.object(VideoEditor, "_read_background_size", return_value=(1080, 1920))
	@mock.patch.object(VideoEditor, "_ensure_ffmpeg", return_value=(True, None))
	@mock.patch("subprocess.run")
	def test_process_one_ffmpeg_fail_retry_fail(self, m_run, m_ffmpeg_ok, m_bgsize):
		# Giả lập FFmpeg trả lỗi cả lần đầu và lần retry
		class ProcFail: returncode = 1; stderr = "error"; stdout = ""
		m_run.return_value = ProcFail()
		
		with tempfile.TemporaryDirectory() as tmp:
			bg = os.path.join(tmp, "bg.png")
			if _HAS_PIL and Image is not None:
				Image.new("RGB", (1080, 1920), color=(0, 0, 0)).save(bg)
			else:
				open(bg, "wb").close()
			out_path = os.path.join(tmp, "out.mp4")
			
			res = self.editor.process_one(
				input_video=os.path.join(tmp, "in.mp4"),
				background_path=bg,
				output_path=out_path,
				config={
					"position": {"x": 0, "y": 0},
					"size": {"width": 720, "height": 1280},
					"keep_ratio": True,
					"pad_color": [0, 0, 0],
					"bitrate": "2500k",
					"preset": "medium"
				}
			)
			self.assertFalse(res.get("success"))
			self.assertIn("failed", (res.get("error") or "").lower())


if __name__ == "__main__":
	unittest.main()


