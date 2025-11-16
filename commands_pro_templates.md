# Commands_PRO.md

# TEMPLATE COMMANDS PRO – DÙNG VỚI SYSTEM INSTRUCTION PRO

Bộ template này tối ưu để sử dụng với System Instruction PRO. Bao gồm mọi tình huống: tạo code, thêm tính năng, sửa bug, refactor, đọc log, test case, tối ưu hiệu suất. Tất cả đảm bảo logging, comment, docstring, module hóa chuẩn.

---

## 1️⃣ Tạo code / thêm chức năng mới
```
Hãy tạo code mới cho chức năng [mô tả chức năng] theo đúng System Instruction PRO.
Yêu cầu:
- Module hóa riêng file [tên file nếu cần].
- Logging đầy đủ: bắt đầu, input, output, kết thúc, lỗi.
- Comment và docstring tiếng Việt.
- Giữ nguyên các module hiện có.
- Giải thích ngắn gọn (3–6 dòng) về cách hoạt động và nơi người dùng cần chỉnh sửa (token, cookie, config...).
- Nếu cần tạo thư mục mới, tuân thủ quy tắc quản lý file.
```

## 2️⃣ Sửa bug / fix lỗi
```
Hãy phân tích code và log trong dự án theo đúng System Instruction PRO.
Phát hiện tất cả bug hoặc lỗi tiềm ẩn.
- Liệt kê file và function liên quan
- Giải thích nguyên nhân lỗi
- Sửa code tương ứng, giữ logging, comment, docstring đầy đủ
- Không thay đổi logic chính
- Sau khi sửa, tóm tắt các thay đổi và lợi ích
```

## 3️⃣ Refactor / tái cấu trúc code
```
Hãy tái cấu trúc toàn bộ code/module này theo đúng System Instruction PRO.
Yêu cầu:
- Giảm trùng lặp, tăng readability và maintainability
- Logging và comment đầy đủ
- Module hóa rõ ràng
- Không làm thay đổi logic chính
- Giải thích ngắn gọn các thay đổi chính
```

## 4️⃣ Phát hiện bug từ log
```
Hãy đọc toàn bộ log trong dự án theo đúng System Instruction PRO.
- Phát hiện bug hoặc hành vi bất thường
- Liệt kê chi tiết lỗi + file + function + nguyên nhân
- Đề xuất cách sửa code
- Giữ logging và comment chuẩn
```

## 5️⃣ Phân tích toàn bộ app / workflow
```
Hãy phân tích toàn bộ dự án theo đúng System Instruction PRO.
- Đọc code và log
- Liệt kê luồng hoạt động, input/output từng function
- Phát hiện vấn đề tiềm ẩn hoặc chỗ cần cải tiến
- Đề xuất refactor, tối ưu hoặc mở rộng
- Giữ logging, comment, docstring chuẩn
```

## 6️⃣ Tối ưu hiệu suất / cải thiện performance
```
Hãy tối ưu hiệu suất dự án theo đúng System Instruction PRO.
- Phân tích bottleneck, memory usage, tốc độ xử lý
- Giữ logging và comment đầy đủ
- Ưu tiên async, caching, giảm log spam
- Giải thích các cải tiến đã thực hiện
```

## 7️⃣ Kiểm tra log / cải tiến log
```
Hãy đọc toàn bộ log trong dự án theo đúng System Instruction PRO.
- Phát hiện chỗ thiếu log, log không đủ chi tiết, format sai
- Đề xuất cải thiện logging
- Nếu cần, sửa code để bổ sung log đúng chuẩn
- Giải thích chi tiết các thay đổi
```

## 8️⃣ Tạo test case / kiểm thử tự động
```
Hãy đọc code và log dự án theo đúng System Instruction PRO.
- Tạo bộ test case cho tất cả chức năng quan trọng
- Logging và comment trong test case đầy đủ
- Không thay đổi logic gốc
- Giải thích cách test và kết quả kỳ vọng
```

## 9️⃣ Đọc log để mô phỏng / phân tích hoạt động app
```
Hãy đọc toàn bộ log trong dự án theo đúng System Instruction PRO.
- Tóm tắt toàn bộ hoạt động app
- Mô phỏng flow thực thi, input/output, function gọi
- Không cần kiểm tra lỗi
- Chuẩn hóa phân tích theo thứ tự thời gian
```

## 🔟 Prompt tổng hợp đa năng (Master Prompt)
```
Hãy đọc toàn bộ code và log dự án theo đúng System Instruction PRO.
- Nếu phát hiện lỗi, hãy sửa code tương ứng
- Nếu có yêu cầu thêm chức năng, hãy thêm module mới chuẩn System Instruction
- Tái cấu trúc code nếu cần để giảm trùng lặp, tăng maintainability
- Tối ưu hiệu suất nếu có bottleneck
- Giữ logging, comment, docstring đầy đủ
- Giải thích tất cả thay đổi, nơi cần chỉnh sửa và ví dụ sử dụng
```

---

# 🎯 Tips sử dụng
1. Khi muốn **sửa lỗi**, dùng template 2 hoặc Master Prompt.  
2. Khi muốn **thêm chức năng**, dùng template 1.  
3. Khi muốn **phân tích app / workflow / log**, dùng template 5 hoặc 9.  
4. Khi muốn **refactor / tối ưu**, dùng template 3 hoặc 6.  
5. Luôn thêm **“theo đúng System Instruction PRO”** để AI tuân thủ mọi quy tắc về logging, comment, docstring, module hóa, bảo mật.