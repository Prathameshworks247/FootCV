import cv2
import numpy as np
from .theme import PALETTE, FONT
from .primitives import draw_rounded_rect


class MinimapRenderer:
    def __init__(self, court_length=23.32, court_width=68):
        self.court_length = court_length
        self.court_width = court_width
        self.map_w = 280
        self.map_h = 180
        self.margin = 20
        # Position will be set dynamically based on frame size
        self.map_x = 0
        self.map_y = 0
        self.scale_x = self.map_w / court_length
        self.scale_y = self.map_h / court_width

    def _set_position(self, frame_width):
        self.map_x = frame_width - self.map_w - self.margin
        self.map_y = self.margin

    def _world_to_minimap(self, position):
        mx = self.map_x + int(position[0] * self.scale_x)
        my = self.map_y + int(position[1] * self.scale_y)
        # Clamp to minimap bounds
        mx = max(self.map_x + 2, min(mx, self.map_x + self.map_w - 2))
        my = max(self.map_y + 2, min(my, self.map_y + self.map_h - 2))
        return (mx, my)

    def _draw_pitch(self, frame):
        x1, y1 = self.map_x, self.map_y
        x2, y2 = x1 + self.map_w, y1 + self.map_h

        # Field background
        draw_rounded_rect(frame, (x1, y1), (x2, y2),
                          PALETTE['minimap_field'], radius=6, alpha=0.8)

        # Border
        draw_rounded_rect(frame, (x1 - 1, y1 - 1), (x2 + 1, y2 + 1),
                          PALETTE['minimap_border'], radius=6, thickness=1)

        # Center line
        cx = x1 + self.map_w // 2
        cv2.line(frame, (cx, y1 + 6), (cx, y2 - 6),
                 PALETTE['minimap_lines'], 1, cv2.LINE_AA)

        # Center circle
        cv2.circle(frame, (cx, y1 + self.map_h // 2), 18,
                   PALETTE['minimap_lines'], 1, cv2.LINE_AA)

        # Label
        cv2.putText(frame, "RADAR", (x1 + 8, y2 - 8),
                    FONT, 0.35, PALETTE['text_secondary'], 1, cv2.LINE_AA)

    def draw(self, frame, tracks, frame_num):
        h, w = frame.shape[:2]
        self._set_position(w)
        self._draw_pitch(frame)

        # Draw players
        player_dict = tracks["players"][frame_num]
        for track_id, player in player_dict.items():
            pos = player.get('position_transformed')
            if pos is None:
                continue
            mp = self._world_to_minimap(pos)
            team_color = tuple(int(c) for c in player.get("team_color", (200, 200, 200)))
            cv2.circle(frame, mp, 4, team_color, cv2.FILLED, cv2.LINE_AA)
            cv2.circle(frame, mp, 4, (255, 255, 255), 1, cv2.LINE_AA)

            # Highlight player with ball
            if player.get('has_ball', False):
                cv2.circle(frame, mp, 7, PALETTE['possession'], 1, cv2.LINE_AA)

        # Draw ball
        ball_dict = tracks["ball"][frame_num]
        for _, ball in ball_dict.items():
            pos = ball.get('position_transformed')
            if pos is None:
                continue
            mp = self._world_to_minimap(pos)
            cv2.circle(frame, mp, 3, PALETTE['ball'], cv2.FILLED, cv2.LINE_AA)
