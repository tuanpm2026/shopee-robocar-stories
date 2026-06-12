#!/usr/bin/env python3
"""Build index.html slideshow cho truyện Shopee từ narration.json + template.

Usage:
    python3 tools/build_story_slideshow.py Shopee-story-6

Đọc <story-dir>/narration.json, fill vào tools/slideshow_template.html,
ghi ra <story-dir>/index.html, rồi kiểm tra mọi asset (ảnh + mp3) tồn tại.
"""
import json
import sys
from pathlib import Path

PLACEHOLDERS = ("__TITLE__", "__VOICE_LABEL__", "__SLIDE_COUNT__", "__COVER__", "__SLIDES_JSON__")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: build_story_slideshow.py <story-dir>")

    story_dir = Path(sys.argv[1]).resolve()
    plan_path = story_dir / "narration.json"
    if not plan_path.exists():
        sys.exit(f"Không tìm thấy {plan_path}")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    slides = plan["slides"]
    voice = plan.get("voice", "vi-VN-HoaiMyNeural")
    voice_label = voice.replace("vi-VN-", "").removesuffix("Neural")

    template = (Path(__file__).parent / "slideshow_template.html").read_text(encoding="utf-8")
    html = (
        template
        .replace("__TITLE__", plan["title"])
        .replace("__VOICE_LABEL__", voice_label)
        .replace("__SLIDE_COUNT__", str(len(slides)))
        .replace("__COVER__", slides[0]["image"])
        .replace("__SLIDES_JSON__", json.dumps(slides, ensure_ascii=False, indent=2))
    )

    leftover = [p for p in PLACEHOLDERS if p in html]
    if leftover:
        sys.exit(f"Template còn placeholder chưa fill: {leftover}")

    out_path = story_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"✓ {out_path} ({len(slides)} slides)")

    missing = []
    for slide in slides:
        for key in ("image", "audio"):
            asset = story_dir / slide[key]
            if not asset.is_file() or asset.stat().st_size == 0:
                missing.append(slide[key])
    if missing:
        print("⚠ Asset thiếu hoặc rỗng:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    print(f"✓ Đủ {len(slides) * 2} asset (ảnh + audio)")


if __name__ == "__main__":
    main()
