import cv2
import numpy as np
from .theme import FONT, PANEL_ALPHA


def lighten_color(bgr, factor=0.4):
    """Brighten a BGR color toward white by a factor (0-1)."""
    return tuple(int(c + (255 - c) * factor) for c in bgr)


def draw_rounded_rect(frame, pt1, pt2, color, radius=10, thickness=-1, alpha=1.0):
    """Draw a rounded rectangle. thickness=-1 for filled."""
    x1, y1 = pt1
    x2, y2 = pt2
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

    if alpha < 1.0:
        overlay = frame.copy()
        target = overlay
    else:
        target = frame

    if thickness == -1:
        # Filled rounded rect
        cv2.rectangle(target, (x1 + r, y1), (x2 - r, y2), color, cv2.FILLED)
        cv2.rectangle(target, (x1, y1 + r), (x2, y2 - r), color, cv2.FILLED)
        cv2.circle(target, (x1 + r, y1 + r), r, color, cv2.FILLED)
        cv2.circle(target, (x2 - r, y1 + r), r, color, cv2.FILLED)
        cv2.circle(target, (x1 + r, y2 - r), r, color, cv2.FILLED)
        cv2.circle(target, (x2 - r, y2 - r), r, color, cv2.FILLED)
    else:
        # Outline only
        cv2.line(target, (x1 + r, y1), (x2 - r, y1), color, thickness, cv2.LINE_AA)
        cv2.line(target, (x1 + r, y2), (x2 - r, y2), color, thickness, cv2.LINE_AA)
        cv2.line(target, (x1, y1 + r), (x1, y2 - r), color, thickness, cv2.LINE_AA)
        cv2.line(target, (x2, y1 + r), (x2, y2 - r), color, thickness, cv2.LINE_AA)
        cv2.ellipse(target, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(target, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(target, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(target, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness, cv2.LINE_AA)

    if alpha < 1.0:
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_glow_ellipse(frame, center, axes, color, glow_color, thickness=2):
    """Draw an ellipse with a soft glow effect behind it."""
    overlay = frame.copy()
    for i in range(3, 0, -1):
        expanded = (axes[0] + i * 3, axes[1] + i * 3)
        cv2.ellipse(overlay, center, expanded, 0, -45, 235,
                     glow_color, thickness + 1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
    # Main ellipse
    cv2.ellipse(frame, center, axes, 0, -45, 235, color, thickness, cv2.LINE_AA)


def draw_pill_badge(frame, cx, cy, text, bg_color, text_color, scale=0.5):
    """Draw a rounded pill-shaped badge with centered text."""
    (tw, th), baseline = cv2.getTextSize(text, FONT, scale, 1)
    pad_x, pad_y = 10, 4
    w = tw + pad_x * 2
    h = th + pad_y * 2
    x1 = cx - w // 2
    y1 = cy - h // 2
    r = h // 2
    draw_rounded_rect(frame, (x1, y1), (x1 + w, y1 + h), bg_color, radius=r, thickness=-1, alpha=0.85)
    tx = x1 + (w - tw) // 2
    ty = y1 + (h + th) // 2 - baseline
    cv2.putText(frame, text, (tx, ty), FONT, scale, text_color, 1, cv2.LINE_AA)


def draw_diamond_marker(frame, center, size, color, outline_color):
    """Draw a diamond shape at the given center."""
    x, y = center
    pts = np.array([
        [x, y - size],
        [x + size // 2, y],
        [x, y + size],
        [x - size // 2, y],
    ])
    cv2.drawContours(frame, [pts], 0, color, cv2.FILLED)
    cv2.drawContours(frame, [pts], 0, outline_color, 1, cv2.LINE_AA)
