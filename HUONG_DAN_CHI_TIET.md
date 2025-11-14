# Hướng dẫn chi tiết cài đặt

## Vấn đề: pip không thể cài đặt

Nếu gặp lỗi khi cài đặt pip, hãy làm theo các bước sau:

### Bước 1: Kiểm tra Python

Mở Command Prompt và chạy:
```bash
python --version
```

Nếu hiển thị phiên bản Python (ví dụ: Python 3.11.0) thì Python đã được cài đặt.

### Bước 2: Cài đặt pip với quyền Administrator

1. **Right-click** vào file `cai_dat_pip_admin.bat`
2. Chọn **"Run as administrator"**
3. Làm theo hướng dẫn trên màn hình

### Bước 3: Hoặc cài đặt thủ công

Mở Command Prompt **với quyền Administrator** (Right-click → Run as administrator) và chạy:

```bash
cd C:\work\git\videoDowloadApp
python -m ensurepip --upgrade
```

Hoặc:

```bash
python get-pip.py
```

### Bước 4: Kiểm tra pip

Sau khi cài đặt, kiểm tra:
```bash
python -m pip --version
```

Nếu hiển thị phiên bản pip thì đã thành công!

### Bước 5: Cài đặt requests

```bash
python -m pip install requests
```

## Nếu vẫn không được

### Giải pháp cuối cùng: Cài đặt lại Python

1. Gỡ Python cũ (nếu có):
   - Control Panel → Programs → Uninstall a program
   - Tìm Python và gỡ cài đặt

2. Tải Python mới từ: https://www.python.org/downloads/

3. Khi cài đặt, **QUAN TRỌNG**:
   - ✅ Tích chọn **"Add Python to PATH"** (ở đầu cửa sổ)
   - ✅ Tích chọn **"pip"** (thường được chọn mặc định)
   - ✅ Tích chọn **"tcl/tk and IDLE"** (cho Tkinter GUI)

4. Cài đặt và **khởi động lại máy tính**

5. Sau khi khởi động lại, mở Command Prompt mới và kiểm tra:
   ```bash
   python --version
   python -m pip --version
   ```

## Sau khi cài đặt thành công

Chạy ứng dụng bằng:
- `run.bat` hoặc
- `run_simple.bat`


