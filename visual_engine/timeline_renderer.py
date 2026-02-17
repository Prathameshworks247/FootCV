import cv2
import numpy as np
from .theme import PALETTE, FONT
from .primitives import draw_rounded_rect


class TimelineRenderer:
    def __init__(self, frame_rate=24):
        self.bar_h = 16
        self.margin_x = 40
        self.margin_bottom = 25
        self.max_frames_shown = frame_rate * 30  # 30 seconds
        self.frame_rate = frame_rate

    def draw(self, frame, frame_num, team_ball_control, team1_color, team2_color):
        h, w = frame.shape[:2]
        bar_x = self.margin_x
        bar_y = h - self.margin_bottom - self.bar_h
        bar_w = w - self.margin_x * 2

        # Background
        draw_rounded_rect(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + self.bar_h),
                          PALETTE['timeline_bg'], radius=4, alpha=0.7)

        # Determine visible range
        start = max(0, frame_num - self.max_frames_shown)
        visible = team_ball_control[start:frame_num + 1]

        if len(visible) == 0:
            return

        team1_bgr = tuple(int(c) for c in team1_color)
        team2_bgr = tuple(int(c) for c in team2_color)

        px_per_frame = bar_w / self.max_frames_shown

        # Draw possession segments in batches
        current_team = visible[0]
        seg_start = 0
        for i in range(1, len(visible) + 1):
            if i == len(visible) or visible[i] != current_team:
                sx = bar_x + int(seg_start * px_per_frame)
                ex = bar_x + int(i * px_per_frame)
                color = team1_bgr if current_team == 1 else team2_bgr
                cv2.rectangle(frame, (sx, bar_y + 2), (ex, bar_y + self.bar_h - 2),
                              color, cv2.FILLED)
                if i < len(visible):
                    current_team = visible[i]
                    seg_start = i

        # Current position marker
        pos_x = bar_x + int(len(visible) * px_per_frame)
        cv2.line(frame, (pos_x, bar_y - 2), (pos_x, bar_y + self.bar_h + 2),
                 (255, 255, 255), 2, cv2.LINE_AA)

        # Time labels
        start_sec = start / self.frame_rate
        curr_sec = frame_num / self.frame_rate
        cv2.putText(frame, f"{start_sec:.0f}s", (bar_x, bar_y - 5),
                    FONT, 0.3, PALETTE['text_secondary'], 1, cv2.LINE_AA)
        cv2.putText(frame, f"{curr_sec:.0f}s", (pos_x - 15, bar_y - 5),
                    FONT, 0.3, PALETTE['text_primary'], 1, cv2.LINE_AA)
