from modules import yolov5
import cv2

class Object_detection:
    def __init__(self, settings):
        self.nn = yolov5.Yolov5(settings['YOLO_MODEL'],
                                settings['YOLO_CLASSES'])
        
        self.nn.model.conf = settings['YOLO_MODEL_CONF']
        self.nn.model.iou = settings['YOLO_MODEL_IOU']
        self.nn.model.max_det = settings['YOLO_MODEL_MAX_DET']
        self.settings = settings
        
    
    def run(self, frame, data):
        data['image'] = frame.copy()
        #crop = frame[self.settings['WOOD_AREA'][0][1]:self.settings['WOOD_AREA'][1][1], 
        #             self.settings['WOOD_AREA'][0][0]:self.settings['WOOD_AREA'][1][0]]

        #data['crop'] = crop.copy()
        data['timber'] = self.nn.detect(frame)
        
        return data
