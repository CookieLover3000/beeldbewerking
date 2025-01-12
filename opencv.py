'''
A simple Program for grabbing video from basler camera and converting it to opencv img.
Uitleg Gert: 
Gebruik de Pylon Viewer om namen van parameters op te zoeken.
Voor python is er geen directe API. Hier staan de sources: https://github.com/basler/pypylon
Zorg dat je in Baslerweb deze camera ingesteld hebt: https://docs.baslerweb.com/pua2500-14uc
Dan kun je een poging doen om te zoeken in de C++ API: https://docs.baslerweb.com/pylonapi/

'''

from pypylon import pylon # type: ignore
import cv2 # type: ignore
import time
import numpy as np

ring_of_bout_array = []
schroef_of_spijker_array = []

shouldSaveImage = False

# Print version string
print ("OpenCV version :  {0}".format(cv2.__version__))

# connecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

#set the dimensions of the image to grab
camera.Open()
camera.Width.Value = 2592  # max width of Basler puA2500-14uc camera
camera.Height.Value = 1944 # max height of Basler puA2500-14uc camera


# camera.OffsetX.Value = 518
camera.AcquisitionFrameRate.SetValue(10) # 10 beelden per seconde

# set features of camera
camera.ExposureTime.Value = 20000
camera.ExposureAuto.SetValue('Off')
camera.BalanceWhiteAuto.SetValue('Continuous')
camera.LightSourcePreset.SetValue('Daylight6500K')
camera.GainAuto.SetValue('Off')
camera.GainRaw.Value = 127
camera.GammaRaw.Value = 2000
camera.PixelFormat = "RGB8"
# pylon.FeaturePersistence.Save("test.txt", camera.GetNodeMap())

print("Using device: ", camera.GetDeviceInfo().GetModelName())
print("width set: ",camera.Width.Value)
print("Height set: ",camera.Height.Value)

# The parameter MaxNumBuffer can be used to control the count of buffers
# allocated for grabbing. The default value of this parameter is 10.
camera.MaxNumBuffer = 5

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

savingImage = False

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()

        if(savingImage == False and shouldSaveImage == True):
            cv2.imwrite('output_image.bmp', img)
            savingImage = True

        # do some image processing
        # img = cv2.GaussianBlur(img, (65,65), 0)
        
        # Enhancement

        # open the image in a window
        imS = cv2.resize(img, ((int)(camera.Width.Value/3),
                               (int)(camera.Height.Value/3)))
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
        dilation = cv2.dilate(erosion, dilate_kernel, iterations=3)  # You can adjust the iterations for stronger dilation
        cv2.imshow('dilated', dilation)

        # Feature Extraction

        frame = np.zeros(dilation.shape, dtype=np.uint8)
        # contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(imS, contours, -1, (255,0,0), 1)


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

        ring_of_bout_array = []
        schroef_of_spijker_array = []


        # press esc (ascii 27) to exit
        k = cv2.waitKey(1)
        if k == 27:
            break
    grabResult.Release()

# Releasing the resource
camera.StopGrabbing()
cv2.destroyAllWindows()
