# Prompt — Build · Xuất bản · Trang xem công khai

> Copy khối PROMPT, dán cho Claude (Artifact).

---

**PROMPT**

Bạn là senior product designer + frontend engineer. Dựng **prototype UI click được** (HTML/React tự chứa, 1 file, **không gọi mạng thật** — giả lập bằng loading + placeholder SVG/gradient).

**SẢN PHẨM:** "Story Studio" — tạo truyện tranh thiếu nhi có giọng đọc bằng AI (bé Shopee + xe cứu hộ Robocar Poli). Truyện gồm nhiều scene, mỗi scene có ảnh dọc A5 (5:7) + lời kể tiếng Việt đọc thành tiếng.

**DESIGN SYSTEM:** vui tươi thân thiện trẻ em, gọn gàng chuyên nghiệp. Màu chính **cam #EE4D2D**, phụ **xanh #2D7FEE**; rounded-2xl, font sans. **Light & dark mode + responsive**. Trạng thái: loading, empty, error, success.

**CÁC MÀN HÌNH CẦN DỰNG:**
1. **Modal "Chuẩn bị xuất bản" (checklist)**: liệt kê từng scene với ✓ (đã có ảnh + audio) hoặc ⚠ (thiếu). Cảnh báo scene còn trống. Nút **[▶ Build]** (disabled nếu thiếu, hoặc cho "Xuất bản một phần" kèm cảnh báo).
2. **Build đang chạy**: progress bar theo bước (Ghép ảnh → Tạo giọng đọc → Đóng gói) + có thể huỷ.
3. **Preview slideshow**: khung xem lật trang, tự đọc lời kể (thanh play giả lập), nút next/prev, bật/tắt tiếng, toàn màn hình.
4. **Xuất bản xong**: hiện **link chia sẻ công khai** (copy được) + **mã QR** + đoạn nhúng (embed) + nút chia sẻ mạng xã hội. Toast "Đã xuất bản".
5. **Trang xem công khai (Viewer)** — bố cục riêng, không có sidebar app: full-screen, ảnh A5 giữa màn, tự lật + tự đọc, nút play/pause, tắt/mở tiếng, next/prev, chỉ số trang (3/12), nút toàn màn hình. Đẹp trên cả mobile.

**EDGE CASES phải có UI:**
- Build khi còn scene trống → cảnh báo, cho chọn chặn hoặc publish một phần.
- Build lỗi giữa chừng → thông báo bước lỗi + nút thử lại, không mất truyện.
- Viewer khi truyện chưa publish / link sai → trang "không tìm thấy" thân thiện.
- Ảnh/audio đang tải trong viewer → skeleton, không vỡ layout.

**SEED:** truyện "Shopee và chiếc xe ăn trộm Poacher", 12 scene (ảnh gradient/SVG placeholder, lời kể tiếng Việt ngắn cho vài scene đầu). Link mẫu dạng `storystudio.app/s/shopee-poacher`.

**ĐẦU RA:** một file chạy được, mọi nút phản hồi thị giác, không backend.
