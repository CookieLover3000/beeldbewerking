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
schroef_spijker_aspect_ratios = {}

def apply_laplacian_filter(img):
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    sharp = cv2.convertScaleAbs(laplacian)
    return sharp

def capture_image():
    # img = cv2.imread('output_image.bmp')
    # img = cv2.imread('Image__2024-12-05__13-31-30.bmp')
    img = cv2.imread('image.png')

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

    # Pattern recognition 1

    for i, h in enumerate(hierarchy[0]):
        if h[3] != -1:
           ring_of_bout_array.append(i)
        elif h[3] == -1 and h[2] == -1:
            schroef_of_spijker_array.append(i)
        # else:
        #     isChild_array.append(i)

    # end Pattern recongition 1, continue with Feature extraction

    spijkerAmount = 0
    schroefAmount = 0
    ringAmount = 0
    boutAmount = 0

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
        # cv2.rectangle(imS, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if side1 > side2:
            aspect_ratio = side2 / side1
        else:
            aspect_ratio = side1 / side2
        print(f"aspect ratio {i}: {aspect_ratio}")

        # Pattern Recognition

        text = None
        if i in ring_of_bout_array:
            area = cv2.contourArea(contour)
            if area > 4000:
                text = f"ring: {i}"
                ringAmount += 1
            elif area > 2000:
                text = f"bout: {i}"
                boutAmount += 1

            print(f"Contour {i} area: {area}")

        # Detect schroef en spijker
        elif i in schroef_of_spijker_array:
            # Spijker
            if aspect_ratio < 0.1:
                spijkerAmount += 1
                text = f"spijker: {i}"    
            # Schroef
            elif aspect_ratio < 0.4:
                schroefAmount += 1
                text = f"schroef: {i}"

        # Display text in center of rectangle around item.
        center_x = x + w // 2
        center_y = y + h // 2

        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

        text_x = center_x - text_width // 2
        text_y = center_y + text_height // 2

        cv2.putText(imS, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 0, 255), 2, cv2.LINE_AA)

    # Display the image with bounding boxes
    cv2.imshow('Bounding Boxes', imS)

    print(f"spijker amount: {spijkerAmount}")
    print(f"schroef amount: {schroefAmount}")
    print(f"bout amount: {boutAmount}")
    print(f"ring amount: {ringAmount}")


    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

    


capture_image()