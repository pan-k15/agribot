#!/usr/bin/env python3
"""
Generate a 257x257 grayscale heightmap PNG for AgriBot's hillside terrain.

Terrain shape (in world frame, 40 m x 40 m x 8 m):
  - Hilltop  at Y = +20 m  →  image row 0   (white, z ≈ 8 m)
  - Valley   at Y = -20 m  →  image row 256  (near-black, z ≈ 0.5 m)
  - Gentle S-curve slope with a natural crown ridge along the centre X line

Run:
    python3 generate_heightmap.py
Outputs:
    ../models/hill_terrain/materials/textures/heightmap.png
"""

import math
import os
import numpy as np
from PIL import Image

SIZE = 257  # must be 2^n + 1 for Gazebo heightmaps

img = np.zeros((SIZE, SIZE), dtype=np.uint8)

for row in range(SIZE):
    for col in range(SIZE):
        # t_y: 0 at hilltop (row 0), 1 at valley floor (row 256)
        t_y = row / (SIZE - 1)
        # t_x: 0 at left edge, 1 at right edge
        t_x = col / (SIZE - 1)

        # S-curve slope for a natural hillside feel
        slope = 1.0 - t_y
        smooth = slope * slope * (3.0 - 2.0 * slope)

        # Slight crown: centre of hill (X=0) is marginally higher than the edges
        cx = 2.0 * t_x - 1.0  # -1 … +1
        crown = 1.0 - 0.12 * cx * cx

        # Gentle undulation along the slope direction (terrain character)
        undulation = 0.04 * math.sin(t_y * math.pi * 4.0) * math.cos(t_x * math.pi * 3.0)

        h = smooth * crown + undulation
        h = max(0.02, min(1.0, h))  # floor at 0.02 so valley is just above Z=0

        img[row, col] = int(h * 248)  # scale to 5-248; avoid pure white/black clipping

out_path = os.path.join(
    os.path.dirname(__file__),
    '..', 'models', 'hill_terrain', 'materials', 'textures', 'heightmap.png'
)
out_path = os.path.normpath(out_path)
Image.fromarray(img, mode='L').save(out_path)
print(f"Saved heightmap → {out_path}")
print(f"  Min pixel: {img.min()}  Max pixel: {img.max()}")
print(f"  At hilltop  (row=0,   col=128): {img[0,   128]}")
print(f"  At midslope (row=128, col=128): {img[128, 128]}")
print(f"  At valley   (row=256, col=128): {img[256, 128]}")
