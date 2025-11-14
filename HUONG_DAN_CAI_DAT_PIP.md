# Hướng dẫn cài đặt pip

Nếu pip chưa được cài đặt, bạn có thể làm theo các cách sau:

## Cách 1: Cài đặt lại Python (Khuyến nghị)

1. Truy cập: https://www.python.org/downloads/
2. Tải Python mới nhất
3. Khi cài đặt, **QUAN TRỌNG**:
   - ✅ Tích chọn **"Add Python to PATH"**
   - ✅ Tích chọn **"pip"** (thường được chọn mặc định)
4. Cài đặt và khởi động lại máy tính

## Cách 2: Sử dụng get-pip.py

1. Tải file `get-pip.py` từ: https://bootstrap.pypa.io/get-pip.py
2. Lưu file vào thư mục dự án
3. Mở Command Prompt và chạy:
   ```bash
   python get-pip.py
   ```

Hoặc chạy file `cai_dat_pip.bat` đã được tạo sẵn.

## Cách 3: Sử dụng ensurepip (nếu Python >= 3.4)

Mở Command Prompt và chạy:
```bash
python -m ensurepip --upgrade
```

## Kiểm tra pip đã được cài đặt

Sau khi cài đặt, kiểm tra bằng lệnh:
```bash
python -m pip --version
```

Nếu hiển thị phiên bản pip thì đã thành công!

## Sau khi cài đặt pip

Chạy lệnh sau để cài đặt dependencies:
```bash
python -m pip install requests
```

Hoặc chạy file `cai_dat_dependencies.bat`


