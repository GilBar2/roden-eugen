#!/usr/bin/env python3
"""Build a Picture Desk page from an article folder's manifest.json.

Usage:
  python3 tools/build_desk.py articles/<folder>                       # review desk (Replace / Approve)
  python3 tools/build_desk.py articles/<folder> --mode record \
          --decision articles/<folder>/decision.json                  # read-only record of the final picks

Downloads every candidate image into <folder>/desk/img/, then writes:
  <folder>/desk/artifact.html   publish this with the Artifact tool (root = <folder>/desk)
  <folder>/desk/index.html      standalone copy (Cloudflare Pages or a browser)
Prints JSON with the Artifact `files` map and any warnings.
"""
import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

UA = "RodenEugenDesk/1.0 (https://github.com/GilBar2/roden-eugen)"
TEMPLATE = Path(__file__).with_name("desk_template.html")
MAGIC = {b"\xff\xd8\xff": ".jpg", b"\x89PNG": ".png", b"GIF8": ".gif", b"RIFF": ".webp"}


def image_ext(path):
    head = path.read_bytes()[:4]
    return next((ext for sig, ext in MAGIC.items() if head.startswith(sig)), None)


def fetch(url, dest):
    urls = [url]
    if "thumb.wikimedia.org" in url:
        urls.append(url.replace("thumb.wikimedia.org/wikipedia", "upload.wikimedia.org/wikipedia"))
    for u in urls:
        subprocess.run(["curl", "-s", "-L", "--max-time", "60", "-A", UA, "-o", str(dest), u])
        if dest.exists() and image_ext(dest):
            return True
    dest.unlink(missing_ok=True)
    return False


def slug(text, n=24):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:n].strip("-")


def apply_decision(desk, decision):
    for a in desk["articles"]:
        chosen = decision["articles"].get(a["key"], {})
        picks = {s["id"]: s for s in chosen.get("slots", [])}
        kept = []
        for s in a["slots"]:
            p = picks.get(s["id"])
            if not p or p.get("removed"):
                continue
            c = next((c for c in s["candidates"] if c["commons"] == p["commons"]), None)
            if c:
                s["candidates"] = [c]
                s["thumb"] = chosen.get("thumbnail") == s["id"]
                kept.append(s)
        a["slots"] = kept
    return desk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--mode", choices=["review", "record"], default="review")
    ap.add_argument("--decision")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    manifest_path = folder / "manifest.json"
    desk = json.loads(manifest_path.read_text())
    out = folder / "desk"
    (out / "img").mkdir(parents=True, exist_ok=True)
    warnings, files = [], {}

    for a in desk["articles"]:
        prefix = slug(a["key"])
        for s in a["slots"]:
            good = []
            for n, c in enumerate(s["candidates"], 1):
                existing = next((out / "img" / f"{prefix}-{s['id']}-{n}{e}" for e in (".jpg", ".png", ".gif", ".webp")
                                 if (out / "img" / f"{prefix}-{s['id']}-{n}{e}").exists()), None)
                if existing is None:
                    tmp = out / "img" / f"{prefix}-{s['id']}-{n}.tmp"
                    if not c.get("url") or not fetch(c["url"], tmp):
                        warnings.append(f"{a['key']}/{s['id']}: could not download {c.get('commons')}")
                        continue
                    existing = tmp.with_suffix(image_ext(tmp))
                    tmp.rename(existing)
                c["file"] = f"img/{existing.name}"
                good.append(c)
            if not good:
                sys.exit(f"{a['key']}/{s['id']}: no usable candidates, search again")
            s["candidates"] = good

    manifest_path.write_text(json.dumps(desk, indent=2, ensure_ascii=False) + "\n")

    page = copy.deepcopy(desk)
    page["mode"] = args.mode
    if args.mode == "record":
        if not args.decision:
            sys.exit("--mode record needs --decision <decision.json>")
        page = apply_decision(page, json.loads(Path(args.decision).read_text()))

    for a in page["articles"]:
        for s in a["slots"]:
            for c in s["candidates"]:
                files[c["file"]] = c["file"]

    title = page.get("deskTitle") or (page["articles"][0]["title"] + " Picture Desk")
    data = json.dumps(page, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text().replace("__TITLE__", title.replace("<", "")).replace("/*__DESK_DATA__*/null", data)
    (out / "artifact.html").write_text(html)
    (out / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + html + "\n</html>\n")

    print(json.dumps({"artifact_file": str(out / "artifact.html"), "root": str(out),
                      "files": files, "warnings": warnings}, indent=2))


if __name__ == "__main__":
    main()
