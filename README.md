# AST Asset Library

A curated, AI-queryable image and icon library built for web developers and graphic designers.
Maintained by **Annan Software Team (AST)**.

---

## What This Is

A GitHub-hosted asset library that Claude can search, preview, and package on demand.
No more manually hunting for images online — describe what you need and Claude finds,
displays, and delivers the right assets as a downloadable zip.

**Designed for:**
- Web developers needing project images fast
- Graphic designers working with Claude on Canva templates
- PWA projects needing standard icon sets
- Any AST client project

---

## Folder Structure

```
ast-asset-library/
│
├── topics.json                  ← Master category index (Claude reads this first)
│
├── images/
│   ├── fashion/
│   │   ├── manifest.json        ← Fashion image index
│   │   ├── mens/
│   │   ├── womens/
│   │   ├── accessories/
│   │   └── footwear/
│   │
│   ├── health/
│   │   ├── manifest.json
│   │   ├── fitness/
│   │   └── nutrition/
│   │
│   ├── kids/
│   ├── food/
│   ├── technology/
│   ├── nature/
│   ├── business/
│   ├── architecture/
│   ├── travel/
│   ├── beauty/
│   ├── sports/
│   ├── education/
│   └── icons/
│       ├── manifest.json
│       ├── pwa/                 ← PWA icons (512x512, 192x192, maskable)
│       ├── svg/
│       └── social/
│
└── scripts/
    └── generate_manifests.py    ← Run this after adding new images
```

---

## Image Naming Convention

Name files descriptively using hyphens. The script reads the filename to auto-generate tags.

```
object-variant-detail.webp

Examples:
  woman-dress-summer-floral.webp
  mens-suit-navy-formal.webp
  sneakers-white-minimal.webp
  kid-playing-toys-indoor.webp
  pwa-icon-512x512.png
  icon-cart-dark.svg
```

---

## Adding New Images

1. Compress image in **Squoosh** (WebP, ~80% quality, under 200KB)
2. Name it descriptively using the convention above
3. Drop it into the correct category/subcategory folder
4. Run the manifest generator:

```bash
cd ast-asset-library
python scripts/generate_manifests.py
```

5. Commit and push to GitHub

The script will update every `manifest.json` automatically.

---

## Image Formats

| Type | Format | Notes |
|------|--------|-------|
| Photos | WebP | Compress in Squoosh, ~80% quality |
| PWA Icons | PNG | Exact sizes: 512x512, 192x192, maskable |
| SVG Icons | SVG | No compression needed |

---

## License

All images are free-to-use, sourced from:
- [Unsplash](https://unsplash.com)
- [Pexels](https://pexels.com)
- [Pixabay](https://pixabay.com)

Always verify license at the original source before use in commercial projects.

---

## Maintained by

**Annan Software Team (AST)** — Nairobi, Kenya  
[GitHub](https://github.com/01annanogero-coder)
