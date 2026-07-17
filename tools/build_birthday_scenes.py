#!/usr/bin/env python3
"""Build slideshow sinh nhật kiểu CẢNH AI + layout ảnh đa dạng.

- Ảnh thật đặt đè lên nền cảnh AI (Shopee-birthday/scenes/*.png, xoay vòng).
- Mỗi slide chọn 1 layout: 1 / 2 / 3 ảnh, vị trí + độ nghiêng + kiểu viền khác nhau
  (polaroid, viền vàng, hình tròn, băng keo, kẹp dây, viền màu).
- Banner chữ ngọt ngào đổi mỗi slide.
- Chuẩn hoá ảnh từ albums/ (xoay EXIF, sắp theo giờ chụp, resize).

Usage:
    python3 tools/build_birthday_scenes.py --seconds 5
    python3 tools/build_birthday_scenes.py --skip-normalize
"""
import argparse
import copy
import itertools
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ALBUMS = ROOT / "albums"
BDIR = ROOT / "Shopee-birthday"
PHOTOS = BDIR / "photos"
SCENES = BDIR / "scenes"
TPL = ROOT / "tools" / "birthday_scene_template.html"
OUT = BDIR / "index.html"

TITLE, SUBTITLE = "Sinh nhật Shopee", "3 tuổi"

# Kho layout (stage 1920x1080, toạ độ theo TÂM khung). Ảnh nằm trong vùng giữa trống của cảnh.
LAYOUTS = {
    "big":    [{"cx": 960, "cy": 560, "w": 560, "h": 716, "rot": -2.5, "frame": "polaroid"}],
    "gold":   [{"cx": 948, "cy": 552, "w": 556, "h": 712, "rot": 3, "frame": "gold"}],
    "pink":   [{"cx": 970, "cy": 558, "w": 548, "h": 704, "rot": -4, "frame": "color", "color": "#ff8fb8"}],
    "blue":   [{"cx": 952, "cy": 556, "w": 548, "h": 704, "rot": 4, "frame": "color", "color": "#7cc6ff"}],
    "round":  [{"cx": 955, "cy": 560, "w": 600, "h": 662, "rot": 2, "frame": "round"}],
    "circle": [{"cx": 960, "cy": 558, "w": 648, "h": 648, "rot": 0, "frame": "circle"}],
    "tape1":  [{"cx": 960, "cy": 556, "w": 544, "h": 702, "rot": -3, "frame": "tape"}],
    "d_sbs":  [{"cx": 600, "cy": 560, "w": 624, "h": 792, "rot": -3, "frame": "polaroid"},
               {"cx": 1320, "cy": 560, "w": 624, "h": 792, "rot": 3, "frame": "polaroid"}],
    "d_stag": [{"cx": 600, "cy": 512, "w": 600, "h": 760, "rot": -3, "frame": "clip"},
               {"cx": 1320, "cy": 604, "w": 600, "h": 760, "rot": 3, "frame": "clip"}],
    "t_row":  [{"cx": 430, "cy": 566, "w": 472, "h": 600, "rot": -4, "frame": "clip"},
               {"cx": 960, "cy": 584, "w": 472, "h": 600, "rot": 2, "frame": "clip"},
               {"cx": 1490, "cy": 566, "w": 472, "h": 600, "rot": -3, "frame": "clip"}],
    "t_stag": [{"cx": 430, "cy": 600, "w": 468, "h": 596, "rot": -6, "frame": "polaroid"},
               {"cx": 960, "cy": 516, "w": 468, "h": 596, "rot": 3, "frame": "tape"},
               {"cx": 1490, "cy": 606, "w": 468, "h": 596, "rot": -5, "frame": "polaroid"}],
}
CAPTIONS = [
    "Bé yêu của ba mẹ 💙", "Cùng nhau lớn lên nhé!", "Lớn thêm 1 tuổi, thêm niềm vui",
    "Chúc mừng sinh nhật bé yêu!", "Mừng Shopee tròn 3 tuổi 🎉", "Nụ cười của con là món quà",
    "Một tuổi mới thật nhiều điều hay!", "Yêu con thật nhiều!",
]


SINGLES = ["big", "gold", "pink", "blue", "round", "circle", "tape1"]
DOUBLES = ["d_sbs", "d_stag"]
TRIPLES = ["t_row", "t_stag"]


def dhash(path, size=8):
    """dHash 64-bit để so độ giống ảnh (không cần thư viện ngoài)."""
    im = Image.open(path).convert("L").resize((size + 1, size), Image.LANCZOS)
    px = im.tobytes()  # 1 byte/pixel (mode L), hàng-trước
    bits = 0
    k = 0
    for r in range(size):
        row = r * (size + 1)
        for c in range(size):
            if px[row + c] > px[row + c + 1]:
                bits |= (1 << k)
            k += 1
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


def group_photos(photo_meta, threshold, max_group=3):
    """Gom ảnh liền kề GIỐNG nhau (burst) thành nhóm ≤ max_group."""
    if not photo_meta:
        return []
    hashes = [dhash(PHOTOS / pm["file"]) for pm in photo_meta]
    groups = [[0]]
    for i in range(1, len(photo_meta)):
        cur = groups[-1]
        if len(cur) < max_group and hamming(hashes[i], hashes[cur[0]]) <= threshold:
            cur.append(i)
        else:
            groups.append([i])
    return groups


def pack_groups(photo_meta, threshold, size_cycle=(3, 2, 3, 2, 1), max_group=3):
    """Ảnh burst (giống nhau) giữ nguyên 1 slide; ảnh lẻ gói thành cụm 2-3 (thỉnh thoảng 1)
    theo size_cycle -> tăng mạnh số slide nhiều-ảnh."""
    bursts = group_photos(photo_meta, threshold, max_group)
    out, ci = [], 0
    i = 0
    while i < len(bursts):
        if len(bursts[i]) >= 2:          # burst thật -> slide riêng
            out.append(bursts[i]); i += 1
            continue
        size = size_cycle[ci % len(size_cycle)]; ci += 1
        grp = []
        while i < len(bursts) and len(bursts[i]) == 1 and len(grp) < size:
            grp.append(bursts[i][0]); i += 1
        out.append(grp)
    return out


def scale_slots(slots, factor, cx0=960, cy0=540, max_h=966, max_w=1480):
    """Phóng to khung ảnh theo factor; giãn vị trí quanh tâm để slide nhiều-ảnh
    không chồng nhau quá; kẹp để không tràn stage (giữ tỉ lệ)."""
    for s in slots:
        s["cx"] = int(round(cx0 + (s["cx"] - cx0) * factor))
        s["cy"] = int(round(cy0 + (s["cy"] - cy0) * factor))
        w, h = s["w"] * factor, s["h"] * factor
        if h > max_h:
            w *= max_h / h; h = max_h
        if w > max_w:
            h *= max_w / w; w = max_w
        s["w"], s["h"] = int(round(w)), int(round(h))
    return slots


def exif_dt(img):
    try:
        ex = img.getexif()
        try:
            sub = ex.get_ifd(0x8769)
            if sub.get(36867):
                return str(sub[36867])
        except Exception:
            pass
        if ex.get(306):
            return str(ex[306])
    except Exception:
        pass
    return ""


def normalize(max_px, quality):
    PHOTOS.mkdir(parents=True, exist_ok=True)
    for old in PHOTOS.glob("p*.jpg"):
        old.unlink()
    srcs = [p for p in ALBUMS.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
    metas = []
    for p in srcs:
        with Image.open(p) as im:
            dt = exif_dt(im)
        metas.append((dt or "9999", p.name, p))
    metas.sort(key=lambda m: (m[0], m[1]))
    out = []
    for i, (_, _, p) in enumerate(metas, 1):
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        im.thumbnail((max_px, max_px), Image.LANCZOS)
        w, h = im.size
        fn = f"p{i:02d}.jpg"
        im.save(PHOTOS / fn, "JPEG", quality=quality, optimize=True)
        out.append({"file": fn, "orient": "land" if w > h else "port"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--music", default="")
    ap.add_argument("--skip-normalize", action="store_true")
    ap.add_argument("--scenes-dir", default=str(SCENES), help="thư mục kho cảnh")
    ap.add_argument("--group-threshold", type=int, default=10,
                    help="ngưỡng gom ảnh giống nhau (0-64, nhỏ = chỉ gom ảnh rất giống)")
    ap.add_argument("--no-group", action="store_true", help="tắt gom nhóm, mỗi ảnh 1 slide")
    ap.add_argument("--no-captions", action="store_true", help="bỏ chữ banner trên slide ảnh")
    args = ap.parse_args()

    scenes_dir = Path(args.scenes_dir).resolve()
    scene_rel = scenes_dir.relative_to(BDIR).as_posix()  # đường dẫn tương đối trong index.html
    # gom theo tiền tố (blue*/scene*), sắp số trong nhóm, rồi XEN KẼ round-robin -> xanh/màu luân phiên
    buckets = defaultdict(list)
    for p in scenes_dir.glob("*.png"):
        if p.stem.startswith("cover"):
            continue  # ảnh cover không nằm trong vòng xoay cảnh
        prefix = "".join(ch for ch in p.stem if not ch.isdigit())
        buckets[prefix].append(p.name)
    for k in buckets:
        buckets[k].sort(key=lambda n: int("".join(filter(str.isdigit, n)) or "0"))
    scenes = [x for row in itertools.zip_longest(*[buckets[k] for k in sorted(buckets)])
              for x in row if x]
    if not scenes:
        raise SystemExit(f"Chưa có cảnh nào trong {scenes_dir}.")
    print(f"Kho cảnh: {len(scenes)} ({scene_rel}, xen kẽ {sorted(buckets)}) | layout: {len(LAYOUTS)}")

    if args.skip_normalize and PHOTOS.exists():
        photo_meta = []
        for f in sorted(PHOTOS.glob("p*.jpg")):
            with Image.open(f) as im:
                w, h = im.size
            photo_meta.append({"file": f.name, "orient": "land" if w > h else "port"})
    else:
        photo_meta = normalize(args.max_px, args.quality)
    if args.max and len(photo_meta) > args.max:
        photo_meta = photo_meta[:args.max]
    print(f"Ảnh dùng: {len(photo_meta)}")

    def scene(i):
        return scene_rel + "/" + scenes[i % len(scenes)]

    if (scenes_dir / "cover.png").exists():
        slides = [{"type": "coverimg", "scene": scene_rel + "/cover.png"}]
    else:
        slides = [{"type": "cover", "scene": scene(0),
                   "text": "Chúc mừng sinh nhật<br>Shopee", "date": "Tròn 3 tuổi 🎉"}]

    groups = ([[k] for k in range(len(photo_meta))] if args.no_group
              else pack_groups(photo_meta, args.group_threshold))
    n_multi = sum(1 for g in groups if len(g) > 1)
    print(f"Slide ảnh: {len(groups)} (trong đó {n_multi} slide 2-3 ảnh)")

    si = di = ti = ci = 0
    sc = 1
    for g in groups:
        cnt = len(g)
        if cnt == 1:
            key = SINGLES[si % len(SINGLES)]; si += 1
        elif cnt == 2:
            key = DOUBLES[di % len(DOUBLES)]; di += 1
        else:
            key = TRIPLES[ti % len(TRIPLES)]; ti += 1
        slots = copy.deepcopy(LAYOUTS[key])
        photos = ["photos/" + photo_meta[idx]["file"] for idx in g]
        # ảnh ngang đứng một mình -> đổi khung sang ngang
        if cnt == 1 and photo_meta[g[0]]["orient"] == "land" and slots[0]["frame"] != "circle":
            slots[0]["w"], slots[0]["h"] = 860, 574
        # ảnh 1 tấm: phóng to 30-50% biến thiên; nhiều tấm: giữ kích thước đã canh (không đè)
        if cnt == 1:
            scale_slots(slots, 1.30 + ((sc * 7 + 3) % 21) / 100.0)
        caption = "" if args.no_captions else CAPTIONS[ci % len(CAPTIONS)]
        slides.append({"type": "photo", "scene": scene(sc), "caption": caption,
                       "slots": slots, "photos": photos})
        sc += 1
        ci += 1

    music_dir = BDIR / "music"
    if music_dir.exists():
        mfiles = sorted([p.name for p in music_dir.iterdir()
                         if p.suffix.lower() in (".mp3", ".m4a", ".wav", ".aac")],
                        key=lambda n: int("".join(filter(str.isdigit, n)) or "0"))
        music_list = ["music/" + f for f in mfiles]
    elif args.music:
        music_list = [args.music]
    else:
        music_list = []
    print(f"Nhạc slideshow: {len(music_list)} bài")

    html = TPL.read_text(encoding="utf-8")
    for k, v in {
        "__TITLE__": TITLE, "__SUBTITLE__": SUBTITLE,
        "__SLIDE_MS__": str(int(args.seconds * 1000)),
        "__MUSIC_JSON__": json.dumps(music_list, ensure_ascii=False),
        "__SLIDES_JSON__": json.dumps(slides, ensure_ascii=False),
    }.items():
        html = html.replace(k, v)
    OUT.write_text(html, encoding="utf-8")
    photo_slides = sum(1 for s in slides if s["type"] == "photo")
    print(f"✓ Ghi {OUT.relative_to(ROOT)} ({len(slides)} slide, {photo_slides} slide ảnh, {args.seconds}s/slide)")


if __name__ == "__main__":
    main()
