# KẾ HOẠCH REFACTORING THEO SYSTEM INSTRUCTION

## Mục tiêu
- Đảm bảo code tuân thủ 100% System Instruction
- Logging đầy đủ theo format: [timestamp] [LEVEL] [Function] Message
- Code sạch, có comment đầy đủ bằng tiếng Việt
- Module rõ ràng, dễ mở rộng
- Không giản lược chức năng

## Các bước thực hiện

### ✅ Bước 1: Tạo Log Helper Utility
- [x] Tạo `utils/log_helper.py` với các hàm:
  - `write_log()` - Ghi log theo System Instruction format
  - `log_function_call()` - Decorator tự động log function
  - `log_api_call()` - Log API calls
  - `log_function_start()` / `log_function_end()` - Log bắt đầu/kết thúc

### ✅ Bước 2: Refactor main.py
- [x] Sử dụng `write_log()` thay vì `logger.info()` trực tiếp
- [x] Thêm docstring đầy đủ
- [x] Cải thiện error handling với `exc_info=True`
- [x] Thêm comment giải thích từng bước

### 🔄 Bước 3: Refactor Models
- [ ] `models/cookie_manager.py`
  - Sử dụng `write_log()` cho tất cả log
  - Thêm docstring cho tất cả methods
  - Đảm bảo tất cả exceptions có `exc_info=True`

### 🔄 Bước 4: Refactor Controllers
- [ ] `controllers/cookie_controller.py`
- [ ] `controllers/download_controller.py`
  - Sử dụng `write_log()` cho tất cả log
  - Thêm docstring đầy đủ
  - Đảm bảo tất cả exceptions có `exc_info=True`

### 🔄 Bước 5: Refactor Services
- [ ] `services/download_service.py`
- [ ] `services/video_downloader.py`
  - Sử dụng `write_log()` cho tất cả log
  - Thêm docstring đầy đủ
  - Đảm bảo tất cả API calls có log đầy đủ
  - Đảm bảo tất cả exceptions có `exc_info=True`

### 🔄 Bước 6: Refactor UI
- [ ] `ui/main_window.py`
  - Sử dụng `write_log()` cho tất cả log
  - Thêm docstring cho các methods quan trọng
  - Đảm bảo tất cả exceptions có `exc_info=True`

### 🔄 Bước 7: Kiểm tra và tối ưu
- [ ] Chạy linter để kiểm tra errors
- [ ] Kiểm tra tất cả imports
- [ ] Đảm bảo không có code bị bỏ sót
- [ ] Test các chức năng chính

## Tiêu chí đánh giá

### Logging
- ✅ Tất cả functions có log bắt đầu và kết thúc
- ✅ Tất cả API calls có log request + status code + error
- ✅ Tất cả exceptions có `exc_info=True`
- ✅ Format log: [timestamp] [LEVEL] [Function] Message

### Code Quality
- ✅ Tất cả functions có docstring bằng tiếng Việt
- ✅ Tất cả parameters và return values được giải thích
- ✅ Tất cả exceptions được ghi rõ
- ✅ Code có comment giải thích logic phức tạp

### Module Structure
- ✅ Mỗi module có trách nhiệm rõ ràng
- ✅ Dễ mở rộng (không hardcode, có config)
- ✅ Dễ test (functions độc lập)

## Lưu ý
- Không giản lược chức năng hiện có
- Giữ nguyên tất cả features
- Chỉ cải thiện code quality và logging


