import cv2
import numpy as np
import imutils
from PIL import ImageFont, ImageDraw, Image


def draw_calibration_info(img, CALIBRATION_LINE_1, CALIBRATION_LINE_2):
    cv2.rectangle(img,
                  CALIBRATION_LINE_1[0],
                  CALIBRATION_LINE_1[1],
                  (255, 0, 255), 5)

    cv2.rectangle(img,
                  CALIBRATION_LINE_2[0],
                  CALIBRATION_LINE_2[1],
                  (255, 0, 255), 5)

    return img


def print_text(img, text, coords=(0,0), color=(255, 255, 255),
               size=1.6, thikness=5, no_back=False):
    if not no_back:
        cv2.putText(img, str(text), coords,
                    cv2.FONT_HERSHEY_SIMPLEX, size,
                    (0, 0, 0), thikness*4)
    cv2.putText(img, str(text), coords,
                cv2.FONT_HERSHEY_SIMPLEX, size,
                color, thikness)

def print_russian_text(img, text, coords=(0,0), color=(255, 255, 255),
               size=16, thikness=5):
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)

    try:
        fontpath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        font = ImageFont.truetype(fontpath, size+1)
    except:
        fontpath = "arial.ttf"
        font = ImageFont.truetype(fontpath, size+1)
    draw.text(coords, text, font=font, fill=(0, 0, 0))
    
    font = ImageFont.truetype(fontpath, size)
    draw.text(coords, text, font=font, fill=color)
    img = np.array(img_pil)
    return img


def hsv_filter(img, hsv_th):

    h1, s1, v1, h2, s2, v2 = hsv_th['h1'], hsv_th['s1'], hsv_th['v1'], hsv_th['h2'], hsv_th['s2'], hsv_th['v2']

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h1 = np.interp(h1, [0, 360], [0, 255])
    s1 = np.interp(s1, [0, 100], [0, 255])
    v1 = np.interp(v1, [0, 100], [0, 255])
    h2 = np.interp(h2, [0, 360], [0, 255])
    s2 = np.interp(s2, [0, 100], [0, 255])
    v2 = np.interp(v2, [0, 100], [0, 255])

    h_min = np.array((h1, s1, v1), np.uint8)
    h_max = np.array((h2, s2, v2), np.uint8)
    thresh = cv2.inRange(hsv, h_min, h_max)
    return thresh


def build_shpon_mask(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = imutils.adjust_brightness_contrast(gray, brightness=-150.0, contrast=250.0)
    gray = np.dstack((gray, gray, gray))
    return gray


def get_max_area(frame):  
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL,
                          cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) == 0:
        return None

    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)
    return [x, y, w, h]


def extract_max_area(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                          cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    if len(cnts) == 0:
        return None
    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)
    frame = frame[y:y + h, x:x + w, :]
    return frame

def adjust_gamma(img, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(img, table)
