#!/usr/bin/env python3
"""Build slideshow sinh nhật Shopee: chuẩn hoá ảnh thật + ghép vào template Robocar.

- Đọc ảnh gốc từ  albums/  (JPG iPhone: tự xoay theo EXIF, sắp theo giờ chụp).
- Chuẩn hoá -> Shopee-birthday/photos/pNN.jpg (resize, nén).
- Sinh SLIDES (cover + ảnh + outro), fill tools/birthday_template.html.
- Ghi Shopee-birthday/index.html. Cảnh báo nếu thiếu decoration.

Usage:
    python3 tools/build_birthday_slideshow.py
    python3 tools/build_birthday_slideshow.py --seconds 4.5 --max 60
"""
import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ALBUMS = ROOT / "albums"
BDIR = ROOT / "Shopee-birthday"
PHOTOS = BDIR / "photos"
DECOR = BDIR / "decorations"
TPL = ROOT / "tools" / "birthday_template.html"
OUT = BDIR / "index.html"

REQUIRED_DECOR = ["confetti_overlay", "bunting", "balloons_bunch", "number3",
                  "poli", "roy", "amber", "rody_cake", "shopee_mascot"]

TITLE = "Chúc mừng sinh nhật Shopee"
SUBTITLE = "Tròn 3 tuổi 🎉"
DATE = ""  # vd "16 · 07 · 2026"


def exif_dt(img):
    try:
        ex = img.getexif()
        try:  # DateTimeOriginal nằm trong Exif sub-IFD (0x8769)
            sub = ex.get_ifd(0x8769)
            if sub.get(36867):
                return str(sub[36867])
        except Exception:
            pass
        if ex.get(306):  # DateTime (base IFD) — fallback
            return str(ex[306])
    except Exception:
        pass
    return ""


def normalize(max_px, quality):
    PHOTOS.mkdir(parents=True, exist_ok=True)
    srcs = sorted([p for p in ALBUMS.iterdir()
                   if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    metas = []
    for p in srcs:
        with Image.open(p) as im:
            dt = exif_dt(im)
        metas.append((dt or "9999", p.name, p))
    metas.sort(key=lambda m: (m[0], m[1]))  # theo giờ chụp, rồi tên

    out = []
    for i, (_, _, p) in enumerate(metas, 1):
        im = Image.open(p)
        im = ImageOps.exif_transpose(im)          # xoay đúng chiều
        im = im.convert("RGB")
        im.thumbnail((max_px, max_px), Image.LANCZOS)
        w, h = im.size
        fn = f"p{i:02d}.jpg"
        im.save(PHOTOS / fn, "JPEG", quality=quality, optimize=True)
        out.append({"file": fn, "orient": "land" if w > h else "port"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=4.5, help="giây mỗi ảnh")
    ap.add_argument("--max", type=int, default=0, help="giới hạn số ảnh (0 = tất cả)")
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--music", default="", help="tên file nhạc trong Shopee-birthday/ (vd music.mp3)")
    ap.add_argument("--skip-normalize", action="store_true")
    args = ap.parse_args()

    # decorations check
    missing = [d for d in REQUIRED_DECOR if not (DECOR / f"{d}.png").exists()]
    if missing:
        print("⚠️  Thiếu decoration (chạy gen_birthday_decorations.py trước):", ", ".join(missing))

    if args.skip_normalize and PHOTOS.exists():
        photos = sorted(PHOTOS.glob("p*.jpg"))
        photo_meta = []
        for f in photos:
            with Image.open(f) as im:
                w, h = im.size
            photo_meta.append({"file": f.name, "orient": "land" if w > h else "port"})
    else:
        photo_meta = normalize(args.max_px, args.quality)

    if args.max and len(photo_meta) > args.max:
        photo_meta = photo_meta[:args.max]
    print(f"Ảnh dùng: {len(photo_meta)}")

    # build slides
    slides = [{"type": "cover", "text": "Chúc mừng sinh nhật<br>Shopee", "date": DATE or SUBTITLE}]
    for idx, pm in enumerate(photo_meta):
        slides.append({"type": "photo", "photo": "photos/" + pm["file"],
                       "orient": pm["orient"], "variant": idx % 3})
    slides.append({"type": "outro", "text": "Yêu con nhiều! 🎂", "date": ""})

    music_attr = f'src="{args.music}"' if args.music else ""
    html = TPL.read_text(encoding="utf-8")
    for k, v in {
        "__TITLE__": TITLE,
        "__SUBTITLE__": SUBTITLE,
        "__DECOR_BASE__": "decorations/",
        "__SLIDE_MS__": str(int(args.seconds * 1000)),
        "__MUSIC_ATTR__": music_attr,
        "__SLIDES_JSON__": json.dumps(slides, ensure_ascii=False),
    }.items():
        html = html.replace(k, v)
    OUT.write_text(html, encoding="utf-8")
    print(f"✓ Ghi {OUT.relative_to(ROOT)}  ({len(slides)} slide, {args.seconds}s/slide)")
    total = args.seconds * len(photo_meta) + 8
    print(f"  Thời lượng ~ {int(total//60)}p{int(total%60):02d}s")


if __name__ == "__main__":
    main()
