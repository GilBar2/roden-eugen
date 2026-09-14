#!/usr/bin/env python3
"""Search Wikimedia Commons for public-domain / CC0 images only.

Usage:
  python3 tools/commons_search.py "Berlin Wall 1989" [--limit 8] [--min-width 800]

Prints a JSON list of candidates. Every result is licensed "Public domain" or CC0;
anything else is filtered out. Uses curl because some Python installs lack SSL certs.
"""
import argparse
import html
import json
import re
import subprocess
import sys
import urllib.parse

API = "https://commons.wikimedia.org/w/api.php"
UA = "RodenEugenDesk/1.0 (https://github.com/GilBar2/roden-eugen)"
FREE = re.compile(r"public domain|\bcc0\b|^pd\b", re.I)


def curl_json(url):
    out = subprocess.run(["curl", "-s", "-L", "--max-time", "40", "-A", UA, url],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def plain(value):
    return html.unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


def search(query, limit, min_width):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": "6",
        "gsrlimit": str(max(limit * 3, 15)), "prop": "imageinfo",
        "iiprop": "url|size|extmetadata", "iiurlwidth": "960",
    }
    data = curl_json(API + "?" + urllib.parse.urlencode(params))
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    results = []
    for page in pages:
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        license_name = plain(meta.get("LicenseShortName", {}).get("value"))
        if not FREE.search(license_name) or info.get("width", 0) < min_width:
            continue
        results.append({
            "commons": page["title"].removeprefix("File:"),
            "license": license_name,
            "url": info.get("thumburl") or info.get("url"),
            "page": info.get("descriptionurl"),
            "width": info.get("width"),
            "height": info.get("height"),
            "artist": plain(meta.get("Artist", {}).get("value"))[:120],
            "description": plain(meta.get("ImageDescription", {}).get("value"))[:240],
            "restrictions": plain(meta.get("Restrictions", {}).get("value")),
        })
        if len(results) >= limit:
            break
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--min-width", type=int, default=800)
    args = ap.parse_args()
    try:
        print(json.dumps(search(args.query, args.limit, args.min_width), indent=2, ensure_ascii=False))
    except (subprocess.CalledProcessError, json.JSONDecodeError) as err:
        sys.exit(f"Commons search failed: {err}")


if __name__ == "__main__":
    main()
