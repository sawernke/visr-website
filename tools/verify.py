"""Static verification for the VISR site. Run: python tools/verify.py"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "index.html",
    "about/index.html",
    "services/index.html",
    "geophysical-survey/index.html",
    "geospatial-projects/index.html",
    "augmented-reality/index.html",
    "trainings/index.html",
    "news/index.html",
    "team/index.html",
]

# Pages compared for chrome (head boilerplate/header/boot/footer) identity.
# 404.html carries the same chrome as every content page but is deliberately
# NOT in PAGES: it should not be subject to checks meant for content pages
# (e.g. internal-link resolution, redirect-stub requirements) that would
# misfire on an error page.
CHROME_PAGES = PAGES + ["404.html"]

# The chrome regions compared byte-for-byte (after normalize_chrome) across
# CHROME_PAGES and against tools/page-template.html. HEAD covers the
# boilerplate <head> boilerplate shared by every page (font preloads,
# stylesheet link, inline boot script) but excludes <title>/<meta
# name="description">, which are legitimately different per page. BOOT
# covers the skip-link through the opening <main> tag (nesting HEADER,
# which is also checked on its own for a more specific failure message).
CHROME_REGIONS = ("HEAD", "HEADER", "BOOT", "FOOTER")

REDIRECTS = {
    "about-visr/index.html": "/about/",
    "visr/about/index.html": "/about/",
    "visr/our-services/index.html": "/services/",
    "visr/geophysical-survey/index.html": "/geophysical-survey/",
    "visr/geospatial-projects/index.html": "/geospatial-projects/",
    "augmented-reality-offerings/index.html": "/augmented-reality/",
    "visr/trainings/index.html": "/trainings/",
    "visr-in-the-news/index.html": "/news/",
    "visr/meet-the-team/index.html": "/team/",
}

# Max bytes per image, by directory under assets/img/
IMG_BUDGETS = {
    "hero": 250_000,
    "inline": 150_000,
    "news": 60_000,
    "portrait": 80_000,
    # Two logo assets share this bucket: visr-logo.png (the header
    # lockup, on the ten pages that show one) and visr-wordmark.png
    # (the home-page band, drawn 320px wide). The wordmark file is
    # 800px, well over the 640px that 2x needs, so it also holds up on
    # a 3x phone and leaves room to enlarge the band later without
    # rebuilding. The topographic texture inside the letterforms is
    # what costs the bytes — it does not palette-compress away. The
    # homepage total still lands far under HOMEPAGE_BUDGET below.
    "logo": 45_000,
}

HOMEPAGE_BUDGET = 800_000

FORBIDDEN = [
    (r"343[-.\s]?1893", "phone number"),
    (r"mailto:", "mailto: link"),
    (r"[\w.]+@vanderbilt\.edu", "plaintext email address"),
    (r"wp-content", "WordPress asset path"),
    (r"visrvu\.org/visr", "legacy /visr/ path"),
    (r"fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net",
     "third-party font/CDN request"),
    (r"PAGE_TITLE", "unreplaced PAGE_TITLE template placeholder"),
    (r"PAGE_DESC", "unreplaced PAGE_DESC template placeholder"),
    (r"PAGE_CONTENT", "unreplaced PAGE_CONTENT template placeholder"),
]

failures = []


def fail(msg):
    failures.append(msg)


class PageParser(HTMLParser):
    """Collects headings, images, links, and landmark elements."""

    def __init__(self):
        super().__init__()
        self.headings = []      # list of int levels
        self.images = []        # list of attr dicts
        self.links = []         # list of href strings
        self.landmarks = set()
        self.title = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        elif tag == "img":
            self.images.append(a)
        elif tag == "a" and "href" in a:
            self.links.append(a["href"])
        elif tag in ("header", "nav", "main", "footer"):
            self.landmarks.add(tag)
        if self._in_title is False and tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and self.title is None:
            self.title = data.strip()


def relative_luminance(hex_color):
    hex_color = hex_color.lstrip("#")
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(fg, bg):
    lighter = max(relative_luminance(fg), relative_luminance(bg))
    darker = min(relative_luminance(fg), relative_luminance(bg))
    return (lighter + 0.05) / (darker + 0.05)


def normalize_chrome(block):
    """Strip per-page attributes so chrome blocks compare equal across pages."""
    return re.sub(r'\s*aria-current="page"', "", block).strip()


def extract_chrome(text, name):
    match = re.search(
        rf"<!-- CHROME:{name}:START -->(.*?)<!-- CHROME:{name}:END -->",
        text, re.S)
    return normalize_chrome(match.group(1)) if match else None


def check_pages_exist():
    for page in PAGES:
        if not (ROOT / page).is_file():
            fail(f"missing page: {page}")


def _iter_html_files():
    """Yield HTML files, excluding docs/ and tools/ at repo root."""
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in ("docs", "tools"):
            continue
        yield path


def check_forbidden_strings():
    for path in _iter_html_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, label in FORBIDDEN:
            if re.search(pattern, text, re.I):
                rel = path.relative_to(ROOT)
                fail(f"{rel}: contains {label} (/{pattern}/)")



# Natalie Robbins is no longer VISR's contact (that's what this check
# guards against — a stale mailto/phone/name pointing a visitor at a
# former staffer). Research credit is a different thing: she is a former
# colleague named as a collaborator on published research, and removing
# her name from that credit was never the intent of the rule. So her name
# is permitted here too, alongside team/index.html's "Past Staff" entry.
NATALIE_PERMITTED_PAGES = {"team/index.html", "geospatial-projects/index.html"}


def check_natalie_scoped():
    for path in _iter_html_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"natalie", text, re.I) and rel not in NATALIE_PERMITTED_PAGES:
            fail(f"{rel}: mentions Natalie outside {sorted(NATALIE_PERMITTED_PAGES)}")


def check_email_format():
    """The literal obfuscated address must appear wherever contact is given."""
    for page in ("index.html", "about/index.html", "team/index.html"):
        path = ROOT / page
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "s.wernke[at]vanderbilt.edu" not in text:
            fail(f"{page}: missing obfuscated contact email")


def check_structure():
    for page in PAGES:
        path = ROOT / page
        if not path.is_file():
            continue
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))

        h1s = [h for h in parser.headings if h == 1]
        if len(h1s) != 1:
            fail(f"{page}: expected exactly one <h1>, found {len(h1s)}")

        prev = 0
        for level in parser.headings:
            if prev and level > prev + 1:
                fail(f"{page}: heading level jumps h{prev} -> h{level}")
            prev = level

        for landmark in ("header", "nav", "main", "footer"):
            if landmark not in parser.landmarks:
                fail(f"{page}: missing <{landmark}> landmark")

        if not parser.title:
            fail(f"{page}: missing or empty <title>")

        for img in parser.images:
            src = img.get("src", "?")
            if "alt" not in img:
                fail(f"{page}: <img src={src}> missing alt")
            if "width" not in img or "height" not in img:
                fail(f"{page}: <img src={src}> missing width/height")


def check_internal_links():
    for page in PAGES:
        path = ROOT / page
        if not path.is_file():
            continue
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        for href in parser.links:
            if href.startswith(("http://", "https://", "#", "tel:")):
                continue
            target = href.split("#")[0].split("?")[0]
            if not target:
                continue
            resolved = (ROOT / target.lstrip("/")) if target.startswith("/") \
                else (path.parent / target)
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.exists():
                fail(f"{page}: broken internal link -> {href}")


def check_redirects():
    for stub, destination in REDIRECTS.items():
        path = ROOT / stub
        if not path.is_file():
            fail(f"missing redirect stub: {stub}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "http-equiv=\"refresh\"" not in text.replace("'", '"'):
            fail(f"{stub}: no meta refresh")
        if destination not in text:
            fail(f"{stub}: does not point at {destination}")
        if "rel=\"canonical\"" not in text.replace("'", '"'):
            fail(f"{stub}: missing canonical link")


def check_image_budgets():
    img_root = ROOT / "assets" / "img"
    if not img_root.is_dir():
        fail("missing assets/img/")
        return
    for path in sorted(img_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in \
                (".jpg", ".jpeg", ".png", ".webp"):
            continue
        bucket = path.relative_to(img_root).parts[0]
        budget = IMG_BUDGETS.get(bucket)
        if budget is None:
            fail(f"assets/img/{bucket}/: not a known budget category")
            continue
        size = path.stat().st_size
        if size > budget:
            rel = path.relative_to(ROOT)
            fail(f"{rel}: {size:,} bytes exceeds {budget:,} budget")


def check_homepage_weight():
    index = ROOT / "index.html"
    if not index.is_file():
        return
    total = index.stat().st_size
    parser = PageParser()
    parser.feed(index.read_text(encoding="utf-8", errors="replace"))
    for img in parser.images:
        src = img.get("src", "").lstrip("/")
        candidate = ROOT / src
        if candidate.is_file():
            total += candidate.stat().st_size
    for asset in ("assets/css/site.css",):
        path = ROOT / asset
        if path.is_file():
            total += path.stat().st_size
    fonts = ROOT / "assets" / "fonts"
    if fonts.is_dir():
        total += sum(f.stat().st_size for f in fonts.glob("*.woff2"))
    if total > HOMEPAGE_BUDGET:
        fail(f"homepage weight {total:,} bytes exceeds "
             f"{HOMEPAGE_BUDGET:,} budget")


def check_chrome_identical():
    """Every page's chrome must match tools/page-template.html (the anchor),
    AND pages must match each other. These are reported as two distinct
    failure kinds because they mean different things to whoever has to fix
    it: "differs from template" points at one wrong page; "differs across
    pages" means the pages themselves have drifted apart from one another
    (which can happen even when a template comparison isn't available).
    Runs over CHROME_PAGES (content pages plus 404.html) and CHROME_REGIONS
    (head boilerplate, header, boot, footer) so chrome that isn't header or
    footer -- the preload links, the stylesheet link, the inline boot
    script, the skip-link, and the opening <main> tag -- is guarded too."""
    template_path = ROOT / "tools" / "page-template.html"
    template_blocks = {}
    if not template_path.is_file():
        fail("missing tools/page-template.html (chrome anchor)")
    else:
        template_text = template_path.read_text(encoding="utf-8", errors="replace")
        for name in CHROME_REGIONS:
            block = extract_chrome(template_text, name)
            if block is None:
                fail(f"tools/page-template.html: missing CHROME:{name} markers")
            template_blocks[name] = block

    seen = {}
    for page in CHROME_PAGES:
        path = ROOT / page
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in CHROME_REGIONS:
            block = extract_chrome(text, name)
            if block is None:
                fail(f"{page}: missing CHROME:{name} markers")
                continue
            seen.setdefault(name, {}).setdefault(block, []).append(page)

            template_block = template_blocks.get(name)
            if template_block is not None and block != template_block:
                fail(f"{page}: CHROME:{name} differs from tools/page-template.html")

    for name, variants in seen.items():
        if len(variants) > 1:
            groups = " | ".join(
                f"{len(pages)} page(s): {pages[0]}"
                for pages in variants.values())
            fail(f"CHROME:{name} differs across pages -> {groups}")


# The decorative gold must NOT be used as a text color anywhere. Matches
# bare `color:` (including the CSS custom-property fallback form) but the
# negative lookbehind stops it from also matching hyphenated color-family
# properties that legitimately use the decorative gold, e.g.
# text-decoration-color, border-color, background-color, outline-color.
# It also correctly does not match --gold-deep, which is the sanctioned
# text accent.
GOLD_TEXT_COLOR_RE = re.compile(
    r"(?<![-\w])color:\s*var\(\s*--gold\s*[,)]", re.I)

# Fixtures pinning that regex's boundary so a future edit can't silently
# reopen either failure mode: missing a real violation, or rejecting a
# legitimate decorative use.
_GOLD_REGEX_MUST_MATCH = [
    "color: var(--gold)",
    "color: var(--gold, #CFAE70)",
    "COLOR: VAR(--GOLD)",
]
_GOLD_REGEX_MUST_NOT_MATCH = [
    "color: var(--gold-deep)",
    "text-decoration-color: var(--gold)",
    "border-color: var(--gold)",
    "background-color: var(--gold)",
    "outline-color: var(--gold)",
]


def check_gold_regex_selftest():
    """Guard against regressions in GOLD_TEXT_COLOR_RE itself."""
    for case in _GOLD_REGEX_MUST_MATCH:
        if not GOLD_TEXT_COLOR_RE.search(case):
            fail(f"harness self-test: gold-text-color regex should match "
                 f"{case!r} but did not")
    for case in _GOLD_REGEX_MUST_NOT_MATCH:
        if GOLD_TEXT_COLOR_RE.search(case):
            fail(f"harness self-test: gold-text-color regex should NOT "
                 f"match {case!r} but did")


def check_contrast():
    css = ROOT / "assets" / "css" / "site.css"
    if not css.is_file():
        fail("missing assets/css/site.css")
        return
    text = css.read_text(encoding="utf-8", errors="replace")
    tokens = dict(re.findall(r"(--[\w-]+):\s*(#[0-9A-Fa-f]{6})", text))
    required = ["--bg", "--ink", "--ink-muted", "--gold-deep", "--bg-subtle"]
    for token in required:
        if token not in tokens:
            fail(f"site.css: missing token {token}")
    if any(t not in tokens for t in required):
        return
    pairs = [
        ("--ink", "--bg", 4.5),
        ("--ink", "--bg-subtle", 4.5),
        ("--ink-muted", "--bg", 4.5),
        ("--gold-deep", "--bg", 4.5),
        # The footer actually renders these two pairs (ink-muted body text
        # and the gold-deep "Contact"/"Quick Links"/"Connect" headings, both
        # against --bg-subtle rather than --bg). gold-deep on bg-subtle is
        # 4.64:1 -- only 0.14 above the 4.5 floor -- so it is worth guarding
        # explicitly rather than trusting it stays clear as tokens change.
        ("--ink-muted", "--bg-subtle", 4.5),
        ("--gold-deep", "--bg-subtle", 4.5),
    ]
    for fg, bg, minimum in pairs:
        ratio = contrast_ratio(tokens[fg], tokens[bg])
        if ratio < minimum:
            fail(f"contrast {fg} on {bg} = {ratio:.2f}:1, "
                 f"below {minimum}:1")
    if GOLD_TEXT_COLOR_RE.search(text):
        fail("site.css: --gold used as a text color (use --gold-deep)")


def main():
    check_gold_regex_selftest()
    check_pages_exist()
    check_forbidden_strings()
    check_natalie_scoped()
    check_email_format()
    check_structure()
    check_internal_links()
    check_redirects()
    check_image_budgets()
    check_homepage_weight()
    check_chrome_identical()
    check_contrast()

    if failures:
        print(f"FAIL — {len(failures)} problem(s):\n")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS — all checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
