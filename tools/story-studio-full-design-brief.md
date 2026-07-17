# Design Brief đầy đủ — "Story Studio" (prompt cho AI design)

> Copy toàn bộ phần dưới (từ "BẠN LÀ..." trở đi) và đưa cho AI design/agent gen UI.
> Vì sản phẩm có nhiều page, nên yêu cầu AI làm **một prototype nhiều màn hình click qua lại được** (single-page app mô phỏng, điều hướng bằng state), hoặc chia thành từng artifact theo nhóm màn hình nếu quá lớn.

---

BẠN LÀ một senior product designer + frontend engineer. Hãy thiết kế và dựng **prototype UI click được** cho một SaaS tên **"Story Studio"** — công cụ web giúp người dùng tạo **truyện tranh thiếu nhi có giọng đọc** bằng AI. Xuất ra HTML/React tự chứa, chạy được trong trình duyệt, **không gọi mạng thật** (mọi thao tác AI đều giả lập bằng loading + placeholder). Điều hướng giữa các màn hình bằng state nội bộ (sidebar / router giả).

## 0. Bối cảnh sản phẩm

- Người dùng tạo truyện gồm nhiều **scene** (trang). Mỗi scene có: 1 ảnh AI (khổ dọc A5, 5:7), 1 đoạn **lời kể** được đọc thành giọng tiếng Việt, và danh sách **nhân vật** xuất hiện.
- Nhân vật phải **nhất quán xuyên suốt** — nên có **thư viện nhân vật** riêng, mỗi nhân vật có ảnh reference; khi gen scene sẽ đính kèm ref các nhân vật được chọn.
- Đối tượng dùng: phụ huynh / giáo viên / nhà sáng tạo nội dung thiếu nhi, **không rành kỹ thuật**. Ưu tiên: rõ ràng, ít bước, thao tác trên từng scene độc lập.
- Mô hình kinh doanh: **subscription + credit**. 1 credit = 1 lần gen ảnh (kể cả gen lại). Mọi thao tác tốn tiền phải hiện **chi phí credit trước khi xác nhận**.

## 1. Design system (áp cho toàn bộ)

- Phong cách: vui tươi, thân thiện trẻ em nhưng gọn gàng chuyên nghiệp — không lòe loẹt.
- Màu nhấn chính: **cam Shopee #EE4D2D** (nút primary, CTA). Phụ: xanh dương (#2D7FEE, tông xe cứu hộ). Success xanh lá, warning vàng, error đỏ, neutral xám.
- Bo góc mềm (rounded-2xl), bóng nhẹ, nhiều khoảng trắng. Font sans hiện đại dễ đọc.
- **Bắt buộc: light & dark mode** (theo prefers-color-scheme + toggle). **Responsive** đầy đủ: desktop (sidebar + nội dung), tablet, mobile (bottom nav / hamburger). Bảng/nội dung rộng phải cuộn trong khung riêng, không tràn ngang trang.
- Component chuẩn cần có sẵn: Button (primary/secondary/ghost/danger), Input, Textarea, Select, Toggle, Checkbox/Chip, Modal, Drawer, Toast, Tooltip, Badge/Status pill, Progress bar, Skeleton loader, Empty state, Card, Avatar, Credit-cost badge, Confirmation dialog.
- **Mọi trạng thái phải thể hiện**: loading (skeleton/spinner), empty, error, success, disabled. Không màn hình nào để trống vô nghĩa.

---

## 2. DANH SÁCH MÀN HÌNH (thiết kế đủ tất cả)

### A. Marketing / Landing (public)
- Hero: tên sản phẩm + tagline "Tạo truyện tranh thiếu nhi có giọng đọc bằng AI — trong vài phút", CTA "Dùng thử miễn phí".
- Section: cách hoạt động (3 bước: Viết nội dung → Gen ảnh nhân vật nhất quán → Xuất bản có giọng đọc).
- Section: showcase truyện mẫu (dùng story 5 làm demo, ảnh placeholder).
- Section: bảng giá rút gọn (link tới trang Pricing).
- Footer: điều khoản, chính sách, liên hệ.

### B. Xác thực (Auth)
- **Đăng ký**: email + mật khẩu, hoặc "Tiếp tục với Google". Hiện điều khoản + checkbox đồng ý. Sau đăng ký → màn hình **"Xác minh email"** (nhập mã 6 số / link).
- **Đăng nhập**: email + mật khẩu, "Quên mật khẩu?", OAuth Google.
- **Quên mật khẩu**: nhập email → màn hình "Đã gửi link" → màn hình đặt lại mật khẩu.
- **Onboarding lần đầu** (sau verify): 2–3 bước ngắn — chọn mục đích dùng, tặng credit chào mừng, gợi ý tạo truyện đầu tiên.

### C. Dashboard / Quản lý truyện (màn hình chính sau đăng nhập)
- Sidebar trái: Truyện của tôi · Thư viện nhân vật · Credit & Gói · Cài đặt · (avatar + số credit còn lại luôn hiển thị góc trên).
- Lưới/List các truyện: thumbnail cover, tên, số scene, trạng thái (Nháp / Đang làm / Đã xuất bản), ngày sửa. Mỗi card có menu: Mở · Nhân bản · Đổi tên · Xuất bản · Xoá.
- Nút lớn **"+ Tạo truyện mới"**. Có tìm kiếm + lọc theo trạng thái + sắp xếp.
- Empty state khi chưa có truyện: minh hoạ + hướng dẫn tạo truyện đầu tiên.

### D. Thư viện nhân vật (Character Library)
- Lưới các nhân vật: avatar, tên, vai trò (nhân vật chính / phụ / phản diện), số truyện đang dùng.
- Có sẵn bộ nhân vật hệ thống (Shopee, Jin, Poli, Mark, Bucky, Poacher, Mẹ, Bố) — đánh dấu "Mẫu", chỉ đọc/nhân bản.
- Nút **"+ Tạo nhân vật mới"**.

### E. Tạo / chỉnh nhân vật (Character Creator) — flow quan trọng
- Form: Tên · Vai trò · Mô tả ngoại hình (text: tuổi, trang phục, màu sắc, đặc điểm) · loại (người / xe-robot).
- **Ảnh reference**: 2 cách — (1) **Upload** ảnh có sẵn; (2) **Gen bằng AI** từ mô tả (tốn credit, hiện cost badge). Cho gen nhiều biến thể, chọn 1 làm ref chính, giữ vài ảnh phụ (nhiều góc).
- Preview thẻ nhân vật. Lưu vào thư viện để tái dùng ở mọi truyện.
- Edge case: mô tả quá ngắn → cảnh báo "cần chi tiết hơn để gen nhất quán"; gen ảnh fail → cho retry không mất credit lần fail.

### F. Story Editor — Scene-board (màn hình làm việc lõi)
- **Header**: tên truyện sửa inline · ô Chủ đề/bài học · chọn giọng đọc (mặc định HoaiMy) + tốc độ (-10%) · số credit còn lại · nút **[▶ Build]** và **[⬆ Xuất bản]**.
- **Vùng nhập nội dung** (thu gọn được): textarea "Dán nội dung truyện" + nút **[✨ Tách thành scene]** (giả lập tách ra các scene).
- **Bảng scene**, mỗi scene 1 hàng-card, 4 cột:
  1. **# + trạng thái**: số thứ tự (0 = Cover); badge: Trống / Đang gen… / Xong / Cần sửa.
  2. **Ảnh** (khung 5:7): chưa có → nút `+ Gen ảnh`; có ảnh → thumbnail + hover overlay `↻ Gen lại` / `⤢ Xem lớn` / `⬆ Thay ảnh (upload)`.
  3. **Lời kể (TTS)**: textarea sửa được + `[▶ Nghe thử]` (thanh play giả lập) + thời lượng ước tính; sửa text → gợi ý regen audio.
  4. **Nhân vật**: chip chọn từ thư viện nhân vật (đính kèm ref khi gen). Nút "+ thêm nhân vật".
- **Drawer phải khi click scene**: prompt tiếng Anh (sửa được) + preview ref đang chọn + nút "Gen ảnh" kèm **credit-cost badge**.
- Kéo-thả đổi thứ tự scene; nút `+ Thêm scene`; nút xoá scene (có xác nhận).
- Auto-save nháp; chỉ báo "Đã lưu".

### G. Retry / Regenerate ảnh (flow chi tiết — user hỏi kỹ phần này)
- Bấm `Gen lại` trên 1 scene → mở **modal so sánh biến thể**: hiện ảnh hiện tại + các bản gen mới cạnh nhau (2–4 bản/lần).
- Mỗi lần gen **trừ credit** và hiển thị rõ "Lần gen này: -1 credit · còn lại N". Cho phép:
  - Tinh chỉnh prompt trước khi gen lại (thêm ghi chú "làm sáng hơn", "thêm núi phía sau"…).
  - Đổi/bớt nhân vật ref.
  - Chọn số biến thể muốn gen (1/2/4) → nhân credit tương ứng, hiện tổng cost trước khi bấm.
- Chọn bản ưng → set làm ảnh chính, các bản khác lưu vào "lịch sử ảnh" của scene (xem lại/khôi phục, không tốn thêm credit).
- **Edge cases**: hết credit giữa chừng → chặn, mở modal mua thêm; gen fail (timeout/nội dung bị chặn) → **không trừ credit**, hiện lý do + nút thử lại; nội dung vi phạm (an toàn trẻ em) → cảnh báo, không gen.

### H. Xuất bản / Xem truyện đã publish
- Trước xuất bản: checklist "mọi scene đã có ảnh + audio?", cảnh báo scene còn trống.
- Sau Build: preview slideshow (lật trang + tự đọc). Nút "Xuất bản" → tạo link chia sẻ công khai + QR + nhúng.
- Trang xem công khai (viewer): full-screen, tự lật + đọc, nút bật/tắt tiếng, next/prev.

### I. Pricing & Đăng ký gói
- Bảng 4 gói dạng cột: **Free / Creator / Pro / Studio**. Mỗi cột: giá tháng, số credit tặng/tháng, tính năng (số truyện, xuất bản, thương mại, độ phân giải…), CTA. Toggle tháng/năm (năm giảm ~2 tháng).
- Đánh dấu gói "Phổ biến nhất". FAQ về credit, hết credit thì sao, hoàn tiền.
- Gợi ý số: Free $0/10 credit · Creator ~$9.99/100 credit · Pro ~$24.99/300 credit · Studio ~$49+/700 credit. (1 credit = 1 ảnh.)

### J. Credit & Thanh toán (Billing)
- Trang **Credit**: số dư lớn, thanh tiến độ chu kỳ, lịch sử tiêu credit (bảng: thời gian, hành động, scene/truyện, -credit), nút **Mua thêm (top-up)**.
- Modal top-up: các gói lẻ ($5/40, $10/90…), hiện đơn giá, xác nhận.
- Trang **Subscription**: gói hiện tại, ngày gia hạn, nút nâng/hạ/huỷ gói, phương thức thanh toán (thẻ), hoá đơn tải về.
- Modal thanh toán (giả lập Stripe): nhập thẻ, xử lý, thành công/thất bại.

### K. Cài đặt tài khoản
- Hồ sơ (tên, avatar, email), đổi mật khẩu, ngôn ngữ, giao diện (light/dark/auto), thông báo, vùng nguy hiểm (xoá tài khoản — có xác nhận gõ tên).

---

## 3. FLOW CHÍNH (happy path) — thiết kế cho khớp

1. **Đăng ký → verify → onboarding → tặng credit → Dashboard.**
2. **Tạo truyện**: Dashboard → +Tạo → đặt tên → Editor → dán nội dung → Tách scene → (chọn/tạo nhân vật) → gen ảnh từng scene → nghe thử audio → Build → Xuất bản → nhận link.
3. **Tạo nhân vật**: Thư viện nhân vật → +Tạo → mô tả → upload/gen ref → lưu → dùng trong editor.
4. **Hết credit**: bất kỳ nút gen nào → phát hiện thiếu → mở modal mua/nâng gói → thanh toán → quay lại đúng chỗ đang làm.
5. **Nâng gói**: Pricing/Subscription → chọn gói → thanh toán → credit cập nhật ngay.

## 4. EDGE CASES bắt buộc phủ (thiết kế UI cho từng cái)

- **Hết credit giữa thao tác** → chặn hành động, giữ nguyên công việc, đề xuất mua thêm; không mất dữ liệu.
- **Gen ảnh thất bại** (timeout / nội dung bị chặn / lỗi API) → không trừ credit, thông báo lý do, nút thử lại.
- **Nội dung không phù hợp trẻ em** → cảnh báo kiểm duyệt, chặn gen, gợi ý sửa.
- **Thanh toán thất bại / thẻ bị từ chối** → thông báo rõ, cho thử thẻ khác, không nâng gói.
- **Gói hết hạn / huỷ giữa kỳ** → hiện trạng thái, truyện cũ vẫn xem được nhưng khoá gen mới; nhắc gia hạn.
- **Credit hết hạn cuối chu kỳ** → cảnh báo trước, hiển thị breakage rõ ràng.
- **Đang gen mà đóng tab / mất mạng** → khôi phục trạng thái, không double-charge; nếu chưa xong thì đánh dấu "đang xử lý".
- **Xung đột chỉnh sửa đồng thời** (2 tab) → cảnh báo, tránh ghi đè.
- **Xoá nhân vật đang được truyện dùng** → cảnh báo "N truyện đang dùng", cho biết ảnh hưởng trước khi xoá.
- **Upload ảnh sai định dạng / quá nặng / khuôn mặt không rõ** → validate, báo lỗi thân thiện.
- **Giới hạn số ref nhân vật/scene** (vd tối đa 4) → chặn chọn thêm, giải thích.
- **Xuất bản khi còn scene trống** → cảnh báo, cho publish một phần hoặc chặn tuỳ chọn.
- **Free tier bị lạm dụng** → rate-limit, yêu cầu verify, thông báo giới hạn.
- **Mạng chậm / tải lâu** → skeleton, progress, cho huỷ tác vụ dài.
- **Empty states** cho mọi danh sách (truyện, nhân vật, lịch sử credit).
- **Lỗi 404 / 500 / mất kết nối** → trang lỗi thân thiện, nút thử lại/về Dashboard.

## 5. Dữ liệu mẫu (seed để mockup sống động)

Seed sẵn 1 truyện demo dùng **story 5 "Shopee và chiếc xe ăn trộm Poacher"** với ~6 scene có lời kể thật và trạng thái khác nhau (Xong / Đang gen / Trống), và thư viện nhân vật gồm: Shopee (bé trai ~3 tuổi, áo nâu "TOGETHER"), Jin (jumpsuit cam), Poli (xe cảnh sát xanh-trắng), Mark (xe utility cam mũ đỏ "M"), Bucky (pickup vàng mũ xanh "B"), Poacher (xe tải quân sự đỏ, phản diện), Mẹ, Bố. Seed số dư credit ví dụ 37, gói Creator.

## 6. Đầu ra

- Prototype click được, điều hướng đủ giữa các màn hình trên. Ảnh dùng placeholder vẽ bằng gradient/SVG (không tải ảnh ngoài).
- Mọi nút có phản hồi thị giác; mọi thao tác tốn credit hiện cost badge + xác nhận. Không cần backend thật.
- Nếu quá lớn cho một file, ưu tiên nhóm: (1) Auth+Onboarding, (2) Dashboard+Editor+Retry, (3) Character library+creator, (4) Pricing+Billing — và nói rõ cách ghép.
