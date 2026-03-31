#!/usr/bin/env python3
"""
patch-claude-in-chrome.py — Patch the Claude-in-Chrome extension to:
1. Bypass site blocking (mcpPermissions-*.js: getCategory → always return "category0")
2. Spoof user agent (client-*.js: getUserAgent → Firefox UA)

Usage:
  python patch-claude-in-chrome.py

After running: disable the original extension in chrome://extensions/,
then Load unpacked → C:/Users/<user>/claude-in-chrome-patched
"""
import shutil
import sys
import re
from pathlib import Path

EXT_ID = "fcoeoabgfenejglbffodgkkbkcdhcgfn"
CHROME_EXTS = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Extensions"
OUTPUT = Path.home() / "claude-in-chrome-patched"

def find_latest_version(ext_path: Path) -> Path:
    versions = sorted(ext_path.glob("*_0"), reverse=True)
    if not versions:
        raise FileNotFoundError(f"No version found in {ext_path}")
    return versions[0]

def patch_user_agent(assets: Path):
    candidates = list(assets.glob("client-*.js"))
    if not candidates:
        print("WARNING: client-*.js not found, skipping UA patch")
        return
    f = candidates[0]
    text = f.read_text(encoding="utf-8")
    old = r'getUserAgent(){return`${this.constructor.name}/JS ${E}`}'
    new = 'getUserAgent(){return"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0"}'
    if old not in text:
        print(f"WARNING: UA pattern not found in {f.name} — may already be patched or changed")
        return
    f.write_text(text.replace(old, new), encoding="utf-8")
    print(f"  [OK] User agent patched in {f.name}")

def patch_get_category(assets: Path):
    candidates = list(assets.glob("mcpPermissions-*.js"))
    if not candidates:
        print("WARNING: mcpPermissions-*.js not found, skipping blocking patch")
        return
    f = candidates[0]
    text = f.read_text(encoding="utf-8")
    start = text.find('async getCategory(e){')
    if start == -1:
        print(f"WARNING: getCategory not found in {f.name}")
        return
    end = text.find('pendingRequests.delete(t)}}', start)
    if end == -1:
        print(f"WARNING: getCategory end not found in {f.name}")
        return
    end += len('pendingRequests.delete(t)}}')
    patched = text[:start] + 'async getCategory(e){return"category0"}' + text[end:]
    f.write_text(patched, encoding="utf-8")
    print(f"  [OK] getCategory patched in {f.name}")

def main():
    ext_path = CHROME_EXTS / EXT_ID
    if not ext_path.exists():
        print(f"ERROR: Extension not found at {ext_path}")
        sys.exit(1)

    src = find_latest_version(ext_path)
    print(f"Source: {src}")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(src, OUTPUT)
    print(f"Copied to: {OUTPUT}")

    assets = OUTPUT / "assets"
    patch_user_agent(assets)
    patch_get_category(assets)

    print(f"\nDone. Load unpacked from: {OUTPUT}")
    print("Disable original extension first, then Load unpacked in chrome://extensions/")

if __name__ == "__main__":
    main()
