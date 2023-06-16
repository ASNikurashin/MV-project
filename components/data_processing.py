import cv2
import imutils
import numpy as np
import time
import json
from modules import functions
from modules import mongo_functions
from modules import json_unpacker

class Data_processing:
    def __init__(self, settings):
        self.OUTPUT_PATH = settings['OUTPUT_PATH']
        self.convert_scale = settings['CONVERT_SCALE']
        self.STEP = settings['STEP']
        self.debug = settings['DEBUG']
        self.settings = settings


    def run(self, data):  
        (detections, data['result'], data['bbox'], 
         data['binary'], data['bbox_coords'], data['diams'], data['interm']) = wood_analisis(data['timber'],
                                                                                             data['image'],
                                                                                             data, 
                                                                                             self.settings)

        return data


#def nothing(*arg):
#    pass

#if True: #self.settings['CALIBRATE_FLTER']:
#    #icol = (284, 6, 0, 355, 20, 40)
#    icol = (250, 3, 0, 355, 40, 40)
#    #icol = (247, 5, 0, 355, 20, 40) # old
#    #icol = (0, 0, 0, 360, 11, 16) # light
#    cv2.namedWindow('calibrate')
#    cv2.createTrackbar('lowHue', 'calibrate', icol[0], 360, nothing)
#    cv2.createTrackbar('lowSat', 'calibrate', icol[1], 100, nothing)
#    cv2.createTrackbar('lowVal', 'calibrate', icol[2], 100, nothing)
#    cv2.createTrackbar('highHue', 'calibrate', icol[3], 360, nothing)
#    cv2.createTrackbar('highSat', 'calibrate', icol[4], 100, nothing)
#    cv2.createTrackbar('highVal', 'calibrate', icol[5], 100, nothing)


def wood_analisis(detections, img, data, settings):
    H, W = img.shape[:2]
    result_img = img.copy()
    bin_img = None
    boundingBox = None
    bbox_coords = None
    interm = None
    diams = []
    #result_img = data['image'].copy()

    convolutionKernel = np.ones((2, 2), np.uint8)
    for detection in detections:

        x, y = int(W * detection[0]), int(H * detection[1])
        w, h = int(W * detection[2]), int(H * detection[3])
        c, d = x, y
        x, y = x - w // 2, y - h // 2
        a, b = x + w, y + h

        line_y_max = settings['WOOD_AREA'][0][1] + (settings['WOOD_AREA'][1][1] - settings['WOOD_AREA'][0][1]) * 0.7 # TODO: Add vars in config
        #line_x_min = settings['WOOD_AREA'][0][0] + (settings['WOOD_AREA'][1][0] - settings['WOOD_AREA'][0][0]) * 0.05 # TODO: Add vars in config
        line_x_max = settings['WOOD_AREA'][0][0] + (settings['WOOD_AREA'][1][0] - settings['WOOD_AREA'][0][0]) * 0.33
        
        if (settings['WOOD_AREA'][0][1] < y < settings['WOOD_AREA'][1][1] and 
            settings['WOOD_AREA'][0][1] < b < settings['WOOD_AREA'][1][1] and 
            settings['WOOD_AREA'][0][0] < x < settings['WOOD_AREA'][1][0] and 
            settings['WOOD_AREA'][0][0] < a < settings['WOOD_AREA'][1][0]) and (b >= line_y_max) and (x <= line_x_max):
            x, y, a, b, w, h = x, y, a, b, w, h
        else:
            x, y, a, b, w, h = 0, 0, 0, 0, 0, 0

        if x != 0:
            startPointOfBbox = (x, y)
            endPointOfBbox = (a, b)
            bbox_coords = (startPointOfBbox, endPointOfBbox)

            boundingBox = result_img[y:b, x:a]
            
            #bin_img = filterT(boundingBox, 150)
            #bin_img = filter2(boundingBox, 150)
            #bin_img = filter3(boundingBox, 150)
            #bin_img = filter4(boundingBox, 150, settings['HSV_TH'])
            #bin_img, interm = filter5(boundingBox, 150, settings['HSV_TH'], settings['CALIBRATE_FLTER'])
            bin_img, interm = filter7(boundingBox, 150, settings['HSV_TH'], settings['CALIBRATE_FLTER'])

            cv2.rectangle(result_img,
                          startPointOfBbox,
                          endPointOfBbox,
                          (255, 255, 100),
                          5)

            with open(r'data/current_mode.json', 'r', encoding='utf-8') as f:
                mode = json.load(f)

            koef = mode['koef'] # TODO
            bin_img, diams = get_diam(bin_img, boundingBox, result_img, 
                                      50, settings['SHOW_BIN'],
                                      settings['CONVERT_SCALE'], koef)

    return detections, result_img, boundingBox, bin_img, bbox_coords, diams, interm


def get_diam(bin_img, boundingBox, image, len_max_cnt, show_bin, convert, koef):

    diam, diam1 = None, None
    
    #contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, _ = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #contours, _ = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find the rotated rectangles and ellipses for each contour
    if len(contours) != 0:
        maxContours = max(contours, key=cv2.contourArea)
        if len(maxContours) > len_max_cnt:
            # TODO: make returning of only one timber
            minRect = cv2.minAreaRect(maxContours)
            minEllipse = cv2.fitEllipse(maxContours)
            # getting diameters from ellipse object
            (_, _), (MA, ma), angle = minEllipse
            
            #diam = convert(ma)
            #diam1 = convert(MA)
            diam = convert(ma, koef)
            diam1 = convert(MA, koef)
            
            #print('Диаметры: ' + diam + ' || ' + diam1)
            cv2.ellipse(boundingBox, minEllipse, (255, 0, 0), 3)
            if show_bin:
                cv2.ellipse(bin_img, minEllipse, (255, 0, 0), 3)
            # rotated rectangle
            #box = cv2.boxPoints(minRect)
            #box = np.intp(box)
            #cv2.drawContours(boundingBox, [box], 0, 10)
            #cv2.drawContours(boundingBox, [maxContours], -1, (0,255,0), 1)

    return bin_img, [diam, diam1] if not(diam is None) else []


def get_diam2(bin_img, boundingBox, image):
    
    cnts = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    # Find the rotated rectangles and ellipses for each contour
    if len(cnts[0]) != 0:
        maxContours = max(cnts, key=cv2.contourArea)
        (x1, y1, w1, h1) = cv2.boundingRect(maxContours)
        
        # TODO: make returning of only one timber
        minRect = cv2.minAreaRect(maxContours)
        minEllipse = cv2.fitEllipse(maxContours)
        
        # getting diameters from ellipse object
        (_, _), (MA, ma), angle = minEllipse
        coefficient = 2.7
        diam = str(round((ma * 0.1 * coefficient), 2)) # 2.7 - coefficient
        diam1 = str(round((MA * 0.1 * coefficient), 2))
        #print('Диаметры: ' + diam + ' || ' + diam1)
        cv2.ellipse(boundingBox, minEllipse, (255, 0, 0), 3)
        #cv2.ellipse(bin_img, minEllipse, (255, 0, 0), 3)
        
        # rotated rectangle
        #box = cv2.boxPoints(minRect)
        #box = np.intp(box)
        #cv2.drawContours(boundingBox, [box], 0, 10)
        cv2.drawContours(boundingBox, [maxContours], -1, (0,255,0), 1)

    return bin_img, [diam, diam1] if not(diam is None) else []


def filterT(boundingBox, th):

    convolutionKernel = np.ones((3, 3), np.uint8)
    h2, w2 = boundingBox.shape[:2]
    hsvImg = cv2.cvtColor(boundingBox, cv2.COLOR_RGB2HSV)
    hue, saturation, value = cv2.split(hsvImg)
    newBlack = cv2.add(saturation, value)
    ret, binaryImage = cv2.threshold(newBlack, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    imageAfterMorphOp = cv2.morphologyEx(binaryImage, cv2.MORPH_OPEN, convolutionKernel)
    binaryImage = cv2.bitwise_not(imageAfterMorphOp)
    # Convert image to gray and blur it
    src_gray = cv2.blur(binaryImage, (3, 3))
    canny_output = cv2.Canny(src_gray, th, th * 2)
    return canny_output


def filter0(boundingBox, th):
    h2, w2 = boundingBox.shape[:2]
    # ---------------------
    hsvImg = cv2.cvtColor(boundingBox, cv2.COLOR_RGB2HSV)
    hue, saturation, value = cv2.split(hsvImg)
    newBlack = cv2.add(saturation, value)
    
    ret, src_gray = cv2.threshold(newBlack, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    src_gray = cv2.blur(src_gray, (3, 3))
    # ----------------------------------

    canny_output = cv2.Canny(src_gray, th, th * 2)

    kernel = np.ones((3, 3), 'uint8')
    canny_output = cv2.dilate(canny_output, kernel, iterations=1)
    canny_output = cv2.medianBlur(canny_output, 5)
    #canny_output = cv2.erode(canny_output, kernel, iterations=1)
    canny_output = cv2.bitwise_not(canny_output)

    return canny_output


def filter1(boundingBox, th):
    h2, w2 = boundingBox.shape[:2]
    # ---------------------
    hsvImg = cv2.cvtColor(boundingBox, cv2.COLOR_RGB2HSV)
    hue, saturation, value = cv2.split(hsvImg)
    newBlack = saturation
    #newBlack = cv2.add(saturation, value)
    
    ret, src_gray = cv2.threshold(newBlack, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # ----------------------------------

    canny_output = cv2.Canny(src_gray, th, th * 2)

    kernel = np.ones((3, 3), 'uint8')
    canny_output = cv2.dilate(canny_output, kernel, iterations=1)
    canny_output = cv2.medianBlur(canny_output, 5)
    canny_output = cv2.erode(canny_output, kernel, iterations=1)

    canny_output = cv2.bitwise_not(canny_output)
    return canny_output


def filter2(boundingBox, th):
    h2, w2 = boundingBox.shape[:2]
    # ---------------------
    hsvImg = cv2.cvtColor(boundingBox, cv2.COLOR_RGB2HSV) # ???
    hue, saturation, value = cv2.split(hsvImg)
    newBlack = cv2.add(saturation, value)
    
    ret, src_gray = cv2.threshold(newBlack, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # ----------------------------------
    kernel = np.ones((2, 2), 'uint8')
    #src_gray = cv2.dilate(src_gray, kernel, iterations=1)
    src_gray = cv2.erode(src_gray, kernel, iterations=1)
    #src_gray = cv2.medianBlur(src_gray, 3)
    return src_gray


def filter3(boundingBox, th):
    h2, w2 = boundingBox.shape[:2]
    # ---------------------
    boundingBox = imutils.adjust_brightness_contrast(boundingBox, brightness=-100.0, contrast=200.0) # 
    gray = cv2.cvtColor(boundingBox, cv2.COLOR_BGR2GRAY)

    th = th+530
    src_gray = cv2.Canny(gray, th, th * 2)

    # ----------------------------------
    src_gray = cv2.medianBlur(src_gray, 1)
    kernel = np.ones((2, 2), 'uint8')
    src_gray = cv2.dilate(src_gray, kernel, iterations=3)
    src_gray = cv2.erode(src_gray, kernel, iterations=1)

    return src_gray

def filter4(boundingBox, th, hsv_th):
    
    #hsv_th = {'h1': 200, 'v1': 0, 's1': 0,
    #          'h2': 290, 's2': 50, 'v2': 40}    

    hsv = functions.hsv_filter(boundingBox, hsv_th)
    #src_gray = cv2.medianBlur(hsv, 3)

    src_gray = hsv

    return src_grayh

def filter5(boundingBox, th, hsv_th, calibrate):

    if calibrate:
        lowHue = cv2.getTrackbarPos('lowHue', 'calibrate')
        lowSat = cv2.getTrackbarPos('lowSat', 'calibrate')
        lowVal = cv2.getTrackbarPos('lowVal', 'calibrate')
        highHue = cv2.getTrackbarPos('highHue', 'calibrate')
        highSat = cv2.getTrackbarPos('highSat', 'calibrate')
        highVal = cv2.getTrackbarPos('highVal', 'calibrate')

        hsv_th['h1'] = np.interp(lowHue, [0, 360], [0, 255])
        hsv_th['s1'] = np.interp(lowSat, [0, 100], [0, 255])
        hsv_th['v1'] = np.interp(lowVal, [0, 100], [0, 255])
        hsv_th['h2'] = np.interp(highHue, [0, 360], [0, 255])
        hsv_th['s2'] = np.interp(highSat, [0, 100], [0, 255])
        hsv_th['v2'] = np.interp(highVal, [0, 100], [0, 255])

    hsv_th2 = {'h1': 0, 'v1': 4, 's1': 0,
               'h2': 35, 's2': 30, 'v2': 40}  

    hsv1 = functions.hsv_filter(boundingBox, hsv_th)
    hsv2 = functions.hsv_filter(boundingBox, hsv_th)
    
    hsv = cv2.bitwise_or(hsv1, hsv2)
    
    #src_gray = cv2.medianBlur(hsv, 3)

    src_gray = hsv

    return src_gray, boundingBox

def filter6(boundingBox, th, hsv_th, calibrate):

    
    #boundingBox = imutils.adjust_brightness_contrast(boundingBox, brightness=50.0, contrast=0.0) # 

    if calibrate:
        lowHue = cv2.getTrackbarPos('lowHue', 'calibrate')
        lowSat = cv2.getTrackbarPos('lowSat', 'calibrate')
        lowVal = cv2.getTrackbarPos('lowVal', 'calibrate')
        highHue = cv2.getTrackbarPos('highHue', 'calibrate')
        highSat = cv2.getTrackbarPos('highSat', 'calibrate')
        highVal = cv2.getTrackbarPos('highVal', 'calibrate')

        hsv_th['h1'] = np.interp(lowHue, [0, 360], [0, 255])
        hsv_th['s1'] = np.interp(lowSat, [0, 100], [0, 255])
        hsv_th['v1'] = np.interp(lowVal, [0, 100], [0, 255])
        hsv_th['h2'] = np.interp(highHue, [0, 360], [0, 255])
        hsv_th['s2'] = np.interp(highSat, [0, 100], [0, 255])
        hsv_th['v2'] = np.interp(highVal, [0, 100], [0, 255])

    hsv = functions.hsv_filter(boundingBox, hsv_th)
    #src_gray = cv2.medianBlur(hsv, 3)

    src_gray = hsv

    return src_gray, boundingBox

def filter7(boundingBox, th, hsv_th, calibrate):

    frameBr = imutils.adjust_brightness_contrast(boundingBox,
                                                 brightness=-255,
                                                 contrast=255)
    #frameBGR = frame
    frameBGR = cv2.GaussianBlur(frameBr, (5, 5), 0)
    #frameBGR = cv2.medianBlur(frameBGR, 7)
    #frameBGR = cv2.bilateralFilter(frameBGR, 15 ,75, 75)

    hsv = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2HSV)
    colorLow = np.array([0,0,0])
    colorHigh = np.array([360,0,0])
    mask = cv2.inRange(hsv, colorLow, colorHigh)

    kernal = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernal)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernal)

    kernal2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernal2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernal)

    src_gray = mask

    return src_gray, frameBGR



 