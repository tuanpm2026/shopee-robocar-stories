# Prompt: dựng UI "Story Studio" (đưa cho Claude / agent gen UI)

> Copy toàn bộ phần trong khối dưới và dán vào Claude (chế độ tạo Artifact) hoặc agent gen UI.

---

Bạn là một senior product designer + frontend engineer. Hãy tạo **một trang HTML tự chứa (self-contained, single file)** làm **prototype UI có thể click** cho một web app tên **"Story Studio"**. Dùng React + Tailwind qua CDN, hoặc HTML/CSS/JS thuần — miễn là 1 file chạy được ngay trong trình duyệt. **Không gọi mạng thật**: mọi hành động gen ảnh/audio chỉ giả lập bằng loading + ảnh placeholder.

## Sản phẩm là gì
Công cụ giúp tạo **truyện tranh thiếu nhi** (nhân vật bé Shopee + đội xe cứu hộ Robocar Poli). Mỗi truyện gồm nhiều "scene" (trang). Với mỗi scene có: một ảnh minh hoạ do AI gen, một đoạn lời kể (được đọc thành tiếng bằng giọng tiếng Việt), và danh sách nhân vật xuất hiện. Người dùng dán nội dung truyện dạng text, app tách thành các scene, rồi họ gen ảnh + nghe thử giọng đọc + xuất bản — tất cả trong một màn hình dạng bảng.

Người dùng là phụ huynh/biên tập không rành kỹ thuật. Ưu tiên: **rõ ràng, ít bước, thao tác trên từng scene độc lập, luôn thấy chi phí trước khi gen.**

## Màn hình chính: SCENE-BOARD (bảng scene)

**Thanh trên cùng (header):**
- Tên truyện có thể sửa inline: "Story 5 — Shopee và chiếc xe ăn trộm Poacher"
- Ô "Chủ đề / bài học": "Không đi theo người lạ, bảo vệ đồ cá nhân, nhờ người lớn giúp đỡ"
- Chọn giọng đọc (dropdown, mặc định "HoaiMy") + tốc độ (mặc định -10%)
- Nút chính bên phải: **[▶ Build truyện]** và **[⬆ Deploy]**
- Chỉ báo tổng chi phí ước tính phiên làm việc (vd "Đã dùng: ~12k token · 8 ảnh")

**Vùng nhập liệu (thu gọn được):** một textarea lớn "Dán nội dung truyện vào đây" + nút **[✨ Tách thành scene]**. Khi bấm, giả lập tách và sinh ra các dòng scene bên dưới.

**Bảng scene — mỗi scene là một hàng (card ngang), gồm 4 cột:**
1. **# + trạng thái**: số thứ tự (0 = Cover), badge trạng thái: `Trống` (xám) / `Đang gen…` (cam, có spinner) / `Xong` (xanh) / `Cần sửa` (đỏ).
2. **Ảnh**: khung 5:7 (dọc, khổ A5). Nếu chưa có → nút lớn `+ Gen ảnh`. Nếu có ảnh → hiện thumbnail + overlay hover với `↻ Gen lại` và `⤢ Xem lớn`. Bấm gen → spinner ~1.5s → hiện ảnh placeholder màu.
3. **Lời kể (TTS)**: textarea sửa được chứa đoạn văn. Bên dưới: nút **[▶ Nghe thử]** (giả lập thanh play chạy) + thời lượng ước tính. Sửa text thì badge chuyển sang `Cần sửa` gợi ý regen audio.
4. **Nhân vật**: nhóm chip checkbox chọn nhân vật xuất hiện trong scene (Shopee, Jin, Poli, Mark, Bucky, Poacher, Mẹ, Bố). Chip đang chọn tô màu. Đây chính là "character reference" đính kèm khi gen ảnh.

**Panel phải trượt ra khi click một scene** (drawer): hiện **prompt tiếng Anh** của scene đó (sửa được), preview các ảnh ref đang chọn, và nút "Gen ảnh với các thiết lập này" kèm **badge chi phí ước tính** (vd "~1 ảnh · ~$0.02").

**Tương tác kéo-thả**: cho phép kéo để đổi thứ tự các scene. Có nút `+ Thêm scene` ở cuối.

## Trạng thái rỗng & phản hồi
- Khi chưa có scene: minh hoạ thân thiện + hướng dẫn "Dán nội dung rồi bấm Tách thành scene".
- Mọi hành động tốn chi phí (gen ảnh, build, deploy) phải hỏi xác nhận nhẹ và hiện ước tính chi phí trước.
- Toast thông báo khi build/deploy xong kèm link giả "Đã xuất bản: …github.io/…".

## Phong cách hình ảnh (rất quan trọng)
- Vui tươi, thân thiện với trẻ em nhưng vẫn gọn gàng chuyên nghiệp — không lòe loẹt.
- Màu nhấn: **cam Shopee (#EE4D2D)** cho nút chính; phụ trợ xanh dương (theo tông xe cứu hộ Poli). Nền sáng, bo góc mềm (rounded-2xl), bóng nhẹ.
- Font sans hiện đại, dễ đọc. Icon dùng emoji hoặc inline SVG đơn giản.
- **Hỗ trợ cả light & dark mode** (theo prefers-color-scheme).
- **Responsive**: trên màn hẹp, mỗi scene card xếp dọc các cột; bảng không được tràn ngang trang.

## Dữ liệu mẫu (seed sẵn 6 scene này để mockup có nội dung thật)
- **0 · Cover** — nhân vật: Shopee, Mark, Bucky, Poacher — lời kể: "Shopee và chiếc xe ăn trộm Poacher. Bài học hôm nay: không đi theo người lạ, biết bảo vệ đồ cá nhân, và nhờ người lớn giúp đỡ khi gặp nguy hiểm." — trạng thái: Xong.
- **1** — Shopee, Mẹ, Bố — "Một buổi sáng đẹp trời, bé Shopee được bố mẹ đưa đến khu cắm trại gần chân núi…" — Xong.
- **2** — Shopee, Jin, Mark, Bucky — "Ở bãi cỏ rộng, chị Jin đang hướng dẫn các bé cách xếp ba lô, giữ đồ cá nhân và không tự ý đi xa khỏi khu cắm trại…" — Xong.
- **3** — Shopee — "Sau giờ học kỹ năng, Shopee đặt chiếc ba lô nhỏ của mình bên cạnh lều…" — Đang gen.
- **4** — Shopee, Poacher — "Đúng lúc đó, từ sau bụi cây, một chiếc xe lạ lén lút xuất hiện. Đó là Poacher, chiếc xe ăn trộm…" — Trống.
- **5** — Shopee, Mark, Bucky, Poacher — "May mắn thay, Bucky đang đứng gần đó đã phát hiện ra…" — Trống.

## Đầu ra
Một file HTML duy nhất, chạy được ngay, dùng ảnh placeholder màu (không tải ảnh ngoài — vẽ bằng gradient/SVG). Tất cả nút phải có phản hồi thị giác (loading, đổi trạng thái). Đây là prototype UX để duyệt layout, **không cần backend thật**.
