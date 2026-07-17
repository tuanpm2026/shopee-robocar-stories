# Prompt — Dashboard / Quản lý truyện

> Copy khối PROMPT, dán cho Claude (Artifact).

---

**PROMPT**

Bạn là senior product designer + frontend engineer. Dựng **prototype UI click được** (HTML/React tự chứa, 1 file, **không gọi mạng thật** — thao tác giả lập bằng loading + placeholder SVG/gradient).

**SẢN PHẨM:** "Story Studio" — web app tạo truyện tranh thiếu nhi có giọng đọc bằng AI (bé Shopee + xe cứu hộ Robocar Poli). Người dùng là phụ huynh/giáo viên **không rành kỹ thuật**. Kinh doanh: subscription + credit (1 credit = 1 lần gen ảnh).

**DESIGN SYSTEM:** vui tươi thân thiện trẻ em, gọn gàng chuyên nghiệp. Màu chính **cam #EE4D2D**, phụ **xanh #2D7FEE**; bo góc rounded-2xl, bóng nhẹ, font sans. **Light & dark mode + responsive** (desktop/tablet/mobile). Mọi trạng thái: loading (skeleton), empty, error, success, disabled.

**MÀN HÌNH — Dashboard (màn hình chính sau đăng nhập):**

- **Sidebar trái** (mobile → hamburger/bottom nav): *Truyện của tôi* (active) · *Thư viện nhân vật* · *Credit & Gói* · *Cài đặt*. Góc trên phải luôn hiện **avatar + số credit còn lại (37)** + toggle light/dark.
- **Thanh công cụ**: tiêu đề "Truyện của tôi", ô tìm kiếm, lọc theo trạng thái (Tất cả / Nháp / Đang làm / Đã xuất bản), sắp xếp (mới sửa / tên / ngày tạo), nút lớn **"+ Tạo truyện mới"**.
- **Lưới truyện** (card): thumbnail cover, tên, số scene, badge trạng thái (Nháp xám / Đang làm cam / Đã xuất bản xanh), ngày sửa. Mỗi card có menu `⋯`: Mở · Nhân bản · Đổi tên · Xuất bản · Xoá. Hover nổi nhẹ.
- **Modal "Tạo truyện mới"**: nhập tên + chọn (Bắt đầu trống / Từ mẫu) → tạo → điều hướng giả tới editor.
- **Modal đổi tên** và **xác nhận xoá** (gõ/nhấn xác nhận).

**EDGE CASES phải có UI:**
- **Empty state** (chưa có truyện): minh hoạ thân thiện + nút "Tạo truyện đầu tiên".
- Kết quả tìm kiếm rỗng → thông báo "không tìm thấy".
- Loading danh sách → skeleton cards.
- Xoá truyện → xác nhận, toast "Đã xoá" + hoàn tác (undo).

**SEED:** 6–8 truyện mẫu quanh chủ đề Shopee (vd "Shopee và chiếc xe ăn trộm Poacher", "Shopee học sang đường", "Shopee và buổi cắm trại an toàn"…) với trạng thái + số scene khác nhau. Cover dùng gradient/SVG placeholder. Gói hiện tại Creator, 37 credit.

**ĐẦU RA:** một file chạy được, mọi nút phản hồi thị giác, không backend.
