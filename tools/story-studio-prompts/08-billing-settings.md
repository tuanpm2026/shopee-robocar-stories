# Prompt — Credit & Thanh toán (Billing) + Cài đặt tài khoản

> Copy khối PROMPT, dán cho Claude (Artifact).

---

**PROMPT**

Bạn là senior product designer + frontend engineer. Dựng **prototype UI click được** (HTML/React tự chứa, 1 file, **không gọi mạng thật** — giả lập bằng loading + placeholder). Điều hướng bằng tab/sidebar nội bộ.

**SẢN PHẨM:** "Story Studio" — web app tạo truyện tranh thiếu nhi có giọng đọc bằng AI. Kinh doanh subscription + credit (**1 credit = 1 lần gen ảnh**). Người dùng không rành kỹ thuật.

**DESIGN SYSTEM:** vui tươi thân thiện trẻ em, gọn gàng chuyên nghiệp. Màu chính **cam #EE4D2D**, phụ **xanh #2D7FEE**; rounded-2xl, bóng nhẹ, font sans. **Light & dark mode + responsive**. Trạng thái: loading (skeleton), empty, error, success, disabled.

**CÁC MÀN HÌNH CẦN DỰNG (chuyển tab được):**

1. **Credit**: số dư lớn (**37 credit**), thanh tiến độ chu kỳ ("37/100 còn lại, làm mới sau 12 ngày"), nút **"Mua thêm"**. Bảng **lịch sử tiêu credit** (thời gian · hành động [Gen ảnh/Gen lại/Gen nhân vật] · scene/truyện · −credit). Lọc + phân trang.
2. **Modal Top-up**: các gói lẻ ($5/40 credit · $10/90 · $20/200), hiện đơn giá mỗi credit, chọn → xác nhận → **modal thanh toán**.
3. **Subscription**: gói hiện tại (Creator $9.99/tháng), ngày gia hạn, nút **Nâng / Hạ / Huỷ** gói, phương thức thanh toán (thẻ ****4242), danh sách **hoá đơn** tải PDF (giả lập).
4. **Modal thanh toán (giả lập Stripe)**: form thẻ (số thẻ, hết hạn, CVC), nút Thanh toán → loading → thành công / thất bại.
5. **Cài đặt tài khoản**: Hồ sơ (tên, avatar upload, email), đổi mật khẩu, ngôn ngữ, **giao diện (Light/Dark/Auto)**, thông báo (email/app), **Vùng nguy hiểm**: xoá tài khoản (xác nhận gõ tên).

**EDGE CASES phải có UI:**
- **Thanh toán thất bại / thẻ bị từ chối** → thông báo rõ, thử thẻ khác, không nâng gói/không cộng credit.
- **Huỷ gói** → cảnh báo giữ đến hết kỳ, sau đó khoá gen mới, truyện cũ vẫn xem được; xác nhận 2 bước.
- **Credit sắp hết hạn cuối chu kỳ** → banner cảnh báo, nêu rõ số credit sẽ mất (breakage).
- Empty state lịch sử credit / hoá đơn.
- Xoá tài khoản → cảnh báo mạnh, gõ đúng tên mới cho xoá.

**SEED:** gói Creator, 37/100 credit, lịch sử ~8 dòng, 3 hoá đơn, thẻ ****4242.

**ĐẦU RA:** một file chạy được, mọi nút phản hồi thị giác, không backend.
