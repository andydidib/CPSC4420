"""
Make Unreal's exported RGB captures viewable.

Unreal's Scene Capture writes the color fine but leaves the alpha (transparency)
channel at 0, so image viewers show the PNG as fully transparent/blank.
This script sets every pixel to fully opaque.

Usage (run from your project folder, next to the .uproject file):
    pip install pillow            (one time only)
    python fix_capture_alpha.py                 # fixes Saved/Captures/*_rgb.png
    python fix_capture_alpha.py path/to/folder

Fixed images are written next to the originals as *_rgb_fixed.png
(the originals are left untouched).
"""

import glob
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is not installed. Run:  pip install pillow")

folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join("Saved", "Captures")
files = sorted(f for f in glob.glob(os.path.join(folder, "*_rgb.png"))
               if not f.endswith("_fixed.png"))
if not files:
    sys.exit(f"No *_rgb.png files found in {folder}. Capture some frames with F first.")

for path in files:
    img = Image.open(path).convert("RGB")      # drops the empty alpha channel
    out = path[:-4] + "_fixed.png"
    img.save(out)
    print("Fixed", os.path.basename(out))

print(f"Done: {len(files)} image(s) fixed in {folder}")
