"""Download and optimize live-site imagery. Run: python tools/optimize_images.py"""
import io
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import IMG_BUDGETS  # noqa: E402  (byte budget per category, Task 1)

# category -> (max_width, starting webp_quality, starting jpeg_quality)
# These are ceilings, not fixed values: process() searches downward from
# them (quality, then width) until the encoded file fits IMG_BUDGETS.
PROFILES = {
    "hero": (1600, 78, 80),
    "inline": (1200, 78, 80),
    "news": (600, 75, 78),
    "portrait": (600, 80, 82),
}

# Logo is displayed at 132px wide in the page header; 264 is 2x for retina.
LOGO_WIDTH = 264

BASE = "https://visrvu.org/wp-content/uploads"

# (category, output basename, source URL)
SOURCES = [
    ("hero", "campus-survey", f"{BASE}/2023/11/DSF6099-1.jpg"),
    ("inline", "field-team", f"{BASE}/2023/11/DSF5942-scaled-e1701790763135.jpg"),
    ("inline", "gpr-survey", f"{BASE}/2024/06/a1.jpg"),
    ("inline", "gpr-cart", f"{BASE}/2024/07/IMG_0281-6-edited.jpg"),
    # IMG_1070 and IMG_0528 both sit under "The Magnetometer" on the live
    # page (confirmed against the live DOM, not just visually) and both
    # depict the Bartington Grad601 fluxgate magnetic gradiometer, not a
    # magnetometer in the standalone-sensor sense; IMG_0268 sits under
    # "Total Stations & RTK GNSS". Named gradiometer-* (not magnetometer-*)
    # so the filename states what the photo shows. The names below replace
    # an earlier guess (total-station / gnss-rover / magnetometer) that had
    # all three swapped.
    ("inline", "gradiometer-survey", f"{BASE}/2024/01/IMG_1070.jpg"),
    ("inline", "gradiometer-array", f"{BASE}/2024/07/IMG_0528-1-edited.jpg"),
    ("inline", "total-station", f"{BASE}/2024/01/IMG_0268.jpg"),
    ("inline", "fieldwork", f"{BASE}/2023/11/IMG_9080-1.jpg"),
    ("news", "edmondson", f"{BASE}/2024/06/Image-2-3.jpg"),
    ("news", "community-grant",
     f"{BASE}/2024/06/267282c3-dcee-4607-bbc4-9b92521821d3.jpg"),
    ("news", "lookout-mountain",
     f"{BASE}/2024/06/2ffcac08-0d1b-45c3-a4fd-40cdb8571404.jpg"),
    ("news", "mud-creek", f"{BASE}/2024/06/a1.jpg"),
]

LOGO_URL = f"{BASE}/2025/02/VISR_logo_03.png"

# Some source photos are the wrong orientation for where they're used and
# need a deliberate crop before resizing. name -> (aspect_w, aspect_h, top).
# `top` is how many pixels down from the source's top edge the crop begins
# (only meaningful when the source is taller than the target aspect ratio);
# it lets the composition be chosen deliberately instead of auto-centering.
#
# campus-survey (the homepage hero) is a portrait photo at full resolution
# (3749x5623) but renders as a full-width landscape banner. Cropped to 3:2
# starting 200px from the top, it keeps the full skyline, the researcher's
# hat and shoulders, and the notebook at the bottom edge.
CROPS = {
    "campus-survey": (3, 2, 200),
}

UA = {"User-Agent": "Mozilla/5.0 (VISR site migration)"}

# Raw source bytes are cached to local disk (outside the repo) so that
# tuning quality/width does not re-fetch multi-megabyte originals over
# this network-share checkout, and so retries don't hammer the live
# site's rate limiter.
CACHE_DIR = Path(tempfile.gettempdir()) / "visr_optimize_images_cache"


def download_raw(url, retries=8, backoff=6):
    """Fetch url, retrying with backoff on transient errors (the live
    site's rate limiting occasionally returns 403 on rapid requests)."""
    req = urllib.request.Request(url, headers=UA)
    last_exc = None
    for attempt in range(retries):
        try:
            time.sleep(1)  # be polite; reduces rate-limit 403s
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
    raise last_exc


def fetch(url):
    """Return raw source bytes for url, using the local cache when present."""
    cache_path = CACHE_DIR / Path(url).name
    if cache_path.is_file():
        return cache_path.read_bytes()
    raw = download_raw(url)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(raw)
    return raw


def crop_to_aspect(img, aspect_w, aspect_h, top=0):
    """Crop img to an aspect_w:aspect_h box. If the source is taller than
    the target ratio, keep full width and take a vertical slice starting
    `top` px down (clamped in-bounds) so composition can be chosen on
    purpose rather than auto-centered; if the source is wider than the
    target ratio, center-crop horizontally instead."""
    target_ratio = aspect_w / aspect_h
    src_ratio = img.width / img.height
    if src_ratio > target_ratio:
        new_w = round(img.height * target_ratio)
        left = (img.width - new_w) // 2
        box = (left, 0, left + new_w, img.height)
    else:
        new_h = round(img.width / target_ratio)
        top = max(0, min(top, img.height - new_h))
        box = (0, top, img.width, top + new_h)
    return img.crop(box)


def encode_under_budget(img, fmt, budget, start_q, floor=15, step=5):
    """Encode img in-memory, stepping quality down until it fits budget
    or floor is reached. Returns (bytes, quality_used)."""
    q = start_q
    data = b""
    while True:
        buf = io.BytesIO()
        if fmt == "WEBP":
            img.save(buf, "WEBP", quality=q, method=6)
        else:
            img.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        data = buf.getvalue()
        if len(data) <= budget or q <= floor:
            return data, q
        q -= step


def process(category, name, url):
    max_w, webp_q0, jpeg_q0 = PROFILES[category]
    budget = IMG_BUDGETS[category]
    target = OUT / category
    target.mkdir(parents=True, exist_ok=True)
    try:
        raw = fetch(url)
    except Exception as exc:
        print(f"  SKIP {name}: {exc}")
        return False

    width = max_w
    webp_data = jpg_data = None
    webp_q = jpeg_q = None
    img = None
    crop = CROPS.get(name)
    for _ in range(8):
        img = Image.open(io.BytesIO(raw))
        # Apply the EXIF orientation (if any) to the actual pixel buffer
        # before anything else touches it — cropping or resizing an
        # un-rotated frame bakes the sideways/upside-down orientation
        # permanently into the output.
        img = ImageOps.exif_transpose(img).convert("RGB")
        if crop:
            img = crop_to_aspect(img, *crop)
        if img.width > width:
            height = round(img.height * width / img.width)
            img = img.resize((width, height), Image.LANCZOS)
        webp_data, webp_q = encode_under_budget(img, "WEBP", budget, webp_q0)
        jpg_data, jpeg_q = encode_under_budget(img, "JPEG", budget, jpeg_q0)
        if len(webp_data) <= budget and len(jpg_data) <= budget:
            break
        width = max(200, round(width * 0.85))

    (target / f"{name}.webp").write_bytes(webp_data)
    (target / f"{name}.jpg").write_bytes(jpg_data)
    over = len(webp_data) > budget or len(jpg_data) > budget
    flag = "  ** OVER BUDGET **" if over else ""
    print(f"  {name}: {img.width}x{img.height}  "
          f"webp {len(webp_data)/1024:.0f}KB(q{webp_q})  "
          f"jpg {len(jpg_data)/1024:.0f}KB(q{jpeg_q}){flag}")
    return True


def process_logo():
    target = OUT / "logo"
    target.mkdir(parents=True, exist_ok=True)
    budget = IMG_BUDGETS["logo"]
    try:
        raw = fetch(LOGO_URL)
    except Exception as exc:
        print(f"  SKIP visr-logo: {exc}")
        return False

    width = LOGO_WIDTH
    data = b""
    img = None
    for _ in range(6):
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        if img.width > width:
            height = round(img.height * width / img.width)
            img = img.resize((width, height), Image.LANCZOS)
        for colors in (256, 128, 64, 32):
            quant = img.quantize(colors=colors)
            buf = io.BytesIO()
            quant.save(buf, "PNG", optimize=True)
            data = buf.getvalue()
            if len(data) <= budget:
                break
        if len(data) <= budget:
            break
        width = max(120, round(width * 0.85))

    (target / "visr-logo.png").write_bytes(data)
    over = len(data) > budget
    flag = "  ** OVER BUDGET **" if over else ""
    print(f"  visr-logo: {img.width}x{img.height}  png {len(data)/1024:.0f}KB{flag}")
    return True


SOURCE_DIR = ROOT / "_source"

# name -> (source filename, vertical crop anchor). The anchor is a fraction
# (0.0-1.0) of the vertical slack between the source height and the 4:5
# crop height: 0.0 anchors the crop at the top of the frame (keeps the
# most headroom, trims from the bottom), 1.0 anchors it at the bottom.
# Both portraits are headshots with the face high in frame, so both use
# a low anchor; the exact values were tuned by eye against the actual
# crops (see task-13-report.md), not computed from face detection.
PORTRAITS = {
    "wernke": ("Wernke_Steven.jpg", 0.12),
    "zimmer-dauphinee": ("JamesHeadshot.jpg", 0.08),
}


def process_portraits():
    """Crop and encode the staff portraits in PORTRAITS to 600x750 (4:5),
    reusing crop_to_aspect() and encode_under_budget() rather than
    hand-rolling crop math. Source files live in the gitignored _source/
    directory and are skipped (not fatal) if not present."""
    target = OUT / "portrait"
    target.mkdir(parents=True, exist_ok=True)
    budget = IMG_BUDGETS["portrait"]
    _, webp_q0, jpeg_q0 = PROFILES["portrait"]
    ok = True
    for name, (filename, anchor) in PORTRAITS.items():
        src = SOURCE_DIR / filename
        if not src.is_file():
            print(f"  SKIP {name}: {src} not found")
            ok = False
            continue
        img = Image.open(src)
        # Apply EXIF orientation before cropping, same as process().
        img = ImageOps.exif_transpose(img).convert("RGB")
        crop_h = round(img.width * 5 / 4)
        slack = max(0, img.height - crop_h)
        top = round(slack * anchor)
        img = crop_to_aspect(img, 4, 5, top)
        img = img.resize((600, 750), Image.LANCZOS)
        webp_data, webp_q = encode_under_budget(img, "WEBP", budget, webp_q0)
        jpg_data, jpeg_q = encode_under_budget(img, "JPEG", budget, jpeg_q0)
        (target / f"{name}.webp").write_bytes(webp_data)
        (target / f"{name}.jpg").write_bytes(jpg_data)
        over = len(webp_data) > budget or len(jpg_data) > budget
        flag = "  ** OVER BUDGET **" if over else ""
        print(f"  {name}: 600x750  "
              f"webp {len(webp_data)/1024:.0f}KB(q{webp_q})  "
              f"jpg {len(jpg_data)/1024:.0f}KB(q{jpeg_q}){flag}")
    return ok


def main():
    print("Processing imagery...")
    ok = sum(process(c, n, u) for c, n, u in SOURCES)
    ok += process_logo()
    ok += process_portraits()
    total = len(SOURCES) + 2
    print(f"\n{ok}/{total} images processed")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
