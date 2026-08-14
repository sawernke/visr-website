# VISR website

This is the source for the Vanderbilt Institute for Spatial Research (VISR)
website. It deploys to **<https://visrvu.org>** via GitHub Pages.

It is a plain static site: nine content pages, each a single hand-written
HTML file, a shared stylesheet, self-hosted images and fonts, and a small
inline script in each page's `<head>` that runs the mobile nav toggle.
There is **no build step** — no npm, no static site generator,
no compiler. Whatever is in a page's `.html` file is exactly what gets
served. That is a deliberate choice: it keeps the site editable by opening
a file in a text editor, with nothing to install and nothing to go stale.

The tradeoff for having no build step is explained in "The nav duplication
warning" below — read that section before editing the header or footer.

**Before touching the Bluehost account, read "The registrar caveat" section
below — cancelling or downgrading it at the wrong time can forfeit the
`visrvu.org` domain, not just take the site offline.**

## Repo layout

```text
index.html                      Homepage
about/index.html                 About VISR
services/index.html              Our Services
geophysical-survey/index.html    Geophysical Survey
geospatial-projects/index.html   Geospatial Projects
augmented-reality/index.html     Augmented Reality
trainings/index.html             Trainings
news/index.html                  VISR in the News
team/index.html                  Meet the Team

404.html             Custom "page not found" page
CNAME                Tells GitHub Pages which domain to serve (visrvu.org)
.nojekyll             Tells GitHub Pages not to run Jekyll over the site
favicon.ico           Browser-tab icon; found automatically at the site
                      root, no <link rel="icon"> needed in any page

about-visr/, augmented-reality-offerings/, visr-in-the-news/, visr/
                      Redirect stubs for old WordPress URLs (see below)

assets/css/site.css   The one stylesheet for the whole site
assets/img/           Site imagery, already sized and compressed
assets/fonts/         Self-hosted web fonts (no Google Fonts, no CDN)

tools/verify.py            Checks the site before you push. Run this.
tools/page-template.html   The master copy of the header/footer chrome
tools/make_redirects.py    Regenerates the nine redirect stub files
tools/optimize_images.py   Re-downloads and re-compresses source imagery

styleguide.html       A reference page showing the design system in one place
```

## How to preview the site locally

Every asset path in this site is root-relative (`/assets/css/site.css`,
not `assets/css/site.css`), so double-clicking `index.html` to open it
directly in a browser does **not** work — the browser resolves those
paths against your filesystem root, not the repo root, so you get an
unstyled page with broken links and broken images. Serve the repo with a
trivial local HTTP server instead:

```bash
python -m http.server 8000
```

Run that from the repo root, then open <http://localhost:8000/>. Every
root-relative path resolves correctly this way, the same as it will once
the site is live.

## How to edit content

Every page is a plain HTML file. To change text, open the relevant file in
any text editor (Notepad, VS Code, whatever you have) and edit the words
between the tags. For example, to change a sentence on the About page,
open `about/index.html`, find the sentence, edit it, save, and you're done.

There is no need to run anything to "build" the site — the file you save
is the file that gets served. You do still need to run the verification
script before pushing (see below), and if you're changing images, see the
asset pipeline section.

A few conventions worth knowing:

- Each page has exactly one `<h1>` (the main page heading) and then `<h2>`,
  `<h3>`, etc. in order, without skipping a level. The verification script
  enforces this, so if you add a new section, pick the right heading level.
- Every `<img>` needs an `alt` description and a `width`/`height`, both
  already set correctly on the existing images.
- The contact email is never written as a real, clickable address. It
  appears as the literal text `s.wernke[at]vanderbilt.edu` — this is
  intentional, to keep it out of spam-harvesting bots' reach. Don't
  "fix" it into a `mailto:` link.

## The nav duplication warning (read this before touching the header or footer)

Because there is no build step, there is no way to share one header and
one footer across every page automatically — each page is a standalone
file with its own copy. Right now the shared chrome appears **eleven
times**: once in each of the nine content pages, once in `404.html`, and
once more in `tools/page-template.html`, which serves as the
master/reference copy.

"Chrome" here means four separate regions, each marked in the HTML with an
`<!-- CHROME:NAME:START -->` / `<!-- CHROME:NAME:END -->` comment pair so
`verify.py` can find and compare them:

- `HEAD` — the font preload links, the stylesheet link, and the inline
  boot script in `<head>` (but not `<title>`/`<meta name="description">`,
  which are correctly different on every page).
- `HEADER` — the `<header>` with the logo and primary nav.
- `BOOT` — the skip-link through the opening `<main id="main"
  tabindex="-1">` tag.
- `FOOTER` — the `<footer>` with contact info and quick links.

**If you change any of these, you must make the identical change in all
eleven places.** Add a nav link, change the address in the footer, tweak
the copyright year — whatever it is, it has to happen eleven times or the
site ends up with pages that look or behave inconsistently depending
which one a visitor lands on.

This sounds fragile, and it would be if nothing were watching for it. It
isn't watching by hand — `python tools/verify.py` (see below) compares all
four chrome regions on every page, including `404.html`, byte-for-byte
against the copy in `tools/page-template.html`, and fails loudly with the
exact page and region name if anything drifted. That check is the entire
reason it's safe to hand-edit HTML like this instead of needing a
templating system: as long as you run verification before you push, you
cannot silently ship a page with stale chrome.

Practical workflow: edit `tools/page-template.html` first to work out the
change, then copy the same block into each of the nine content pages and
into `404.html`, then run `python tools/verify.py` to confirm all eleven
agree.

## How to remove the hiring banner

The homepage currently shows a banner announcing that VISR is hiring a
Program Manager. Once that position is filled, remove it by deleting the
`<aside class="hiring">...</aside>` block from `index.html` — the whole
element, from `<aside class="hiring">` to its closing `</aside>`. Save,
run verification, and push.

## How to run verification

Before every push, run:

```bash
python tools/verify.py
```

from the repo root. It checks, among other things:

- All nine pages exist and have the required structure (one `<h1>`,
  no skipped heading levels, alt text on images, etc).
- The chrome (head boilerplate, header, boot region, footer) hasn't
  drifted between any of the eleven copies, `404.html` included (see
  above).
- No forbidden content has crept in: the real phone number, a `mailto:`
  link, a plaintext `@vanderbilt.edu` address, leftover WordPress asset
  paths, or a request to a third-party font/CDN service.
- All internal links point somewhere that actually exists.
- The nine legacy-URL redirect stubs are present and correctly configured.
- Images are within their size budgets, and the homepage's total weight
  is under budget.
- Text has enough contrast against its background to be readable.

If it prints `PASS — all checks green` and exits with status 0, you're
good to push. If it prints `FAIL` followed by a list of problems, **do
not push** — each line names the file and the specific problem, which is
usually enough to go fix directly. Re-run the script after fixing until
it passes.

## How to re-run the asset pipeline

The images on the site were downloaded from the old WordPress site,
cropped, resized, and compressed by `tools/optimize_images.py`. You
should only need to run this again if you're replacing or adding imagery.

First, install the one dependency it needs:

```bash
pip install --user Pillow
```

Then run:

```bash
python tools/optimize_images.py
```

**Important Windows-specific warning:** Windows ships with its own
built-in `convert.exe` (in `System32`), which converts a disk's file
system from FAT to NTFS — it has nothing to do with images. It is easy
to invoke it by accident if you type `convert` at a prompt expecting the
unrelated ImageMagick tool of the same name — ImageMagick is **not**
used anywhere in this project. All image processing here goes through
Pillow (the Python library imported by `optimize_images.py`). Never run
`convert.exe` expecting it to touch an image file.

Staff portrait photos are cropped from originals kept in `_source/`,
which is intentionally excluded from the repository (see `.gitignore`) —
it holds full-resolution originals that don't need to be published. If
you're adding a new portrait, drop the source photo in `_source/`, add
an entry to the `PORTRAITS` dict near the top of `optimize_images.py`,
and re-run the script.

## Legacy URL redirects

The old WordPress site had different URLs than this one (for example,
`/visr/about/` instead of `/about/`). To keep old inbound links and
search engine results working, nine small "redirect stub" pages exist at
the old paths; each one immediately forwards the visitor to the new page.

These are generated, not hand-written, from the `REDIRECTS` mapping at
the top of `tools/verify.py`. If a URL ever needs to move again, update
that mapping and regenerate the stubs with:

```bash
python tools/make_redirects.py
```

Do not hand-edit the files under `about-visr/`, `augmented-reality-offerings/`,
`visr-in-the-news/`, or `visr/` — regenerate them instead, so all nine stay
consistent with one template.

## DNS records for the cutover

The domain `visrvu.org` currently points at the old Bluehost-hosted
WordPress site. Moving the live domain to GitHub Pages requires updating
DNS. **DNS is managed at Bluehost** (`ns1.bluehost.com` /
`ns2.bluehost.com`), regardless of where the site itself is hosted — this
is a separate step from anything in this repository, and it is the step
that actually makes `visrvu.org` show the new site to the public.

The current apex `A` record points at `66.235.200.147`. Replace it with
these four `A` records (all four, not just one — GitHub Pages load-balances
across them):

```text
A    @    185.199.108.153
A    @    185.199.109.153
A    @    185.199.110.153
A    @    185.199.111.153
```

Optionally, also add IPv6 support:

```text
AAAA @    2606:50c0:8000::153
AAAA @    2606:50c0:8001::153
AAAA @    2606:50c0:8002::153
AAAA @    2606:50c0:8003::153
```

And point `www` at GitHub's hosting instead of the apex:

```text
CNAME www  sawernke.github.io.
```

**Before making this change, re-verify these IP addresses against
GitHub's current Pages documentation.** They have been stable for years,
but GitHub does not guarantee they are permanent, and a stale address
here would take the entire site offline with no obvious error message.
Do not treat the list above as something to trust indefinitely — it was
verified against GitHub's documentation on 2026-08-13, and DNS values can
change without much notice.

After DNS propagates, enable **Enforce HTTPS** in the repository's GitHub
Pages settings once GitHub has issued a certificate for the domain — this
can take a few minutes to a few hours after the DNS change lands.

## The registrar caveat (important — read before touching the Bluehost account)

Moving *hosting* to GitHub Pages (the DNS change above) is separate from
domain *registration*, which stays with Bluehost. **`visrvu.org` remains
registered through Bluehost even after the site itself is served from
GitHub Pages.**

**Do not cancel or downgrade the Bluehost account until the domain
registration has been separately transferred elsewhere (or a plan
covering just registration has been confirmed to remain active).**
Cancelling the Bluehost account while it is still the domain's registrar
would let the registration lapse and could forfeit `visrvu.org` entirely
— it does not merely take the website offline, it can lose the domain
name itself, which is a much harder problem to undo. Registrar transfer
is a separate, deliberate step and is not addressed by anything in this
repository.

## Deploying (not yet done)

As of this repository's current state, the site has not been pushed to a
public GitHub repository or connected to GitHub Pages — that is a
deliberate decision requiring the site owner's authorization, not
something automated as part of building the pages.

**A sequencing problem to know about before pushing:** `CNAME` (containing
`visrvu.org`) is already committed to this repo. GitHub Pages reads that
file on the very first deploy and configures the custom domain
immediately — so `https://<username>.github.io/<repo>/` will **not** show
a working preview of the new site. It will instead redirect straight to
`visrvu.org`, which still points at the old Bluehost site until the DNS
change above is made. "Push, then verify at the `github.io` URL before
touching DNS" therefore cannot work as long as `CNAME` ships in that first
push. Use one of these two sequences instead:

1. **Hold `CNAME` out of the first push, add it back after verifying.**
   Push everything except `CNAME` (temporarily move it aside, or delete
   and re-add it in a later commit), enable Pages, and confirm the site
   looks right at the `github.io` URL. Once satisfied, commit `CNAME` and
   push again — *then* make the DNS change described above.
2. **Skip `github.io` verification and verify after DNS propagates.**
   Push everything including `CNAME` from the start, enable Pages, make
   the DNS change immediately, and do the visual/functional check at
   `visrvu.org` itself once DNS has propagated (anywhere from a few
   minutes to about 48 hours, depending on the old record's TTL).

Either way, broadly: create the GitHub repository, push this code, enable
Pages (source: the default branch, folder `/`), and only then make the
DNS change described above.
