import cv2
import numpy as np
from .theme import PALETTE, FONT, FONT_SCALE_LABEL, FONT_SCALE_VALUE, PANEL_ALPHA
from .primitives import draw_rounded_rect


def draw_ball_control_panel(frame, frame_num, team_ball_control, team1_color, team2_color):
    """Draw a modern dark panel with team-colored possession progress bar."""
    h, w = frame.shape[:2]
    x1 = w - 540
    y1 = h - 160
    x2 = w - 20
    y2 = h - 20

    # Dark panel background
    draw_rounded_rect(frame, (x1, y1), (x2, y2), PALETTE['panel_bg'],
                      radius=12, alpha=PANEL_ALPHA)

    # Gold accent line at top
    cv2.line(frame, (x1 + 14, y1 + 3), (x2 - 14, y1 + 3),
             PALETTE['panel_border'], 2, cv2.LINE_AA)

    # Calculate percentages
    control_slice = team_ball_control[:frame_num + 1]
    t1_count = np.sum(control_slice == 1)
    t2_count = np.sum(control_slice == 2)
    total = t1_count + t2_count
    t1_pct = t1_count / total if total > 0 else 0.5
    t2_pct = t2_count / total if total > 0 else 0.5

    # Title
    cv2.putText(frame, "POSSESSION", (x1 + 20, y1 + 30),
                FONT, FONT_SCALE_LABEL, PALETTE['text_secondary'], 1, cv2.LINE_AA)

    # Progress bar
    bar_x = x1 + 20
    bar_y = y1 + 45
    bar_w = x2 - x1 - 40
    bar_h = 22
    t1_bar_w = int(bar_w * t1_pct)

    # Team 1 portion
    team1_bgr = tuple(int(c) for c in team1_color)
    team2_bgr = tuple(int(c) for c in team2_color)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + t1_bar_w, bar_y + bar_h),
                  team1_bgr, cv2.FILLED)
    # Team 2 portion
    cv2.rectangle(frame, (bar_x + t1_bar_w, bar_y),
                  (bar_x + bar_w, bar_y + bar_h), team2_bgr, cv2.FILLED)

    # Percentage labels with team color dots
    label_y = bar_y + bar_h + 30
    # Team 1
    cv2.circle(frame, (bar_x + 6, label_y - 5), 6, team1_bgr, cv2.FILLED, cv2.LINE_AA)
    cv2.putText(frame, f"Team 1:  {t1_pct * 100:.1f}%", (bar_x + 18, label_y),
                FONT, FONT_SCALE_VALUE, PALETTE['text_primary'], 1, cv2.LINE_AA)
    # Team 2
    t2_label_x = bar_x + bar_w // 2 + 10
    cv2.circle(frame, (t2_label_x + 6, label_y - 5), 6, team2_bgr, cv2.FILLED, cv2.LINE_AA)
    cv2.putText(frame, f"Team 2:  {t2_pct * 100:.1f}%", (t2_label_x + 18, label_y),
                FONT, FONT_SCALE_VALUE, PALETTE['text_primary'], 1, cv2.LINE_AA)


def draw_pressing_panel(frame, pressing_label, avg_distance, unit="m"):
    """Draw a pressing intensity panel on the left side of the screen."""
    if pressing_label is None:
        return

    x1, y1 = 15, 70
    x2, y2 = 290, 120
    draw_rounded_rect(frame, (x1, y1), (x2, y2), PALETTE['panel_bg'],
                      radius=8, alpha=0.7)

    # Color code by intensity
    if pressing_label == "HIGH":
        color = (0, 0, 220)       # red
    elif pressing_label == "MED":
        color = (0, 180, 230)     # yellow
    else:
        color = (0, 180, 0)       # green

    cv2.circle(frame, (x1 + 16, y1 + 26), 6, color, cv2.FILLED, cv2.LINE_AA)
    dist_text = f"({avg_distance:.0f}{unit})" if unit == "m" else ""
    cv2.putText(frame, f"PRESS: {pressing_label}  {dist_text}",
                (x1 + 30, y1 + 32), FONT, 0.45,
                PALETTE['text_primary'], 1, cv2.LINE_AA)


def draw_camera_info(frame, camera_movement):
    """Draw a small camera movement indicator (only when movement is significant)."""
    x_movement, y_movement = camera_movement
    if abs(x_movement) < 0.5 and abs(y_movement) < 0.5:
        return

    x1, y1 = 15, 15
    x2, y2 = 290, 55
    draw_rounded_rect(frame, (x1, y1), (x2, y2), PALETTE['panel_bg'],
                      radius=8, alpha=0.6)
    cv2.putText(frame, f"CAM  X:{x_movement:+.1f}  Y:{y_movement:+.1f}",
                (x1 + 12, y1 + 28), FONT, 0.45,
                PALETTE['text_secondary'], 1, cv2.LINE_AA)
