#!/usr/bin/env python3
"""Convert an edited article.md into body.html for pasting into the Substack editor.

Usage:
  python3 tools/md_to_html.py articles/<folder>/article.md > articles/<folder>/body.html

Handles the subset the articles use: # title (skipped, it goes in Substack's title field),
## / ### headings, paragraphs, *italic*, **bold**, [links](url), bullet and numbered lists, ---.
"""
import html
import re
import sys


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", text)
    return text


def convert(md):
    out, para, items, kind = [], [], [], None

    def flush():
        nonlocal para, items, kind
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if items:
            out.append(f"<{kind}>" + "".join(f"<li><p>{inline(i)}</p></li>" for i in items) + f"</{kind}>")
            items, kind = [], None

    for raw in md.splitlines():
        line = raw.strip()
        bullet = re.match(r"^[*-]\s+(.*)", line)
        number = re.match(r"^\d+[.)]\s+(.*)", line)
        if not line:
            flush()
        elif line.startswith("# "):
            flush()
        elif line.startswith("### "):
            flush(); out.append("<h3>" + inline(line[4:]) + "</h3>")
        elif line.startswith("## "):
            flush(); out.append("<h2>" + inline(line[3:]) + "</h2>")
        elif re.fullmatch(r"-{3,}|\*{3,}", line):
            flush(); out.append("<hr>")
        elif bullet or number:
            if para:
                flush()
            want = "ul" if bullet else "ol"
            if kind and kind != want:
                flush()
            kind = want
            items.append((bullet or number).group(1))
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(convert(open(sys.argv[1], encoding="utf-8").read()))
