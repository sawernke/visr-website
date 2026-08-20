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

**Work in progress:** the domain is due to move from Bluehost to easyDNS,
after which Bluehost is to be closed. It is paused and not started. Pick it
up at "Registrar transfer to easyDNS (paused — start here)" below.

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
assets/img/           Site imagery, already sized and compressed.
                      logo/ holds two files: visr-logo.png (header)
                      and visr-wordmark.png (home-page band).
assets/fonts/         Self-hosted web fonts (see "Fonts" below)

tools/verify.py            Checks the site before you push. Run this.
tools/page-template.html   The master copy of the header/footer chrome
tools/make_redirects.py    Regenerates the nine redirect stub files
tools/optimize_images.py   Re-downloads and re-compresses source imagery

styleguide.html       A reference page showing the design system in one place

docs/                 The original design spec and build plan, dated
                      2026-08-13. A historical record of how the site was
                      built, deliberately left unedited — it describes the
                      site as first designed, not as it stands today. Where
                      the two disagree, this README is correct. (The spec
                      still describes serif headings, for example.)
```

## How to preview the site locally

Every asset path in this site is root-relative (`/assets/css/site.css`,
not `assets/css/site.css`), so double-clicking `index.html` to open it
directly in a browser does **not** work — the browser resolves those
paths against your filesystem root, not the repo root, so you get an
unstyled page with broken links and broken images. Serve the repo with a
trivial local HTTP server instead:

```bash
python3 -m http.server 8000
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
- The director's name links to `https://stevenwernke.com` in exactly three
  places: the footer `Contact` block (so, every page), and on the Team page
  only, both the `Get in touch` line and the card heading. The `Get in
  touch` line on the other five pages is deliberately plain text — one link
  per page in the body is enough, and the footer already carries it. The
  footer copy takes `class="name-link"` because the footer's own link style
  is colored and underline-free, which would make the name read as *less*
  prominent than the text beside it; that class restores the normal
  underlined-link look. These three take `target="_blank"` so the director's
  site opens in a new tab; every other external link on the site (LinkedIn,
  the job posting) stays in the same tab with `rel="noopener"` and no
  `target`.
- The primary nav carries eight items and the page each one points at marks
  its own link with `aria-current="page"`. That attribute is the one part of
  the chrome allowed to differ per page — `verify.py` strips it before
  comparing, so a nav item that is current on one page does not read as
  drift. If you add a nav item, remember to add it to all eleven copies,
  including `tools/page-template.html`, and to set `aria-current` on the
  page it targets.
- Vertical rhythm is one value: `section { padding-block: var(--s7) }`, so
  every section has 48px above and below it and neighbours sit 96px apart.
  Change that one declaration and the whole site moves together. `h1 +
  .prose` adds a 16px gap under a page title, because the reset zeroes every
  heading margin and an `<h1>` is large enough to need it.
- An entry in a `.titled-list` can carry a photo beside its own text: give
  the `<li>` `class="has-figure"` and put a `<picture>` inside it, after the
  `<p>`. The rules in `site.css` put the text left and the photo right in a
  200px column, and stack them on a phone. The Geophysical Survey page uses
  this for its three instrument photos. Don't put `class="img-portrait"` on
  those images — that class centres a standalone image and fights the grid.

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
isn't watching by hand — `python3 tools/verify.py` (see below) compares all
four chrome regions on every page, including `404.html`, byte-for-byte
against the copy in `tools/page-template.html`, and fails loudly with the
exact page and region name if anything drifted. That check is the entire
reason it's safe to hand-edit HTML like this instead of needing a
templating system: as long as you run verification before you push, you
cannot silently ship a page with stale chrome.

Practical workflow: edit `tools/page-template.html` first to work out the
change, then copy the same block into each of the nine content pages and
into `404.html`, then run `python3 tools/verify.py` to confirm all eleven
agree.

## How to remove the hiring banner

The homepage currently shows a banner announcing that VISR is hiring a
Program Manager. Once that position is filled, remove it by deleting the
`<aside class="hiring">...</aside>` block from `index.html` — the whole
element, from `<aside class="hiring">` to its closing `</aside>`. Save,
run verification, and push.

## The home-page wordmark band

`index.html` opens with a full-width tinted band holding the VISR
wordmark, above the hero heading. It is the `<div class="logo-band">`
block, and it is the only place `visr-wordmark.png` is used — no other
page has one, so `.logo-band` only ever matches on the home page.

Two things to know before changing it:

- The image carries `alt=""` **on purpose**. The header lockup directly
  above it already announces "VISR — Vanderbilt Institute for Spatial
  Research", so giving this one alt text too would make a screen reader
  say the same thing twice in a row. It is decorative here.
- Its displayed width is set once, in `.logo-band img` in `site.css`
  (320 px). The asset is 800 px, so you can go up to about 400 px before
  a retina screen starts to soften. Past that, raise `WORDMARK_WIDTH` in
  `optimize_images.py` to twice the displayed width and re-run it.

**The home page hides the header lockup.** With the band directly beneath
it, the header's small logo would repeat the same mark twice within about
40 px. The header markup is *not* different there — it cannot be, it is
CHROME. Instead `index.html` alone carries `<body class="home">`, and two
rules in `site.css` (`.home .site-header .wrap > a`) hide the lockup and
push the nav right. The `<body>` tag sits just above
`<!-- CHROME:BOOT:START -->`, so it is outside every chrome region and safe
to differ. If you ever add a second page that should behave this way, give
it the same body class rather than editing the header.

To remove the band, delete the whole `<div class="logo-band">...</div>`
block from `index.html`, drop `class="home"` from its `<body>` so the
header lockup comes back, and raise `.hero h1` again — it was stepped down
when the band was added, because it became a subtitle to the wordmark
rather than the top of the page.

## How to run verification

Before every push, run:

```bash
python3 tools/verify.py
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
pip3 install --user Pillow
```

Then run:

```bash
python3 tools/optimize_images.py
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

### The two logo files

`process_logo()` writes **two** assets from one master, because the logo
does two different jobs at two different sizes:

```text
assets/img/logo/visr-logo.png       400 x 163   the header lockup, on all 11 pages
assets/img/logo/visr-wordmark.png   800 x 325   the home-page wordmark band only
```

The header draws its copy 119 px wide (`.site-header img` in `site.css`),
so 400 px keeps it sharp down to a 3x phone screen. The wordmark band
draws its copy 400 px wide, so 800 px is the 2x retina size. Both are
palette PNGs; the topographic texture inside the letterforms is what
makes them cost ~16 KB and ~39 KB rather than a few KB.

The master is `_source/VISR_logo_v05_for_web/2x/VISR_logo_03@2x.png`
(1392 x 566), supplied by the owner at five resolutions. Like the
portraits, it lives in the gitignored `_source/` tree, so a fresh clone
without it falls back to downloading `LOGO_URL` from the old WordPress
site. **Do not put the master pack back under `assets/img/`** — every
file there is checked against a per-directory byte budget, and the 4x
master alone is 444 KB.

## Fonts

Two families are used, and which one applies depends only on the heading
level:

| Where | Family | Files |
|---|---|---|
| `h1` and `h2` | Roboto 600 | `roboto-600.woff2` |
| `h3` and below, and all body text | Inter 400/500/600 | `inter-400.woff2`, `inter-500.woff2`, `inter-600.woff2` |

That split is set in two places in `assets/css/site.css`: the
`--font-display` and `--font-body` custom properties near the top of the
file, and the `h1, h2, h3` rule under "Typography" (`h3` deliberately
overrides itself back to `--font-body`).

Headings were originally set in Newsreader, a serif. They changed to
sans-serif on 2026-08-17, and Newsreader was removed entirely at the same
time because nothing else referenced it.

### The no-CDN rule

The font *files* are downloaded once, committed to this repository, and
served from this domain. **A visitor's browser never contacts Google Fonts,
jsDelivr, or any other third party.** `verify.py` enforces this: it fails
the build if any page requests `fonts.googleapis.com`, `fonts.gstatic.com`,
or `cdn.jsdelivr.net`.

Note that "no Google Fonts" means no *request* to Google, not that a font
published by Google is off-limits. Roboto is a Google-published font under
the Apache 2.0 licence, downloaded and self-hosted here like any other.
Inter is under the SIL Open Font License. Both licences permit this, and
`assets/fonts/LICENSES.md` records which is which.

### Adding or replacing a font

1. Get the **Latin subset** `.woff2`, not the full family. The subset files
   are 12–25 KB; a full family is many times that. Google Fonts serves the
   subset directly if you request one weight and follow the `latin` block
   of the CSS it returns.
2. Put the file in `assets/fonts/` and record its licence in
   `assets/fonts/LICENSES.md`.
3. Add an `@font-face` rule in the "Fonts" block of `assets/css/site.css`,
   and point `--font-display` or `--font-body` at it.
4. **If the new font replaces a preloaded one, update the preload too.** The
   `<head>` of every page preloads the body font and the heading font by
   filename. That line lives in the shared chrome, so it appears **eleven
   times** — see "The nav duplication warning" above. A preload pointing at
   a deleted file makes every page fetch a 404 at high priority; a preload
   left pointing at an unused font wastes the same bandwidth silently.
5. Delete any font that is no longer referenced, and run
   `python3 tools/verify.py`. It checks the total weight of
   `assets/fonts/*.woff2` against a budget.

As of 2026-08-17 the site ships four files totalling about 89 KB.

## Legacy URL redirects

The old WordPress site had different URLs than this one (for example,
`/visr/about/` instead of `/about/`). To keep old inbound links and
search engine results working, nine small "redirect stub" pages exist at
the old paths; each one immediately forwards the visitor to the new page.

These are generated, not hand-written, from the `REDIRECTS` mapping at
the top of `tools/verify.py`. If a URL ever needs to move again, update
that mapping and regenerate the stubs with:

```bash
python3 tools/make_redirects.py
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

## Deployment status (live)

The site is deployed. It is served by GitHub Pages from
<https://github.com/sawernke/visr-website>, from the default branch, folder
`/`.

The DNS cutover described above has been made. As verified on 2026-08-17:

- The four apex `A` records point at GitHub Pages. The old Bluehost
  address (`66.235.200.147`) is gone.
- `www.visrvu.org` is a `CNAME` to `sawernke.github.io.`
- `https://sawernke.github.io/visr-website/` redirects to `visrvu.org`,
  which is the expected behaviour once `CNAME` is deployed.
- The optional `AAAA` (IPv6) records listed above were never added. They
  remain optional.
- The domain has no `CAA` record, so nothing blocks certificate issuance.

### HTTPS

Done on 2026-08-17. GitHub issued the certificate and **Enforce HTTPS** is
ticked in the repository's Settings → Pages panel. Verified the same day:

- `https://visrvu.org` returns `HTTP/2 200`.
- `http://visrvu.org` returns `301` to the `https://` address.
- `https://www.visrvu.org` returns `301` to `https://visrvu.org`.

To re-check any of that from a terminal:

```bash
curl -sS -I https://visrvu.org/
```

An error reading `SSL: no alternative certificate subject name matches
target host name` would mean the certificate has lapsed or been revoked.

### Domain verification (do not delete this DNS record)

Done on 2026-08-17. GitHub reports `visrvu.org` as **Verified** under
<https://github.com/settings/pages>.

This is a security measure, not a cosmetic one. An *unverified* custom
domain can be claimed by any other GitHub user the moment it stops being
linked to this repository — if the repo is deleted, made private on a plan
that disallows Pages, or otherwise unlinked, while DNS still points at
GitHub. That is a domain takeover: a stranger's site appears at
`visrvu.org`. Verification restricts Pages publishing on this domain to
repositories owned by the `sawernke` account, which closes that window.

Verification rests on one `TXT` record living in the DNS zone:

```text
Name:  _github-pages-challenge-sawernke.visrvu.org.
Type:  TXT
Value: a8b1eeed4f2ad4fd62ba1befef837c
TTL:   14400
```

**This record must stay in place permanently, and must be recreated in any
new DNS zone the domain is ever moved to** — see the easyDNS section below.
Deleting it silently returns the domain to the unverified, takeover-prone
state. To confirm it is still live:

```bash
dig +short TXT _github-pages-challenge-sawernke.visrvu.org
```

One entry-format note, since the two Bluehost DNS screens differ: the
cPanel **Zone Editor** takes the fully-qualified name with the trailing dot
exactly as written above, whereas the simpler Bluehost **Domains → DNS**
tab takes only the `_github-pages-challenge-sawernke` prefix and appends
the domain itself. Entering the full name into the second one produces a
broken `..visrvu.org.visrvu.org` record that never verifies.

## Registrar transfer to easyDNS (paused — start here)

The domain is to be moved off Bluehost entirely and consolidated at
**easydns.com**, where the owner's other domains are registered, after
which the Bluehost account is to be closed outright.

**Status: not started. Paused 2026-08-18 for lack of time.** Nothing below
has been done — no zone built, no unlock requested, no contact checked. The
site is live and healthy meanwhile; this transfer is housekeeping, not a
repair. There is no deadline pressure, as the registration runs to
**2027-05-19**.

### Verified state as of 2026-08-18

Re-verified from RDAP (`rdap.publicinterestregistry.org`) and public DNS
(`8.8.8.8`) on 2026-08-18. Re-check these before acting on anything below,
because a paused plan goes stale:

```text
Registrar:          Bluehost Inc.
Domain status:      clientTransferProhibited   (transfer lock, still on)
Registered:         2023-05-19
Registry expiry:    2027-05-19
Registry changed:   2026-08-12                 (see "the 60-day block")
Nameservers:        ns1.bluehost.com, ns2.bluehost.com
Apex A records:     the four GitHub Pages addresses
Challenge TXT:      present, a8b1eeed4f2ad4fd62ba1befef837c
https://visrvu.org: HTTP 200
```

To reproduce that check:

```bash
curl -sS "https://rdap.publicinterestregistry.org/rdap/domain/visrvu.org"
nslookup -type=NS  visrvu.org 8.8.8.8
nslookup -type=TXT _github-pages-challenge-sawernke.visrvu.org 8.8.8.8
curl -sS -I https://visrvu.org/
```

`whois` is not installed on the owner's Windows machine; RDAP is the
working substitute and returns the same registry facts.

### Split the move into two halves — DNS first, registrar second

This supersedes the single ordered list that stood here previously. The
sequence is the same in spirit, but the nameserver change is deliberately
pulled out ahead of the registrar transfer instead of riding along with it.

- **Half 1 — DNS.** Point the nameservers at easyDNS while Bluehost is
  still the registrar.
- **Half 2 — Registrar.** Transfer the registration to easyDNS. DNS does
  not move during this half, because it moved already.
- **Half 3 — Cancel Bluehost.** Only after half 2 is confirmed.

The reason is that this isolates the one genuinely dangerous failure. If the
new zone is wrong, the site goes down — but during half 1 that is undone in
minutes by setting the nameservers back to Bluehost, because Bluehost still
holds the registration and the old zone is still sitting there intact. Run
the two moves together and a zone error instead arrives at the same moment
as a registrar handover, when the escape hatch is gone and an unverified
domain is exposed to the GitHub Pages takeover described under "Domain
verification" above.

A second reason: half 1 is unaffected by the 60-day transfer block, so it
can proceed immediately even if that block turns out to be active.

### Step 0 — two things to check at Bluehost before anything else

Neither of these blocks half 1. Both block half 2.

**1. The registrant contact email.** Two different things are easy to
confuse here, and only one of them is a risk:

- The `@visrvu.org` *mailbox* Bluehost can host. The owner confirms this was
  never used at all (see "Email records" below). Nothing depends on it and
  it needs no protecting.
- The *registrant contact address written on the domain record*. This is a
  separate field, and it is where the registrar sends the EPP code and the
  approval request that ICANN requires for a transfer.

WHOIS and RDAP both redact that second field for privacy, so it can only be
read from inside the Bluehost control panel. Look at it before starting. If
whoever registered the domain in 2023 entered a `@visrvu.org` address, the
approval mail lands in a mailbox that was never created, and the transfer
stalls with no error shown anywhere. If it is an address the owner actually
reads, there is nothing to do.

**2. The 60-day transfer block.** ICANN blocks a transfer for 60 days after
a registrant contact change. The registry's last-changed date is
**2026-08-12**; if that date reflects a contact change, a block runs to
approximately **2026-10-11**. RDAP does not say what changed, so this cannot
be settled from outside — ask Bluehost support directly rather than
guessing. Note that changing the contact email under point 1 can itself
start a fresh 60-day block, so do that first and then wait, rather than
discovering it later.

### Half 1 — move DNS to easyDNS

1. **Lower the TTLs at Bluehost first.** In the Bluehost zone editor, set
   the TTL on the apex `A` records and the `www` `CNAME` to `300`, then wait
   about four hours (the current TTL is 14400, i.e. four hours). This is
   what makes the rollback in step 5 fast instead of an all-day wait.
2. **Build the zone at easyDNS.** Three records:

   ```text
   ALIAS  @                                  sawernke.github.io
   CNAME  www                                sawernke.github.io.
   TXT    _github-pages-challenge-sawernke   a8b1eeed4f2ad4fd62ba1befef837c
   ```

   Use `ALIAS` at the apex rather than the four `A` records — see "Use an
   ALIAS record at the apex" below for why. If easyDNS will not take an
   `ALIAS`, fall back to the four `A` records listed under "DNS records for
   the cutover" above, and re-verify them against GitHub's documentation
   first.

   The `TXT` record is not optional and not cosmetic; omitting it reopens
   the domain-takeover window described under "Domain verification" above.
   Enter only the `_github-pages-challenge-sawernke` prefix if easyDNS
   appends the domain itself.

   Do **not** recreate the `MX` or `SPF` records — see "Email records".
3. **Change the nameservers at Bluehost** to the ones easyDNS gives at zone
   setup. This is a registrar-side setting, not a zone record.
4. **Wait about an hour, then verify** with the four commands under
   "Verified state" above. All of it must still hold: easyDNS nameservers,
   the same challenge `TXT` value, and `HTTP 200` over HTTPS. Then open
   <https://github.com/settings/pages> and confirm `visrvu.org` still reads
   **Verified**.
5. **Rollback, if needed.** Set the nameservers at Bluehost back to
   `ns1.bluehost.com` and `ns2.bluehost.com`. The old zone is untouched and
   the site returns. Then find the fault in the easyDNS zone before trying
   again.

Leave it alone for a few days before starting half 2. There is no benefit to
rushing, and a slow-burning zone error is easier to catch while the escape
hatch is still open.

### Half 2 — transfer the registration

6. **Unlock at Bluehost.** Clear `clientTransferProhibited`, and disable
   WHOIS privacy if it blocks release of the code.
7. **Request the EPP (authorization) code** from Bluehost.
8. **Start the transfer at easyDNS**, supplying the EPP code.
9. **Approve it** from the contact mailbox confirmed in step 0.
10. **Wait.** ICANN transfers take up to five days.
11. **Verify again** with the same four commands. RDAP must now report
    easyDNS as the registrar, and the site and the challenge `TXT` must be
    unchanged.

### Half 3 — cancel Bluehost

Only after step 11 passes. The warning under "The registrar caveat" above
applies in full until then: cancelling while Bluehost is still the registrar
risks forfeiting `visrvu.org` itself, not merely taking the site offline.

12. Confirm the domain no longer appears in the Bluehost account.
13. Cancel the hosting plan and close the account.
14. Ask about a refund for the unused term.

### Use an ALIAS record at the apex

easyDNS supports `ALIAS` records, and GitHub's documentation explicitly
permits `ALIAS`/`ANAME` at the apex as an alternative to `A` records. Point
an apex `ALIAS` at `sawernke.github.io` rather than copying the four
hardcoded GitHub IPs across.

The reason is durability. The four `A` addresses in "DNS records for the
cutover" above are correct today — re-verified against GitHub's
documentation on 2026-08-17 — but GitHub does not guarantee them forever,
and a stale hardcoded address takes the whole site offline with no useful
error. An `ALIAS` follows GitHub's own DNS and survives such a change
without any action here. Bluehost's zone editor offers no `ALIAS` record
type, which is the only reason the `A` records are used at present.

### Email records

The zone still carries mail routing left over from Bluehost:

```text
MX   visrvu.org  →  mail.visrvu.org  →  162.241.226.124  (Bluehost)
TXT  v=spf1 ip4:162.241.226.124 a mx include:websitewelcome.com ~all
```

**The `@visrvu.org` mailbox this points at has never been used.** The owner
confirmed this directly on 2026-08-17: it was never set up and never read.
That is consistent with the site itself — no address at this domain appears
anywhere on it. The published contact address is
`s.wernke[at]vanderbilt.edu`, and `verify.py` actively fails the build if a
`@vanderbilt.edu` address or a `mailto:` link is written in plain form.
Nothing depends on this mail routing.

Because of that, **the Bluehost account can be closed outright** once the
domain is safely at easyDNS. There is no mailbox to migrate and no mail to
preserve first. The only constraint on closing it is timing, not content —
see "Half 3" above, and "The registrar caveat" further up.

So these two records can simply be dropped when the zone is rebuilt at
easyDNS; they need not be recreated. Cancelling Bluehost will stop that
mail path regardless. The `SPF` record above is additionally stale: its `a`
mechanism now resolves to GitHub's Pages addresses, which never send mail.

This is also why the dead mailbox cannot serve as an escape hatch in step 0.
If the registrant contact is an `@visrvu.org` address, preserving the `MX`
record does not help, because there is no mailbox behind it at either
registrar. The only fix is to change the contact address itself.



## Line endings

This repository stores every text file with Unix (LF) line endings, and
`.gitattributes` enforces that on checkout. This is not cosmetic. Editing a
page on Windows, or on a network volume that rewrites line endings on save,
can convert a file to CRLF. The visible text does not change at all, but
git then reports every line of every page as modified — on 2026-08-17 this
produced a diff of 1691 added and 1691 removed lines across twenty files
with not one word actually changed, which would hide any genuine edit.

If you ever see a suspiciously large diff where added and removed line
counts are identical, check for this before assuming the worst:

```bash
git diff --ignore-cr-at-eol --stat
```

If that prints nothing, the only difference is line endings, and
`git checkout -- .` restores the files safely.
