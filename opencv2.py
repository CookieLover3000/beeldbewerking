# Gebaseerd https://github.com/CookieLover3000/lc-af-opencv-test/
# want ik heb niet die dure camera's thuis en had geen zin omdat andere script aan te passen

# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import os

def apply_laplacian_filter(img):
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    sharp = cv2.convertScaleAbs(laplacian)
    return sharp

def capture_image():
    img = cv2.imread('ijzer.png')

    while True:

        kernel = np.array([[-1, -1, -1], 
                           [-1,  8, -1], 
                           [-1, -1, -1]])
        

        sharp_img = apply_laplacian_filter(img)
        blur = cv2.GaussianBlur(img,(23,23),0)
        img2 = cv2.filter2D(img, -1, kernel)
        canny = cv2.Canny(sharp_img, 100, 200)
        # Display the frame
        cv2.imshow("image", img)
        cv2.imshow('sharp image', sharp_img)
        cv2.imshow("modified image", canny)

        # Wait 1 ms for a scherptepress, stop if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the camera and windows because we're done.
    cap.release()
    cv2.destroyAllWindows()



def resizeFrame(frame, frameSize):
    # Calculate the size of the center that is used to apply the filter to
    # if imageSize = 100 then an area of 100x100 pixels is used to apply the filter.
    frameSize = frameSize // 2
    # Get the dimensions of the image
    height, width = frame.shape[:2]

    # Calculate the coordinates for the center of the image
    centerX, centerY = width // 2, height // 2

    # Define the top-left corner of the 100x100 region
    startX = max(centerX - frameSize, 0)
    startY = max(centerY - frameSize, 0)

    # Define the bottom-right corner of the 100x100 region
    endX = min(centerX + frameSize, width)
    endY = min(centerY + frameSize, height)

    # Crop the image to the 100x100 region
    return frame[startY:endY, startX:endX]


capture_image()