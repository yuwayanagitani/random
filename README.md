# ✨ Random Images for Anki (anki-random-images)

Study can get repetitive. This add-on adds a small surprise: it shows a random image in the Reviewer when a card is displayed.

- No AI
- No network
- No data upload
- Works with any note type (does not require template edits)

---

## 🔗 AnkiWeb

Official AnkiWeb page:

👉 https://ankiweb.net/shared/info/1726486470

(Recommended install method for easy setup and automatic updates.)

---

## ✅ What it does

When a card is shown in the Reviewer, the add-on can:

- Pick a random image from a folder inside `collection.media/`
- Inject the image into the card HTML (Question side, Answer side, or both)
- Optionally show a cleaned filename caption under the image
- Optionally avoid showing the same image twice in a row

It uses Anki’s `card_will_show` hook, so it works with any note type without touching your templates.

---

## 🚀 Quick Start

### 1) Put images in your media subfolder

1. Open Anki
2. Go to: Tools → Add-ons → Random Images → Config
3. Click: Open folder

This creates (or opens) a folder like:

- `collection.media/random_images/`

Drop your images into that folder.

Supported extensions:

- `.png`
- `.jpg`
- `.jpeg`
- `.gif`

### 2) Choose where images appear

In the Config GUI, enable:

- Show on Question side
- Show on Answer side

You can enable one or both.

---

## ⚙️ Settings (Config GUI)

Open:

- Tools → Add-ons → Random Images → Config

Main options:

### Enable add-on
Turn the add-on on/off.

### Show on Question / Answer
Choose which side(s) of the card will get the random image.

### Image folder (inside `collection.media`)
Default: `random_images`

Safety rules:

- Must be a simple subfolder name
- Absolute paths are rejected
- `..` is rejected
- Windows backslashes are normalized

Examples:

- OK: `random_images`
- OK: `motivation/pics`
- NG: `C:\Users\...`
- NG: `../something`

### Max width (%)
Default: `80%`  
Set `0` to disable the limit.

### Max height (vh)
Default: `60vh`  
Set `0` to disable the limit.

### Avoid repeat
Default: ON  
If multiple images exist, it avoids showing the same file twice in a row.

### Show filename caption
Default: ON  
Shows a cleaned-up filename under the image.

Example:

- `cute-cat_2024-01.jpg` → `CUTE CAT`

### Show every N cards
Default: `1` (every card)  
Set the display interval for random images.

Examples:

- `1` = Show an image on every card (default behavior)
- `10` = Show an image only on every 10th card
- `50` = Show an image only on every 50th card

When a card is selected to show an image, it appears on both the Question and Answer sides (if both are enabled in settings).

---

## 🧩 How it works (technical overview)

- Chooses a random file from your configured folder under `collection.media/`
- Injects HTML like:
  - An `<img>` tag with size limits
  - An optional caption block

Important:

- It does not modify notes
- It does not change your collection permanently
- It only affects what is rendered in the Reviewer

---

## 🛠 Troubleshooting

### No image shows up
Check:

- The add-on is enabled
- The folder exists and contains supported image files
- “Show on Question/Answer” is enabled for that side

### “Open folder” says “No collection is open”
Open a collection/deck first, then try again.

### Images are too big / small
Adjust:

- Max width (%)
- Max height (vh)

### It keeps showing the same image
Enable:

- Avoid repeat  
(Works best when you have multiple images in the folder.)

---

## 🔒 Privacy

- No network calls
- No AI
- No data upload

Everything stays in your local Anki collection.

---

## 📦 Installation

### Install from AnkiWeb (recommended)

1. Tools → Add-ons → Browse & Install
2. Open the AnkiWeb page and install:
   - https://ankiweb.net/shared/info/1726486470
3. Restart Anki

### Manual install (GitHub)

1. Download this repository
2. Put it into:
   - `Anki2/addons21/anki-random-images`
3. Restart Anki

---

## 📜 License

MIT License (see `LICENSE`).
