---
name: shopee-story-prompts
description: Generate AI image-prompt plan for stories in the Shopee-robocar-stories series. Auto-trigger when the user opens, references, edits, or pastes the content of a `content` file inside a `Shopee-story-N/` folder (or asks to gen/tạo prompts/ảnh for such a story). Reads the plain-text story content, breaks it into 8-11 scenes, asks the user about any new side characters (gender, age, outfit), then writes `image-prompts-plan.md` next to the content file with: cover + scene prompts + infographic, character refs matrix, A5 portrait (--ar 5:7), Pixar 3D style. Output guide is Vietnamese, prompts are English. Skill is project-local for the Shopee-robocar-stories series only.
---

# Shopee Story → Image Prompts Plan

You are generating an AI image-generation plan for a children's storybook in the **Shopee-robocar-stories** series. The plan is consumed by the user (Vietnamese parent/creator) to copy-paste prompts into Midjourney/Nano Banana/Flux/Sora.

## ⚠️ LESSONS LEARNED — HARD RULES (đọc TRƯỚC, áp dụng cho MỌI prompt)

Đây là các lỗi đã thực sự gặp khi gen các story trước. **Mọi prompt phải tự động phòng các lỗi này** — đừng để user phải nhắc lại từng lần.

1. **XE/TÀU KHÔNG ĐƯỢC MỌC TAY NGƯỜI.** Mọi nhân vật phương tiện (taxi, tàu, cần cẩu, xe quét đường, xe ben…) ở **dạng vehicle thuần**, chỉ có **khuôn mặt dễ thương (mắt + miệng)** ở phần kính/đầu xe. **KHÔNG** cánh tay người, bàn tay, ngón tay, găng tay. Chúng biểu cảm bằng **nét mặt + nghiêng thân + đèn + bộ phận máy móc**.
   - **Ngoại lệ — bộ phận máy được phép:** cần trục + móc cẩu, cánh tay quét/chổi chà cơ khí, gàu xúc, mỏ neo, phao cứu sinh… (mô tả rõ "*a machine part, not a human hand*").
   - **Con người (Shopee, Mẹ, Bố, Jin) VẪN có tay bình thường.** Vì vậy chỉ chặn ở phần `--no`: `human arms on vehicles, human hands on vehicles` — **TUYỆT ĐỐI không** ghi `--no hands` trống (sẽ mất tay người).

2. **CHẶN CHỮ RÁC NHƯNG GIỮ LOGO/KÝ HIỆU MONG MUỐN.** AI hay tự sinh bong bóng thoại + chữ ngẫu nhiên; nhưng nếu chặn chữ quá mạnh thì **mất luôn logo áo** (lỗi "gen ra toàn thiếu logo").
   - **GIỮ:** logo in trên áo gia đình (Shopee — áo **nâu** in **TOGETHER**; Mẹ/Bố — áo in **MEMORIES / Let's grow TOGETHER**) **và** ký hiệu thiết kế trên xe (biển **TAXI** của Cap, **phong bì** của Posty, **logo R** của Rody, **logo tái chế** của Cleany, chữ **P** trên Poli, chữ **H/R/B/M** trên các Robocar…).
   - **CHẶN:** speech bubble, dialogue balloon, thought bubble, caption, signboard, **random floating text**.
   - **TUYỆT ĐỐI KHÔNG** dùng `--no text` / `--no words` / `--no letters` → sẽ xoá luôn logo. Suffix `--no` chuẩn: `--no speech bubbles, dialogue balloons, thought bubbles, captions, human arms on vehicles, human hands on vehicles, watermark, signature`.
   - Với tool không có `--no` (Nano Banana/Flux/Sora): viết dạng khẳng định *"no speech bubbles or random floating text, but DO keep the printed wordmark on the shirts and the vehicles' design markings"*.
   - **Thực tế:** chữ nhỏ AI hay méo → khuyến nghị **overlay logo sạch khi hậu kỳ** cho ảnh in to.

3. **LOGO ÁO PHẢI ĐƯỢC TẢ RÕ + NHÌN THẤY.** Trong mỗi prompt có người, luôn ghi rõ *"Shopee in his brown T-shirt with the printed wordmark TOGETHER clearly visible on the chest"* (+ áo bố mẹ nếu có), và **luôn upload đúng ref** Shopee.png / mother.png / father.png.

4. **PHỐI CẢNH XA-GẦN cho scene đông hoặc cảnh rộng.** Scene nhiều nhân vật/đông xe dễ bị "dàn phẳng, sai tỉ lệ". Bắt buộc mô tả **chiều sâu 3 lớp**: nhân vật chính lớn nhất ở **foreground (đáy khung)**; nhóm hoạt động ở **midground**; vật/nhân vật xa **nhỏ hơn + mờ nhẹ (atmospheric perspective)** ở background. Thêm: đường/vạch kẻ **lùi dần về điểm tụ (vanishing point)**, *eye-level hoặc slightly low camera angle, wide cinematic lens, deep depth of field*. Dùng **upper/lower half** (không dùng left/right) cho khung dọc.

5. **NHÂN VẬT PHỤ ĐÃ CÓ REF → KHÔNG HỎI USER.** Nếu nhân vật có sẵn file trong `Characters/` và được mô tả trong `Characters/CHARACTERS.md`, **dùng luôn** mô tả đó (đừng PAUSE hỏi user). Chỉ hỏi khi nhân vật **hoàn toàn mới, không có ref**. (Xem Step 3–4.)

6. **Shopee là BÉ TRAI.** he/him/his/little boy. Không bao giờ girl/she/her/daughter.

7. **TIÊU ĐỀ trên cover & infographic → RENDER THẲNG vào ảnh (đừng để trống).** Lỗi user hay gặp: cover/infographic bị **thiếu title** vì prompt cũ bảo *"chừa chỗ trống cho title thêm sau"*. **Mặc định mới:** Scene 0 (cover) render đúng **tên truyện**; scene infographic cuối render đúng **tiêu đề bài học**, dạng *"render the title as a large, bold, clean, neatly-spelled storybook title banner reading exactly: «…» with correct Vietnamese diacritics"*.
   - Hai scene này **bỏ `captions`** khỏi đuôi `--no` (cover) / **bỏ hẳn `--no`** (infographic) để không triệt tiêu chữ tiêu đề; vẫn giữ `human arms on vehicles, human hands on vehicles` nếu có xe.
   - AI dễ méo chữ Việt dài nhiều dấu → ghi chú cho user **gen 2–3 lần** hoặc **overlay tiêu đề sạch khi hậu kỳ** (Canva/Photoshop). Nhưng prompt **luôn yêu cầu render title**, không để trống mặc định nữa.

8. **TRÁNH động từ "pointing / gesturing / waving" cho XE.** Các từ này dễ làm AI mọc tay/bàn tay người cho xe (ngược HARD RULE #1). Thay bằng *"tilting its nose / leaning / nodding its body / lights blinking"*. (Người thì vẫn vẫy tay bình thường.)

9. **TỈ LỆ XE/VẬT–NGƯỜI PHẢI ĐÚNG THỰC TẾ.** Lỗi user đã gặp: AI gen **xe đạp, ô tô, xe to… quá nhỏ so với em bé/người** (hoặc ngược lại). Khác với HARD RULE #4 (chiều sâu xa-gần): rule này về **kích thước thật**. Mọi prompt có phương tiện + người **phải ép tỉ lệ thực**:
   - Tàu hỏa / xe buýt / xe ben / máy kéo / xe tải = **rất to, cao hơn hẳn người lớn**, em bé 3 tuổi (Shopee) chỉ tới ngang **bánh xe / cửa dưới**.
   - Ô tô con / van / taxi = **bự hơn em bé nhiều**, đầu Shopee chỉ tới ngang **cửa kính/nóc capo**.
   - Xe đạp trẻ em = **vừa tầm bé** (yên xe ngang hông bé), không tí hon như đồ chơi.
   - Câu mẫu nhét vào prompt: *"render correct real-world scale: the [vehicle] is [much larger / appropriately sized] relative to the child — [Shopee's head only reaches about X] — do NOT shrink the vehicle or enlarge the child."* Với xe quá to, thêm **slightly low camera angle** để nhấn sự đồ sộ.
   - Nếu AI vẫn sai tỉ lệ: thêm *"exaggerate the size difference; the child is tiny next to the huge [vehicle]"*.

10. **NHÂN VẬT PHỤ KHÔNG GIỐNG REF → 2 nguyên nhân, phải chặn cả hai.** Lỗi đã gặp: gen scene đông (vd cover 4 nhân vật) thì nhân vật phụ (Camp, Tracky…) chỉ giống ~60–70%.
   - **Nguyên nhân 1 — "mô tả chốt" quá sơ sài.** Phải **đọc kỹ character sheet (đọc ảnh PNG)** và tả **ĐẦY ĐỦ mọi chi tiết đặc trưng**, KHÔNG tóm tắt 1 dòng chung chung: vật/rơ-moóc kéo theo (màu **từng nửa**, giá nóc + hành lý), **vị trí & hình dạng công cụ** (cào ở trước hay sau, cong hay thẳng), răng/mắt/lông mày đặc biệt (vd Tracky có **răng thỏ**), mũ, sticker, màu chính xác (steel-blue ≠ bright blue). Thiếu chi tiết nào → AI tự chế generic đúng chỗ đó.
   - **Nguyên nhân 2 — loãng multi-ref.** MJ chỉ bám tốt 2–3 `--cref`; nhồi 4+ ref thì nhân vật phụ méo nhiều nhất. **Cách chặn:** gen từng nhân vật **solo (1 ref) trước để "khoá" 1 ảnh chuẩn 90–100%**, rồi dùng chính ảnh đó làm ref cho cover/scene đông; hoặc dùng tool multi-ref mạnh (Nano Banana / Flux Kontext / Sora); hoặc ghép inpaint. **Đừng kỳ vọng 1 lần gen giữ 90% cho cả 4 nhân vật.** → Đưa bước "khoá nhân vật trước" lên đầu mục "Thứ tự gen đề xuất" của mọi plan.

11. **NGƯỜI Ở CỬA SỔ XE/TÀU → THÂN NGƯỜI PHẢI Ở TRONG XE.** Lỗi đã gặp (story 12, scene 5): tả *"reach his head and hand out the window"* → AI gen **cả 3 nhân vật nhoài nửa thân ra ngoài** — vừa sai vật lý vừa **phản tác dụng với truyện dạy an toàn**. Khi có nhân vật ở cửa sổ/cửa ra vào phương tiện đang chạy:
   - Mặc định tả **"visible through the window, bodies fully inside the vehicle"** — chỉ thấy mặt/đầu qua khung cửa.
   - Nếu cốt truyện cần hành động "định thò ra" (để bị nhắc nhở), chỉ cho **chớm**: *"only just BEGINNING to lean — only the top of his head and one small hand barely peek past the window frame, his whole body still inside"* + câu khoá: *"CRITICAL: no character's torso, chest or shoulders may extend outside the window — all bodies stay completely inside; do NOT show anyone hanging or leaning out."*
   - Thêm vào đuôi `--no`: `people hanging out of windows, torsos leaning out of windows`.
   - Đặc biệt chú ý với **truyện dạy an toàn**: ảnh minh hoạ không được vô tình vẽ hành vi nguy hiểm đậm hơn mức "chớm vi phạm để được nhắc".

12. **ĐỊA ĐIỂM CÓ TÊN/ĐẶC TRƯNG → PHẢI TẢ KIẾN TRÚC CỤ THỂ, ĐỪNG CHỈ NÊU TÊN.** Lỗi đã gặp (story 12, scene 7): prompt chỉ ghi *"a small rural station named Brooms Farm"* → AI ra **sân ke trống trơn, không thấy nhà ga đâu**, ảnh nhạt. Hai nguyên nhân phải chặn cả hai:
   - **Tả rõ kiến trúc + đạo cụ đặc trưng của địa điểm** (ga tàu: nhà ga mái ngói, mái che sân ke, biển tên ga, ghế gỗ, đồng hồ ga, cột đèn; trường học: cổng trường, sân cờ; chợ: sạp hàng, ô dù…) và đưa địa điểm vào **mid/upper frame của composition** — đừng để nhân vật chiếm hết khung còn địa điểm chỉ là một dải nền.
   - **Lệnh cấm `signboards`/`captions` triệt tiêu biển tên địa điểm.** Scene cần hiện tên địa điểm: viết khẳng định *"a wooden platform sign on two posts reading exactly: «Tên», clearly and neatly spelled — DO render this sign"*, bỏ `signboards` khỏi câu cấm trong prompt và bỏ `captions` khỏi đuôi `--no` của riêng scene đó (giống cách xử lý title ở rule #7).

13. **SCENE FULL-CAST (>10 nhân vật, vd bìa tổng series) → AI BỎ SÓT NHÂN VẬT + CO XE THÀNH ĐỒ CHƠI.** Lỗi đã gặp (bìa tổng 36 nhân vật): AI lặng lẽ **bỏ hẳn 3–4 xe** (Max, Titan, Lifty, Posty), gộp/làm mờ đặc điểm các xe nhỏ (Benny/Rody khó phân biệt, Camp mất rơ-moóc, Helly mất cánh quạt), và **co toàn bộ xe thành toy-scale** bé hơn người (vi phạm rule #9 nặng hơn bình thường vì khung quá đông). Cách chặn:
   - Thêm **CHECKLIST ĐẾM** vào cuối prompt: liệt kê đích danh từng nhân vật phải có + câu *"render ALL of these, do not omit any vehicle. Count: N vehicles + M humans."* Nhân vật nào hay bị bỏ → kèm 1 đặc điểm khoá ngay trong checklist (vd *"Titan (giant six-wheel dump truck)"*, *"Helly (WITH visible main rotor blades on top)"*, *"Camp (towing his camping trailer)"*).
   - Khối scale phải **gắt hơn rule #9**: mở đầu *"STRICT REAL-WORLD SCALE — this is NOT a toy scene"* + mốc so sánh cụ thể (*"Poli's roof reaches the father's shoulder height; no vehicle may appear smaller than a human"*).
   - **Trực thăng/máy bay trong scene đông hay bị rụng cánh quạt** → luôn ghi *"WITH visible main rotor blades"*.
   - Sau khi gen: **đếm lại theo checklist** trước khi nghiệm thu; thiếu con nào thì inpaint bổ sung con đó (Nano Banana / Flux Kontext) thay vì gen lại cả ảnh — trừ khi lỗi là scale toàn cục (không inpaint được, phải regen).

14. **CHATGPT TỪ CHỐI VÌ "similarity to third-party content" → THỦ PHẠM LÀ TÊN STUDIO/THƯƠNG HIỆU TRONG PROMPT.** Lỗi đã gặp (story 15, character sheet cô chủ quán): ChatGPT/DALL-E chặn prompt vì cụm **"3D Pixar-style"** (và *"art directed by Pixar"* trong tip cứu style) — tên studio có bản quyền dễ trip guardrail IP; guardrail này **stochastic** (lúc chặn lúc không, prompt cũ từng qua không có nghĩa prompt mới sẽ qua). Cách xử lý:
   - **Mỗi plan phải kèm sẵn "câu style thay thế không thương hiệu"** trong mục TIPS để user tự swap khi bị chặn: thay `3D Pixar-style children's book illustration` bằng `cute stylized 3D-animated children's storybook illustration in an original art style (not imitating any specific studio or franchise)`; thay `art directed by Pixar` bằng `with the polished warmth of a high-end animated feature film`.
   - Thứ tự xử lý khi bị từ chối: **(1) retry nguyên prompt 1 lần** (guardrail stochastic) → **(2) swap câu style như trên** → (3) nếu vẫn chặn, bỏ thêm các tham số Midjourney (`--ar`, `--style raw`, `--no …`) và chuyển thành câu khẳng định (ChatGPT không cần các flag này; ghi *"Square 1:1 image"* / *"Vertical 5:7 portrait image"* thay cho `--ar`).
   - **Giữ nguyên "3D Pixar-style" làm mặc định** cho Midjourney/Flux (không bị chặn, style đã validate 14 truyện) — chỉ swap khi gen bằng ChatGPT/DALL-E và bị từ chối.

15. **SCENE CHIA TAY / DI CHUYỂN → PHẢI KHOÁ HƯỚNG TỪNG NHÂN VẬT SO VỚI CAMERA.** Lỗi đã gặp (story 15, scene 8 tạm biệt Carey): prompt chỉ ghi *"waves goodbye, looking back at the plane"* + *"parents walk a few steps ahead"* → AI vẽ **ngược hướng**: bố mẹ quay lưng đi VỀ PHÍA máy bay (như sắp lên máy bay chứ không phải vừa rời đi), còn bé vẫy về phía camera thay vì vẫy nhân vật được chào. "Looking back / ahead" là **tương đối, không đủ** — AI không biết hướng di chuyển của cả nhóm. Với mọi scene có chia tay, rời đi, đón chào, đi bộ:
   - Khoá **hướng di chuyển của cả nhóm so với camera** trước: *"the family is walking AWAY from the plane, TOWARD the camera"*.
   - Rồi khoá **mặt từng nhân vật**: ai *"faces clearly visible to the camera"*, ai *"turned around — back/shoulder in three-quarter rear view to the camera, face visible in profile as he looks back at X"*.
   - Đối tượng được chào (xe/người ở lại) đặt rõ **ở background phía sau nhân vật ngoái lại**.
   - Chốt bằng 1 câu tóm hướng để AI không lẫn: *"The walking direction is unmistakable: [parents] face the camera, [Shopee] faces the [plane]."*

---

## Series character roster (HARD-CODED — do not ask user about these)

| Character | Giới tính / Loại | Pronoun (EN) | Ref file (relative to project root) |
|-----------|------------------|--------------|-------------------------------------|
| Shopee | **bé trai (boy)** — nhân vật chính | **he / him / his** | `Characters/Shopee.png` |
| Jin | nữ — chị gái Shopee | she / her | `Characters/Jin.png` |
| Mother (Mẹ) | nữ | she / her | `Characters/mother.png` |
| Father (Bố) | nam | he / him | `Characters/father.png` |
| Poli | xe cảnh sát anthropomorphic (blue & white, smiling windshield, chữ "P") | it / the police car character | `Characters/poli.png` |
| Amber | xe cứu thương Robocar Poli (trắng-hồng, chữ thập đỏ) | it | `Characters/Amber.png` |
| Helly | trực thăng cứu hộ Robocar Poli (xanh lá, chữ "H") | it | `Characters/Helly.png` |
| Roy | xe cứu hỏa Robocar Poli (đỏ-vàng, chữ "R") | it | `Characters/roy.png` |

**🚨 CRITICAL GUARDRAIL:** Shopee là **bé trai**. NEVER use "girl / daughter / she / her" for Shopee. Always "little boy / he / him / his / son". Double-check every prompt before writing.

### Extended cast (nhân vật phụ ĐÃ CÓ REF — dùng trực tiếp, không hỏi user)

Ngoài 8 nhân vật lõi trên, series có **~30 nhân vật xe/tàu khác đã có character sheet** trong `Characters/` (xe công trường, xe dịch vụ thành phố, tàu thuyền-cảng, nông trại-du lịch, phản diện Poacher…). **Nguồn chuẩn:** [`Characters/CHARACTERS.md`](../../../Characters/CHARACTERS.md) — có tên, loại, giới tính (anh/chị/em), màu sắc, ký hiệu nhận dạng và tính cách cho từng nhân vật.

→ Khi story dùng các nhân vật này: **đọc CHARACTERS.md, lấy mô tả + ref PNG, KHÔNG PAUSE hỏi user.** Viết một đoạn "mô tả chốt" (xem Bước 2 của output) cho mỗi nhân vật và lặp lại nguyên trong mọi prompt liên quan để giữ nhất quán.

## Workflow (must follow in order)

### Step 1 — Locate inputs

- Story content file: `Shopee-story-N/content` (plain text, no extension)
- Character reference folder: `Characters/` (relative to project root) — kèm `Characters/CHARACTERS.md` là danh bạ nhân vật.
- Output target: `Shopee-story-N/image-prompts-plan.md` (same folder as content)

If invoked but the path doesn't match this pattern, ask the user to clarify which story folder.

### Step 2 — Read & analyze the story content

Read the `content` file. Parse:
- **Title** (dòng đầu, hoặc sau "Bài học:")
- **Topic / lesson** (suy từ nội dung; mục "Bài học cho bé" ở cuối)
- **Narrative body** + character dialogues

### Step 3 — Identify characters in this story

Make a list of characters that appear. For each, resolve in THIS order:
1. **Trong roster lõi** (bảng trên) → dùng gender/pronoun/ref hard-coded.
2. **Có trong `Characters/CHARACTERS.md` / có file ref trong `Characters/`** → dùng mô tả + ref đó. **KHÔNG hỏi user.** (Đọc CHARACTERS.md để lấy màu sắc, ký hiệu, giới tính, tính cách.)
3. **Hoàn toàn mới, KHÔNG có ref** → đây mới là new side character. PAUSE workflow (Step 4).

### Step 4 — Ask about new characters (CHỈ khi thật sự mới, không có ref)

Nếu phát hiện nhân vật mới **không có trong CHARACTERS.md và không có file ref**, hỏi user một câu/nhân vật:

> "Story này có nhân vật mới chưa có ref: **[tên]**. Cho mình biết: (1) giới tính & độ tuổi (nếu là xe thì loại xe + giới tính), (2) màu sắc/đặc điểm nhận dạng, (3) vai trò trong truyện?"

Wait for answers before proceeding. Then generate a **character sheet prompt** for each new character in the output (Bước 2 of the plan).

### Step 5 — Break the story into scenes

Aim for **8–11 narrative scenes** + 1 cover (Scene 0) + 1 infographic ending (final scene). Decide autonomously based on the narrative beats — user said "skill tự quyết, user xem rồi sửa".

Common beats to look for:
- Setup / introduction
- Inciting moment (problem/conflict appears)
- Character's emotional reaction (often anxiety, surprise)
- Flashback / memory of advice (if mentioned in dialogue, e.g., "nhớ lời chị/anh dặn")
- Calming / decision / problem-solving moment
- Action / first attempt
- Help arrives or response from others (often TEAMWORK — nhiều xe mỗi xe một việc → đây thường là scene đông, áp dụng HARD RULE #4 phối cảnh)
- Reunion / payoff
- Celebration / praise from supporting characters
- Final lesson page (infographic)

### Step 6 — Map characters to scenes

For EACH scene, decide which characters appear. Build a lookup matrix:

| Scene | Shopee | Mother | Jin | [other roster] | [extended cast] |
|-------|:------:|:------:|:---:|:--------------:|:---------------:|

This matrix goes near the top of the output file. Dùng `(bg)` cho nhân vật chỉ xuất hiện mờ ở background.

### Step 7 — Write the output file

Use the **EXACT template** in the next section. Write to `Shopee-story-N/image-prompts-plan.md`.
- Nếu story có **nhân vật xe/tàu** → MỞ ĐẦU file bằng khối **"⚠️ 2 QUY TẮC BẮT BUỘC"** (chặn tay-người + giữ logo/ký hiệu) như mẫu Story 9/10.
- Đưa "mô tả chốt" từng nhân vật xe vào **Bước 2**.

### Step 8 — Confirm with user

After writing, summarize in a short message: scene count, characters used (đặc biệt nhân vật phụ lấy từ CHARACTERS.md), file path. Mention they can request edits to scenes/order.

---

## Output template (write EXACTLY this structure)

```markdown
# Plan tạo ảnh AI cho Story N: "[Tên truyện]"

## Tổng quan
- **Chủ đề:** [topic / lesson]
- **Số scene đề xuất:** [total] ảnh (1 cover + [N] scene nội dung + 1 infographic bài học)
- **Khổ in:** Sách A5 (148 × 210 mm) — **portrait/dọc**, aspect ratio `5:7` (gần A5 chuẩn) hoặc `2:3` nếu tool không hỗ trợ 5:7
- **Character refs cần upload:** [list of characters appearing in this story]

---

## ⚠️ 2 QUY TẮC BẮT BUỘC CHO MỌI PROMPT  (CHỈ thêm khối này nếu story có nhân vật XE/TÀU)

1. **Xe/tàu KHÔNG có tay/bàn tay người** — vehicle form, chỉ khuôn mặt (mắt+miệng); ngoại lệ bộ phận máy (cần cẩu, chổi cơ khí, gàu, mỏ neo). Con người vẫn có tay.
2. **Chặn bong bóng thoại/chữ rác NHƯNG giữ logo áo (TOGETHER / MEMORIES Let's grow TOGETHER) + ký hiệu xe (TAXI, phong bì, logo R, logo tái chế, chữ P…).** Không dùng `--no text/words/letters`.

---

## QUY TRÌNH THỰC HIỆN (Step-by-step)

### Bước 1: Chuẩn bị reference characters

Upload các ảnh sau lên AI tool (Midjourney/Nano Banana/Sora/Flux):
- [Characters/<file>.png](../Characters/<file>.png) → <Tên nhân vật> (+ ghi chú logo áo / ký hiệu xe)
- ... (only list characters that appear in this story)

### Bước 2: Tạo / mô tả chốt nhân vật

- Nếu nhân vật **đã có ref** (kể cả extended cast): ✅ không cần gen sheet. Viết một **đoạn "mô tả chốt"** (tiếng Anh) cho mỗi nhân vật xe/tàu — vehicle form, màu sắc, ký hiệu, "no human arms or hands" — để dùng nguyên trong mọi prompt.
- Nếu có **nhân vật mới không ref**: gen character sheet trước:
\`\`\`
Character sheet of <description from user answer>, T-pose and 3/4 view, white background, consistent character design for children's book. 3D Pixar-style children's book illustration, soft cinematic lighting, warm vibrant colors, cute chibi proportions, high detail, friendly atmosphere, professional children's storybook art. --ar 1:1 --style raw
\`\`\`

### Bước 3: Gen từng scene theo thứ tự

Với mỗi scene: **upload đúng character refs liệt kê ở đầu scene → copy nguyên prompt → paste → gen**.
Mỗi prompt đã chứa sẵn Style Bible + tham số A5 + câu nhắc match reference (+ chặn tay-người/chữ rác nếu có xe), không cần thêm gì.

#### 📋 Bảng tra cứu nhanh: Scene nào cần ref nào

| Scene | Shopee | Mother | Jin | ... | [extended cast] |
|-------|:------:|:------:|:---:|:---:|:---------------:|
| 0 — Cover | ... |
| ... |

> **Lưu ý:** Midjourney chấp nhận tối đa ~2–3 `--cref` cùng lúc; với scene đông nhân vật nên gen 2–3 lần và pick bản map ref chuẩn nhất, hoặc dùng tool hỗ trợ multi-ref tốt hơn (Nano Banana, Flux Kontext, Sora). Scene đông: ưu tiên giữ chuẩn Shopee + 1–2 nhân vật gần nhất, còn lại để xa/blur ở background.

---

## CÁC PROMPT CHI TIẾT (Copy & Paste 1 lần là xong)

---

### 🎬 SCENE 0 — COVER (Bìa truyện)
**Mục đích:** Ảnh bìa, giới thiệu chủ đề.
**👥 Refs cần upload:** <list>

\`\`\`
<English prompt - see "Prompt construction rules" below>
\`\`\`

---

### 🎬 SCENE 1 — [Tên scene tiếng Việt]
**Bối cảnh:** [1-2 câu tiếng Việt]
**👥 Refs cần upload:** <list>

\`\`\`
<English prompt>
\`\`\`

[... repeat for all scenes ...]

---

### 🎬 SCENE [N] — Bài học kết (Infographic)
**Mục đích:** Trang tổng kết bài học cho bé.
**👥 Refs cần upload:** Shopee (+ ai khác nếu hợp lý)

\`\`\`
<English infographic prompt>
\`\`\`

---

## TIPS QUAN TRỌNG

### 🚫 Chặn xe/tàu mọc tay người & chặn chữ/bong bóng thoại (lỗi hay gặp)
- Mỗi prompt có xe đã sẵn câu *"every vehicle is in pure vehicle form with only a cute cartoon face… NO human arms, NO hands, NO fingers"* + đuôi `--no … human arms on vehicles, human hands on vehicles`.
- Nếu xe **vẫn mọc tay**: thêm `the vehicle has absolutely no humanlike arms, hands, fingers or gloves; it is a normal vehicle body with only a face on the front` và `--no human arms, human hands, fingers, gloves`.
- Bộ phận máy (cần cẩu/chổi/gàu/mỏ neo) → giữ, đừng chặn.
- Nếu hiện **chữ rác/bong bóng**: tăng `--no speech bubble, caption, signboard, typography`. ⚠️ **Đừng** thêm `--no text/words/letters` (mất logo áo + ký hiệu xe).
- Nếu **logo áo thiếu/mờ**: nhấn mạnh logo trong prompt + upload đúng ref; ảnh in to thì **overlay logo sạch khi hậu kỳ**.
- Chỉ cấm tay ở **xe**; **người vẫn có tay** → không dùng `--no hands` trống.

### Phối cảnh xa-gần (scene đông / cảnh rộng)
Thêm khối: *"Strong three-layer depth with correct near-far perspective: [main char] largest in the immediate foreground at the bottom; [group] in the midground at larger scale; [distant things] farther back, smaller and softly hazy with atmospheric perspective. Streets/lines recede diagonally toward a vanishing point. Eye-level, slightly low camera angle, wide cinematic lens, deep depth of field."*

### Giữ nhất quán nhân vật
- **Luôn upload ref ảnh nhân vật** ở mỗi prompt (Midjourney: `--cref URL`, Nano Banana: attach image).
- Nhân vật xe/tàu: luôn dùng đúng ref trong `Characters/` + giữ nguyên "mô tả chốt" ở Bước 2.
- Nhân vật mới (nếu có): dùng character sheet đã tạo ở Bước 2 làm ref.

### Nếu nhân vật bị lệch style
Thêm vào prompt:
\`\`\`
consistent character design matching the reference image, same face shape, same outfit, same proportions
\`\`\`

### Nếu ảnh ra quá "AI-generated" giả tạo
Thêm:
\`\`\`
hand-painted storybook quality, subtle texture, not overly glossy, art directed by Pixar
\`\`\`

### Tỷ lệ in A5 (148 × 210 mm)

- **Chuẩn nhất:** `--ar 5:7` (rất gần tỉ lệ A5 thật ≈ 1:1.414)
- **Thay thế nếu tool không nhận 5:7:** `--ar 2:3`
- **Khi gen xong:** Export ở DPI ≥ 300 để in A5 nét. Kích thước pixel tối thiểu nên là **1748 × 2480 px** (A5 @ 300 DPI).

### Thứ tự gen đề xuất
1. Gen **Scene 0 (cover)** trước → chốt style tổng + "look" các xe (không tay người, giữ ký hiệu).
2. Gen **scene đông nhân vật nhất** (vd teamwork) → chốt thiết kế nhất quán cho các xe.
3. Gen character sheet nhân vật mới (nếu có).
4. Gen lần lượt **Scene 1 → N-1** theo thứ tự câu chuyện.
5. Gen **Scene N (infographic)** cuối cùng.

---

## CHECKLIST HOÀN THÀNH
- [ ] Scene 0 — Cover
- [ ] Character sheet [nhân vật mới] (nếu có)
- [ ] Scene 1 — [tên]
- [ ] Scene 2 — [tên]
- ...
```

---

## Prompt construction rules (CRITICAL — apply to every scene prompt)

Each scene prompt is **one long English paragraph** containing these elements in order:

1. **Opening narrative**: Describe the action, who is doing what, emotion, posture, gaze.
   - Always identify Shopee as `"little boy Shopee"` (NEVER "girl").
   - Reference other characters with the correct gender per roster / CHARACTERS.md.

2. **Setting**: Where the scene takes place (modern Vietnamese supermarket, cozy living room, city street, seaport, construction site…), lighting mood (warm overhead light, soft golden hour, desaturated cool tones for anxiety, etc.).

3. **Composition note (portrait-specific)**: e.g., "Vertical portrait composition with [framing detail]", "low camera angle looking up", "medium close-up shot", "split composition upper/lower half" (use upper/lower NOT left/right for portrait). **Scene đông/rộng → thêm khối phối cảnh xa-gần 3 lớp (HARD RULE #4).**

4. **Vehicle no-human-arms instruction** (BẮT BUỘC nếu có xe/tàu):
   > `IMPORTANT: every vehicle/boat is in pure vehicle form with only a cute cartoon face (eyes and mouth) on its front — NO human arms, NO hands, NO fingers; [mechanical parts like crane booms, sweeper brush arm, anchors are fine]. They emote through facial expression, body tilt and their machine parts.`

5. **Text-handling instruction** (BẮT BUỘC):
   > `No speech bubbles, no dialogue balloons, no signboards and no random floating text or captions anywhere in the image — but DO keep the printed wordmark on the family members' shirts and the vehicles' design markings (it is part of their design, not unwanted text).`

6. **Character match instruction** (mandatory, names the characters in the scene):
   > `[Character names] must exactly match the uploaded reference images — same face shape, same outfit — Shopee in his brown T-shirt with the printed wordmark TOGETHER clearly visible on the chest[, and the parents in their T-shirts printed MEMORIES Let's grow TOGETHER] — same proportions[, same vehicle design].`

7. **Style Bible** (verbatim, every prompt):
   > `3D Pixar-style children's book illustration, soft cinematic lighting, warm vibrant colors, cute chibi proportions, high detail, friendly atmosphere, professional children's storybook art, A5 portrait page layout with safe margins for print, leave safe margins, no important details near edges.`

8. **Suffix** (verbatim):
   - Scene có xe/tàu: `--ar 5:7 --style raw --no speech bubbles, dialogue balloons, thought bubbles, captions, human arms on vehicles, human hands on vehicles, watermark, signature`
   - Scene chỉ có người (không xe): `--ar 5:7 --style raw --no speech bubbles, dialogue balloons, thought bubbles, captions, watermark, signature`
   - **Cover (Scene 0) — cố ý render tiêu đề:** bỏ `captions` khỏi đuôi. Nếu có xe: `--ar 5:7 --style raw --no speech bubbles, dialogue balloons, thought bubbles, human arms on vehicles, human hands on vehicles, watermark, signature`.
   - **Infographic (cố ý có chữ + tiêu đề):** chỉ `--ar 5:7 --style raw` (KHÔNG có `--no`).

**Pronoun guardrails** (re-check before writing each prompt):
- Shopee → `he / him / his / boy / son`. **Never** `she / her / girl / daughter`.
- Jin → `she / her / older sister`.
- Mother → `she / her / mother`. Father → `he / him / father`.
- Vehicle characters → giới tính theo CHARACTERS.md (anh/chị/em) khi viết truyện; khi gen ảnh mô tả là *"the [color] [vehicle type] character named X"*. Pronoun EN: `it` cho roster lõi, hoặc `he/she` theo sheet với extended cast (vd Cici/Mini/Amber = she).

**Special elements to use when appropriate:**
- Flashback → thought bubble with cloud-like edges, upper half of portrait
- Emotional anxiety → "slightly desaturated cooler tones, still child-friendly and not scary"
- Calm/decision moment → "subtle glowing aura of calm"
- Reunion joy → "sparkles and small heart particles floating in the air"
- Movement → "subtle motion blur lines"
- Honking / sound → "little sound-burst marks around the horn" (đừng dùng chữ "BEEP")
- Educational infographic → "soft rounded pastel-colored bubbles", "clean white background with subtle dotted pattern", numbered tips, và **render tiêu đề bài học** ở banner trên cùng: *"a title banner at the top rendering exactly: «Bài học: …» in large bold clean lettering with correct Vietnamese diacritics"* (xem HARD RULE #7 — KHÔNG để trống title mặc định)
- Tiêu đề cover → RENDER thẳng tên truyện ở banner trên cùng (HARD RULE #7), bỏ `captions` khỏi đuôi `--no`

---

## Canonical reference
- **Cấu trúc & tone:** `Shopee-story-1/image-prompts-plan.md` (bản đầu user đã validate).
- **Mẫu story có nhân vật xe/tàu (đầy đủ HARD RULES):** `Shopee-story-9/image-prompts-plan.md` (cảng biển) và `Shopee-story-10/image-prompts-plan.md` (xe dịch vụ thành phố) — copy khối "2 QUY TẮC BẮT BUỘC", "mô tả chốt", và scene teamwork có phối cảnh xa-gần từ đây.
- **Danh bạ nhân vật:** `Characters/CHARACTERS.md`.
Read the relevant one before generating a new story to match format exactly.

## When the user says "edit scene X" or "thêm/bớt scene"
Just edit the existing `image-prompts-plan.md` directly — don't regenerate the whole file. Preserve all other scenes.
