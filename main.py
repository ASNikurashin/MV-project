import time
import cv2

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

from components import get_data
from components import get_frame
from components import frame_processing
from components import object_detection
from components import data_processing
from components import frame_draw_debug
from components import send_data


data = dict()
data['stop'] = False
data['result_img'] = None


from config import settings

get_data_component         = get_data.Get_data(settings)
get_frame_component        = get_frame.Get_frame(settings)
frame_processing_component = frame_processing.Frame_processing(settings)
object_detection_component = object_detection.Object_detection(settings)
data_processing_component  = data_processing.Data_processing(settings)
frame_draw_debug_component = frame_draw_debug.Frame_draw_debug(settings)
send_data_component        = send_data.Send_data(settings)


def nothing(*arg):
    pass


if settings['CALIBRATE_FLTER']:
    #icol = (284, 6, 0, 355, 20, 40)
    icol = (250, 3, 0, 355, 40, 40)
    #icol = (247, 5, 0, 355, 20, 40) # old
    #icol = (0, 0, 0, 360, 11, 16) # light
    cv2.namedWindow('calibrate')
    cv2.createTrackbar('lowHue', 'calibrate', icol[0], 360, nothing)
    cv2.createTrackbar('lowSat', 'calibrate', icol[1], 100, nothing)
    cv2.createTrackbar('lowVal', 'calibrate', icol[2], 100, nothing)
    cv2.createTrackbar('highHue', 'calibrate', icol[3], 360, nothing)
    cv2.createTrackbar('highSat', 'calibrate', icol[4], 100, nothing)
    cv2.createTrackbar('highVal', 'calibrate', icol[5], 100, nothing)


while not data['stop']:
    data = get_data_component.run(data)

    frame, data = get_frame_component.run(data)
    if frame is None:
        time.sleep(0.1)
        continue
    
    data = frame_processing_component.run(frame, data)
    data = object_detection_component.run(frame, data)
    data = data_processing_component.run(data)
    data = frame_draw_debug_component.run(data)
    send_data_component.run(data)
