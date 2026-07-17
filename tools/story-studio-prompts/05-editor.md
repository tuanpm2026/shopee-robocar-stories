# Prompt — Màn hình LÕI: Story Editor (scene-board) + Retry ảnh

> Copy toàn bộ khối PROMPT bên dưới, dán cho Claude (chế độ Artifact). Đây là màn hình quan trọng nhất — dựng nó trước.

---

**PROMPT**

Bạn là senior product designer + frontend engineer. Dựng **prototype UI click được** (HTML/React tự chứa, 1 file chạy trong trình duyệt, **không gọi mạng thật** — mọi thao tác AI giả lập bằng loading + ảnh placeholder vẽ bằng gradient/SVG).

**SẢN PHẨM:** "Story Studio" — web app tạo truyện tranh thiếu nhi có giọng đọc bằng AI (bé Shopee + đội xe cứu hộ Robocar Poli). Truyện gồm nhiều *scene*; mỗi scene có 1 ảnh dọc A5 (tỷ lệ 5:7), 1 đoạn *lời kể* tiếng Việt (đọc thành tiếng), và các *nhân vật* xuất hiện. Người dùng là phụ huynh/giáo viên **không rành kỹ thuật** — ưu tiên rõ ràng, ít bước, thao tác từng scene độc lập. Kinh doanh: subscription + credit, **1 credit = 1 lần gen ảnh (kể cả gen lại)**; mọi thao tác tốn tiền hiện **cost badge + xác nhận**.

**DESIGN SYSTEM:** vui tươi thân thiện trẻ em nhưng gọn gàng chuyên nghiệp. Màu chính **cam Shopee #EE4D2D** (primary/CTA), phụ **xanh #2D7FEE**; success xanh lá, warning vàng, error đỏ. Bo góc rounded-2xl, bóng nhẹ, nhiều khoảng trắng, font sans hiện đại. **Bắt buộc light & dark mode + responsive** (desktop/tablet/mobile). Mọi trạng thái phải có: loading (skeleton), empty, error, success, disabled.

**NHÂN VẬT seed:** Shopee (bé trai ~3t, áo nâu "TOGETHER"), Jin (jumpsuit cam), Poli (xe cảnh sát xanh-trắng), Mark (xe utility cam mũ đỏ "M"), Bucky (pickup vàng mũ xanh "B"), Poacher (xe tải quân sự đỏ — phản diện), Mẹ, Bố. Số dư ví dụ **37 credit**, gói Creator.

**MÀN HÌNH CẦN DỰNG — Story Editor (scene-board):**

Header: tên truyện "Story 5 — Shopee và chiếc xe ăn trộm Poacher" (sửa inline) · ô Chủ đề/bài học ("Không đi theo người lạ, bảo vệ đồ cá nhân, nhờ người lớn giúp đỡ") · chọn giọng đọc (mặc định "HoaiMy") + tốc độ (-10%) · **số credit còn lại (37)** · nút **[▶ Build]** và **[⬆ Xuất bản]** · chỉ báo "Đã lưu".

Vùng nhập nội dung (thu gọn được): textarea "Dán nội dung truyện" + nút **[✨ Tách thành scene]** (bấm → giả lập tách, sinh các hàng scene).

Bảng scene — mỗi scene 1 hàng-card, 4 cột:
1. **# + trạng thái**: số thứ tự (0 = Cover); badge màu: `Trống` (xám) / `Đang gen…` (cam + spinner) / `Xong` (xanh lá) / `Cần sửa` (đỏ).
2. **Ảnh** khung 5:7: chưa có → nút `+ Gen ảnh`; có ảnh → thumbnail + overlay hover `↻ Gen lại` / `⤢ Xem lớn` / `⬆ Thay ảnh`. Bấm gen → spinner ~1.5s → hiện placeholder màu.
3. **Lời kể (TTS)**: textarea sửa được + `[▶ Nghe thử]` (thanh play chạy giả lập) + thời lượng ước tính; sửa text → badge chuyển `Cần sửa`, gợi ý regen audio.
4. **Nhân vật**: chip checkbox chọn từ danh sách nhân vật; chip chọn tô màu. Nút `+ thêm`.

Kéo-thả đổi thứ tự scene; nút `+ Thêm scene`; xoá scene (có xác nhận). Auto-save nháp.

Drawer phải khi click 1 scene: **prompt tiếng Anh của scene** (sửa được) + preview ref nhân vật đang chọn + nút "Gen ảnh" kèm **credit-cost badge** ("~1 credit · còn 37").

**RETRY / REGEN ẢNH (làm kỹ phần này):**
Bấm `Gen lại` → mở **modal so sánh biến thể**: ảnh hiện tại + các bản gen mới cạnh nhau (2–4 bản/lần). Trong modal:
- Ô tinh chỉnh prompt trước khi gen ("làm sáng hơn", "thêm núi phía sau"…).
- Đổi/bớt nhân vật ref.
- Chọn số biến thể 1 / 2 / 4 → nhân credit tương ứng, hiện **tổng cost trước khi bấm**; mỗi lần gen hiện "-N credit · còn lại M".
- Chọn bản ưng → set làm ảnh chính; các bản khác lưu "lịch sử ảnh" của scene (xem lại/khôi phục, **không tốn thêm credit**).

**EDGE CASES phải có UI:**
- Hết credit giữa chừng → chặn, mở modal mua thêm, **không mất công việc**.
- Gen fail (timeout / nội dung bị chặn) → **không trừ credit**, hiện lý do + nút thử lại.
- Nội dung không phù hợp trẻ em → cảnh báo kiểm duyệt, chặn gen.
- Giới hạn ref/scene (tối đa 4) → chặn chọn thêm, giải thích.
- Xuất bản khi còn scene trống → cảnh báo.

**SEED 6 scene thật:**
- 0 Cover — [Shopee, Mark, Bucky, Poacher] — "Shopee và chiếc xe ăn trộm Poacher. Bài học hôm nay: không đi theo người lạ, biết bảo vệ đồ cá nhân, và nhờ người lớn giúp đỡ khi gặp nguy hiểm." — **Xong**.
- 1 — [Shopee, Mẹ, Bố] — "Một buổi sáng đẹp trời, bé Shopee được bố mẹ đưa đến khu cắm trại gần chân núi…" — **Xong**.
- 2 — [Shopee, Jin, Mark, Bucky] — "Ở bãi cỏ rộng, chị Jin đang hướng dẫn các bé cách xếp ba lô, giữ đồ cá nhân…" — **Xong**.
- 3 — [Shopee] — "Sau giờ học kỹ năng, Shopee đặt chiếc ba lô nhỏ bên cạnh lều…" — **Đang gen**.
- 4 — [Shopee, Poacher] — "Đúng lúc đó, từ sau bụi cây, một chiếc xe lạ lén lút xuất hiện. Đó là Poacher…" — **Trống**.
- 5 — [Shopee, Mark, Bucky, Poacher] — "May mắn thay, Bucky đang đứng gần đó đã phát hiện ra…" — **Trống**.

**ĐẦU RA:** một file chạy được, mọi nút có phản hồi thị giác, ảnh dùng gradient/SVG placeholder, không backend.
