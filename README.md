# Sommaire website

Static marketing site for the Sommaire iOS app, plus the two legal pages the App Store
requires. No build step, no dependencies, no framework. Four files and an assets folder.

```
index.html        landing page
privacy.html      generated from Memcorder/Legal/PRIVACY_POLICY.md
terms.html        generated from Memcorder/Legal/TERMS_OF_USE.md
styles.css        shared styles for all three pages
build_legal.py    regenerates the two legal pages
assets/           app icon, favicon, screenshots
```

Preview locally with any static server:

```bash
python3 -m http.server 8000
```

---

## Read this before deploying

**The app links to `/privacy` and `/terms`, not to `/privacy.html`.** See
`Memcorder/Models/LegalLinks.swift`:

```swift
static let privacyPolicy = URL(string: "https://www.sommaire.app/privacy")!
static let termsOfUse    = URL(string: "https://www.sommaire.app/terms")!
```

Those links are live in the shipping app and are also what App Store Connect points at.
If they 404, review will almost certainly reject the build. Two ways to make them resolve:

1. **Host with clean URLs.** Netlify, Vercel, Cloudflare Pages and GitHub Pages all serve
   `privacy.html` at `/privacy` automatically. Nothing to configure. This is the easy path.
2. **Or change the app** to link at `/privacy.html` and `/terms.html`, which works on any
   host including plain nginx, Apache or S3. One-line edit to `LegalLinks.swift`, but it
   needs a new build.

Whichever you pick, **open both URLs in a browser before submitting.** This is the single
most likely thing to go wrong on launch day.

The site must also be reachable at `https://www.sommaire.app` with a valid certificate.
Note that `.app` is on the HSTS preload list built into every major browser, so HTTPS is not
optional here: plain `http://` will not load at all, with no fallback and no warning page.
Get the certificate working before pointing the app or App Store Connect at it.

---

## Legal pages are generated, not hand-edited

`privacy.html` and `terms.html` are built from the Markdown in `../Memcorder/Legal/`. That
Markdown is the single source of truth, and the same text is what goes to App Store Connect.

```bash
python3 build_legal.py
```

Edit the Markdown, run that, commit both. **Never edit the HTML directly**, since the next
run overwrites it.

The script handles the Markdown subset those documents use: headings, bold, bullet lists,
tables, and autolinks. It also builds the table of contents, lifts the "Last updated" line
into the header pill, and prefixes any heading id that would otherwise start with a digit
(the Terms headings are numbered, and `#1-licence` is a valid HTML id but not a valid CSS
selector).

---

## Conventions

These were deliberate. Please keep them.

**No em-dashes anywhere.** Not in the pages, not in the Markdown, not in code comments.

**Copy matches the app's onboarding**, word for word where the same idea appears in both:
the headline, the lede, "Built for how you work", "Private by design", "All processing by
Apple Intelligence stays on your device", and all four use-case cards. When onboarding copy
changes in the app, change it here too. US spelling, matching the app ("summarizes").

**Claims must match what ships.** The previous version of this site advertised "iCloud sync
across devices", which does not exist, and listed six free features as Pro. App Store Review
reads the marketing URL, and Guideline 2.3.1 covers accurate metadata. Before adding a
feature row, confirm it is in the build.

**Icons are hand-drawn SVG, not SF Symbols.** Apple's licence covers SF Symbols inside apps
on Apple platforms, not web pages, and specifically excludes marketing use. The sprite at the
top of `index.html` redraws the exact symbols the app uses (`waveform`, `camera.fill`,
`note.text`, `sparkles`, `magnifyingglass`, `square.and.arrow.up`, `mic.fill`, `book.fill`,
`lightbulb.fill`, `lock.shield.fill`) on the same 24px grid with matching stroke weights.
They inherit `currentColor`, so each one tints itself with the artifact colour it belongs to.

**Colours come from the app.** `--summary`, `--audio`, `--photo` and `--note` in `styles.css`
are the app's artifact colours, which are also the four petals in the app icon.

**The reveal animation is gated on a `.js` class** added by an inline script in `<head>`.
Without it, every `.fade-up` section would sit at `opacity: 0` and the page would render
blank if scripts failed. Do not remove that script without also removing the `.js` prefix
from those rules in `styles.css`.

**`.site-nav` is class-scoped on purpose.** A bare `nav` selector also matched the legal
pages' table of contents and pinned it over the header.

---

## Assets

`assets/sommaire-icon.png` is the 900px app icon from
`Memcorder/Assets.xcassets/sommaire_Pro_logo.imageset/`, with a 180px apple-touch-icon and a
64px favicon derived from it.

Screenshots are device captures resized to 700px wide with `sips --resampleWidth 700` (note:
`-Z` scales the longest side, which gives you a 322px-wide image). They are framed by CSS
rather than baked-in bezels, so the framing can be restyled without recapturing.

To replace one, drop in a new file at the same path and keep the `width`/`height` attributes
in sync with the real pixel dimensions, so the browser reserves the right space while loading.

---

## Outstanding

- **`TODO` markers in `index.html`** at the two App Store links, currently `#`. Search for
  `TODO` before publishing.
- **Pricing appears in three places** and must agree: this site, `MemcorderPro.storekit`, and
  App Store Connect. Currently $29.99/year and $5.99/month, a 58% annual saving.
- **Language waves** in the Languages section promise Italian and Portuguese, then Chinese,
  Japanese and Korean. Only English, French, German and Spanish ship today.
