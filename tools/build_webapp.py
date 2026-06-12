#!/usr/bin/env python3
"""Build the single-page reader app for the Shopee story series.

Two targets, one source of truth:
  python3 tools/build_webapp.py             -> ./index.html  (uses ORIGINAL .png, for local preview)
  python3 tools/build_webapp.py --deploy    -> ./docs/...    (WebP images + audio, ready for GitHub Pages)

Originals are never modified. The deploy build writes a self-contained copy
under docs/ (index.html + per-story WebP images + copied audio) so you can keep
the full-resolution PNGs for printing.
"""
import json, os, glob, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBP_QUALITY = "82"

HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Truyện Shopee & Robocar Poli</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html, body { height:100%; font-family:-apple-system,"Segoe UI",Roboto,sans-serif; background:#1a1423; color:#fff7ea; }
  body { overflow:hidden; }

  /* ============ LIBRARY ============ */
  #library { position:fixed; inset:0; overflow-y:auto; -webkit-overflow-scrolling:touch;
    background:linear-gradient(160deg,#1a1423 0%,#241a36 50%,#1a2740 100%); padding:26px 16px 56px; }
  #library.hidden { display:none; }
  .lib-head { text-align:center; margin-bottom:24px; }
  .lib-head h1 { font-size:clamp(21px,5vw,32px); font-weight:800; }
  .lib-head p { margin-top:7px; color:#c9bfe0; font-size:clamp(13px,2.4vw,15px); }
  .grid { max-width:1080px; margin:0 auto; display:grid; gap:16px;
    grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); }
  .card { cursor:pointer; background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08);
    border-radius:16px; overflow:hidden; display:flex; flex-direction:column;
    transition:transform .18s, box-shadow .18s, background .18s; }
  .card:hover,.card:active { transform:translateY(-4px); background:rgba(255,255,255,.09);
    box-shadow:0 12px 32px rgba(0,0,0,.45); }
  .thumb { position:relative; aspect-ratio:5/7; background:#0e0a17; overflow:hidden; }
  .thumb img { width:100%; height:100%; object-fit:cover; display:block; }
  .num { position:absolute; top:8px; left:8px; background:rgba(0,0,0,.6); backdrop-filter:blur(4px);
    font-size:12px; font-weight:700; padding:3px 9px; border-radius:999px; }
  .cap { padding:11px 12px; font-size:13.5px; line-height:1.4; font-weight:600; flex:1; }

  /* ============ READER ============ */
  #reader { position:fixed; inset:0; display:none; background:#1a1423; }
  #reader.active { display:block; }
  #stage { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; }
  #stage img { max-width:100%; max-height:100%; object-fit:contain; border-radius:8px;
    box-shadow:0 8px 40px rgba(0,0,0,.6); animation:fadeIn .6s ease; }
  @keyframes fadeIn { from{opacity:0;transform:scale(.985);} to{opacity:1;transform:scale(1);} }

  .tapzone { position:fixed; top:0; bottom:120px; width:28%; z-index:5; cursor:pointer; }
  #tapPrev { left:0; } #tapNext { right:0; }

  #caption { position:fixed; left:50%; transform:translateX(-50%); bottom:86px;
    max-width:min(92vw,700px); max-height:32vh; overflow-y:auto;
    background:rgba(20,14,30,.82); backdrop-filter:blur(8px); color:#fff7ea;
    font-size:clamp(15px,2.2vmin,19px); line-height:1.55; padding:14px 18px; border-radius:14px;
    z-index:6; display:none; white-space:pre-wrap; }
  #reader.show-caption #caption { display:block; }

  /* top-left back button */
  #btnHome { position:fixed; top:12px; left:12px; z-index:11; border:none; border-radius:999px;
    background:rgba(0,0,0,.55); backdrop-filter:blur(6px); color:#fff; font-size:14px; font-weight:600;
    padding:9px 16px; cursor:pointer; display:flex; align-items:center; gap:6px; }
  #btnHome:active { transform:scale(.94); }

  #bar { position:fixed; left:0; right:0; bottom:0; height:76px; z-index:10;
    display:flex; align-items:center; justify-content:center; gap:14px;
    background:linear-gradient(transparent, rgba(10,6,16,.85) 40%); }
  #bar button { border:none; border-radius:50%; width:48px; height:48px; background:rgba(255,255,255,.12);
    color:#fff; font-size:20px; cursor:pointer; display:flex; align-items:center; justify-content:center;
    transition:background .15s, transform .1s; }
  #bar button:active { transform:scale(.92); }
  #bar button:hover { background:rgba(255,255,255,.25); }
  #btnPlay { width:60px !important; height:60px !important; font-size:26px !important; background:#ff7a2f !important; }
  #pageNum { color:#ffd9b3; font-size:15px; min-width:64px; text-align:center; font-variant-numeric:tabular-nums; }

  #dots { position:fixed; top:12px; left:50%; transform:translateX(-50%); display:flex; gap:7px; z-index:10;
    max-width:70vw; flex-wrap:wrap; justify-content:center; }
  #dots span { width:9px; height:9px; border-radius:50%; background:rgba(255,255,255,.25); cursor:pointer; transition:all .2s; }
  #dots span.done { background:rgba(255,170,90,.55); }
  #dots span.cur { background:#ff7a2f; transform:scale(1.35); }

  .overlay { position:fixed; inset:0; z-index:50; display:none; flex-direction:column;
    align-items:center; justify-content:center; gap:24px; text-align:center; padding:24px; }
  .overlay.show { display:flex; }
  #startOverlay { background:radial-gradient(ellipse at center,#3b2a55 0%,#1a1423 75%); }
  #startOverlay h1 { color:#ffe9cf; font-size:clamp(22px,4.5vmin,36px); max-width:80vw; line-height:1.3; text-shadow:0 3px 16px rgba(0,0,0,.5); }
  #startOverlay .sub { color:#bda8d8; font-size:clamp(14px,2.2vmin,18px); }
  #startCover { width:min(38vh,68vw); border-radius:12px; box-shadow:0 10px 50px rgba(0,0,0,.7); }
  .bigbtn { border:none; background:linear-gradient(135deg,#ff8c42,#ff5e3a); color:#fff;
    font-size:clamp(17px,3vmin,22px); font-weight:700; padding:15px 40px; border-radius:999px;
    cursor:pointer; box-shadow:0 6px 26px rgba(255,110,60,.45); transition:transform .12s; }
  .bigbtn:active { transform:scale(.95); }
  #endOverlay { background:rgba(18,12,28,.92); backdrop-filter:blur(6px); }
  #endOverlay h2 { color:#ffe9cf; font-size:clamp(22px,4vmin,32px); }
  .end-row { display:flex; gap:14px; flex-wrap:wrap; justify-content:center; }
  .end-row .bigbtn.alt { background:rgba(255,255,255,.14); box-shadow:none; }
  .toggle { display:flex; align-items:center; gap:10px; cursor:pointer; color:#e8dcff;
    font-size:clamp(14px,2.2vmin,17px); font-weight:600; user-select:none; }
  .toggle input { position:absolute; opacity:0; width:0; height:0; }
  .toggle .slider { position:relative; width:48px; height:27px; border-radius:999px; flex:none;
    background:rgba(255,255,255,.22); transition:background .2s; }
  .toggle .slider::before { content:""; position:absolute; top:3px; left:3px; width:21px; height:21px;
    border-radius:50%; background:#fff; transition:transform .2s; }
  .toggle input:checked + .slider { background:#ff7a2f; }
  .toggle input:checked + .slider::before { transform:translateX(21px); }
  #autoNextCountdown { color:#ffd9b3; font-size:clamp(14px,2.4vmin,18px); min-height:1.5em;
    font-weight:600; text-align:center; }
</style>
</head>
<body>

<!-- ============ LIBRARY VIEW ============ -->
<div id="library">
  <div class="lib-head">
    <h1>📚 Truyện Shopee &amp; Robocar Poli</h1>
    <p>Chạm vào một truyện để nghe kể chuyện &amp; xem hình</p>
  </div>
  <div class="grid" id="grid"></div>
</div>

<!-- ============ READER VIEW ============ -->
<div id="reader" class="show-caption">
  <div id="stage"><img id="slideImg" alt="trang truyện"></div>
  <div id="tapPrev" class="tapzone"></div>
  <div id="tapNext" class="tapzone"></div>
  <div id="caption"></div>
  <div id="dots"></div>
  <button id="btnHome">‹ Thư viện</button>
  <div id="bar">
    <button id="btnPrev" title="Trang trước">⏮</button>
    <button id="btnPlay" title="Phát / Dừng">▶</button>
    <button id="btnNext" title="Trang sau">⏭</button>
    <span id="pageNum"></span>
    <button id="btnReplay" title="Đọc lại trang này">🔁</button>
    <button id="btnCaption" title="Ẩn / hiện chữ">Aa</button>
  </div>

  <div id="startOverlay" class="overlay">
    <img id="startCover" alt="bìa truyện">
    <h1 id="startTitle"></h1>
    <div class="sub" id="startSub"></div>
    <button id="btnStart" class="bigbtn">▶ &nbsp;Bắt đầu đọc truyện</button>
  </div>

  <div id="endOverlay" class="overlay">
    <h2>🎉 Hết truyện rồi! Bé giỏi lắm!</h2>
    <label class="toggle"><input type="checkbox" id="chkAutoNext"><span class="slider"></span><span>Tự động mở truyện tiếp theo</span></label>
    <div id="autoNextCountdown"></div>
    <div class="end-row">
      <button id="btnAgain" class="bigbtn">📖 Đọc lại</button>
      <button id="btnNextStory" class="bigbtn">➡️ Truyện tiếp theo</button>
      <button id="btnLibrary" class="bigbtn alt">📚 Chọn truyện khác</button>
    </div>
  </div>
</div>

<script>
const STORIES = __STORIES__;
const AUTO_ADVANCE_DELAY = 1000;

const library  = document.getElementById("library");
const reader   = document.getElementById("reader");
const grid     = document.getElementById("grid");
const img      = document.getElementById("slideImg");
const caption  = document.getElementById("caption");
const pageNum  = document.getElementById("pageNum");
const dots     = document.getElementById("dots");
const btnPlay  = document.getElementById("btnPlay");
const startOverlay = document.getElementById("startOverlay");
const endOverlay   = document.getElementById("endOverlay");
const audio = new Audio();

let storyIdx = 0;
let SLIDES = [];
let base = "";
let cur = 0;
let playing = false;
let advanceTimer = null;

/* ---------- Auto-open next story ---------- */
const AUTO_NEXT_SECONDS = 10;
let autoNextTimer = null;
const chkAutoNext = document.getElementById("chkAutoNext");
const autoNextCountdownEl = document.getElementById("autoNextCountdown");
chkAutoNext.checked = localStorage.getItem("autoNext") !== "0";   // default ON

function cancelAutoNext() {
  clearInterval(autoNextTimer);
  autoNextTimer = null;
  autoNextCountdownEl.textContent = "";
}

function goNextStory() {
  cancelAutoNext();
  openStory((storyIdx + 1) % STORIES.length);
  startOverlay.classList.remove("show");
  playing = true;
  go(0);
}

function startAutoNext() {
  cancelAutoNext();
  if (!chkAutoNext.checked || STORIES.length < 2) return;
  let remain = AUTO_NEXT_SECONDS;
  const nextTitle = STORIES[(storyIdx + 1) % STORIES.length].title;
  const tick = () => {
    if (remain <= 0) { goNextStory(); return; }
    autoNextCountdownEl.textContent = "➡️ Tự động mở “" + nextTitle + "” sau " + remain + "s…";
    remain--;
  };
  tick();
  autoNextTimer = setInterval(tick, 1000);
}

chkAutoNext.addEventListener("change", () => {
  localStorage.setItem("autoNext", chkAutoNext.checked ? "1" : "0");
  if (chkAutoNext.checked && endOverlay.classList.contains("show")) startAutoNext();
  else cancelAutoNext();
});

/* ---------- Library ---------- */
STORIES.forEach((st, i) => {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML =
    '<div class="thumb"><img loading="lazy" src="' + st.base + '/' + st.cover + '" alt="">' +
    '<span class="num">' + st.n + '</span></div>' +
    '<div class="cap">' + st.title + '</div>';
  card.addEventListener("click", () => openStory(i));
  grid.appendChild(card);
});

function openStory(i) {
  storyIdx = i;
  const st = STORIES[i];
  SLIDES = st.slides;
  base = st.base;
  cur = 0;
  playing = false;
  clearTimeout(advanceTimer);
  cancelAutoNext();
  audio.pause();

  dots.innerHTML = "";
  SLIDES.forEach((_, k) => {
    const d = document.createElement("span");
    d.addEventListener("click", () => go(k, true));
    dots.appendChild(d);
  });

  document.getElementById("startCover").src = base + "/" + st.cover;
  document.getElementById("startTitle").textContent = st.title;
  document.getElementById("startSub").innerHTML =
    "Giọng kể: chị HoaiMy &nbsp;•&nbsp; " + (SLIDES.length - 1) + " trang";
  endOverlay.classList.remove("show");
  startOverlay.classList.add("show");
  btnPlay.textContent = "▶";

  render();
  library.classList.add("hidden");
  reader.classList.add("active");
  window.scrollTo(0, 0);
}

function goHome() {
  playing = false;
  clearTimeout(advanceTimer);
  cancelAutoNext();
  audio.pause();
  btnPlay.textContent = "▶";
  reader.classList.remove("active");
  library.classList.remove("hidden");
  location.hash = "";
}

/* ---------- Player ---------- */
function render() {
  const s = SLIDES[cur];
  img.src = base + "/" + s.image;
  caption.textContent = s.text;
  caption.scrollTop = 0;
  pageNum.textContent = (cur === 0 ? "Bìa" : "Trang " + cur) + " / " + (SLIDES.length - 1);
  [...dots.children].forEach((d, i) => {
    d.className = i < cur ? "done" : i === cur ? "cur" : "";
  });
  if (cur + 1 < SLIDES.length) { (new Image()).src = base + "/" + SLIDES[cur + 1].image; }
}

function playCurrent() {
  clearTimeout(advanceTimer);
  audio.src = base + "/" + SLIDES[cur].audio;
  audio.play().catch(() => {});
  btnPlay.textContent = "⏸";
}

function stopAudio() {
  clearTimeout(advanceTimer);
  audio.pause();
  btnPlay.textContent = "▶";
}

function go(i, manual) {
  if (i < 0 || i >= SLIDES.length) return;
  cancelAutoNext();
  cur = i;
  endOverlay.classList.remove("show");
  render();
  if (playing || manual) playCurrent();
}

audio.addEventListener("ended", () => {
  if (!playing) { btnPlay.textContent = "▶"; return; }
  if (cur + 1 < SLIDES.length) {
    advanceTimer = setTimeout(() => go(cur + 1), AUTO_ADVANCE_DELAY);
  } else {
    playing = false;
    btnPlay.textContent = "▶";
    endOverlay.classList.add("show");
    startAutoNext();
  }
});

/* ---------- Controls ---------- */
document.getElementById("btnStart").addEventListener("click", () => {
  startOverlay.classList.remove("show");
  playing = true;
  go(0);
});
document.getElementById("btnAgain").addEventListener("click", () => { playing = true; go(0); });
document.getElementById("btnLibrary").addEventListener("click", goHome);
document.getElementById("btnHome").addEventListener("click", goHome);
document.getElementById("btnNextStory").addEventListener("click", goNextStory);
document.getElementById("btnPrev").addEventListener("click", () => go(cur - 1, true));
document.getElementById("btnNext").addEventListener("click", () => go(cur + 1, true));
document.getElementById("tapPrev").addEventListener("click", () => go(cur - 1, true));
document.getElementById("tapNext").addEventListener("click", () => go(cur + 1, true));
document.getElementById("btnReplay").addEventListener("click", playCurrent);
document.getElementById("btnCaption").addEventListener("click", () => reader.classList.toggle("show-caption"));

btnPlay.addEventListener("click", () => {
  if (audio.paused) {
    playing = true;
    if (audio.src && !audio.ended) { audio.play(); btnPlay.textContent = "⏸"; }
    else playCurrent();
  } else {
    playing = false;
    stopAudio();
  }
});

document.addEventListener("keydown", (e) => {
  if (!reader.classList.contains("active")) return;
  if (e.key === "ArrowRight") go(cur + 1, true);
  else if (e.key === "ArrowLeft") go(cur - 1, true);
  else if (e.key === " ") { e.preventDefault(); btnPlay.click(); }
  else if (e.key === "Escape") goHome();
});

/* ---------- Deep link: index.html#story=3 ---------- */
function applyHash() {
  const m = (location.hash || "").match(/story=(\d+)/);
  if (m) {
    const idx = STORIES.findIndex(s => s.n === parseInt(m[1], 10));
    if (idx >= 0) openStory(idx);
  }
}
applyHash();
</script>
</body>
</html>
"""


def load_stories():
    stories = []
    dirs = sorted(
        glob.glob(os.path.join(ROOT, "Shopee-story-*")),
        key=lambda p: int(re.search(r"(\d+)$", p).group(1)) if re.search(r"(\d+)$", p) else 0,
    )
    for d in dirs:
        if not os.path.isdir(d):
            continue
        m = re.search(r"Shopee-story-(\d+)$", d)
        if not m:
            continue
        nj = os.path.join(d, "narration.json")
        if not os.path.exists(nj):
            continue
        with open(nj, encoding="utf-8") as f:
            data = json.load(f)
        stories.append({
            "n": int(m.group(1)),
            "title": data.get("title", "Truyện " + m.group(1)),
            "base": os.path.basename(d),
            "slides": data.get("slides", []),
        })
    return stories


def write_html(stories, out_path, cover="cover.png", img_ext_map=None):
    """img_ext_map: optional fn(filename)->filename to rewrite image paths (e.g. png->webp)."""
    payload = []
    for st in stories:
        slides = []
        for s in st["slides"]:
            image = img_ext_map(s["image"]) if img_ext_map else s["image"]
            slides.append({"image": image, "audio": s["audio"], "text": s["text"]})
        cov = img_ext_map(cover) if img_ext_map else cover
        payload.append({"n": st["n"], "title": st["title"], "base": st["base"],
                        "cover": cov, "slides": slides})
    js = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    html = HTML.replace("__STORIES__", js)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


def build_local(stories):
    size = write_html(stories, os.path.join(ROOT, "index.html"), cover="cover.png")
    print("LOCAL  -> index.html  ({} stories, {} KB, uses original .png)".format(
        len(stories), round(size / 1024, 1)))


def to_webp(name):
    return re.sub(r"\.(png|jpg|jpeg)$", ".webp", name, flags=re.I)


def build_deploy(stories):
    docs = os.path.join(ROOT, "docs")
    os.makedirs(docs, exist_ok=True)
    total_png = total_webp = 0
    converted = 0
    for st in stories:
        src_dir = os.path.join(ROOT, st["base"])
        dst_dir = os.path.join(docs, st["base"])
        os.makedirs(dst_dir, exist_ok=True)

        # collect images: cover + every slide image
        images = {"cover.png"} | {s["image"] for s in st["slides"]}
        for png in sorted(images):
            src = os.path.join(src_dir, png)
            if not os.path.exists(src):
                print("  WARN missing image:", os.path.join(st["base"], png))
                continue
            dst = os.path.join(dst_dir, to_webp(png))
            total_png += os.path.getsize(src)
            subprocess.run(["cwebp", "-quiet", "-q", WEBP_QUALITY, src, "-o", dst], check=True)
            total_webp += os.path.getsize(dst)
            converted += 1

        # copy audio as-is (mp3 already compressed)
        src_audio = os.path.join(src_dir, "audio")
        if os.path.isdir(src_audio):
            dst_audio = os.path.join(dst_dir, "audio")
            shutil.copytree(src_audio, dst_audio, dirs_exist_ok=True)

    size = write_html(stories, os.path.join(docs, "index.html"),
                      cover="cover.png", img_ext_map=to_webp)
    # GitHub Pages: don't run the folder through Jekyll
    open(os.path.join(docs, ".nojekyll"), "w").close()
    print("DEPLOY -> docs/  ({} stories, index.html {} KB)".format(len(stories), round(size / 1024, 1)))
    pct = round(100 * (1 - total_webp / total_png)) if total_png else 0
    print("  images: {} converted, {} MB PNG -> {} MB WebP ({}% smaller)".format(
        converted, round(total_png / 1e6, 1), round(total_webp / 1e6, 1), pct))
    print("  audio copied as-is. Set GitHub Pages source = branch /docs.")


if __name__ == "__main__":
    stories = load_stories()
    build_local(stories)
    if "--deploy" in sys.argv:
        build_deploy(stories)
    else:
        print("(run with --deploy to also build the optimized docs/ folder)")
