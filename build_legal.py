#!/usr/bin/env python3
"""
Regenerates privacy.html and terms.html from the Markdown in Memcorder/Legal/.

The Markdown is the single source of truth. Edit it there, run this, and the
pages follow. Nothing here is hand-maintained, so the site and the documents
you point App Store Connect at can never drift apart.

    python3 build_legal.py
"""

import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LEGAL = os.path.normpath(os.path.join(HERE, "..", "Memcorder", "Legal"))

PAGES = [
    ("PRIVACY_POLICY.md", "privacy.html", "Privacy Policy", "Privacy Policy | Sommaire"),
    ("TERMS_OF_USE.md", "terms.html", "Terms of Use", "Terms of Use | Sommaire"),
]


def slug(text):
    s = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    # The Terms headings are numbered ("1. Licence"), which would yield an id
    # starting with a digit. HTML permits it and fragment links still work, but
    # it is not a valid CSS selector, so querySelector and any CSS targeting break.
    if not s or s[0].isdigit():
        s = "section-" + s
    return s


def inline(text):
    """Bold, autolinks and inline code, applied after escaping."""
    out = html.escape(text)
    out = re.sub(r"&lt;(https?://[^&\s]+)&gt;",
                 r'<a href="\1" rel="noopener">\1</a>', out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                 r'<a href="\2" rel="noopener">\1</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out


def convert(md):
    """Markdown subset used by these documents: headings, lists, tables, paragraphs."""
    lines = md.split("\n")
    body, toc = [], []
    i, n = 0, len(lines)
    title = updated = None

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1 and title is None:
                title = text
            elif level == 2:
                anchor = slug(text)
                toc.append((text, anchor))
                body.append(f'<h2 id="{anchor}">{inline(text)}</h2>')
            else:
                body.append(f"<h{min(level,4)}>{inline(text)}</h{min(level,4)}>")
            i += 1
            continue

        # Table
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in header)
            trs = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows
            )
            body.append(f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>")
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(inline(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            body.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue

        # Horizontal rule
        if re.match(r"^-{3,}$", stripped):
            i += 1
            continue

        # Paragraph. The "Last updated" line becomes the header pill instead
        para = [stripped]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|[-*]\s|\|)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        text = " ".join(para)
        if updated is None and text.lower().startswith("**last updated"):
            updated = re.sub(r"\*\*", "", text)
            continue
        body.append(f"<p>{inline(text)}</p>")

    return title, updated, toc, "\n".join(body)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="index, follow" />
  <title>{page_title}</title>
  <meta name="description" content="{description}" />
  <link rel="icon" type="image/png" href="assets/favicon.png" />
  <link rel="apple-touch-icon" href="assets/sommaire-icon-180.png" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>

<nav class="site-nav">
  <a class="nav-logo" href="index.html">
    <img src="assets/sommaire-icon.png" alt="" />
    Sommaire
  </a>
  <div class="nav-links">
    <a href="index.html">Home</a>
    <a href="privacy.html">Privacy</a>
    <a href="terms.html">Terms</a>
  </div>
</nav>

<main class="legal">
  <div class="container-narrow">
    <h1>{heading}</h1>
    {updated_pill}
    <nav class="legal-toc" aria-label="On this page">
      <div>On this page</div>
      <ul>
{toc}
      </ul>
    </nav>
{body}
  </div>
</main>

<footer>
  <a class="footer-logo" href="index.html">
    <img src="assets/sommaire-icon.png" alt="" />
    Sommaire
  </a>
  <p>Capture everything. Understand instantly.</p>
  <div class="footer-links">
    <a href="index.html">Home</a>
    <a href="privacy.html">Privacy Policy</a>
    <a href="terms.html">Terms of Use</a>
    <a href="mailto:support@elyzeo.com">Contact</a>
  </div>
  <p style="margin-top:18px;">© 2026 Elyzeo. All rights reserved.</p>
</footer>

</body>
</html>
"""


def main():
    for md_name, out_name, heading, page_title in PAGES:
        src = os.path.join(LEGAL, md_name)
        with open(src, encoding="utf-8") as f:
            title, updated, toc, body = convert(f.read())

        toc_html = "\n".join(
            f'        <li><a href="#{a}">{html.escape(t)}</a></li>' for t, a in toc
        )
        pill = f'<span class="updated">{html.escape(updated)}</span>' if updated else ""
        description = (
            "How Sommaire handles your data: everything stays on your device."
            if "PRIVACY" in md_name
            else "Terms of Use and End User License Agreement for Sommaire."
        )

        out = TEMPLATE.format(
            page_title=html.escape(page_title),
            description=html.escape(description),
            heading=html.escape(heading),
            updated_pill=pill,
            toc=toc_html,
            body=body,
        )
        dest = os.path.join(HERE, out_name)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"{md_name}  ->  {out_name}   ({len(toc)} sections, {len(out):,} bytes)")


if __name__ == "__main__":
    main()
