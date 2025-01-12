# Gebaseerd https://github.com/CookieLover3000/lc-af-opencv-test/
# want ik heb niet die dure camera's thuis en had geen zin omdat andere script aan te passen

# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import os

ring_of_bout_array = []
schroef_of_spijker_array = []
isChild_array = []

def apply_laplacian_filter(img):
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    sharp = cv2.convertScaleAbs(laplacian)
    return sharp

def capture_image():
    img = cv2.imread('output_image.bmp')
    # img = cv2.imread('Image__2024-12-05__13-31-30.bmp')

    # imS = cv2.resize(img, ((int)(2592/3),
    #                            (int)(1944/3)))
    # cv2.namedWindow('camera', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('camera', img)    

    # Enhancement

    # open the image in a window
    imS = cv2.resize(img, ((int)(2592/3),
                               (int)(1944/3)))
    cv2.namedWindow('camera', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('camera', imS)
    gray = cv2.cvtColor(imS, cv2.COLOR_BGR2GRAY)
    cv2.imshow('grayscale', gray)
    blur = cv2.GaussianBlur(gray,(7,7),0)
    cv2.imshow('blur', blur)

        # Segmentation

    otsu_threshold, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,)
    cv2.imshow('threshold', thresh)
    dilate_kernel = np.ones((9, 9), np.uint8)
    erode_kernel = np.ones((3, 3), np.uint8)
    erosion = cv2.erode(thresh, erode_kernel, iterations=1)
    dilation = cv2.dilate(erosion, dilate_kernel, iterations=1)  # You can adjust the iterations for stronger dilation
    cv2.imshow('dilated', dilation)
    # Feature Extraction
    frame = np.zeros(dilation.shape, dtype=np.uint8)
    # contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(imS, contours, -1, (255,0,0), 1)
    # print(f"hierarchy: {hierarchy}")

    for i, h in enumerate(hierarchy[0]):
        if h[2] != -1:
           ring_of_bout_array.append(i)
        elif h[3] == -1 and h[2] == -1:
            schroef_of_spijker_array.append(i)
        else:
            isChild_array.append(i)



        # !!!!!! Didn´t work because it doesn´t work with objects that aren´t vertical or horizontal !!!!!!!!!!!!
        # Loop over contours and draw bounding boxes
        # for contour in contours:
        #     # Get the bounding box for each contour
        #     x, y, w, h = cv2.boundingRect(contour)
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 3)

    for i, contour in enumerate(contours):
        # Get the rotated bounding box for each contour using minAreaRect
        rect = cv2.minAreaRect(contour)
        # Get the box points (vertices of the rotated rectangle)
        box = cv2.boxPoints(rect)
        # Convert the box points to integers
        box = np.int_(box)

        side1 = np.linalg.norm(box[0] - box[1])
        side2 = np.linalg.norm(box[1] - box[2])
        # print(f"box: {box}")
        # Draw the rotated bounding box (rectangle) using polylines
        cv2.drawContours(imS, [box], 0, (0,255,0), 3)

        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(imS, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if side1 > side2:
            aspect_ratio = side2 / side1
        else:
            aspect_ratio = side1 / side2
        print(f"aspect ratio {i}: {aspect_ratio}")

        # Put the width and height text above the bounding box
        text = None
        if i in ring_of_bout_array:
            text = f"ring of bout: {i}"
            area = cv2.contourArea(contour)
            print(f"Contour {i} area: {area}")
        elif i in schroef_of_spijker_array:
            text = f"schroef of spijker: {i}"
        cv2.putText(imS, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # if i in isChild_array:
        #     area = cv2.contourArea(contour)
        #     print(f"Contour {i} area: {area}")

        # Print hierarchy information
        # print(f"Contour {i} hierarchy: {hierarchy[0][i]}")



    # Display the image with bounding boxes
    cv2.imshow('Bounding Boxes', imS)




    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def id_ring_or_moer(childNr):
    if(childNr == -1):
        return
    

    


capture_image()