# BẢN THIẾT KẾ ĐƠN GIẢN — APP TẢI VIDEO DOUYIN BẰNG COOKIE



## 1. Mục tiêu



Tạo ứng dụng PC đơn giản cho phép người dùng nhập **cookie Douyin** và **danh sách link video**, sau đó tải hàng loạt video về máy.



Ứng dụng phải dễ mở rộng để sau này thêm các chức năng mới như tải ảnh, tải bằng UID, tải playlist, hoặc auto crawl.



---



## 2. Tính năng chính (phiên bản đầu tiên — bản đơn giản)



### ✔ 1. Nhập cookie Douyin



* Người dùng paste cookie thủ công vào ô nhập.

* App lưu cookie vào file `config.json` để không phải nhập lại.



### ✔ 2. Nhập danh sách link video



* Người dùng có thể:



  * Dán nhiều link (mỗi dòng một link), hoặc

  * Import file `.txt` chứa danh sách link.



### ✔ 3. Tải video hàng loạt



* App gửi request có gắn cookie → lấy link video thực.

* Tải từng video về folder đã chọn.

* Tự động đặt tên file theo:



  * ID video

  * hoặc thời gian tải



### ✔ 4. Hiển thị tiến trình tải



* Hiển thị danh sách video đang tải, thành công, thất bại.

* Cho phép dừng / tạm dừng hàng đợi.



---



## 3. Cấu trúc ứng dụng



```
/
/// main.py — điểm chạy chính
/// downloader.py — xử lý tải video
/// cookie_manager.py — lưu & đọc cookie
/// ui/ — giao diện (Tkinter hoặc Electron)
/// config.json — lưu cookie + settings
```



---



## 4. Quy trình xử lý



### Bước 1 — Người dùng dán cookie



→ App kiểm tra định dạng cookie

→ Lưu cookie vào `config.json`



### Bước 2 — Người dùng nhập các link video



→ App chuẩn hóa link (loại bỏ param thừa)



### Bước 3 — App xử lý từng link



1. Gửi request có cookie để lấy thông tin video.

2. Lấy link `.mp4` thực.

3. Tải file về và ghi vào thư mục.



### Bước 4 — Hoàn tất & báo trạng thái



→ Hiển thị video tải thành công / thất bại.

→ Gợi ý xem folder.



---



## 5. Giao diện (UI đơn giản)



**Phần 1 — Cookie:**



* Ô nhập cookie

* Nút "Lưu Cookie"



**Phần 2 — Link video:**



* Ô input nhiều dòng

* Nút Import file `.txt`



**Phần 3 — Tải:**



* Nút "Start Download"

* Progress bar

* Danh sách trạng thái



---



## 6. Khả năng mở rộng trong tương lai



Thiết kế để dễ thêm tính năng:



* Tải video theo UID tài khoản

* Tải ảnh từ bài post

* Auto crawl toàn bộ profile

* Tự động vượt anti-bot (nếu cần)

* Thêm login QR thay vì cookie

* Xuất metadata video



---



## 7. Yêu cầu dành cho AI khi tạo app



* Viết code rõ ràng, có comment đầy đủ

* Module hóa: mỗi chức năng một file

* Không hardcode cookie → phải lấy từ config

* UI đơn giản, dễ sửa

* Log đầy đủ: success, fail, error



---



## 8. Output mong muốn



Sau khi cho AI tạo app, cần output:



* Code đầy đủ (Python hoặc NodeJS)

* File chạy được `.exe` (nếu dùng PyInstaller / Node GUI)

* File `config.json`

* Hướng dẫn build lại app


