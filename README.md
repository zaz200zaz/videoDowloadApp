# Douyin Video Downloader

Ứng dụng PC đơn giản để tải video Douyin hàng loạt bằng cookie.

## Tính năng

- ✅ Nhập và lưu cookie Douyin
- ✅ Nhập danh sách link video (thủ công hoặc import từ file .txt)
- ✅ Tải video hàng loạt với cookie xác thực
- ✅ Hiển thị tiến trình tải và trạng thái từng video
- ✅ Tự động đặt tên file theo video ID hoặc timestamp

## Yêu cầu hệ thống

- Python 3.7 trở lên
- Windows / macOS / Linux

## Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
python main.py
```

## Hướng dẫn sử dụng

### Bước 1: Lấy Cookie Douyin

1. Mở trình duyệt và truy cập [douyin.com](https://www.douyin.com)
2. Đăng nhập tài khoản của bạn
3. Mở Developer Tools (F12)
4. Vào tab **Application** (hoặc **Storage**)
5. Tìm **Cookies** → chọn `https://www.douyin.com`
6. Copy toàn bộ cookie string (hoặc các cookie quan trọng như `sessionid`, `sid_guard`, `uid_tt`, `sid_tt`)

### Bước 2: Nhập Cookie vào App

1. Mở ứng dụng
2. Dán cookie vào ô "Nhập cookie Douyin"
3. Click nút **"Lưu Cookie"**

### Bước 3: Nhập danh sách Link Video

Có 2 cách:

**Cách 1: Dán trực tiếp**
- Dán các link video vào ô text (mỗi dòng một link)

**Cách 2: Import từ file**
- Click nút **"Import từ file .txt"**
- Chọn file .txt chứa danh sách link (mỗi dòng một link)

### Bước 4: Tải Video

1. (Tùy chọn) Click **"Chọn thư mục"** để chọn nơi lưu video
2. Click nút **"Bắt đầu tải"**
3. Theo dõi tiến trình trong phần "Trạng thái tải"
4. Video sẽ được lưu vào thư mục `./downloads` (hoặc thư mục bạn đã chọn)

## Cấu trúc thư mục

```
/
├── main.py                 # Điểm chạy chính
├── cookie_manager.py       # Quản lý cookie
├── downloader.py           # Xử lý tải video
├── ui/
│   └── main_window.py      # Giao diện chính
├── config.json             # File cấu hình
├── requirements.txt        # Dependencies
└── README.md              # Hướng dẫn này
```

## Build thành file .exe (Windows)

### Sử dụng PyInstaller

1. Cài đặt PyInstaller:
```bash
pip install pyinstaller
```

2. Build file .exe:
```bash
pyinstaller --onefile --windowed --name "DouyinDownloader" main.py
```

3. File .exe sẽ nằm trong thư mục `dist/`

### Tùy chọn build nâng cao

```bash
# Build với icon
pyinstaller --onefile --windowed --icon=icon.ico --name "DouyinDownloader" main.py

# Build không có console window
pyinstaller --onefile --noconsole --name "DouyinDownloader" main.py
```

## Lưu ý quan trọng

⚠️ **Cookie có thể hết hạn**: Cookie Douyin thường có thời hạn. Nếu gặp lỗi xác thực, vui lòng lấy cookie mới.

⚠️ **API có thể thay đổi**: Douyin có thể thay đổi API endpoint. Nếu app không hoạt động, có thể cần cập nhật code trong `downloader.py`.

⚠️ **Tốc độ tải**: Tốc độ tải phụ thuộc vào tốc độ mạng và server Douyin. Không nên tải quá nhiều video cùng lúc để tránh bị chặn.

## Khắc phục sự cố

### Lỗi "Không thể lấy thông tin video"
- Kiểm tra lại cookie có còn hợp lệ không
- Thử lấy cookie mới từ trình duyệt
- Kiểm tra link video có đúng định dạng không

### Lỗi "URL không hợp lệ"
- Đảm bảo link là link Douyin hợp lệ
- Kiểm tra link có đầy đủ không (ví dụ: `https://www.douyin.com/video/...`)

### Video tải về bị lỗi
- Kiểm tra dung lượng ổ cứng còn đủ không
- Kiểm tra quyền ghi file vào thư mục đã chọn
- Thử tải lại video đó

## Mở rộng trong tương lai

App được thiết kế để dễ mở rộng với các tính năng:
- Tải video theo UID tài khoản
- Tải ảnh từ bài post
- Auto crawl toàn bộ profile
- Tự động vượt anti-bot
- Login QR thay vì cookie
- Xuất metadata video

## License

MIT License

## Tác giả

Được tạo bởi AI Assistant dựa trên bản thiết kế.

