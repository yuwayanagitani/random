# Random Image Add-on for Anki

This add-on displays a random image each time a card is shown. Images are loaded from a folder inside your Anki collection.media directory. All behavior can be customized through `config.json`.

## Features
- Show a random image on card display.
- Select images from a subfolder in collection.media.
- Configurable behavior (folder, alt text, scaling, per-card filters).

## Requirements
- Anki 2.1+
- Images stored in Anki’s collection.media folder (or subfolders)

## Installation
1. Clone or download the add-on.
2. Open Anki → Tools → Add-ons → Open Add-ons Folder.
3. Copy the add-on folder to the add-ons folder and restart Anki.

## Configuration
Edit `config.json` in the add-on folder (or use the add-on settings UI if present). Example:
```json
{
  "folder": "random-images",
  "mode": "per-show", 
  "scale": "contain",
  "extensions": [".jpg", ".png", ".gif"]
}
```
- folder: subfolder inside collection.media where images are stored
- mode: when to pick a new image (per-show, per-card)
- scale: how images are sized on cards

## Usage
- Include a placeholder in your card template where the random image should appear, e.g.:
```html
<div id="random-image"></div>
```
- The add-on injects an <img> tag or background image into the placeholder at display time.

## Troubleshooting
- If images do not appear, confirm they exist in the specified media subfolder and that file extensions match.
- If caching occurs, try restarting Anki.

## Development
- Contributions are welcome. Please open an issue for desired features or bugs.

## License
MIT License — see LICENSE file.

## Contact
Author: yuwayanagitani
