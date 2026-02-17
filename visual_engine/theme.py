import cv2

# All colors in BGR (OpenCV format)
PALETTE = {
    'referee': (180, 180, 180),
    'ball': (0, 245, 255),
    'possession': (0, 220, 255),
    'panel_bg': (40, 35, 30),
    'panel_border': (200, 160, 60),
    'text_primary': (240, 240, 240),
    'text_secondary': (160, 160, 160),
    'minimap_field': (60, 100, 40),
    'minimap_lines': (90, 140, 70),
    'minimap_border': (200, 160, 60),
    'timeline_bg': (30, 28, 25),
}

PANEL_ALPHA = 0.75
GLOW_ALPHA = 0.3
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_LABEL = 0.45
FONT_SCALE_VALUE = 0.6
FONT_SCALE_TITLE = 0.7
MARKER_THICKNESS = 2
