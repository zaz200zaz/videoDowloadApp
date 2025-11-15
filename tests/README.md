# Test Cases Documentation
# テストケースドキュメント

## Mục đích / 目的

Test cases này được tạo ra để:
- Test tất cả các chức năng quan trọng của dự án
- Đảm bảo logging đầy đủ theo System Instruction
- Test các edge cases và error handling
- Đảm bảo code quality và reliability

## Cấu trúc Test / テスト構造

```
tests/
├── __init__.py                 # Test package init
├── test_video_downloader.py    # VideoDownloader tests
├── test_download_service.py    # DownloadService tests
├── test_cookie_manager.py      # CookieManager tests
├── run_all_tests.py            # Test runner
└── README.md                   # This file
```

## Test Cases / テストケース

### 1. VideoDownloader Tests

#### test_normalize_url_valid_douyin_url
- **Mục đích**: Test URL正規化が正常に動作することを確認
- **Input**: Valid Douyin URL
- **Expected**: Normalized URL

#### test_normalize_url_direct_video_url
- **Mục đích**: Test direct video URLが正しく処理されることを確認
- **Input**: Direct video URL
- **Expected**: Same URL (không normalize)

#### test_normalize_url_invalid_url
- **Mục đích**: Test invalid URLが正しく処理されることを確認
- **Input**: None, empty string, non-Douyin URL
- **Expected**: None

#### test_extract_video_id_valid_url
- **Mục đích**: Test video ID extractionが正常に動作することを確認
- **Input**: Valid Douyin URL với video ID
- **Expected**: Video ID string

#### test_extract_video_id_no_id
- **Mục đích**: Test URL without video IDが正しく処理されることを確認
- **Input**: URL không có video ID
- **Expected**: None

#### test_get_video_info_direct_url
- **Mục đích**: Test direct video URL handlingが正常に動作することを確認
- **Input**: Direct video URL
- **Expected**: Dict với video_url và default values

#### test_get_video_info_audio_file
- **Mục đích**: Test audio file detectionが正常に動作することを確認
- **Input**: Audio URL (MP3)
- **Expected**: None (audio files should be skipped)

#### test_download_video_success
- **Mục đích**: Test video downloadが正常に動作することを確認
- **Input**: Video URL, save path, timeout settings
- **Expected**: Success dict với file_path và file_size

#### test_process_video_invalid_url
- **Mục đích**: Test invalid URL handlingが正常に動作することを確認
- **Input**: Invalid URL
- **Expected**: Success: False, error message

### 2. DownloadService Tests

#### test_start_download_empty_links
- **Mục đích**: Test empty links listが正しく処理されることを確認
- **Input**: Empty links list
- **Expected**: Download không được started

#### test_stop_download
- **Mục đích**: Test stop_downloadが正常に動作することを確認
- **Input**: Download đang chạy
- **Expected**: should_stop = True, is_downloading = False

#### test_progress_callback
- **Mục đích**: Test progress callbackが正しく呼び出されることを確認
- **Input**: Progress callback function, download links
- **Expected**: Progress callback được gọi với đúng parameters

#### test_result_callback
- **Mục đích**: Test result callbackが正しく呼び出されることを確認
- **Input**: Result callback function, download links
- **Expected**: Result callback được gọi với đúng parameters

#### test_complete_callback
- **Mục đích**: Test complete callbackが正しく呼び出されることを確認
- **Input**: Complete callback function, download links
- **Expected**: Complete callback được gọi một lần khi download hoàn thành

### 3. CookieManager Tests

#### test_save_cookie
- **Mục đích**: Test cookie保存が正常に動作することを確認
- **Input**: Cookie string
- **Expected**: Cookie được lưu vào config file

#### test_get_cookie
- **Mục đích**: Test cookie取得が正常に動作することを確認
- **Input**: Cookie đã được lưu
- **Expected**: Cookie string được trả về

#### test_get_download_folder
- **Mục đích**: Test download folder取得が正常に動作することを確認
- **Input**: Config file với download_folder setting
- **Expected**: Download folder path được trả về

#### test_get_setting
- **Mục đích**: Test setting取得が正常に動作することを確認
- **Input**: Setting key
- **Expected**: Setting value được trả về

#### test_config_caching
- **Mục đích**: Test config caching mechanismが正常に動作することを確認
- **Input**: Multiple get operations trong cache duration
- **Expected**: Cache được sử dụng trong cache duration

## Cách chạy Tests / テストの実行方法

### Chạy tất cả tests
```bash
python tests/run_all_tests.py
```

### Chạy từng test module
```bash
python -m unittest tests.test_video_downloader -v
python -m unittest tests.test_download_service -v
python -m unittest tests.test_cookie_manager -v
```

### Chạy từng test case
```bash
python -m unittest tests.test_video_downloader.TestVideoDownloader.test_normalize_url_valid_douyin_url -v
```

## Logging / ロギング

Tất cả test cases đều có logging đầy đủ theo System Instruction:
- Format: `[timestamp] [LEVEL] [Function] Message`
- Log levels: INFO, DEBUG, WARNING, ERROR
- Log files được lưu trong `logs/tests/`
- Mỗi test run tạo một log file mới với timestamp

## Requirements / 要件

Test cases yêu cầu:
- Python 3.7+
- unittest (built-in)
- unittest.mock (built-in)
- Các dependencies của dự án (requests, opencv-python, etc.)

## Notes / 注意事項

- Test cases sử dụng mock objects để tránh actual network calls
- Temporary directories được tự động cleanup sau mỗi test
- Test cases không thay đổi code gốc
- Tất cả test cases đều có detailed comments và logging

