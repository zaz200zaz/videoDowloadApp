import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from services.edit_service import EditService


class TestEditServiceAudioExtract(unittest.TestCase):
	def test_extract_audio_when_video_and_configured(self):
		tmp = tempfile.TemporaryDirectory()
		try:
			bg = os.path.join(tmp.name, "bg.png"); open(bg, "wb").close()
			inp = os.path.join(tmp.name, "in"); os.makedirs(inp, exist_ok=True)
			out = os.path.join(tmp.name, "out"); os.makedirs(out, exist_ok=True)
			# Tạo 1 file .mp4 giả để quét
			src = os.path.join(inp, "a.mp4"); open(src, "wb").close()
			audio_src_video = os.path.join(tmp.name, "music_video.mp4"); open(audio_src_video, "wb").close()
			audio_lib = os.path.join(tmp.name, "assets_audio")
			cfg = {
				"position": {"x": 0, "y": 0},
				"size": {"width": 100, "height": 100},
				"keep_ratio": True,
				"pad_color": [0,0,0],
				"bitrate": "500k",
				"preset": "ultrafast",
				"output_suffix": "_edited",
				"skip_existing": False,
				"audio_source_path": audio_src_video,
				"audio_extract_when_video": True,
				"audio_library_dir": audio_lib
			}
			# Mock VideoEditor.extract_audio và process_one
			with patch("services.edit_service.VideoEditor") as V:
				ve = V.return_value
				# extract_audio tạo file m4a
				def _extract_audio(_src, _dir, base_name=None):
					os.makedirs(_dir, exist_ok=True)
					out_audio = os.path.join(_dir, f"{(base_name or 'x')}_audio.m4a")
					open(out_audio, "wb").close()
					return True, None, out_audio
				ve.extract_audio.side_effect = _extract_audio
				ve.process_one.return_value = {"success": True, "input": src, "output": os.path.join(out, "a_edited.mp4")}
				svc = EditService(bg, inp, out, cfg, threads=1)
				summary = svc.run()
				# Đã gọi extract_audio và dùng audio đã tách
				self.assertEqual(summary["success"], 1)
				ve.extract_audio.assert_called_once()
				# Sau khi run, config trong svc phải đã được cập nhật audio_source_path thành path m4a
				self.assertTrue(svc.config["audio_source_path"].endswith("_audio.m4a"))
		finally:
			tmp.cleanup()


if __name__ == "__main__":
	unittest.main()


