#!/usr/bin/env python3
"""Gen ảnh trang trí (cutout nhân vật + asset tiệc) cho slideshow sinh nhật Shopee.

Dùng OpenAI Images API. Cutout cần NỀN TRONG SUỐT -> model gpt-image-1.5
(gpt-image-2 không hỗ trợ background=transparent).

Đọc  : Shopee-birthday/decorations-plan.json
Ghi  : Shopee-birthday/decorations/<name>.png  (RGBA, nền trong suốt)
Key  : Shopee-birthday/.env  (OPENAI_API_KEY=...  [OPENAI_BASE_URL=...])

Usage:
    python3 tools/gen_birthday_decorations.py                 # gen ảnh còn thiếu
    python3 tools/gen_birthday_decorations.py --only poli,roy # chỉ vài asset
    python3 tools/gen_birthday_decorations.py --force         # gen lại tất cả
    python3 tools/gen_birthday_decorations.py --model gpt-image-1.5 --quality high
"""
import argparse
import base64
import io
import json
import sys
import time
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BDIR = ROOT / "Shopee-birthday"
OUT = BDIR / "decorations"
PLAN = BDIR / "decorations-plan.json"

# Phong cách chung — dán vào mọi prompt để đồng nhất với art Robocar Poli hiện có.
STYLE = (
    "Pixar-style glossy 3D render, cute children's cartoon, soft studio lighting, "
    "smooth rounded shapes, vibrant saturated colors, high detail, clean edges. "
    "Full object centered with a little padding, isolated on a FULLY TRANSPARENT "
    "background (alpha), absolutely no background scenery, no floor, no shadow slab, "
    "no text, no letters, no watermark."
)


def load_env() -> dict:
    env = {}
    f = BDIR / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def decode_first(resp_json: dict) -> bytes:
    d = resp_json["data"][0]
    if d.get("b64_json"):
        return base64.b64decode(d["b64_json"])
    # một số backend trả url
    return requests.get(d["url"], timeout=60).content


def ref_bytes(path: Path, max_px: int) -> bytes:
    """Đọc ảnh reference; nếu max_px>0 thì thu nhỏ để giảm input token."""
    if not max_px:
        return path.read_bytes()
    im = Image.open(path).convert("RGBA")
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def gen_one(item, key, base, model, quality, background, style, ref_max_px=0, retries=4):
    prompt = f"{item['prompt'].strip()} {style}".strip()
    size = item.get("size", "1024x1024")
    bg = item.get("background", background)
    refs = item.get("refs", [])
    headers = {"Authorization": f"Bearer {key}"}

    for attempt in range(1, retries + 1):
        try:
            if refs:  # có ảnh tham chiếu -> /images/edits (giữ đúng nhân vật)
                files = []
                for rp in refs:
                    p = (ROOT / rp)
                    files.append(("image[]", (p.name, ref_bytes(p, ref_max_px), "image/png")))
                data = {
                    "model": model, "prompt": prompt, "size": size,
                    "background": bg, "quality": quality, "n": "1",
                }
                r = requests.post(base + "/images/edits", headers=headers,
                                  data=data, files=files, timeout=300)
            else:  # asset thuần -> /images/generations
                payload = {
                    "model": model, "prompt": prompt, "size": size,
                    "background": bg, "quality": quality, "n": 1,
                }
                r = requests.post(base + "/images/generations",
                                  headers={**headers, "Content-Type": "application/json"},
                                  json=payload, timeout=300)
            if r.status_code == 200:
                return decode_first(r.json())
            # lỗi có thể thử lại
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = 5 * attempt
                print(f"    ! HTTP {r.status_code}, thử lại sau {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        except requests.RequestException as e:
            if attempt < retries:
                wait = 5 * attempt
                print(f"    ! {type(e).__name__}, thử lại sau {wait}s...")
                time.sleep(wait)
                continue
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="chỉ gen các name này (phân tách bằng dấu phẩy)")
    ap.add_argument("--force", action="store_true", help="gen lại kể cả đã có")
    ap.add_argument("--model", default="gpt-image-1.5")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    ap.add_argument("--plan", default=str(PLAN), help="đường dẫn plan JSON")
    ap.add_argument("--out-dir", default=str(OUT), help="thư mục ghi ảnh")
    ap.add_argument("--background", default="transparent", help="transparent|opaque|auto")
    ap.add_argument("--ref-max-px", type=int, default=0, help="thu nhỏ ảnh reference (0 = giữ nguyên)")
    args = ap.parse_args()

    env = load_env()
    key = env.get("OPENAI_API_KEY")
    if not key:
        sys.exit("Thiếu OPENAI_API_KEY trong Shopee-birthday/.env")
    base = env.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    items = plan["items"]
    style = plan.get("style", STYLE)              # plan có thể tự định nghĩa style riêng
    background = plan.get("background", args.background)
    out_dir = Path(args.out_dir)
    if args.only:
        want = {n.strip() for n in args.only.split(",")}
        items = [it for it in items if it["name"] in want]

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Model: {args.model} | quality: {args.quality} | bg: {background} | {len(items)} asset\n")
    done = skip = fail = 0
    for it in items:
        out = out_dir / f"{it['name']}.png"
        if out.exists() and not args.force:
            print(f"  ⏭  {it['name']} (đã có)")
            skip += 1
            continue
        tag = f"[ref:{len(it.get('refs', []))}]" if it.get("refs") else "[gen]"
        print(f"  → {it['name']} {tag} {it.get('size', '1024x1024')} ...")
        try:
            png = gen_one(it, key, base, args.model, args.quality, background, style, args.ref_max_px)
            out.write_bytes(png)
            print(f"    ✓ {out.name} ({len(png)//1024} KB)")
            done += 1
        except Exception as e:
            print(f"    ✗ LỖI: {e}")
            fail += 1
    print(f"\nXong. Tạo mới {done}, bỏ qua {skip}, lỗi {fail}.")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
