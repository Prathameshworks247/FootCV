import math


class XGEstimator:
    def __init__(self, goal_x=0, goal_center_y=34, goal_width=7.32):
        self.goal_x = goal_x
        self.goal_center_y = goal_center_y
        self.goal_width = goal_width
        self.post1_y = goal_center_y - goal_width / 2
        self.post2_y = goal_center_y + goal_width / 2

    def calculate_xg(self, x, y):
        """Calculate expected goals from a position using distance and angle to goal."""
        dx = abs(x - self.goal_x)
        dy = y - self.goal_center_y
        distance = math.sqrt(dx * dx + dy * dy)

        # Angle subtended by goal posts from the player's position
        angle1 = math.atan2(abs(x - self.goal_x), abs(y - self.post1_y))
        angle2 = math.atan2(abs(x - self.goal_x), abs(y - self.post2_y))
        angle = abs(angle1 - angle2)

        # Logistic model coefficients (calibrated from xG research)
        # Higher distance -> lower xG, higher angle -> higher xG
        b0 = 1.0
        b_distance = -0.15
        b_angle = 3.0
        log_odds = b0 + b_distance * distance + b_angle * angle
        xg = 1.0 / (1.0 + math.exp(-log_odds))

        return max(0.0, min(1.0, xg))

    def add_xg_to_tracks(self, tracks):
        """Add xG values to all player tracks with valid transformed positions."""
        for object_type, object_tracks in tracks.items():
            if object_type != "players":
                continue
            for frame_num, frame_tracks in enumerate(object_tracks):
                for track_id, track_info in frame_tracks.items():
                    position = track_info.get('position_transformed')
                    if position is None:
                        continue
                    x, y = position
                    xg = self.calculate_xg(x, y)
                    tracks[object_type][frame_num][track_id]['xg'] = xg
