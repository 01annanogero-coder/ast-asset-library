"""
AST Asset Library — Manifest Generator
=======================================
Drop images into their category/subcategory folders,
name them descriptively, run this script, and the
manifest.json for each category plus search.json
are auto-generated.

Naming convention for your image files:
  object-variant-detail-detail.webp
  Examples:
    woman-dress-summer-floral.webp
    mens-suit-navy-formal.webp
    sneakers-white-minimal.webp
    pwa-icon-512x512.png

New fields auto-generated this version:
  - orientation  (portrait / landscape / square) — from filename or Pillow
  - style        (photorealistic / illustrated / minimal / flat)
  - search_terms (expanded keyword list for semantic matching)
  - title        (human-readable full title)
  - width/height (if Pillow installed)

Also generates:
  - search.json  (keyword → [image ids]) for fast AI lookup

Usage:
  python scripts/generate_manifests.py

Run from the root of the ast-asset-library folder.
"""

import os
import json
from datetime import date
from pathlib import Path
from collections import defaultdict


# ─── CONFIG ───────────────────────────────────────────────────────────────────

IMAGES_ROOT   = "images"
TOPICS_FILE   = "topics.json"
SEARCH_FILE   = "search.json"
SUPPORTED_FORMATS = {".webp", ".jpg", ".jpeg", ".png", ".svg", ".gif"}

GITHUB_USERNAME = "01annanogero-coder"
GITHUB_REPO     = "ast-asset-library"
GITHUB_BRANCH   = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# ─── SEMANTIC EXPANSION MAP ───────────────────────────────────────────────────
# Maps filename tokens → extra search terms so AI can match natural language
# queries even when the exact word isn't in the filename.

SEMANTIC_MAP = {
    # People / gender
    "woman": ["female", "women", "lady", "girl"],
    "man":   ["male", "men", "guy", "gentleman"],
    "mens":  ["male", "men", "man", "guy"],
    "womens":["female", "women", "woman", "lady"],
    "kid":   ["child", "children", "boy", "girl", "youth"],
    "baby":  ["infant", "toddler", "newborn"],

    # Clothing
    "dress":      ["gown", "frock", "outfit"],
    "suit":       ["formal", "business attire", "blazer"],
    "shirt":      ["top", "blouse", "tee"],
    "jacket":     ["coat", "outerwear", "layer"],
    "jeans":      ["denim", "pants", "trousers"],
    "skirt":      ["midi", "mini", "maxi"],
    "jumpsuit":   ["romper", "playsuit", "one-piece"],
    "sweater":    ["knitwear", "pullover", "knit"],
    "blouse":     ["top", "shirt", "women top"],
    "coat":       ["overcoat", "trench", "outerwear"],
    "sneakers":   ["shoes", "trainers", "footwear", "kicks"],
    "heels":      ["pumps", "stiletto", "footwear"],
    "boots":      ["ankle boots", "footwear", "shoes"],
    "accessories":["jewelry", "bag", "belt", "hat", "watch"],

    # Styles / moods
    "formal":     ["professional", "business", "elegant", "office"],
    "casual":     ["everyday", "relaxed", "informal", "streetwear"],
    "summer":     ["warm", "sunny", "bright", "tropical", "beach"],
    "winter":     ["cold", "snow", "warm layer", "cozy"],
    "minimal":    ["clean", "simple", "understated", "modern"],
    "floral":     ["flowers", "botanical", "print", "pattern"],
    "dark":       ["black", "moody", "dramatic", "night"],
    "bright":     ["colorful", "vibrant", "vivid", "light"],

    # Colors
    "navy":   ["dark blue", "blue", "deep blue"],
    "camel":  ["tan", "beige", "brown", "warm neutral"],
    "cream":  ["off-white", "ivory", "white", "light"],
    "beige":  ["nude", "neutral", "sand", "tan"],
    "grey":   ["gray", "silver", "neutral"],
    "black":  ["dark", "ebony", "onyx"],
    "white":  ["clean", "pure", "light", "bright"],

    # Materials
    "leather":["genuine leather", "faux leather", "skin"],
    "denim":  ["jeans", "cotton", "fabric"],
    "silk":   ["satin", "smooth", "luxurious", "shiny"],
    "wool":   ["knit", "warm", "fabric", "cozy"],
    "linen":  ["cotton", "lightweight", "breathable", "natural"],
    "pleated":["layered", "structured", "folds"],

    # Business / tech
    "office":     ["workspace", "professional", "corporate", "desk"],
    "meeting":    ["conference", "team", "boardroom", "discussion"],
    "startup":    ["modern office", "coworking", "tech", "innovation"],
    "laptop":     ["computer", "device", "tech", "work"],
    "coding":     ["programming", "developer", "code", "software"],

    # Nature
    "landscape":  ["scenery", "outdoor", "nature", "view"],
    "mountain":   ["hill", "peak", "terrain", "highland"],
    "forest":     ["trees", "woods", "nature", "green"],
    "ocean":      ["sea", "water", "beach", "coast"],
    "sunset":     ["dusk", "golden hour", "sky", "orange"],

    # Food
    "meal":       ["food", "dish", "plate", "cuisine"],
    "drink":      ["beverage", "liquid", "glass"],
    "dessert":    ["sweet", "cake", "pastry", "sugar"],

    # Icons
    "pwa":        ["app icon", "progressive web app", "icon", "logo"],
    "svg":        ["vector", "icon", "graphic"],
    "social":     ["facebook", "instagram", "twitter", "linkedin"],
}

# ─── ORIENTATION HINTS FROM FILENAME ──────────────────────────────────────────

LANDSCAPE_HINTS = {"landscape", "wide", "banner", "cover", "background", "bg", "hero"}
PORTRAIT_HINTS  = {"portrait", "tall", "vertical", "person", "model", "woman", "man",
                   "mens", "womens", "dress", "suit", "jacket", "shirt"}

# ─── STYLE HINTS ──────────────────────────────────────────────────────────────

ILLUSTRATED_HINTS = {"icon", "svg", "illustration", "cartoon", "flat", "vector", "logo"}
MINIMAL_HINTS     = {"icon", "pwa", "symbol", "ui", "minimal", "clean", "white"}

# ─── SUBCATEGORY LABELS ───────────────────────────────────────────────────────

SUBCATEGORY_LABELS = {
    "mens":"Mens","womens":"Womens","kids-fashion":"Kids Fashion",
    "accessories":"Accessories","footwear":"Footwear","fitness":"Fitness",
    "nutrition":"Nutrition","mental-health":"Mental Health","medical":"Medical",
    "toys":"Toys","education":"Education","activities":"Activities","babies":"Babies",
    "meals":"Meals","drinks":"Drinks","desserts":"Desserts","ingredients":"Ingredients",
    "restaurant":"Restaurant","devices":"Devices","coding":"Coding","ai":"AI",
    "networking":"Networking","workspace":"Workspace","landscapes":"Landscapes",
    "animals":"Animals","plants":"Plants","sky":"Sky","water":"Water",
    "office":"Office","meetings":"Meetings","finance":"Finance","startup":"Startup",
    "people":"People","interiors":"Interiors","exteriors":"Exteriors","modern":"Modern",
    "traditional":"Traditional","commercial":"Commercial","africa":"Africa",
    "europe":"Europe","asia":"Asia","americas":"Americas","landmarks":"Landmarks",
    "skincare":"Skincare","makeup":"Makeup","haircare":"Haircare","products":"Products",
    "football":"Football","basketball":"Basketball","athletics":"Athletics",
    "gym":"Gym","outdoor":"Outdoor","classroom":"Classroom","books":"Books",
    "elearning":"E-Learning","science":"Science","writing":"Writing",
    "pwa":"PWA Icons","svg":"SVG Icons","social":"Social Media Icons",
    "ecommerce":"E-Commerce Icons","arrows":"Arrows","ui":"UI Icons",
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def filename_to_parts(filename: str) -> list:
    stem = Path(filename).stem
    return [p.lower() for p in stem.replace("_", "-").split("-") if len(p) > 1]

def filename_to_tags(parts: list) -> list:
    return list(parts)

def filename_to_object(parts: list) -> str:
    return " ".join(parts[:2]).title()

def filename_to_variant(parts: list) -> str:
    return " ".join(parts[2:]).lower() if len(parts) > 2 else "default"

def filename_to_title(parts: list, subcategory: str) -> str:
    """Human readable title: 'Womens Coat — Wool Camel'"""
    obj     = " ".join(parts[:2]).title()
    variant = " ".join(parts[2:]).title() if len(parts) > 2 else ""
    return f"{obj} — {variant}" if variant else obj

def get_format(filename: str) -> str:
    return Path(filename).suffix.lstrip(".")

def get_file_size_kb(filepath: str) -> int:
    try:
        return round(os.path.getsize(filepath) / 1024)
    except:
        return 0

def generate_id(category: str, index: int) -> str:
    return f"{category}-{str(index).zfill(3)}"

def guess_orientation(parts: list) -> str:
    token_set = set(parts)
    if token_set & LANDSCAPE_HINTS:
        return "landscape"
    if token_set & PORTRAIT_HINTS:
        return "portrait"
    return "unknown"

def guess_style(parts: list, fmt: str) -> str:
    token_set = set(parts)
    if fmt == "svg" or token_set & ILLUSTRATED_HINTS:
        return "illustrated"
    if token_set & MINIMAL_HINTS:
        return "minimal"
    return "photorealistic"

def build_search_terms(parts: list, category_id: str, subcategory: str) -> list:
    """Expand filename tokens using SEMANTIC_MAP for richer AI matching."""
    terms = set(parts)
    terms.add(category_id)
    terms.add(subcategory)
    for token in parts:
        if token in SEMANTIC_MAP:
            terms.update(SEMANTIC_MAP[token])
    # Add combined phrases (first two tokens)
    if len(parts) >= 2:
        terms.add(f"{parts[0]} {parts[1]}")
    if len(parts) >= 3:
        terms.add(f"{parts[0]} {parts[2]}")
    return sorted(terms)


# ─── CORE: per-category manifest ──────────────────────────────────────────────

def generate_manifest_for_category(category_path, category_id, category_label):
    images  = []
    counter = 1

    category_dir = Path(category_path)
    if not category_dir.exists():
        print(f"  ⚠ Folder not found: {category_path} — skipping")
        return None

    for root, dirs, files in os.walk(category_dir):
        dirs.sort()
        for filename in sorted(files):
            ext = Path(filename).suffix.lower()
            if ext not in SUPPORTED_FORMATS:
                continue

            filepath          = Path(root) / filename
            relative_path     = filepath.relative_to(Path("."))
            relative_to_cat   = filepath.relative_to(category_dir)
            subcategory       = relative_to_cat.parts[0] if len(relative_to_cat.parts) > 1 else "general"

            parts        = filename_to_parts(filename)
            tags         = filename_to_tags(parts)
            fmt          = get_format(filename)
            clean_path   = str(relative_path).replace("\\", "/")
            raw_url      = f"{GITHUB_RAW_BASE}/{clean_path}"

            # Enrich tags with category + subcategory
            if category_id not in tags: tags.insert(0, category_id)
            if subcategory  not in tags: tags.insert(1, subcategory)

            entry = {
                "id":           generate_id(category_id, counter),
                "title":        filename_to_title(parts, subcategory),
                "object":       filename_to_object(parts),
                "variant":      filename_to_variant(parts),
                "subcategory":  subcategory,
                "orientation":  guess_orientation(parts),
                "style":        guess_style(parts, fmt),
                "file":         clean_path,
                "raw_url":      raw_url,
                "format":       fmt,
                "width":        0,       # auto-filled if Pillow installed (see below)
                "height":       0,
                "size_kb":      get_file_size_kb(str(filepath)),
                "tags":         tags,
                "search_terms": build_search_terms(parts, category_id, subcategory),
                "colors":       [],      # fill manually: ["navy", "white", "black"]
                "mood":         "",      # fill manually: bright | dark | warm | minimal | neutral
                "license":      "free",
                "source":       "",      # fill manually: unsplash.com | pexels.com | pixabay.com
                "description":  filename_to_title(parts, subcategory),
            }

            # ── Optional Pillow auto-dimensions ────────────────────────────
            try:
                from PIL import Image as PILImage
                with PILImage.open(str(filepath)) as img:
                    entry["width"], entry["height"] = img.size
                    w, h = img.size
                    if   w > h * 1.2: entry["orientation"] = "landscape"
                    elif h > w * 1.2: entry["orientation"] = "portrait"
                    else:             entry["orientation"] = "square"
            except Exception:
                pass  # Pillow not installed or can't read file — guessed value stays
            # ───────────────────────────────────────────────────────────────

            images.append(entry)
            counter += 1

    manifest = {
        "category":     category_id,
        "label":        category_label,
        "last_updated": str(date.today()),
        "total_images": len(images),
        "images":       images,
    }

    manifest_path = category_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"  ✓ {category_label}: {len(images)} images → {manifest_path}")
    return images  # return list so run() can build search.json


# ─── CORE: search.json ────────────────────────────────────────────────────────

def build_search_index(all_images: list):
    """
    Build a flat keyword → [image_ids] index across ALL categories.
    AI can fetch this single file and resolve any query instantly
    without reading every category manifest.

    Example:
      "formal suit" → ["fashion-002"]
      "summer"      → ["fashion-001", "fashion-003"]
    """
    index = defaultdict(list)

    for img in all_images:
        img_id = img["id"]
        tokens = set()

        # All search_terms
        tokens.update(img.get("search_terms", []))
        # All tags
        tokens.update(img.get("tags", []))
        # object + variant words
        tokens.update(img["object"].lower().split())
        tokens.update(img["variant"].lower().split())
        # subcategory
        tokens.add(img.get("subcategory", ""))
        # mood + colors
        if img.get("mood"):
            tokens.add(img["mood"])
        tokens.update(img.get("colors", []))

        for token in tokens:
            token = token.strip().lower()
            if token and img_id not in index[token]:
                index[token].append(img_id)

    # Sort for readability
    sorted_index = {k: sorted(v) for k, v in sorted(index.items())}

    with open(SEARCH_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "generated":    str(date.today()),
            "total_terms":  len(sorted_index),
            "index":        sorted_index,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ search.json → {len(sorted_index)} searchable terms")


# ─── RUN ──────────────────────────────────────────────────────────────────────

def run():
    print("\n━━━ AST Asset Library — Manifest Generator ━━━\n")

    if not Path(TOPICS_FILE).exists():
        print("✗ topics.json not found. Run from the repo root folder.")
        return

    with open(TOPICS_FILE, "r") as f:
        topics = json.load(f)

    total_images        = 0
    categories_processed = 0
    all_images          = []   # collected across categories for search.json

    for category in topics["categories"]:
        cat_id    = category["id"]
        cat_label = category["label"]
        cat_path  = category["path"]

        print(f"📂 {cat_label}")
        images = generate_manifest_for_category(cat_path, cat_id, cat_label)
        if images:
            total_images         += len(images)
            categories_processed += 1
            all_images.extend(images)

    # Build global search index
    print("\n📇 Building search.json")
    build_search_index(all_images)

    # Update topics.json timestamp
    topics["last_updated"] = str(date.today())
    with open(TOPICS_FILE, "w") as f:
        json.dump(topics, f, indent=2)

    print(f"\n━━━ Done ━━━")
    print(f"Categories processed : {categories_processed}")
    print(f"Total images indexed : {total_images}")
    print(f"search.json terms    : see above")
    print(f"topics.json updated  : {date.today()}\n")
    print("💡 Tip: install Pillow for auto width/height detection:")
    print("   pip install Pillow\n")


if __name__ == "__main__":
    run()