# Anki Random Images

AnkiWeb: https://ankiweb.net/shared/by-author/2117859718

Display a random image each time a card is shown. Images are loaded from a folder inside your Anki `collection.media` directory. All behavior can be customized through `config.json`.

## Features
- Show random images from a folder on card display
- Configurable folder, filename filters, and image sizing
- Option to cache or reshuffle per session or per show

## Installation
1. Tools → Add-ons → Open Add-ons Folder.
2. Copy the add-on folder into `addons21/`.
3. Put your images in `collection.media/<your-folder>`.
4. Restart Anki.

## Usage
- Configure folder and options in Tools → Random Images → Settings.
- Include placeholder tags or fields in your template where the random image will appear (see docs).

## Configuration
`config.json` options:
- folder (string)
- pattern (regex for filenames)
- shuffle_mode (`per_card`, `per_review`, `session`)
- css/size settings

Example:
```json
{
  "folder": "random_images",
  "pattern": ".*\\.(jpg|png)$",
  "shuffle_mode": "per_card"
}
```

## Issues & Support
When reporting issues include example template code and an example image set.

## License
See LICENSE.
