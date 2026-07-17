# Story Studio — bộ prompt tách theo màn hình

Mỗi file là **một prompt tự chứa**: đã có sẵn phần bối cảnh sản phẩm + design system + nhân vật seed ở đầu, nên **copy trọn một file** là dán được cho AI design (Claude Artifact) mà không cần ghép file khác.

| File | Màn hình | Ưu tiên dựng |
|---|---|---|
| `01-marketing.md` | Landing / trang bán hàng | Sau cùng |
| `02-auth-onboarding.md` | Đăng ký · đăng nhập · verify · quên MK · onboarding | 3 |
| `03-dashboard.md` | Quản lý truyện (lưới, tìm/lọc, menu) | 2 |
| `04-character.md` | Thư viện nhân vật + tạo/chỉnh nhân vật | 4 |
| `05-editor.md` | Story Editor scene-board + retry/regen ảnh | **1 — lõi** |
| `06-publish-viewer.md` | Build · xuất bản · trang xem công khai | 5 |
| `07-pricing.md` | Bảng giá + đăng ký gói | 6 |
| `08-billing-settings.md` | Credit · thanh toán · subscription · cài đặt | 7 |

**Cách dùng:** mở 1 file → copy toàn bộ phần trong khối `PROMPT` → dán vào Claude (chế độ Artifact). Làm `05-editor.md` trước vì đó là màn hình lõi; duyệt xong style ở đó rồi các file sau sẽ đồng bộ theo.

**Design token dùng chung** (nhắc AI giữ nhất quán giữa các màn hình): cam #EE4D2D, xanh #2D7FEE, rounded-2xl, font sans, light+dark, responsive.
