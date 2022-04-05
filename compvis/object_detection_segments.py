# OBJECT DETECTION

import cv2
import numpy as np
import pyrealsense2 as rs
from imutils.object_detection import non_max_suppression
import serial

ROBOT_WIDTH = 0.6  # meters
ROBOT_HEIGHT = 1  # meters
SAFE_DISTANCE = 3  # meters
CLIPPING_DISTANCE = 3  # meters

global PATH_OBSTRUCTED
global PERSON_IN_PATH


def main():
    PATH_OBSTRUCTED = False
    PERSON_IN_PATH = True

    # ser = serial.Serial('/dev/ttyACM0')  # open serial port

    video_feed = cv2.VideoCapture(0)
    img_width = int(video_feed.get(3))
    img_height = int(video_feed.get(4))
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    # videoWriter = cv2.VideoWriter("output.avi", fourcc=fourcc, fps=30.0, frameSize=(img_width, img_height))

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

            cv2.line(color_image, (212, 0), (212, 479), (0, 0, 255), 2)
            cv2.line(color_image, (425, 0), (425, 479), (0, 0, 255), 2)

            # get min distance on left side
            min_left = 9000     # meters
            min_center = 9000  # meters
            min_right = 9000  # meters

            min_left_coord = [1000, 1000]
            min_center_coord = [1000, 1000]
            min_right_coord = [1000, 1000]
            distance_left = SAFE_DISTANCE
            distance_center = SAFE_DISTANCE
            distance_right = SAFE_DISTANCE
            for row in range(479):
                for column in range(212):
                    distance_left = aligned_depth_frame.get_distance(column, row)
                    distance_center = aligned_depth_frame.get_distance(column + 213, row)
                    distance_right = aligned_depth_frame.get_distance(column + 426, row)

                    if distance_left < min_left:
                        min_left = distance_left
                        min_left_coord = [column, row]

                    if distance_center < min_center:
                        min_center = distance_center
                        min_center_coord = [column + 213, row]

                    if distance_right < min_right:
                        min_right = distance_right
                        min_right_coord = [column + 426, row]

            cv2.drawMarker(color_image, markerType=cv2.MARKER_CROSS, markerSize=40, thickness=2,
                           color=(0, 255, 255),
                           position=(min_left_coord[0], min_left_coord[1]))
            cv2.putText(color_image, fontScale=2, fontFace=cv2.FONT_HERSHEY_PLAIN,
                        org=(min_left_coord[0], min_left_coord[1]), color=(0, 255, 255), thickness=2,
                        text=f"({round(distance_left, 2)})")

            cv2.drawMarker(color_image, markerType=cv2.MARKER_CROSS, markerSize=40, thickness=2,
                           color=(0, 255, 255),
                           position=(min_center_coord[0], min_center_coord[1]))
            cv2.putText(color_image, fontScale=2, fontFace=cv2.FONT_HERSHEY_PLAIN,
                        org=(min_center_coord[0], min_center_coord[1]), color=(0, 255, 255), thickness=2,
                        text=f"({round(distance_center, 2)})")

            cv2.drawMarker(color_image, markerType=cv2.MARKER_CROSS, markerSize=40, thickness=2,
                           color=(0, 255, 255),
                           position=(min_right_coord[0], min_right_coord[1]))
            cv2.putText(color_image, fontScale=2, fontFace=cv2.FONT_HERSHEY_PLAIN,
                        org=(min_right_coord[0], min_right_coord[1]), color=(0, 255, 255), thickness=2,
                        text=f"({round(distance_right, 2)})")

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
                    cv2.rectangle(color_image, (xA, yA), (xB, yB), (0, 255, 0), 2)
            # ======================================================================================================

            # Render images:
            #   depth align to color on left
            #   depth on right
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # write to output
            # videoWriter.write(frame)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]),
                                                 interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))

            else:
                images = np.hstack((color_image, depth_colormap))

            cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Align Example', images)
            key = cv2.waitKey(1)
            # Press esc or 'q' to close the image window
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break
    finally:
        pipeline.stop()

    #ser.close()

    # videoWriter.release()


if __name__ == "__main__":
    main()

