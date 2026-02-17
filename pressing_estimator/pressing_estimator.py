import math


class PressingEstimator:
    # Thresholds in real-world meters
    HIGH_THRESHOLD = 8
    MEDIUM_THRESHOLD = 15

    # Fallback thresholds in pixels (when transformed positions unavailable)
    HIGH_THRESHOLD_PX = 150
    MEDIUM_THRESHOLD_PX = 300

    def calculate_pressing(self, tracks, frame_num, ball_holder_team):
        """Calculate pressing intensity of the defending team for a given frame.

        Returns (label, avg_distance, unit) where label is "HIGH", "MED", or "LOW",
        avg_distance is the mean distance of defending players to the ball,
        and unit is "m" or "px".
        Returns (None, None, None) if data is insufficient.
        """
        if ball_holder_team is None:
            return None, None, None

        ball_data = tracks['ball'][frame_num].get(1, {})
        ball_pos = ball_data.get('position_transformed')
        use_transformed = ball_pos is not None
        pos_key = 'position_transformed' if use_transformed else 'position_adjusted'

        if not use_transformed:
            ball_pos = ball_data.get(pos_key)
        if ball_pos is None:
            return None, None, None

        bx, by = ball_pos
        distances = []

        for track_id, player in tracks['players'][frame_num].items():
            team = player.get('team')
            if team is None or team == ball_holder_team:
                continue
            pos = player.get(pos_key)
            if pos is None:
                continue
            dx = pos[0] - bx
            dy = pos[1] - by
            distances.append(math.sqrt(dx * dx + dy * dy))

        if not distances:
            return None, None, None

        avg_distance = sum(distances) / len(distances)

        if use_transformed:
            high_t, med_t, unit = self.HIGH_THRESHOLD, self.MEDIUM_THRESHOLD, "m"
        else:
            high_t, med_t, unit = self.HIGH_THRESHOLD_PX, self.MEDIUM_THRESHOLD_PX, "px"

        if avg_distance < high_t:
            label = "HIGH"
        elif avg_distance < med_t:
            label = "MED"
        else:
            label = "LOW"

        return label, avg_distance, unit
