import os
import cv2
import numpy as np

np.random.seed(18)

settings = dict()

settings['DEBUG'] = False
settings['FAKE_IP_CAM'] = False 
settings['DB_USE'] = True
settings['DB_TXT'] = False
settings['ENCODER_USE'] = True # Для тестов с контроллером
settings['SHOW_BIN'] = False
settings['SAVE_VIDEO'] = False
settings['FRAME_RATE'] = 15
settings['PASSWORD'] = '123'
settings['CALIBRATE_FLTER'] = False
settings['SAVE_TIMBER'] = False


if settings['FAKE_IP_CAM']:
    settings['CAMERA_TYPE'] = 'debug'
    settings['CAMERA_IP'] = 'ip'
    settings['CAMERA_PORT'] = 5058
    
    settings['OUTPUT_PATH'] = 'static/data/'
    settings['JSON_SETTINGS'] =  r'current_mode.json'
    
else:
    settings['CAMERA_TYPE'] = 'ip'
    settings['CAMERA_SRC'] = "rtsp://pass@ip/cam/realmonitor?channel=1&subtype=0"
        
    settings['OUTPUT_PATH'] = 'static/data/'
    settings['JSON_SETTINGS'] =  r'current_mode.json'


settings['DB_IP'] = 'ip'
settings['DB_PORT'] = 28818
settings['DB_DATABASE'] = 'timber'
settings['DB_THEME'] = 'rskr'


settings['ENCODER_IP'] = 'ip'   # параметры контроллера
settings['ENCODER_RACK'] = 0
settings['ENCODER_SLOT'] = 1

settings['STREAM_IP'] = '0.0.0.0'
settings['STREAM_PORT'] = 5055

settings['STREAMER_IP_FRONT'] = '10.12.36.2'

settings['DB_TEMPLATE'] = {
                           'date': '01.01.1970',
                           'time': '00:00:00',
                           'sec_time': 0,
                           'saw': 1,
                           'L': 0,
                           'L_uch': 0,
                           'D': 0,
                           'mode': '',
                           'auto': True,
                           'plc_saw': 1
                          }

settings['LEN_TH'] = [2000, 3200, 3930, 4900, 5360, 6600]
settings['LEN_UCH'] = [1600, 2600, 3200, 3900, 4800, 5200]


settings['YOLO_MODEL'] = 'models/timber_best_small.pt'
settings['YOLO_CLASSES'] = ['timber']
settings['YOLO_COLORS'] = np.random.uniform(0, 255,
                                            size=(len(settings['YOLO_CLASSES']),
                                            3))

settings['YOLO_MODEL_CONF'] = 0.55
settings['YOLO_MODEL_IOU'] = 0.3
settings['YOLO_MODEL_MAX_DET'] = 15

settings['KOEF'] = 0.687 * 4
settings['CONVERT_SCALE'] = lambda x, koef : round((x * koef * 4), 2)
#settings['CONVERT_SCALE'] = lambda x: round((x * settings['KOEF']), 2)

settings['STEP'] = int(500 / settings['KOEF'])

settings['WIDTH'] = 1920
settings['HIGHT'] = 1080
settings['RESIZE_FACTOR'] = 2

#settings['HSV_TH'] = {'h1': 100, 'v1': 0, 's1': 0,         # Настройка HSV фильтра для оценки диаметра
#                      'h2': 250, 's2': 100, 'v2': 100}  

#settings['HSV_TH'] = {'h1': 170, 'v1': 0, 's1': 5,         # Настройка HSV фильтра для оценки диаметра
#                      'h2': 250, 's2': 50, 'v2': 50}  

settings['HSV_TH'] = {'h1': 247, 'v1': 4, 's1': 0,         # Настройка HSV фильтра для оценки диаметра
                      'h2': 355, 's2': 20, 'v2': 40}  

#settings['HSV_TH'] = {'h1': 200, 'v1': 0, 's1': 0,
#                      'h2': 290, 's2': 50, 'v2': 40}  


settings['WOOD_AREA'] = [(int(settings['WIDTH'] * 0.645),   #  редактировать окно где ищем торец бревна
                          int(settings['HIGHT'] * 0.295)),
                         (int(settings['WIDTH'] * 0.760),
                          int(settings['HIGHT'] * 0.55))]
#'''

