import cv2
import numpy as np

DIFF_THRESHOLD = 120000  # number of pixels
DELAY_SEC = 0.5
FRAME_WIDTH = 576
FRAME_HEIGHT = 324


def get_diff_times(path):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)  # reduce resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)  # reduce resolution for better performance

    times = []
    last_diff_time = 0

    if cap.isOpened():
        prev_ret, prev_frame = cap.read()
    else:
        return times

    while cap.isOpened():
        curr_ret, curr_frame = cap.read()

        if not prev_ret or not curr_ret:
            break

        prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_frame_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        diff_count = np.count_nonzero(prev_frame_gray - curr_frame_gray)

        frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Current position of the video file in seconds
        if diff_count >= DIFF_THRESHOLD and frame_time - last_diff_time >= DELAY_SEC:
            times.append(frame_time)
            last_diff_time = frame_time

        prev_ret, prev_frame = cap.read()

    return times
