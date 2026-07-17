# Prompt — Bảng giá + Đăng ký gói

> Copy khối PROMPT, dán cho Claude (Artifact).

---

**PROMPT**

Bạn là senior product designer + frontend engineer. Dựng **prototype UI click được** (HTML/React tự chứa, 1 file, **không gọi mạng thật** — giả lập bằng loading + placeholder).

**SẢN PHẨM:** "Story Studio" — web app tạo truyện tranh thiếu nhi có giọng đọc bằng AI. Kinh doanh **subscription + credit**: **1 credit = 1 lần gen ảnh (kể cả gen lại)**. Người dùng không rành kỹ thuật → giải thích credit thật đơn giản.

**DESIGN SYSTEM:** vui tươi thân thiện trẻ em, gọn gàng chuyên nghiệp. Màu chính **cam #EE4D2D**, phụ **xanh #2D7FEE**; rounded-2xl, bóng nhẹ, font sans. **Light & dark mode + responsive**. Trạng thái: hover, selected, disabled, loading.

**MÀN HÌNH — Trang Pricing:**
- Tiêu đề + phụ đề ngắn giải thích "credit là gì" (1 credit = 1 ảnh).
- **Toggle Tháng / Năm** (năm giảm ~2 tháng, badge "-17%").
- **4 cột gói**:
  | Gói | Giá tháng | Credit/tháng | Điểm nhấn |
  |---|---|---|---|
  | **Free** | $0 | 10 | Dùng thử, có watermark |
  | **Creator** ⭐ | $9.99 | 100 | *Phổ biến nhất* — xuất bản không watermark |
  | **Pro** | $24.99 | 300 | Thương mại, độ phân giải cao |
  | **Studio** | $49.99 | 700 | Nhiều thành viên, ưu tiên gen |
  Mỗi cột: giá lớn, số credit, danh sách tính năng (dấu ✓), CTA ("Bắt đầu miễn phí" / "Chọn gói" / "Gói hiện tại" nếu đang dùng). Cột Creator nổi bật (viền cam, badge).
- **Bảng so sánh tính năng** chi tiết bên dưới (số truyện, watermark, xuất bản, độ phân giải, thương mại, hỗ trợ…).
- **FAQ** (accordion): "Credit là gì?", "Hết credit thì sao?", "Credit có cộng dồn không?", "Huỷ/hoàn tiền?", "Gen lại có tốn credit không?".
- Khi bấm chọn gói → mở **modal xác nhận** (tóm tắt gói + giá + nút "Tiếp tục thanh toán" — chỉ giả lập, không cần form thẻ ở đây).

**EDGE CASES phải có UI:**
- Đang ở gói nào thì cột đó hiện "Gói hiện tại" (disabled CTA).
- Hạ gói → cảnh báo mất tính năng/credit.
- Nhấn chọn Free khi đang trả phí → cảnh báo huỷ gói trả phí.

**ĐẦU RA:** một file chạy được, mọi nút phản hồi thị giác, không backend.
