# OBJECT DETECTION

import cv2
import numpy as np
import pyrealsense2 as rs
from imutils.object_detection import non_max_suppression
import serial

ROBOT_WIDTH = 0.6  # meters
ROBOT_HEIGHT = 1  # meters
SAFE_DISTANCE = 1.5  # meters
CLIPPING_DISTANCE = 3  # meters

global PATH_OBSTRUCTED
global PERSON_IN_PATH


def get_bounding_box_meters(depth_at_center, top_left_x, top_left_y, bottom_right_x, bottom_right_y, center_x, center_y,
                            fx, fy, cx, cy):
    # transform of camera coordinates to world coordinates
    # CENTER COORDINATE IN METERS
    x_w_center = ((center_x - cx) * depth_at_center) / fx
    y_w_center = -((center_y - cy) * depth_at_center) / fy

    # TOP LEFT COORDINATE IN METERS
    x_w_top_left = ((top_left_x - cx) * depth_at_center) / fx
    y_w_top_left = -((top_left_y - cy) * depth_at_center) / fy

    # BOTTOM RIGHT
    x_w_bottom_right = ((bottom_right_x - cx) * depth_at_center) / fx
    y_w_bottom_right = -((bottom_right_y - cy) * depth_at_center) / fy

    # TOP RIGHT
    x_w_top_right = x_w_bottom_right
    y_w_top_right = y_w_top_left

    # BOTTOM LEFT
    x_w_bottom_left = x_w_top_left
    y_w_bottom_left = y_w_bottom_right

    bounding_box_world = np.array([[x_w_center, y_w_center],
                                   [x_w_top_left, y_w_top_left],
                                   [x_w_top_right, y_w_top_right],
                                   [x_w_bottom_left, y_w_bottom_left],
                                   [x_w_bottom_right, y_w_bottom_right]], dtype="long")

    return bounding_box_world


def check_for_obstruction(x, y, z):
    if (x > ROBOT_WIDTH / 2 or x < -ROBOT_WIDTH / 2) or y > ROBOT_HEIGHT or z > SAFE_DISTANCE:  # safe area
        return False
    else:
        return True


def main():
    PATH_OBSTRUCTED = False
    PERSON_IN_PATH = True

    ser = serial.Serial('/dev/ttyACM0')  # open serial port

    video_feed = cv2.VideoCapture(0)
    img_width = int(video_feed.get(3))
    img_height = int(video_feed.get(4))
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    videoWriter = cv2.VideoWriter("output.avi", fourcc=fourcc, fps=30.0, frameSize=(img_width, img_height))

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
    cx = intrinsics.ppx
    cy = intrinsics.ppy
    fx = intrinsics.fx
    fy = intrinsics.fy

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

    # Streaming loop
    try:
        while True:
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image

            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()

            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Remove background - Set pixels further than clipping_distance to grey
            grey_color = 0
            depth_image_3d = np.dstack(
                (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
            bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
            grayscale = cv2.cvtColor(bg_removed, cv2.COLOR_BGR2GRAY)
            _, binary_img = cv2.threshold(grayscale, thresh=1, maxval=255, type=cv2.THRESH_BINARY)

            # create box filter kernels for closing and opening
            kernel_close = np.ones((10, 10), np.uint8)
            kernel_open = np.ones((5, 5), np.uint8)

            # closing
            binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel_close)
            # opening
            binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel_open)

            cv2.imshow("Binary Image", binary_img)

            # get connected components
            nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(binary_img, connectivity=8)
            if centroids is not None:  # if at least one object is found

                # PEDESTRIAN TRACKING WITH HOG FILTER
                # ======================================================================================================
                hog = cv2.HOGDescriptor()
                hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

                boxes, weights = hog.detectMultiScale(color_image, winStride=(4, 4), padding=(8, 8), scale=1.05)
                npboxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
                pick = non_max_suppression(npboxes, probs=None, overlapThresh=0.65)
                for (xA, yA, xB, yB) in pick:
                    person_center = np.array([[((xA + xB) / 2)], [((yA + yB) / 2)]])
                    depth_center = aligned_depth_frame.get_distance(person_center[0], person_center[1])
                    if depth_center < CLIPPING_DISTANCE:
                        # print(f"Person Detected: ({round((xA + xB) / 2)}, {round((yA + yB) / 2)})")
                        cv2.rectangle(bg_removed, (xA, yA), (xB, yB), (0, 255, 0), 2)

                        person_bounding_box = get_bounding_box_meters(depth_center, xA, yA, xB, yB,
                                                                      person_center[0], person_center[1],
                                                                      fx, fy, cx, cy)
                        person_center_meters = person_bounding_box[0]
                        person_bottom_left_meters = person_bounding_box[3]
                        person_bottom_right_meters = person_bounding_box[4]

                        if check_for_obstruction(person_center_meters[0], person_center_meters[1], depth_center):
                            PERSON_IN_PATH = True
                        elif check_for_obstruction(person_bottom_left_meters[0], person_bottom_left_meters[1],
                                                   depth_center):
                            PERSON_IN_PATH = True
                        elif check_for_obstruction(person_bottom_right_meters[0], person_bottom_right_meters[1],
                                                   depth_center):
                            PERSON_IN_PATH = True
                        else:
                            PERSON_IN_PATH = False
                # ======================================================================================================

                for detected_object in range(nb_components):

                    # draw bounding  boxes:
                    left_edge = stats[detected_object, cv2.CC_STAT_LEFT]
                    top_edge = stats[detected_object, cv2.CC_STAT_TOP]
                    box_height = stats[detected_object, cv2.CC_STAT_HEIGHT]
                    box_width = stats[detected_object, cv2.CC_STAT_WIDTH]

                    cv2.rectangle(bg_removed, color=(0, 0, 255), pt1=(left_edge, top_edge),
                                  pt2=(left_edge + box_width, top_edge + box_height))

                    center = centroids[detected_object]

                    x = round(center[0])
                    y = round(center[1])
                    distance = aligned_depth_frame.get_distance(x, y)

                    if distance < CLIPPING_DISTANCE:

                        # transform of camera coordinates to world coordinates
                        x_w = ((x - cx) * distance)/fx
                        y_w = -((y - cy) * distance)/fy

                        if (x_w > ROBOT_WIDTH/2 or x_w < -ROBOT_WIDTH/2) or y_w > ROBOT_HEIGHT \
                                or distance > SAFE_DISTANCE:  # safe area
                            marker_color = (0, 255, 0)
                        else:
                            PATH_OBSTRUCTED = True
                            marker_color = (0, 0, 255)
                        cv2.drawMarker(bg_removed, markerType=cv2.MARKER_CROSS, markerSize=40, thickness=2,
                                       color=marker_color,
                                       position=(x, y))
                        cv2.putText(bg_removed, fontScale=2, fontFace=cv2.FONT_HERSHEY_PLAIN,
                                    org=(x, y), color=marker_color, thickness=2,
                                    text=f"({round(x_w, 2)}, {round(y_w, 2)}, {round(distance, 2)})")

                        if PERSON_IN_PATH:
                            PATH_OBSTRUCTED = True
                        # if PATH_OBSTRUCTED:
                            # print(f"Object Detected, Centered at: ({x_w}, {y_w}, {distance}) meters")

            # Render images:
            #   depth align to color on left
            #   depth on right
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # write to output
            # videoWriter.write(frame)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = bg_removed.shape

            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(bg_removed, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]),
                                                 interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))

            else:
                images = np.hstack((bg_removed, depth_colormap))

            if PATH_OBSTRUCTED:
                print("Object in path")
                ser.write(b'Object_obstructed')
            else:
                ser.write(b'Clear_path')

            cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Align Example', images)
            key = cv2.waitKey(1)
            # Press esc or 'q' to close the image window
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    finally:
        pipeline.stop()

    ser.close()

    # videoWriter.release()


if __name__ == "__main__":
    main()

