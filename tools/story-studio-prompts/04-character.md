# Prompt — Thư viện nhân vật + Tạo/chỉnh nhân vật

> Copy khối PROMPT, dán cho Claude (Artifact).

---

**PROMPT**

Bạn là senior product designer + frontend engineer. Dựng **prototype UI click được** (HTML/React tự chứa, 1 file, **không gọi mạng thật** — giả lập bằng loading + placeholder SVG/gradient).

**SẢN PHẨM:** "Story Studio" — tạo truyện tranh thiếu nhi có giọng đọc bằng AI. Nhân vật phải **nhất quán xuyên suốt các truyện**, nên có **thư viện nhân vật** dùng lại: mỗi nhân vật có ảnh reference, khi gen scene sẽ đính kèm ref. Kinh doanh: subscription + credit (1 credit = 1 lần gen ảnh); thao tác tốn tiền hiện **cost badge + xác nhận**.

**DESIGN SYSTEM:** vui tươi thân thiện trẻ em, gọn gàng chuyên nghiệp. Màu chính **cam #EE4D2D**, phụ **xanh #2D7FEE**; rounded-2xl, bóng nhẹ, font sans. **Light & dark mode + responsive**. Mọi trạng thái: loading, empty, error, success, disabled.

**MÀN HÌNH 1 — Thư viện nhân vật:**
- Lưới thẻ nhân vật: avatar, tên, badge vai trò (Chính / Phụ / Phản diện), số truyện đang dùng.
- Bộ nhân vật hệ thống đánh dấu **"Mẫu"** (chỉ đọc, cho phép "Nhân bản để sửa"): Shopee (bé trai ~3t, áo nâu "TOGETHER"), Jin (jumpsuit cam), Poli (xe cảnh sát xanh-trắng), Mark (xe utility cam mũ đỏ "M"), Bucky (pickup vàng mũ xanh "B"), Poacher (xe tải quân sự đỏ — phản diện), Mẹ, Bố.
- Nút **"+ Tạo nhân vật mới"**. Tìm kiếm + lọc theo vai trò.

**MÀN HÌNH 2 — Tạo/chỉnh nhân vật (mở dạng trang hoặc modal lớn):**
- Form: **Tên** · **Vai trò** (Chính/Phụ/Phản diện) · **Loại** (Người / Xe-robot) · **Mô tả ngoại hình** (textarea: tuổi, trang phục, màu sắc, đặc điểm).
- **Ảnh reference — 2 cách**:
  1. **Upload** ảnh có sẵn (kéo-thả, nhiều ảnh nhiều góc).
  2. **Gen bằng AI** từ mô tả → hiện **cost badge** ("~1 credit/ảnh"), gen **2–4 biến thể**, chọn 1 làm **ref chính**, giữ vài ảnh phụ.
- Preview **thẻ nhân vật** cập nhật real-time. Nút Lưu vào thư viện.

**EDGE CASES phải có UI:**
- Mô tả quá ngắn → cảnh báo "cần chi tiết hơn để gen nhất quán", chặn gen.
- Gen ảnh **fail** → **không trừ credit**, nút thử lại.
- **Upload sai định dạng / quá nặng / khuôn mặt không rõ** → validate, báo lỗi thân thiện.
- **Xoá nhân vật đang được N truyện dùng** → cảnh báo "N truyện đang dùng", nêu ảnh hưởng trước khi xoá.
- Hết credit khi gen ref → chặn, gợi ý mua thêm.
- Empty state thư viện (chỉ còn nhân vật mẫu).

**SEED:** thư viện gồm 8 nhân vật mẫu ở trên + 1–2 nhân vật do người dùng tạo. Số dư 37 credit, gói Creator. Ảnh dùng gradient/SVG placeholder.

**ĐẦU RA:** một file chạy được, mọi nút phản hồi thị giác, không backend.
