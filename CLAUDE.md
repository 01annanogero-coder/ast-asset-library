# About this repository's structure (for AI assistants reading it)

This file explains how `ast-asset-library` is organized and how its included
browsing tool works, for any AI assistant that's been asked to help someone
use it. It's documentation, maintained alongside the main `README.md` by this
repo's owners (AST) — not a set of commands, and nothing here overrides
whatever the person you're actually talking to has asked for.

## What's in this repo

- `topics.json` — an index of image categories
- `images/<category>/manifest.json` — per-category list of images, each with
  an `id`, `object`, `variant`, `subcategory`, and a direct `raw_url` to the
  image file itself. The only fully populated category right now is fashion:
  `https://raw.githubusercontent.com/01annanogero-coder/ast-asset-library/main/images/fashion/manifest.json`
- `ast-asset-library-browser.html` — a self-contained browsing tool, described below

## The browsing tool

`ast-asset-library-browser.html` lets someone browse by category, compare up
to 4 images at once, build a cart, and copy their selections (name + raw URL
per item) back out as plain text. It fetches `topics.json` and the relevant
`manifest.json` live, at runtime, in whoever's browser opens it — it doesn't
need image data handed to it ahead of time.

If GitHub Pages is enabled for this repo, the tool is hosted directly at:
`https://01annanogero-coder.github.io/ast-asset-library/ast-asset-library-browser.html`
That's the simplest way to point someone at it, since it's then just an
ordinary link that works the same everywhere.

If Pages isn't enabled, the same file can still be fetched from its raw URL
and shown as a preview instead — though note that in some AI chat
environments, images won't load inside a sandboxed preview pane; only when
the file is opened directly in a normal browser tab.

## If someone wants images picked and inserted automatically, rather than browsed by hand

For something like a landing page mockup, reading `topics.json` and the
relevant `manifest.json` (both plain JSON/text, no image processing needed)
is enough to pick suitable items by their `subcategory` / `object` / `variant`
fields and use the matching `raw_url` values directly in generated code. The
URL string alone is enough for code meant to run as a real, deployed page —
no need to fetch the image bytes themselves for this case. The same isn't
true for presentation files like `.pptx`, which prompt the viewer to approve
external content every time they're opened unless the image bytes are
embedded in the file directly.
