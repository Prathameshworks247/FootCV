import cv2
import numpy as np
import sys
sys.path.append('../')
from utils import get_center_of_bbox, get_bbox_width, get_foot_position
from .theme import PALETTE, FONT
from .primitives import draw_glow_ellipse, draw_pill_badge, draw_diamond_marker, lighten_color


def draw_player_marker(frame, bbox, team_color, track_id=None):
    """Draw a glow ellipse at player feet with optional pill badge ID."""
    y2 = int(bbox[3])
    x_center, _ = get_center_of_bbox(bbox)
    width = get_bbox_width(bbox)

    center = (x_center, y2)
    axes = (int(width), int(0.35 * width))
    glow_color = lighten_color(team_color, 0.4)

    draw_glow_ellipse(frame, center, axes, team_color, glow_color)

    if track_id is not None:
        draw_pill_badge(frame, x_center, y2 + 18, str(track_id),
                        bg_color=team_color, text_color=(255, 255, 255), scale=0.45)


def draw_ball_marker(frame, bbox, color=None):
    """Draw a gold diamond marker above the ball."""
    if color is None:
        color = PALETTE['ball']
    x, _ = get_center_of_bbox(bbox)
    y = int(bbox[1])
    draw_diamond_marker(frame, (x, y - 12), size=10, color=color,
                        outline_color=(255, 255, 255))


def draw_possession_indicator(frame, bbox, frame_num, color=None):
    """Draw a pulsing ring above the player who has the ball."""
    if color is None:
        color = PALETTE['possession']
    x, _ = get_center_of_bbox(bbox)
    y = int(bbox[1]) - 25

    # Pulse radius oscillates between 8 and 12 over 12 frames
    cycle = frame_num % 12
    pulse = 8 + int(4 * abs(cycle - 6) / 6)

    cv2.circle(frame, (x, y), pulse, color, 2, cv2.LINE_AA)
    cv2.circle(frame, (x, y), 3, color, cv2.FILLED, cv2.LINE_AA)


def draw_speed_halo(frame, bbox, speed, team_color):
    """Draw a translucent ring around fast-moving players."""
    if speed is None or speed < 2.0:
        return

    x_center, _ = get_center_of_bbox(bbox)
    y2 = int(bbox[3])
    glow_color = lighten_color(team_color, 0.5)

    radius = int(15 + (min(speed, 30) / 30.0) * 35)

    overlay = frame.copy()
    cv2.circle(overlay, (x_center, y2), radius, glow_color, 2, cv2.LINE_AA)
    alpha = min(0.15 + (speed / 30.0) * 0.25, 0.4)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_xg_badge(frame, bbox, xg_value):
    """Draw an xG pill badge above the player's head."""
    x_center, _ = get_center_of_bbox(bbox)
    y_top = int(bbox[1])
    draw_pill_badge(frame, x_center, y_top - 45, f"xG: {xg_value:.2f}",
                    bg_color=(0, 40, 120), text_color=(100, 200, 255), scale=0.45)


def draw_speed_badge(frame, bbox, speed, distance):
    """Draw speed and distance as dark pill badges below the player."""
    x_center = int((bbox[0] + bbox[2]) / 2)
    y_foot = int(bbox[3])

    draw_pill_badge(frame, x_center, y_foot + 38, f"{speed:.1f} km/h",
                    bg_color=PALETTE['panel_bg'], text_color=PALETTE['text_primary'],
                    scale=0.35)
    draw_pill_badge(frame, x_center, y_foot + 56, f"{distance:.0f}m",
                    bg_color=PALETTE['panel_bg'], text_color=PALETTE['text_secondary'],
                    scale=0.3)
