"""
AST Asset Library — Manifest Generator
=======================================
Drop images into their category/subcategory folders,
name them descriptively, run this script, and the
manifest.json for each category is auto-generated.

Naming convention for your image files:
  object-variant-extra.webp
  Examples:
    woman-dress-summer-floral.webp
    mens-suit-navy-formal.webp
    sneakers-white-minimal.webp
    pwa-icon-512x512.png
    logo-dark-bg.svg

Usage:
  python generate_manifests.py

Run from the root of the ast-asset-library folder.
"""

import os
import json
from datetime import date
from pathlib import Path


# ─── CONFIG ───────────────────────────────────────────────────────────────────

IMAGES_ROOT = "images"
TOPICS_FILE = "topics.json"
SUPPORTED_FORMATS = {".webp", ".jpg", ".jpeg", ".png", ".svg", ".gif"}

# GitHub repo details — update these to match your repo
GITHUB_USERNAME = "01annanogero-coder"
GITHUB_REPO = "ast-asset-library"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# Map subcategory folder names to readable labels
SUBCATEGORY_LABELS = {
    "mens": "Mens",
    "womens": "Womens",
    "kids-fashion": "Kids Fashion",
    "accessories": "Accessories",
    "footwear": "Footwear",
    "fitness": "Fitness",
    "nutrition": "Nutrition",
    "mental-health": "Mental Health",
    "medical": "Medical",
    "toys": "Toys",
    "education": "Education",
    "activities": "Activities",
    "babies": "Babies",
    "meals": "Meals",
    "drinks": "Drinks",
    "desserts": "Desserts",
    "ingredients": "Ingredients",
    "restaurant": "Restaurant",
    "devices": "Devices",
    "coding": "Coding",
    "ai": "AI",
    "networking": "Networking",
    "workspace": "Workspace",
    "landscapes": "Landscapes",
    "animals": "Animals",
    "plants": "Plants",
    "sky": "Sky",
    "water": "Water",
    "office": "Office",
    "meetings": "Meetings",
    "finance": "Finance",
    "startup": "Startup",
    "people": "People",
    "interiors": "Interiors",
    "exteriors": "Exteriors",
    "modern": "Modern",
    "traditional": "Traditional",
    "commercial": "Commercial",
    "africa": "Africa",
    "europe": "Europe",
    "asia": "Asia",
    "americas": "Americas",
    "landmarks": "Landmarks",
    "skincare": "Skincare",
    "makeup": "Makeup",
    "haircare": "Haircare",
    "products": "Products",
    "football": "Football",
    "basketball": "Basketball",
    "athletics": "Athletics",
    "gym": "Gym",
    "outdoor": "Outdoor",
    "classroom": "Classroom",
    "books": "Books",
    "elearning": "E-Learning",
    "science": "Science",
    "writing": "Writing",
    "pwa": "PWA Icons",
    "svg": "SVG Icons",
    "social": "Social Media Icons",
    "ecommerce": "E-Commerce Icons",
    "arrows": "Arrows",
    "ui": "UI Icons",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def filename_to_tags(filename: str) -> list:
    """Convert a filename like 'woman-dress-summer-floral' into tags."""
    stem = Path(filename).stem
    parts = stem.replace("_", "-").split("-")
    return [p.lower() for p in parts if len(p) > 1]


def filename_to_object(filename: str) -> str:
    """Convert filename to a readable object name."""
    stem = Path(filename).stem
    parts = stem.replace("_", "-").split("-")
    # First 2 parts = object name
    return " ".join(parts[:2]).title()


def filename_to_variant(filename: str) -> str:
    """Extract variant from filename (parts after first 2 words)."""
    stem = Path(filename).stem
    parts = stem.replace("_", "-").split("-")
    if len(parts) > 2:
        return " ".join(parts[2:]).lower()
    return "default"


def get_format(filename: str) -> str:
    return Path(filename).suffix.lstrip(".")


def get_file_size_kb(filepath: str) -> int:
    try:
        return round(os.path.getsize(filepath) / 1024)
    except:
        return 0


def generate_id(category: str, index: int) -> str:
    return f"{category}-{str(index).zfill(3)}"


# ─── CORE ─────────────────────────────────────────────────────────────────────

def generate_manifest_for_category(category_path: str, category_id: str, category_label: str):
    """
    Walk a category folder, find all images across subcategories,
    and generate a manifest.json for that category.
    """
    images = []
    counter = 1

    category_dir = Path(category_path)
    if not category_dir.exists():
        print(f"  ⚠ Folder not found: {category_path} — skipping")
        return

    # Walk all files including subcategory folders
    for root, dirs, files in os.walk(category_dir):
        dirs.sort()  # Alphabetical order
        for filename in sorted(files):
            ext = Path(filename).suffix.lower()
            if ext not in SUPPORTED_FORMATS:
                continue

            filepath = Path(root) / filename
            relative_path = filepath.relative_to(Path("."))

            # Determine subcategory from folder name
            relative_to_category = filepath.relative_to(category_dir)
            parts = relative_to_category.parts
            subcategory = parts[0] if len(parts) > 1 else "general"

            tags = filename_to_tags(filename)
            # Add category and subcategory to tags automatically
            if category_id not in tags:
                tags.insert(0, category_id)
            if subcategory not in tags:
                tags.insert(1, subcategory)

            clean_path = str(relative_path).replace("\\", "/")
            raw_url = f"{GITHUB_RAW_BASE}/{clean_path}"

            entry = {
                "id": generate_id(category_id, counter),
                "object": filename_to_object(filename),
                "variant": filename_to_variant(filename),
                "subcategory": subcategory,
                "file": clean_path,
                "raw_url": raw_url,
                "format": get_format(filename),
                "dimensions": "—",         # Fill manually or add Pillow support below
                "size_kb": get_file_size_kb(str(filepath)),
                "tags": tags,
                "colors": [],              # Fill manually for best results
                "mood": "",                # Fill manually: bright, dark, minimal, warm...
                "license": "free",
                "source": "",              # Fill manually: unsplash.com, pexels.com...
                "description": f"{filename_to_object(filename)} — {filename_to_variant(filename)}"
            }

            images.append(entry)
            counter += 1

    manifest = {
        "category": category_id,
        "label": category_label,
        "last_updated": str(date.today()),
        "total_images": len(images),
        "images": images
    }

    manifest_path = category_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"  ✓ {category_label}: {len(images)} images → {manifest_path}")
    return len(images)


def run():
    print("\n━━━ AST Asset Library — Manifest Generator ━━━\n")

    # Load topics.json
    if not Path(TOPICS_FILE).exists():
        print("✗ topics.json not found. Run from the repo root folder.")
        return

    with open(TOPICS_FILE, "r") as f:
        topics = json.load(f)

    total_images = 0
    categories_processed = 0

    for category in topics["categories"]:
        cat_id = category["id"]
        cat_label = category["label"]
        cat_path = category["path"]

        print(f"📂 {cat_label}")
        count = generate_manifest_for_category(cat_path, cat_id, cat_label)
        if count:
            total_images += count
            categories_processed += 1

    # Update topics.json with updated date
    topics["last_updated"] = str(date.today())
    with open(TOPICS_FILE, "w") as f:
        json.dump(topics, f, indent=2)

    print(f"\n━━━ Done ━━━")
    print(f"Categories processed : {categories_processed}")
    print(f"Total images indexed : {total_images}")
    print(f"topics.json updated  : {date.today()}\n")


# ─── OPTIONAL: Auto-detect image dimensions using Pillow ──────────────────────
# Uncomment the block below if you have Pillow installed (pip install Pillow)
# and want dimensions filled automatically.

# from PIL import Image as PILImage
#
# def get_dimensions(filepath: str) -> str:
#     try:
#         with PILImage.open(filepath) as img:
#             w, h = img.size
#             return f"{w}x{h}"
#     except:
#         return "—"
#
# Then replace:
#   "dimensions": "—",
# with:
#   "dimensions": get_dimensions(str(filepath)),


if __name__ == "__main__":
    run()
