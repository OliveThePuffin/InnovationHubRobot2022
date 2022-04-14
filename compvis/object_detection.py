#!/bin/python3.9

# OBJECT DETECTION

import cv2
import numpy as np
import pyrealsense2 as rs
from imutils.object_detection import non_max_suppression


def get_height_meters(y, depth, fy, cy):
    y_w = -((y - cy) * depth) / fy
    return y_w


def get_depths():

    ROBOT_HEIGHT = 2  # meters
    SAFE_DISTANCE = 3  # meters

    pipeline = rs.pipeline()

    # Create a config and configure the pipeline to stream
    # different resolutions of color and depth streams
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    profile = pipeline.start(config)

    # camera properties:
    profile = pipeline.get_active_profile()
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    intrinsics = depth_profile.get_intrinsics()
    cy = intrinsics.ppy
    fy = intrinsics.fy

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)

    # get camera image
    try:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        cv2.line(color_image, (212, 0), (212, 479), (0, 0, 255), 2)
        cv2.line(color_image, (425, 0), (425, 479), (0, 0, 255), 2)

        # get min distance on left side
        min_left = SAFE_DISTANCE     # meters
        min_center = SAFE_DISTANCE  # meters
        min_right = SAFE_DISTANCE  # meters

        distance_left = SAFE_DISTANCE
        distance_center = SAFE_DISTANCE
        distance_right = SAFE_DISTANCE
        for row in range(479):
            for column in range(212):
                distance_left = aligned_depth_frame.get_distance(column, row)
                distance_center = aligned_depth_frame.get_distance(column + 213, row)
                distance_right = aligned_depth_frame.get_distance(column + 426, row)

                height_left = get_height_meters(row, distance_left, fy, cy)
                height_center = get_height_meters(row, distance_center, fy, cy)
                height_right = get_height_meters(row, distance_right, fy, cy)

                if min_left > distance_left > 0.1 and height_left < ROBOT_HEIGHT:
                    min_left = distance_left

                if min_center > distance_center > 0.1 and height_center < ROBOT_HEIGHT:
                    min_center = distance_center

                if min_right > distance_right > 0.1 and height_right < ROBOT_HEIGHT:
                    min_right = distance_right

    finally:
        pipeline.stop()

    return distance_left, distance_center, distance_right


def detect_person():

    person_exists = False
    SAFE_DISTANCE = 3  # meters

    pipeline = rs.pipeline()

    # Create a config and configure the pipeline to stream
    # different resolutions of color and depth streams
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    profile = pipeline.start(config)

    # camera properties:
    profile = pipeline.get_active_profile()

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)

    # get camera image
    try:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        cv2.line(color_image, (212, 0), (212, 479), (0, 0, 255), 2)
        cv2.line(color_image, (425, 0), (425, 479), (0, 0, 255), 2)

        # PEDESTRIAN TRACKING WITH HOG FILTER
        # ======================================================================================================
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        boxes, weights = hog.detectMultiScale(color_image, winStride=(8, 8), padding=(8, 8), scale=1.05)
        npboxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
        pick = non_max_suppression(npboxes, probs=None, overlapThresh=0.65)
        for (xA, yA, xB, yB) in pick:
            person_center = np.array([[((xA + xB) / 2)], [((yA + yB) / 2)]])
            depth_center = aligned_depth_frame.get_distance(person_center[0], person_center[1])
            if depth_center < SAFE_DISTANCE:
                person_exists = True
        # ======================================================================================================

    finally:
        pipeline.stop()

    return person_exists
