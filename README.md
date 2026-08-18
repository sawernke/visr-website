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

## Planned: registrar transfer to easyDNS

The domain is to be moved off Bluehost entirely and consolidated at
**easydns.com**, where the owner's other domains are registered. This has
not been started as of 2026-08-17. There is no deadline pressure — the
registration runs to **2027-05-19**.

Current registration facts, from `whois visrvu.org` on 2026-08-17:

```text
Registrar:      Bluehost Inc.
Created:        2023-05-19
Registry expiry: 2027-05-19
Domain status:  clientTransferProhibited   (the registrar transfer lock)
Nameservers:    ns1.bluehost.com, ns2.bluehost.com
```

### Two things to check before starting

**1. The registrant contact email.** Two different things are easy to
confuse here, and only one of them is a risk:

- The `@visrvu.org` *mailbox* Bluehost can host. The owner confirms this was
  never used at all (see "Email records" below). Nothing depends on it and
  it needs no protecting.
- The *registrant contact address written on the domain record*. This is a
  separate field, and it is where the registrar sends the EPP code and the
  approval request that ICANN requires for a transfer.

WHOIS redacts that second field for privacy, so it can only be read from
inside the Bluehost control panel. Look at it before starting. If whoever
registered the domain in 2023 entered a `@visrvu.org` address, the approval
mail lands in a mailbox that was never created, and the transfer stalls
with no error shown anywhere. If it is an address the owner actually reads,
there is nothing to do.

**2. The 60-day transfer block.** ICANN blocks a transfer for 60 days after
a registrant contact change. The WHOIS "Updated Date" was 2026-08-12, five
days before this was written, so a block may be active into roughly
mid-October 2026. Ask Bluehost directly rather than guessing. Note that
changing the contact email under point 1 can itself start a fresh 60-day
block, so do that first and then wait, rather than discovering it later.

### Order of operations

Getting this out of order is what forfeits a domain, so do not compress it:

1. **Build the zone at easyDNS first,** before the transfer runs. It needs
   the four apex `A` records, the `www` `CNAME`, and — critically — the
   `_github-pages-challenge-sawernke` `TXT` record from the section above.
   See "Use an ALIAS record" below before copying the `A` records blindly.
2. **Unlock at Bluehost.** Clear `clientTransferProhibited` and request the
   EPP (authorization) code. Disable WHOIS privacy if it blocks the code.
3. **Start the transfer at easyDNS** and approve it from the contact
   mailbox confirmed in step 1 above.
4. **Verify after the nameservers change.** The site must still load over
   HTTPS, and `dig +short TXT _github-pages-challenge-sawernke.visrvu.org`
   must still return the challenge value. If that record did not survive
   the move, re-add it immediately.
5. **Only then cancel Bluehost.** Not before step 4 passes. The warning in
   "The registrar caveat" above applies in full until the transfer has
   actually completed.

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
see "Order of operations" above, and "The registrar caveat" further up.

So these two records can simply be dropped when the zone is rebuilt at
easyDNS; they need not be recreated. Cancelling Bluehost will stop that
mail path regardless. The `SPF` record above is additionally stale: its `a`
mechanism now resolves to GitHub's Pages addresses, which never send mail.



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
