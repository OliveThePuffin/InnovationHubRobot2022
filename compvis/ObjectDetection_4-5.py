# Julian Reynolds
# CSCI 507
# Homework 4

import math
import numpy as np
import cv2


def main():
    # read in video
    video_cap = cv2.VideoCapture("input_vid.avi")

    # set up video output
    width = int(video_cap.get(3))
    height = int(video_cap.get(4))
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    videoWriter = cv2.VideoWriter("output.avi", fourcc=fourcc, fps=30.0, frameSize=(width, height))

    # camera properties:
    fx = 675
    fy = 675
    cx = 320
    cy = 240
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    # ArUco tag properties
    MARKER_LENGTH = 2

    # create ArUco tag dictionary
    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)

    # VIDEO LOOP
    # =================================================================================================================
    while True:
        got_image, bgr_image = video_cap.read()
        if not got_image:
            break  # End of video; exit the while loop

        # convert to grayscale
        grayscale = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        # histogram equalizing on grayscale image, this will help find ArUco tags later
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        grayscale = clahe.apply(grayscale)

        # create binary image
        output_thresh, binary_image = cv2.threshold(grayscale, 0, 255, cv2.THRESH_OTSU)

        # find tags, mark them
        corners, ids, _ = cv2.aruco.detectMarkers(image=binary_image, dictionary=arucoDict)
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(image=bgr_image, corners=corners, ids=ids, borderColor=(0, 0, 255))

            dist_coeff = None
            aruco_rvecs, aruco_tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners=corners,
                                                                              markerLength=MARKER_LENGTH,
                                                                              cameraMatrix=K.astype("float32"),
                                                                              distCoeffs=dist_coeff)
            # get translation and rotation vectors of tags
            aruco_rvec = aruco_rvecs[0]
            aruco_tvec = aruco_tvecs[0]
            aruco_rmat = cv2.Rodrigues(aruco_rvec)[0]

            # draw pose of tags
            cv2.aruco.drawAxis(image=bgr_image, cameraMatrix=K.astype("float32"), distCoeffs=dist_coeff,
                               rvec=aruco_rvec, tvec=aruco_tvec, length=MARKER_LENGTH)

            pyramid_coord = np.array([[-0.7, -0.7, -2.6], [0.7, -0.7, -2.6], [0.7, 0.7, -2.6],
                                      [-0.7, 0.7, -2.6], [0, 0, 0]])

            if ids[0] == 1:  # if ID 1 is showing, use these coordinates for power switch location
                switch_loc = np.array([[-2.5, -2.0, -5.0]])
                theta_z_pyramid = math.radians(90)
            elif ids[0] == 0:  # if ID 0 is showing, use these coordinates
                switch_loc = np.array([[2.5, -2.0, -1.0]])
                theta_z_pyramid = -math.radians(90)
            else:
                continue
            # find sines and cosines for rotation matrix of pyramid
            sz = math.sin(theta_z_pyramid)
            cz = math.cos(theta_z_pyramid)
            R_pyramid = np.array([[cz, 0, sz], [0, 1, 0], [-sz, 0, cz]])

            # pyramid coordinates to tag coordinates
            H_p_t = np.block([[R_pyramid, switch_loc.T], [0, 0, 0, 1]])

            # tag coordinates to camera coordinates
            H_t_c = np.block([[aruco_rmat, aruco_tvec.T], [0, 0, 0, 1]])

            # pyramid to camera transform
            H_p_c = H_t_c @ H_p_t
            Mext = H_p_c[0:3, :]

            # create matrix to store points of pyramid, this will be used to draw the lines later
            points = np.empty(shape=(5, 2))
            point_count = 0
            for i in pyramid_coord:
                P_w = np.append(i, [1])
                p = K @ Mext @ P_w
                p = p/p[2]
                # store points to use to draw lines for pyramid
                points[point_count, 0] = p[0]
                points[point_count, 1] = p[1]
                point_count += 1

            for i in points:
                cv2.line(bgr_image, pt1=(int(i[0]), int(i[1])), pt2=(int(points[4, 0]), int(points[4, 1])),
                         color=(0, 0, 255), thickness=2)

            point_count = 0
            for i in range(4):
                cv2.line(bgr_image, pt1=(int(points[point_count, 0]), int(points[point_count, 1])),
                         pt2=(int(points[point_count + 1, 0]), int(points[point_count + 1, 1])), color=(0, 0, 255),
                         thickness=2)
                point_count += 1

            cv2.line(bgr_image, pt1=(int(points[0, 0]), int(points[0, 1])),
                     pt2=(int(points[3, 0]), int(points[3, 1])), color=(0, 0, 255), thickness=2)

        # write to output
        videoWriter.write(bgr_image)

        # show frame
        cv2.imshow("ArUco Tracking", bgr_image)
        cv2.waitKey(30)

    # =================================================================================================================

    videoWriter.release()


if __name__ == "__main__":
    main()
