#!/usr/bin/env python3
"""Avisa a Bing (y otros buscadores con IndexNow) de todas las páginas del blog tras cada publicación."""
import json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
keys = [f.stem for f in (ROOT / "static").glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", f.stem)]
if not keys:
    sys.exit("Sin clave IndexNow")
key = keys[0]
urls = [f"{BASE}/"]
for f in sorted((ROOT / "content" / "posts").glob("*.md")):
    m = re.search(r"^slug:\s*(\S+)", f.read_text(encoding="utf-8"), re.M)
    if m:
        urls.append(f"{BASE}/{m.group(1)}/")
data = json.dumps({"host": BASE.split("://", 1)[1], "key": key,
                   "keyLocation": f"{BASE}/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=data,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow: {r.status} · {len(urls)} URLs enviadas")
except Exception as e:
    print(f"IndexNow no respondió bien: {e}")
