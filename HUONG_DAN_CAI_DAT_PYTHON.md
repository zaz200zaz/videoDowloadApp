# Hướng dẫn cài đặt Python

Nếu bạn gặp lỗi "Python chưa được cài đặt", vui lòng làm theo các bước sau:

## Cách 1: Cài đặt Python từ trang chính thức (Khuyến nghị)

### Bước 1: Tải Python
1. Truy cập: https://www.python.org/downloads/
2. Tải phiên bản Python 3.7 trở lên (khuyến nghị Python 3.10 hoặc 3.11)

### Bước 2: Cài đặt Python
1. Chạy file installer đã tải về
2. **QUAN TRỌNG**: Tích chọn **"Add Python to PATH"** ở đầu cửa sổ cài đặt
3. Click "Install Now"
4. Đợi quá trình cài đặt hoàn tất

### Bước 3: Kiểm tra
1. Mở Command Prompt (cmd) hoặc PowerShell
2. Gõ lệnh: `python --version`
3. Nếu hiển thị phiên bản Python (ví dụ: Python 3.11.0) thì đã thành công

## Cách 2: Cài đặt Python từ Microsoft Store

1. Mở Microsoft Store
2. Tìm kiếm "Python"
3. Chọn "Python 3.11" hoặc phiên bản mới nhất
4. Click "Get" hoặc "Install"
5. Sau khi cài đặt xong, Python sẽ tự động được thêm vào PATH

## Cách 3: Thêm Python vào PATH thủ công (Nếu đã cài đặt nhưng không chạy được)

1. Tìm vị trí cài đặt Python (thường là):
   - `C:\Program Files\Python3XX\`
   - `C:\Users\[Tên người dùng]\AppData\Local\Programs\Python\Python3XX\`

2. Mở System Properties:
   - Nhấn `Win + R`
   - Gõ `sysdm.cpl` và Enter
   - Vào tab "Advanced"
   - Click "Environment Variables"

3. Thêm Python vào PATH:
   - Trong "System variables", tìm biến "Path"
   - Click "Edit"
   - Click "New"
   - Thêm đường dẫn đến thư mục Python (ví dụ: `C:\Program Files\Python311`)
   - Thêm đường dẫn đến Scripts (ví dụ: `C:\Program Files\Python311\Scripts`)
   - Click "OK" để lưu

4. Khởi động lại Command Prompt và thử lại

## Kiểm tra sau khi cài đặt

Sau khi cài đặt xong, mở Command Prompt mới và chạy:

```bash
python --version
```

Nếu hiển thị phiên bản Python, bạn có thể chạy lại file `run.bat`!

## Vẫn không được?

Nếu vẫn gặp vấn đề, vui lòng:
1. Khởi động lại máy tính
2. Mở Command Prompt mới (không dùng cửa sổ cũ)
3. Thử chạy lại `run.bat`


