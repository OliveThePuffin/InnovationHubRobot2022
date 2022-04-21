#!/bin/python3.9

# OBJECT DETECTION

import cv2
import numpy as np
import pyrealsense2 as rs
import time


def get_height_meters(y, depth, fy, cy):
    y_w = -((y - cy) * depth) / fy
    return y_w

def reset_camera():
    ctx = rs.context()
    devices = ctx.query_devices()
    for dev in devices:
        dev.hardware_reset()

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
    depth_scale = depth_sensor.get_depth_scale()

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
        depth_image = depth_scale * depth_image
        np.delete(depth_image, 639, 1)
        color_image = np.asanyarray(color_frame.get_data())
        
        left_segment, center_segment, right_segment = np.split(depth_image, 3, 0)

        # get min distance on left side
        min_left = SAFE_DISTANCE     # meters
        min_center = SAFE_DISTANCE  # meters
        min_right = SAFE_DISTANCE  # meters

        distance_left = SAFE_DISTANCE
        distance_center = SAFE_DISTANCE
        distance_right = SAFE_DISTANCE
        start = time.time()
        distance_left = np.amin(left_segment)
        distance_center = np.amin(center_segment)
        distance_right = np.amin(right_segment)
        """for row in range(479):
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
        """
        end = time.time()
        print(end - start)
    except Exception as e:
        print(e)

    finally:
        pipeline.stop()
    return distance_left, distance_center, distance_right


def detect_person():

    person_exists = False
    SAFE_DISTANCE = 3  # meters
    CLIPPING_DISTANCE = 3  # meters

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
    depth_scale = depth_sensor.get_depth_scale()

    # We will be removing the background of objects more than clipping_distance_in_meters meters away
    clipping_distance = CLIPPING_DISTANCE / depth_scale

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
        
        # remove background
        grey_color = 0
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

        # PEDESTRIAN TRACKING WITH HOG FILTER
        # ======================================================================================================
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        boxes, weights = hog.detectMultiScale(bg_removed, winStride=(8, 8), padding=(8, 8), scale=1.05)
        npboxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
        if np.size(npboxes) != 0:
            person_exists = True
        # ======================================================================================================

    finally:
        pipeline.stop()

    return person_exists
