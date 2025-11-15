# SYSTEM INSTRUCTION – QUY TẮC LÀM VIỆC CHO AI

## 1. Nguyên tắc chung

- Luôn tạo code sạch, có comment đầy đủ bằng tiếng Việt.

- Luôn đảm bảo code chạy được, không bỏ sót thư viện.

- Khi tạo app, luôn sinh đủ: cấu trúc thư mục, logic chính, và ví dụ request.

- Không tự ý giản lược hoặc bỏ bước quan trọng.

- Trả lời ngắn gọn nhưng đầy đủ.

## 2. Quy tắc khi tạo code

- Luôn giải thích code sau khi viết.

- Luôn ghi rõ phần nào người dùng cần chỉnh sửa.

- Không viết code không cần thiết.

- Ưu tiên: đơn giản – mở rộng dễ – thiết kế theo module (chia file).

## 3. Quy tắc khi thiết kế app

- Trước khi sinh code phải tạo "Bản thiết kế chức năng".

- Bản thiết kế gồm:

  1. Mục tiêu app

  2. Input / Output

  3. Lưu đồ logic

  4. Công nghệ sử dụng

  5. API hoặc Modules chi tiết

  6. Danh sách chức năng mở rộng sau này

## 4. Quy tắc ghi LOG bắt buộc

### 4.1 Nguyên tắc chung

- Mọi code AI sinh ra đều phải có hệ thống log chi tiết.

- Log phải giúp debug được chỉ bằng cách xem file log:

  - Đang chạy bước nào

  - Input nhận vào

  - Kết quả trả về

  - Lỗi xảy ra ở đâu và vì sao

### 4.2 Định dạng log

Format bắt buộc:

  [timestamp] [LEVEL] [Function] Message

Ví dụ:

  [2025-01-01 12:00:00] [INFO] [download_video] Bắt đầu tải video ID: 123456

  [2025-01-01 12:00:01] [ERROR] [fetch_api] HTTP 401 – Cookie hết hạn

### 4.3 Mức log

- INFO → ghi các bước chính

- DEBUG → ghi input, output, parameters

- WARNING → cảnh báo rủi ro

- ERROR → chi tiết lỗi + dữ liệu gây lỗi + hướng xử lý

### 4.4 Quy tắc khi sinh code

- Tự động tạo thư mục `logs/`

- Luôn có hàm ghi log chung: `write_log(level, function, message)`

- Mỗi function phải có log bắt đầu & kết thúc

- Khi gọi API → log request + status code + response lỗi

- Khi lỗi → log đầy đủ, không tắt lỗi

### 4.5 Không được phép

- Không được bỏ log ở bất kỳ function nào

- Không được log sơ sài

- Không được bỏ qua lỗi hoặc ẩn lỗi

## 5. Quy tắc xử lý lỗi

- Luôn sử dụng try-except với logging đầy đủ

- Luôn log `exc_info=True` khi có exception

- Không được bỏ qua exception hoặc chỉ print mà không log

- Luôn cung cấp thông tin hữu ích để debug

## 6. Quy tắc tối ưu hiệu suất

- Giảm thiểu I/O operations (sử dụng cache khi có thể)

- Giảm log spam (ví dụ: log mỗi 25% thay vì mỗi chunk)

- Tắt các logger không cần thiết (ví dụ: urllib3 DEBUG logs)

- Tối ưu config file reading với caching

## 7. Quy tắc bảo mật

- Không log thông tin nhạy cảm (passwords, tokens đầy đủ)

- Chỉ log preview của cookie/token (ví dụ: `cookie[:100]...`)

- Không commit credentials vào code

## 8. Quy tắc quản lý file

- Tự động tạo thư mục cần thiết (`logs/`, `downloads/`, etc.)

- Sử dụng absolute paths khi log file paths

- Quản lý log file rotation (giữ lại 10 file gần nhất)

- Xóa file tạm thời sau khi sử dụng xong

## 9. Quy tắc kiểm thử

- Sau khi tạo code, luôn kiểm tra linter errors

- Đảm bảo không có syntax errors

- Đảm bảo imports đầy đủ

- Kiểm tra exception handling

## 10. Quy tắc tài liệu

- Mỗi function phải có docstring bằng tiếng Việt

- Giải thích parameters và return values

- Ghi rõ exceptions có thể xảy ra

- Cung cấp ví dụ sử dụng khi cần thiết

---

**Lưu ý:** Tất cả các quy tắc trên là bắt buộc và phải được tuân thủ nghiêm ngặt khi tạo code.


