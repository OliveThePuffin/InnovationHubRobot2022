#!/bin/python3.9

# OBJECT DETECTION

import cv2
import numpy as np
import pyrealsense2 as rs


def get_height_meters(y, depth, fy, cy):
    y_w = -((y - cy) * depth) / fy
    return y_w


def reset_camera():
    ctx = rs.context()
    devices = ctx.query_devices()
    for dev in devices:
        dev.hardware_reset()


def initialize_pipeline():

    pipeline = rs.pipeline()

    # Create a config and configure the pipeline to stream
    # different resolutions of color and depth streams
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Start streaming
    pipeline.start(config)

    # camera properties:
    profile = pipeline.get_active_profile()
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    intrinsics = depth_profile.get_intrinsics()
    cy = intrinsics.ppy
    fy = intrinsics.fy

    return pipeline, config, profile


def get_depths(pipeline, config, profile):
    ROBOT_HEIGHT = 2  # meters
    SAFE_DISTANCE = 3  # meters

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    # get camera image
    try:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()

        # Get aligned frames
        depth_frame = frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image

        depth_image = np.asanyarray(depth_frame.get_data())
        depth_image = depth_scale * depth_image
        np.delete(depth_image, 639, 1)

        # this is used to eliminate noise in depth image, sometimes camera reports random spots that are 0 meters away
        # this throws out points less than 0.08 meters (about 3 in) and replaces them with SAFE_DISTANCE
        depth_image = np.where(depth_image < 0.02, SAFE_DISTANCE, depth_image)

        # split depth image into three columns
        right_segment, center_segment, left_segment = np.split(depth_image, 3, 0)

        # get min distances in each column
        distance_left = np.amin(left_segment)
        distance_center = np.amin(center_segment)
        distance_right = np.amin(right_segment)

        if distance_left > SAFE_DISTANCE:
            distance_left = SAFE_DISTANCE
        if distance_center > SAFE_DISTANCE:
            distance_center = SAFE_DISTANCE
        if distance_right > SAFE_DISTANCE:
            distance_right = SAFE_DISTANCE

    except Exception as e:
        # if there is an error, report all distances as zero so that the robot stops
        distance_left = 0
        distance_center = 0
        distance_right = 0

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
        depth_image_3d = np.dstack(
            (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
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