import logging
import time
import os
from utils import read_video, save_video
from trackers import Tracker
import cv2
import numpy as np
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
from xg_estimator import XGEstimator
from pressing_estimator import PressingEstimator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

INPUT_VIDEO = 'input_videos/08fd33_3.mp4'


def get_stub_path(video_path, stub_name):
    """Generate a video-specific stub path, e.g. stubs/4_track_stubs.pkl"""
    video_stem = os.path.splitext(os.path.basename(video_path))[0]
    return f'stubs/{video_stem}_{stub_name}.pkl'



def main():
    pipeline_start = time.time()

    # Read Video
    logger.info("Reading video...", )
    t = time.time()
    video_frames = read_video(INPUT_VIDEO)
    logger.info(f"Video read: {len(video_frames)} frames ({time.time()-t:.1f}s)")

    # Initialize Tracker
    logger.info("Running object tracking...")
    t = time.time()
    tracker = Tracker('models/best.pt')
    tracks = tracker.get_object_tracks(video_frames,
                                       read_from_stub=True,
                                       stub_path=get_stub_path(INPUT_VIDEO, 'track_stubs'))
    tracker.add_position_to_tracks(tracks)
    logger.info(f"Tracking done ({time.time()-t:.1f}s)")

    # Camera movement estimator
    logger.info("Estimating camera movement...")
    t = time.time()
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,
                                                                                read_from_stub=True,
                                                                                stub_path=get_stub_path(INPUT_VIDEO, 'camera_movement'))
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks,camera_movement_per_frame)
    logger.info(f"Camera movement done ({time.time()-t:.1f}s)")

    # View Transformer
    logger.info("Applying view transform...")
    t = time.time()
    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)
    logger.info(f"View transform done ({time.time()-t:.1f}s)")

    # Interpolate Ball Positions
    logger.info("Interpolating ball positions...")
    t = time.time()
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    logger.info(f"Ball interpolation done ({time.time()-t:.1f}s)")

    # Speed and distance estimator
    logger.info("Calculating speed and distance...")
    t = time.time()
    speed_and_distance_estimator = SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)
    logger.info(f"Speed/distance done ({time.time()-t:.1f}s)")

    # xG Estimator
    logger.info("Calculating xG...")
    t = time.time()
    xg_estimator = XGEstimator()
    xg_estimator.add_xg_to_tracks(tracks)
    logger.info(f"xG done ({time.time()-t:.1f}s)")

    # Assign Player Teams
    logger.info("Assigning player teams...")
    t = time.time()
    team_assigner = TeamAssigner()
    # Find first frame with player detections for color calibration
    init_frame_idx = 0
    for i, player_track in enumerate(tracks['players']):
        if len(player_track) > 0:
            init_frame_idx = i
            break
    team_assigner.assign_team_color(video_frames[init_frame_idx],
                                    tracks['players'][init_frame_idx])

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],
                                                 track['bbox'],
                                                 player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
    logger.info(f"Team assignment done ({time.time()-t:.1f}s)")

    # Assign Ball Acquisition
    logger.info("Assigning ball possession...")
    t = time.time()
    player_assigner =PlayerBallAssigner()
    team_ball_control= []
    for frame_num, player_track in enumerate(tracks['players']):
        ball_bbox = tracks['ball'][frame_num][1]['bbox']
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)

        if assigned_player != -1:
            tracks['players'][frame_num][assigned_player]['has_ball'] = True
            team_ball_control.append(tracks['players'][frame_num][assigned_player]['team'])
        else:
            team_ball_control.append(team_ball_control[-1] if team_ball_control else 1)
    team_ball_control= np.array(team_ball_control)
    logger.info(f"Ball possession done ({time.time()-t:.1f}s)")

    # Draw output
    logger.info("Drawing annotations...")
    t = time.time()
    pressing_estimator = PressingEstimator()
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control,
                                                    camera_movement_per_frame,
                                                    pressing_estimator=pressing_estimator)
    logger.info(f"Drawing done ({time.time()-t:.1f}s)")

    # Save video
    logger.info("Saving video...")
    t = time.time()
    save_video(output_video_frames, 'output_videos/output_video.avi')
    logger.info(f"Video saved ({time.time()-t:.1f}s)")

    logger.info(f"Pipeline complete! Total time: {time.time()-pipeline_start:.1f}s")

if __name__ == '__main__':
    main()