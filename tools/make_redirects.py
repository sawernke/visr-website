"""Generate the legacy-URL redirect stubs from REDIRECTS in verify.py.

Run: python tools/make_redirects.py

Each stub is a tiny static HTML file at the old WordPress path that
meta-refreshes the visitor to the new location, so existing inbound links
and search results keep working. Generating all nine from one template
means they cannot drift from each other or from REDIRECTS in verify.py,
which is the single source of truth for where each old path should go.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from verify import REDIRECTS, ROOT  # noqa: E402  (path must be set first)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={dest}">
<link rel="canonical" href="https://visrvu.org{dest}">
<title>Redirecting…</title>
</head>
<body>
<p>This page has moved. <a href="{dest}">Continue to its new location</a>.</p>
</body>
</html>
"""


def main():
    for stub, dest in REDIRECTS.items():
        path = ROOT / stub
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TEMPLATE.format(dest=dest), encoding="utf-8")
        print(f"  {stub} -> {dest}")


if __name__ == "__main__":
    main()
