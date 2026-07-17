#!/usr/bin/env python3
"""Build slideshow sinh nhật từ ẢNH ĐÃ GOM SẴN THEO THƯ MỤC (mỗi thư mục = 1 chủ đề/slide).

Khác với build_birthday_scenes.py (tự gom ảnh từ albums/ theo giờ EXIF), script này
đọc thư mục do người dùng gom sẵn:

    <SRC>/Slide 0. <caption>            (có thể là 1 FILE ảnh, hoặc 1 THƯ MỤC ảnh)
    <SRC>/Slide 1. Shopee tháng 8/      (thư mục nhiều ảnh)
    ...

- Số "N" trong "Slide N." dùng để SẮP THỨ TỰ; phần chữ còn lại làm CAPTION banner.
- Chủ đề có >3 ảnh -> tự chia thành nhiều slide (2-3 ảnh/slide) CÙNG caption.
- Ảnh .heic được convert sang jpg bằng `sips` (macOS).
- Ảnh thật đặt đè lên nền cảnh AI (Shopee-birthday/scenes/*.png), tái dùng layout/frame
  và template của build_birthday_scenes.py.

Usage:
    python3 tools/build_birthday_from_folders.py
    python3 tools/build_birthday_from_folders.py --src "Shopee-birthday/new_photo/Shopee 3t" --seconds 5
"""
import argparse
import copy
import itertools
import json
import random
import re
import subprocess
import sys
import tempfile
import unicodedata
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_birthday_scenes import (  # tái dùng kho layout + tiện ích
    LAYOUTS, SINGLES, DOUBLES, TRIPLES, scale_slots, exif_dt,
)

ROOT = Path(__file__).resolve().parent.parent
BDIR = ROOT / "Shopee-birthday"
PHOTOS = BDIR / "photos"
SCENES = BDIR / "scenes"
TPL = ROOT / "tools" / "birthday_scene_template.html"
OUT = BDIR / "index.html"
DEFAULT_SRC = BDIR / "new_photo" / "Shopee 3t"

TITLE, SUBTITLE = "Sinh nhật Shopee", "3 tuổi"

# Layout thêm cho slide NHIỀU ảnh (stage 1920x1080, toạ độ theo TÂM khung).
# Ảnh nằm trong vùng giữa của cảnh AI; grid cân đối, xoay nhẹ cho tự nhiên.
EXTRA_LAYOUTS = {
    # 4 ảnh — lưới 2x2 (khung to, kéo sát tâm, cho đè nhẹ để tăng diện tích ảnh)
    "q_grid": [{"cx": 775, "cy": 334, "w": 430, "h": 448, "rot": -3, "frame": "polaroid"},
               {"cx": 1145, "cy": 328, "w": 430, "h": 448, "rot": 2, "frame": "clip"},
               {"cx": 775, "cy": 794, "w": 430, "h": 448, "rot": 2, "frame": "clip"},
               {"cx": 1145, "cy": 800, "w": 430, "h": 448, "rot": -2, "frame": "polaroid"}],
    "q_stag": [{"cx": 775, "cy": 326, "w": 426, "h": 436, "rot": -5, "frame": "tape"},
               {"cx": 1145, "cy": 340, "w": 434, "h": 448, "rot": 4, "frame": "polaroid"},
               {"cx": 775, "cy": 800, "w": 434, "h": 448, "rot": 3, "frame": "polaroid"},
               {"cx": 1145, "cy": 786, "w": 426, "h": 436, "rot": -4, "frame": "clip"}],
    # 5 ảnh — 2 trên + 3 dưới  /  3 trên + 2 dưới
    "p_2_3": [{"cx": 680, "cy": 360, "w": 520, "h": 414, "rot": -3, "frame": "polaroid"},
              {"cx": 1240, "cy": 360, "w": 520, "h": 414, "rot": 3, "frame": "polaroid"},
              {"cx": 480, "cy": 750, "w": 452, "h": 360, "rot": -4, "frame": "clip"},
              {"cx": 960, "cy": 762, "w": 452, "h": 360, "rot": 2, "frame": "tape"},
              {"cx": 1440, "cy": 750, "w": 452, "h": 360, "rot": -3, "frame": "clip"}],
    "p_3_2": [{"cx": 480, "cy": 372, "w": 452, "h": 360, "rot": -4, "frame": "clip"},
              {"cx": 960, "cy": 360, "w": 452, "h": 360, "rot": 2, "frame": "polaroid"},
              {"cx": 1440, "cy": 372, "w": 452, "h": 360, "rot": -3, "frame": "clip"},
              {"cx": 700, "cy": 756, "w": 520, "h": 414, "rot": 3, "frame": "polaroid"},
              {"cx": 1260, "cy": 756, "w": 520, "h": 414, "rot": -3, "frame": "tape"}],
    # 6 ảnh — lưới 3x2
    "s_grid": [{"cx": 490, "cy": 372, "w": 452, "h": 360, "rot": -3, "frame": "clip"},
               {"cx": 960, "cy": 360, "w": 452, "h": 360, "rot": 2, "frame": "polaroid"},
               {"cx": 1430, "cy": 372, "w": 452, "h": 360, "rot": -2, "frame": "clip"},
               {"cx": 490, "cy": 748, "w": 452, "h": 360, "rot": 3, "frame": "polaroid"},
               {"cx": 960, "cy": 760, "w": 452, "h": 360, "rot": -2, "frame": "tape"},
               {"cx": 1430, "cy": 748, "w": 452, "h": 360, "rot": 3, "frame": "clip"}],
    # 8 ảnh — lưới 4x2 (khung to, sát lại, cho đè nhẹ để tăng diện tích ảnh)
    "e_grid": [{"cx": 440, "cy": 346, "w": 400, "h": 400, "rot": -3, "frame": "clip"},
               {"cx": 785, "cy": 334, "w": 400, "h": 400, "rot": 2, "frame": "polaroid"},
               {"cx": 1130, "cy": 334, "w": 400, "h": 400, "rot": -2, "frame": "polaroid"},
               {"cx": 1475, "cy": 346, "w": 400, "h": 400, "rot": 3, "frame": "clip"},
               {"cx": 440, "cy": 770, "w": 400, "h": 400, "rot": 3, "frame": "polaroid"},
               {"cx": 785, "cy": 782, "w": 400, "h": 400, "rot": -2, "frame": "tape"},
               {"cx": 1130, "cy": 782, "w": 400, "h": 400, "rot": 2, "frame": "tape"},
               {"cx": 1475, "cy": 770, "w": 400, "h": 400, "rot": -3, "frame": "polaroid"}],
}
ALL_LAYOUTS = {**LAYOUTS, **EXTRA_LAYOUTS}
QUADS = ["q_grid", "q_stag"]
QUINTS = ["p_2_3", "p_3_2"]
SIXES = ["s_grid"]
EIGHTS = ["e_grid"]
# số ảnh -> danh sách layout khớp đúng số đó (xoay vòng để đa dạng)
COUNT_LAYOUTS = {1: SINGLES, 2: DOUBLES, 3: TRIPLES,
                 4: QUADS, 5: QUINTS, 6: SIXES, 8: EIGHTS}

# padding NGANG (px) của mỗi kiểu khung (để tính đúng vùng ảnh trong khung)
FRAME_PAD = {"polaroid": 30, "clip": 28, "tape": 24, "color": 32,
             "gold": 38, "round": 28, "circle": 32}


def fit_slot(slot, ar):
    """Chỉnh w/h của ô cho KHỚP tỉ lệ ảnh (ar = rộng/cao), nằm gọn trong vùng bố cục.
    Nhờ vậy object-fit:cover gần như không cắt -> thấy toàn cảnh. Khung tròn giữ vuông."""
    frame = slot.get("frame", "polaroid")
    if frame == "circle":
        return
    bw, bh = slot["w"], slot["h"]
    pad = FRAME_PAD.get(frame, 30)
    if ar >= (bw - pad) / bh:      # ảnh ngang hơn ô -> giới hạn theo chiều rộng
        slot["w"] = bw
        slot["h"] = int(round((bw - pad) / ar))
    else:                         # ảnh dọc hơn ô -> giới hạn theo chiều cao
        slot["h"] = bh
        slot["w"] = int(round(bh * ar + pad))


def align_hanging(slots):
    """Ảnh 'treo dây' (khung kẹp clip) cùng một hàng thì canh MÉP TRÊN bằng nhau,
    thay vì canh tâm — để ảnh ngang không bị treo thấp hơn ảnh dọc."""
    clips = sorted((s for s in slots if s.get("frame") == "clip"),
                   key=lambda s: s["cy"])
    rows = []
    for s in clips:
        if rows and s["cy"] - rows[-1][-1]["cy"] <= 120:
            rows[-1].append(s)          # cùng hàng (cy gần nhau)
        else:
            rows.append([s])
    for row in rows:
        if len(row) >= 2:
            top = min(x["cy"] - x["h"] / 2 for x in row)
            for x in row:
                x["cy"] = int(round(top + x["h"] / 2))


def jitter(slots, seed):
    """Lệch nhẹ vị trí + xoay mỗi ảnh một hướng cho đỡ đơn điệu (mỗi slide 1 seed
    -> khác nhau giữa các slide nhưng ổn định qua các lần build)."""
    rng = random.Random(seed)
    for s in slots:
        s["cx"] += rng.randint(-40, 40)
        s["cy"] += rng.randint(-28, 28)
        s["rot"] = round(s.get("rot", 0) + rng.uniform(-3, 3), 1)
IMG_EXT = (".jpg", ".jpeg", ".png", ".heic", ".heif")
SLIDE_RE = re.compile(r"^Slide\s+(\d+)\s*[.\-]?\s*(.*)$", re.IGNORECASE)


def clean_caption(text: str) -> str:
    """Bỏ đuôi mở rộng nếu lỡ dính, gọn khoảng trắng/underscore."""
    text = unicodedata.normalize("NFC", text)  # macOS lưu tên file dạng NFD
    text = re.sub(r"\.(jpg|jpeg|png|heic|heif)$", "", text, flags=re.IGNORECASE)
    text = text.replace("_", " – ").strip()
    text = re.sub(r"\s+", " ", text)
    # bỏ tiền tố "Chúc mừng sinh nhật ... -" (câu intro Slide 0), giữ phần sau dấu gạch
    if text.lower().startswith("chúc mừng") and " - " in text:
        text = text.split(" - ", 1)[1].strip()
    # bỏ số thứ tự ở cuối (vd "Nha Trang 1" -> "Nha Trang"), TRỪ dạng "tháng N"
    if not re.search(r"tháng\s*\d+\s*$", text, re.IGNORECASE):
        text = re.sub(r"\s*\d+\s*$", "", text).strip()
    return text


def load_image(path: Path) -> Image.Image:
    """Mở ảnh; .heic -> convert qua sips ra file tạm rồi mở."""
    if path.suffix.lower() in (".heic", ".heif"):
        tmp = Path(tempfile.mkstemp(suffix=".jpg")[1])
        subprocess.run(["sips", "-s", "format", "jpeg", str(path), "--out", str(tmp)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        im = Image.open(tmp)
        im.load()
        tmp.unlink(missing_ok=True)
        return im
    return Image.open(path)


def chunk_sizes(n: int):
    """Chia n ảnh thành các cụm 2-3 (tránh cụm lẻ 1 khi n>=2). n==1 -> [1]."""
    if n <= 1:
        return [n] if n else []
    if n == 2:
        return [2]
    r = n % 3
    if r == 0:
        return [3] * (n // 3)
    if r == 2:
        return [3] * (n // 3) + [2]
    # r == 1: đổi một cụm 3 thành hai cụm 2  (n>=4)
    return [3] * (n // 3 - 1) + [2, 2]


def list_topic_images(entry: Path):
    """Trả list Path ảnh của 1 chủ đề (entry là file -> [file]; là thư mục -> ảnh bên trong)."""
    if entry.is_file():
        return [entry] if entry.suffix.lower() in IMG_EXT else []
    imgs = [p for p in entry.iterdir()
            if p.is_file() and p.suffix.lower() in IMG_EXT and not p.name.startswith(".")]

    def keyf(p):
        nums = [int(x) for x in re.findall(r"\d+", p.stem)]
        return (nums, p.name.lower())
    return sorted(imgs, key=keyf)


def gather_topics(src: Path):
    """Đọc <src>, trả list (order, caption, [image_paths]) đã sắp theo N."""
    topics = []
    for entry in src.iterdir():
        if entry.name.startswith("."):
            continue
        stem = entry.stem if entry.is_file() else entry.name
        m = SLIDE_RE.match(stem)
        if not m:
            continue
        order = int(m.group(1))
        caption = clean_caption(m.group(2))
        imgs = list_topic_images(entry)
        if not imgs:
            print(f"  · bỏ qua (rỗng): {entry.name}")
            continue
        topics.append((order, caption, imgs))
    topics.sort(key=lambda t: t[0])
    return topics


def scene_pool(scenes_dir: Path):
    """Gom cảnh theo tiền tố (blue*/scene*), sắp số, xen kẽ round-robin."""
    buckets = defaultdict(list)
    for p in scenes_dir.glob("*.png"):
        if p.stem.startswith("cover"):
            continue
        prefix = "".join(ch for ch in p.stem if not ch.isdigit())
        buckets[prefix].append(p.name)
    for k in buckets:
        buckets[k].sort(key=lambda n: int("".join(filter(str.isdigit, n)) or "0"))
    scenes = [x for row in itertools.zip_longest(*[buckets[k] for k in sorted(buckets)])
              for x in row if x]
    if not scenes:
        raise SystemExit(f"Chưa có cảnh nào trong {scenes_dir}.")
    return scenes, sorted(buckets)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(DEFAULT_SRC), help="thư mục chứa các 'Slide N. ...'")
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--no-captions", action="store_true")
    args = ap.parse_args()

    src = Path(args.src).resolve()
    if not src.exists():
        raise SystemExit(f"Không thấy thư mục nguồn: {src}")

    scenes_dir = SCENES.resolve()
    scene_rel = scenes_dir.relative_to(BDIR).as_posix()
    scenes, bucket_names = scene_pool(scenes_dir)
    print(f"Kho cảnh: {len(scenes)} (xen kẽ {bucket_names}) | layout: {len(LAYOUTS)}")

    topics = gather_topics(src)
    print(f"Chủ đề (thư mục): {len(topics)}")

    # chuẩn hoá ảnh -> photos/pNNN.jpg, đồng thời dựng cấu trúc chunk theo chủ đề
    PHOTOS.mkdir(parents=True, exist_ok=True)
    for old in PHOTOS.glob("p*.jpg"):
        old.unlink()

    idx = 0
    topic_metas = []  # list of (caption, [photo_meta,...])  — mỗi topic = 1 slide
    for order, caption, imgs in topics:
        metas = []
        for p in imgs:
            try:
                im = ImageOps.exif_transpose(load_image(p)).convert("RGB")
            except Exception as e:
                print(f"  ! lỗi đọc ảnh, bỏ qua: {p.name} ({e})")
                continue
            im.thumbnail((args.max_px, args.max_px), Image.LANCZOS)
            w, h = im.size
            idx += 1
            fn = f"p{idx:03d}.jpg"
            im.save(PHOTOS / fn, "JPEG", quality=args.quality, optimize=True)
            metas.append({"file": fn, "orient": "land" if w > h else "port",
                          "ar": round(w / h, 4)})
        if not metas:
            continue
        n = len(metas)
        note = "" if n in COUNT_LAYOUTS else "  (không có layout khớp -> chia nhỏ)"
        topic_metas.append((caption, metas))
        print(f"  Slide {order:>2} · {caption[:42]:<42} {n} ảnh{note}")

    print(f"Tổng ảnh dùng: {idx}")

    # dựng SLIDES
    if (scenes_dir / "cover.png").exists():
        slides = [{"type": "coverimg", "scene": scene_rel + "/cover.png"}]
    else:
        slides = [{"type": "cover", "scene": scene_rel + "/" + scenes[0],
                   "text": "Chúc mừng sinh nhật<br>Shopee", "date": "Tròn 3 tuổi 🎉"}]

    counters = defaultdict(int)  # xoay vòng biến thể layout theo từng số ảnh
    sc = 1  # chỉ số cảnh (bỏ cover)

    def emit(caption, metas):
        nonlocal sc
        cnt = len(metas)
        keys = COUNT_LAYOUTS[cnt]
        key = keys[counters[cnt] % len(keys)]; counters[cnt] += 1
        slots = copy.deepcopy(ALL_LAYOUTS[key])
        if cnt == 1:
            # ảnh đơn: vùng giữa lớn; khung sẽ co theo đúng tỉ lệ ảnh ở fit_slot
            slots[0]["cx"], slots[0]["cy"] = 960, 556
            if slots[0].get("frame") == "circle":
                slots[0]["w"], slots[0]["h"] = 820, 820
            else:
                slots[0]["w"], slots[0]["h"] = 1180, 900
        for slot, m in zip(slots, metas):
            fit_slot(slot, m["ar"])
        if cnt > 1:
            jitter(slots, sc)      # lệch ngẫu nhiên cho đa dạng (ảnh đơn giữ nguyên giữa)
        align_hanging(slots)
        slides.append({
            "type": "photo",
            "scene": scene_rel + "/" + scenes[sc % len(scenes)],
            "caption": "" if args.no_captions else caption,
            "slots": slots,
            "photos": ["photos/" + m["file"] for m in metas],
        })
        sc += 1

    for caption, metas in topic_metas:
        if len(metas) in COUNT_LAYOUTS:
            emit(caption, metas)                 # 1 folder = 1 slide, layout khớp số ảnh
        else:                                    # số ảnh lạ (7, >8...) -> chia nhỏ 2-3
            start = 0
            for size in chunk_sizes(len(metas)):
                emit(caption, metas[start:start + size])
                start += size

    # nhạc
    music_dir = BDIR / "music"
    if music_dir.exists():
        mfiles = sorted([p.name for p in music_dir.iterdir()
                         if p.suffix.lower() in (".mp3", ".m4a", ".wav", ".aac")],
                        key=lambda n: int("".join(filter(str.isdigit, n)) or "0"))
        music_list = ["music/" + f for f in mfiles]
    else:
        music_list = []
    print(f"Nhạc slideshow: {len(music_list)} bài")

    # SFX slide cuối (pháo hoa + vỗ tay): mọi file trong Shopee-birthday/sfx/
    sfx_dir = BDIR / "sfx"
    sfx_list = []
    if sfx_dir.exists():
        sfx_list = ["sfx/" + p.name for p in sorted(sfx_dir.iterdir())
                    if p.suffix.lower() in (".wav", ".mp3", ".m4a", ".aac")]
    print(f"SFX slide cuối: {len(sfx_list)} file")

    html = TPL.read_text(encoding="utf-8")
    for k, v in {
        "__TITLE__": TITLE, "__SUBTITLE__": SUBTITLE,
        "__SLIDE_MS__": str(int(args.seconds * 1000)),
        "__MUSIC_JSON__": json.dumps(music_list, ensure_ascii=False),
        "__SFX_JSON__": json.dumps(sfx_list, ensure_ascii=False),
        "__SLIDES_JSON__": json.dumps(slides, ensure_ascii=False),
    }.items():
        html = html.replace(k, v)
    OUT.write_text(html, encoding="utf-8")
    photo_slides = sum(1 for s in slides if s["type"] == "photo")
    print(f"✓ Ghi {OUT.relative_to(ROOT)} ({len(slides)} slide, {photo_slides} slide ảnh, {args.seconds}s/slide)")


if __name__ == "__main__":
    main()
