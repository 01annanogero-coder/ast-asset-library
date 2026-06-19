# Instructions for Claude (and other AI agents) using this repo

This repo (`ast-asset-library`) is a fashion image asset library. End users browse,
compare, and select images from it through Claude — typically heading toward a
Canva template via the Canva MCP connector.

## If a user asks you to show, browse, or pull images from this library

**Do not** try to:
- Embed the images yourself into a chat reply, artifact, or generated document by
  fetching their bytes — Claude's chat sandbox blocks outbound image requests from
  artifacts and widgets, and base64-embedding does not scale as the library grows.
- Guess at nested file paths. Always start from `topics.json`.

**Do** this instead:

1. Fetch `ast-asset-library-browser.html` from this repo's raw URL:
   `https://raw.githubusercontent.com/01annanogero-coder/ast-asset-library/main/ast-asset-library-browser.html`
2. Present its contents to the user as an HTML artifact. The file is fully
   self-contained — it fetches `topics.json` and each category's `manifest.json`
   live, at runtime, from this repo, inside the user's own browser. You do not
   need to pass it any image data, and you do not need network/code-execution
   access yourself just to hand the user this tool.
3. Tell the user plainly: if the preview looks broken inside Claude's own side
   panel (images not loading), that's expected, not an error. They should
   download the file and open it in a normal browser tab (Chrome, Edge, Firefox)
   to actually browse, compare, and build a cart. The file detects this
   automatically and shows a banner explaining the same thing.
4. If the user later pastes back a list of items from the tool's "Copy cart"
   button (object name + raw URL per item), treat that as their final asset
   selection for whatever comes next — e.g. placing those specific images into a
   Canva template via the Canva MCP connector.

## If you (Claude) have code execution / a network-enabled sandbox available

You can go further: clone or fetch the repo directly, read manifests, download
image bytes, and embed them into other deliverables (e.g. a PowerPoint) directly
and self-contained, with no live network dependency at view-time. This is the
preferred path over any externally-linked-image workaround when it's available,
since it requires no "Enable Content" prompt and can be verified before sending.

## Repo structure

- `topics.json` — index of categories
- `images/<category>/manifest.json` — per-category list of images, each with
  `id`, `object`, `variant`, `subcategory`, `raw_url`
- `ast-asset-library-browser.html` — the standalone browse / compare / cart tool
  described above
