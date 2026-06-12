#!/usr/bin/env python3
"""Gen audio mp3 cho slideshow truyện Shopee từ narration.json bằng edge-tts.

Usage:
    ~/.venvs/edge-tts/bin/python tools/gen_story_audio.py Shopee-story-5 [--force]

Đọc <story-dir>/narration.json, gen từng slide ra <story-dir>/audio/*.mp3.
Bỏ qua file đã tồn tại trừ khi có --force.
"""
import asyncio
import json
import sys
from pathlib import Path

import edge_tts


async def gen_one(text: str, voice: str, rate: str, out_path: Path, retries: int = 4) -> None:
    for attempt in range(1, retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
            await communicate.save(str(out_path))
            print(f"  ✓ {out_path.name} ({out_path.stat().st_size // 1024} KB)")
            return
        except Exception as exc:  # NoAudioReceived / network — thử lại với backoff
            if out_path.exists():
                out_path.unlink()
            if attempt == retries:
                raise
            wait = 3 * attempt
            print(f"  ! {out_path.name} lỗi ({exc.__class__.__name__}), thử lại sau {wait}s...")
            await asyncio.sleep(wait)


async def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if not args:
        sys.exit("Usage: gen_story_audio.py <story-dir> [--force]")

    story_dir = Path(args[0]).resolve()
    plan_path = story_dir / "narration.json"
    if not plan_path.exists():
        sys.exit(f"Không tìm thấy {plan_path}")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    voice = plan.get("voice", "vi-VN-HoaiMyNeural")
    rate = plan.get("rate", "-10%")
    slides = plan["slides"]

    print(f"Story: {plan.get('title', story_dir.name)}")
    print(f"Voice: {voice}  rate: {rate}  slides: {len(slides)}")

    for slide in slides:
        out_path = story_dir / slide["audio"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.exists() and out_path.stat().st_size > 0 and not force:
            print(f"  - {out_path.name} đã có, bỏ qua")
            continue
        await gen_one(slide["text"], voice, rate, out_path)
        await asyncio.sleep(1.5)  # tránh throttle của dịch vụ Edge TTS

    print("Xong.")


if __name__ == "__main__":
    asyncio.run(main())
