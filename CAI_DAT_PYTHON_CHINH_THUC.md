# Hướng dẫn cài đặt Python chính thức

## Vấn đề hiện tại

Hiện tại hệ thống đang sử dụng Windows Store Python, nhưng nó không hoạt động đúng cách.
Cần cài đặt Python chính thức từ python.org.

## Các bước cài đặt

### Bước 1: Tải Python

1. Truy cập: **https://www.python.org/downloads/**
2. Click nút **"Download Python 3.x.x"** (phiên bản mới nhất, ví dụ 3.11 hoặc 3.12)

### Bước 2: Cài đặt Python

1. Chạy file installer đã tải về
2. **QUAN TRỌNG**: Ở đầu cửa sổ cài đặt, tích chọn:
   - ✅ **"Add Python to PATH"** (Rất quan trọng!)
   - ✅ **"Install launcher for all users"** (Tùy chọn)

3. Click **"Install Now"** hoặc **"Customize installation"**

4. Nếu chọn "Customize installation":
   - ✅ Tích tất cả các tùy chọn (Optional Features)
   - ✅ Trong "Advanced Options":
     - ✅ **"Add Python to environment variables"**
     - ✅ **"Install for all users"** (nếu có quyền)
     - ✅ **"Precompile standard library"**

5. Đợi quá trình cài đặt hoàn tất

### Bước 3: Khởi động lại máy tính

Sau khi cài đặt xong, **khởi động lại máy tính** để đảm bảo PATH được cập nhật.

### Bước 4: Kiểm tra

Sau khi khởi động lại, mở **Command Prompt mới** và chạy:

```bash
python --version
```

Nếu hiển thị phiên bản Python (ví dụ: Python 3.11.5) thì đã thành công!

Kiểm tra pip:
```bash
python -m pip --version
```

### Bước 5: Cài đặt dependencies

```bash
cd C:\work\git\videoDowloadApp
python -m pip install requests
```

### Bước 6: Chạy ứng dụng

```bash
python main.py
```

Hoặc chạy `run.bat`

## Lưu ý

- **KHÔNG** sử dụng Windows Store để cài đặt Python cho mục đích phát triển
- Luôn cài đặt từ python.org để có đầy đủ tính năng
- Nhớ tích "Add Python to PATH" khi cài đặt


