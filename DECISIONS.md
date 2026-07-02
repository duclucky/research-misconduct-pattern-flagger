# Decisions

- **Package manager**: *Chưa quyết định*
- **Runtime**: Python
- **Test command**: Dự kiến dùng `pytest` với plugin `gltest` (*Chưa xác minh lệnh chi tiết*)
- **Build command**: *Chưa quyết định*

**Các quyết định không được tự đổi:**
- Không tự ý thay đổi công cụ quản lý package khi đã chốt.
- Bắt buộc tuân thủ quy tắc file thuần ASCII cho contract.

## Bài học & Giới hạn cốt lõi của GenVM (Ghi nhớ vĩnh viễn)
1. **Không được instantiate `DynArray` bằng tay**: GenVM (v0.2.16) sẽ quăng lỗi `TypeError` nếu người dùng cố khởi tạo `self.storage = DynArray[str]()`. Luôn khai báo kiểu ở class-level và để hệ thống tự handle lazy initialization (chỉ dùng `append`).
2. **Crash khi dùng cấu trúc lồng (Nested State)**: Máy ảo GenVM hiện tại sẽ ném `KeyError` và crash nếu bạn cố lưu một mảng động bên trong một map, ví dụ: `TreeMap[str, DynArray[str]]`. Hệ thống giải mã (serialization) của máy ảo chưa hoàn thiện.
3. **Giải pháp bắt buộc (State Flattening)**: Khi cần lưu trữ mảng bên trong một Key-Value Store, **TUYỆT ĐỐI KHÔNG DÙNG cấu trúc lồng**. Thay vào đó, dùng `TreeMap[str, str]` và mã hóa mảng thành JSON string bằng `json.dumps()` trước khi lưu, sau đó parse lại bằng `json.loads()` khi cần đọc. Đây là cách an toàn và dứt điểm nhất để lách lỗi nội bộ của GenVM.
