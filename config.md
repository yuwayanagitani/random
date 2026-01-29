# Random Image Per Card - Config Guide<br>
<br>
This add-on displays a random image from your Anki collection.media folder each time a card is shown.<br>
Below are the available configuration options in config.json.<br>
<br>
## Configuration Options<br>
<br>
**enabled** (true/false)<br>
Enable or disable the entire add-on.<br>
<br>
**show_on_question** (true/false)<br>
Show a random image on the question side of the card.<br>
<br>
**show_on_answer** (true/false)<br>
Show a random image on the answer side of the card.<br>
<br>
**folder_name** (string)<br>
Subfolder inside collection.media where images are stored.<br>
Example: `"random_images"` → place images in `collection.media/random_images/`<br>
<br>
**max_width_percent** (number)<br>
Maximum display width of the image as a percentage.<br>
Example: `80` → max-width:80%<br>
<br>
**max_height_vh** (number)<br>
Maximum display height of the image in viewport height units.<br>
Example: `60` → max-height:60vh<br>
Set to 0 for no height limit.<br>
<br>
**avoid_repeat** (true/false)<br>
Avoid showing the same image twice in a row.<br>
<br>
**show_filename** (true/false)<br>
Show a cleaned-up filename caption under the image.<br>
<br>
**show_every_n_cards** (number, min 1)<br>
Display interval for random images. Set to 1 to show an image on every card, 10 to show only on every 10th card, etc.<br>
Example: `10` → shows images only on every 10th Question (and its corresponding Answer if enabled).<br>
Default: `1` (every card)<br>
