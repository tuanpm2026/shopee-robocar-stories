# Prompt — Xác thực (Auth) + Onboarding

> Copy khối PROMPT, dán cho Claude (Artifact).

---

**PROMPT**

Bạn là senior product designer + frontend engineer. Dựng **prototype UI click được** (HTML/React tự chứa, 1 file, **không gọi mạng thật** — giả lập bằng loading + placeholder). Điều hướng giữa các bước bằng state nội bộ.

**SẢN PHẨM:** "Story Studio" — web app tạo truyện tranh thiếu nhi có giọng đọc bằng AI (bé Shopee + xe cứu hộ Robocar Poli). Người dùng: phụ huynh/giáo viên **không rành kỹ thuật**. Kinh doanh: subscription + credit.

**DESIGN SYSTEM:** vui tươi thân thiện trẻ em, gọn gàng chuyên nghiệp. Màu chính **cam #EE4D2D**, phụ **xanh #2D7FEE**; rounded-2xl, bóng nhẹ, font sans. **Light & dark mode + responsive**. Trạng thái: loading, error, success, disabled. Bố cục auth: 2 cột trên desktop (trái minh hoạ thương hiệu vui nhộn, phải form), 1 cột trên mobile.

**CÁC MÀN HÌNH CẦN DỰNG (điều hướng qua lại được):**
1. **Đăng ký**: email + mật khẩu (có nút hiện/ẩn, thanh độ mạnh mật khẩu), nút **"Tiếp tục với Google"**, checkbox đồng ý điều khoản. → sang màn Verify.
2. **Xác minh email**: nhập **mã 6 số** (6 ô), nút gửi lại mã (đếm ngược 60s), trạng thái nhập sai/đúng.
3. **Đăng nhập**: email + mật khẩu, "Ghi nhớ tôi", link "Quên mật khẩu?", OAuth Google.
4. **Quên mật khẩu**: nhập email → màn "Đã gửi link đặt lại" → màn **đặt lại mật khẩu** (2 ô mật khẩu mới + xác nhận).
5. **Onboarding** (sau verify, 3 bước có progress): (a) "Bạn dùng để làm gì?" chọn thẻ (Cá nhân/Giáo viên/Sáng tạo nội dung); (b) "Tặng bạn 10 credit chào mừng 🎉"; (c) "Tạo truyện đầu tiên?" — nút Bắt đầu / Bỏ qua → giả lập vào Dashboard.

**EDGE CASES phải có UI:**
- Email sai định dạng / đã tồn tại → lỗi inline.
- Mật khẩu yếu → gợi ý; sai mật khẩu khi đăng nhập → lỗi rõ, không tiết lộ email có tồn tại hay không.
- Nhập mã verify sai → báo lỗi + còn N lần thử; mã hết hạn → nút gửi lại.
- Đang submit → nút loading, khoá double-submit.
- Lỗi mạng → toast "Thử lại".

**ĐẦU RA:** một file chạy được, mọi nút phản hồi thị giác, không backend.
