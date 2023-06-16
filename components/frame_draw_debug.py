import time
import cv2
import numpy as np
#import keyboard

from modules import functions

class Frame_draw_debug:
    def __init__(self, settings):
        self.WOOD_AREA = settings['WOOD_AREA']
        self.debug = settings['DEBUG']
        self.t = time.time()
        self.settings = settings
        self.flag = False

        if self.settings['SAVE_VIDEO']: # and self.debug:
            self.codec = cv2.VideoWriter_fourcc('m', 'j', 'p', 'g')
            # self.codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            #self.vid_out = cv2.VideoWriter('{}.mp4'.format(str(time.ctime()).replace(':', '_')),
            self.vid_out = cv2.VideoWriter('{}.avi'.format(str(time.ctime()).replace(':', '_')),
                                            self.codec, self.settings['FRAME_RATE'],
                                           (int(self.settings['WIDTH']/4), int(self.settings['HIGHT']/4)))
            self.vid_out_2 = cv2.VideoWriter('{}_pure.avi'.format(str(time.ctime()).replace(':', '_')),
                                             self.codec, self.settings['FRAME_RATE'],
                                            (int(self.settings['WIDTH']/4), int(self.settings['HIGHT']/4)))
        

    def run(self, data):
        result = data['result'].copy()

        cv2.rectangle(result,
                      self.WOOD_AREA[0],
                      self.WOOD_AREA[1],
                      (0, 0, 0), 10)

        cv2.rectangle(result,
                      self.WOOD_AREA[0],
                      self.WOOD_AREA[1],
                      (255, 255, 255), 5)


        self.t = 1 / (time.time() - self.t)
        functions.print_text(result, 'FPS {}'.format(int(self.t)),
                             (50, 100),
                             (255, 255, 255),
                             1.6, 5)

        functions.print_text(result, time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(time.time())), ## time.ctime(), ## %a 
                            (50, 50),
                            (255, 255, 255),
                            1.6, 5)

        if len(data['diams']) != 0:
            if not(data['diams'][0] is None) and not(data['diams'][1] is None):
                average_diam = round(sum(data['diams'])/len(data['diams']), 2)
                #functions.print_text(result, '{} || {} || {}'.format(data['diams'][0], data['diams'][1], average_diam), 
                functions.print_text(result, 'D: {}'.format(average_diam), 
                                    (50, 150),
                                    (255, 255, 255), 
                                     1.6, 5)

        '''
        if self.settings['SHOW_BIN']:
            if keyboard.is_pressed('space'):
                if self.flag:
                    self.flag = False
                else:
                    self.flag = True
            if self.flag:                
                if (not (data['binary'] is None)) and (not (data['bbox_coords'] is None)):
                    binary = data['binary'].copy()
                    binary = cv2.merge([binary,binary,binary])
                    bbox_coords = data['bbox_coords']
                    result[bbox_coords[0][1]:bbox_coords[1][1],bbox_coords[0][0]:bbox_coords[1][0]] = binary
        '''

        area = result[self.WOOD_AREA[0][1]:self.WOOD_AREA[1][1],self.WOOD_AREA[0][0]:self.WOOD_AREA[1][0]]
        area = cv2.resize(area, (int(area.shape[1] * 2.5), int(area.shape[0] * 2.5)), interpolation = cv2.INTER_AREA)
        result[result.shape[0] - area.shape[0]:result.shape[0], 0:area.shape[1]] = area

        data['result'] = result.copy()

        if (not (data['interm'] is None)) and (not (data['bbox_coords'] is None)):
            binary = data['interm'].copy()
            #binary = cv2.merge([binary,binary,binary])
            bbox_coords = data['bbox_coords']
            result[bbox_coords[0][1]:bbox_coords[1][1],bbox_coords[0][0]:bbox_coords[1][0]] = binary

        if self.debug: 

            if not (data['result_img'] is None):
                cv2.imshow('result_img', data['result_img'])

            if not (data['binary'] is None):
                cv2.imshow('bin',  data['binary'])

            if not (data['interm'] is None):
                cv2.imshow('interm',  data['interm'])

            if self.settings['SAVE_VIDEO']:
                save_res = cv2.resize(result, (int(self.settings['WIDTH']/4), int(self.settings['HIGHT']/4)), interpolation = cv2.INTER_AREA)
                self.vid_out.write(save_res)
                save_pure = cv2.resize(data['vid_pure'], (int(self.settings['WIDTH']/4), int(self.settings['HIGHT']/4)), interpolation = cv2.INTER_AREA)
                self.vid_out_2.write(save_pure)

            k = self.settings['RESIZE_FACTOR']
            cv2.imshow('res',  cv2.resize(result, (1920 // k, 1080 // k)))
            
            
            if self.settings['SAVE_TIMBER']:
                if not (data['interm'] is None):
                    timber = result[self.WOOD_AREA[0][1]:self.WOOD_AREA[1][1],self.WOOD_AREA[0][0]:self.WOOD_AREA[1][0]]
                    timber_pure = data['vid_pure'][self.WOOD_AREA[0][1]:self.WOOD_AREA[1][1],self.WOOD_AREA[0][0]:self.WOOD_AREA[1][0]]
                    timber_bin = data['binary']
                    cv2.imwrite('data/timber/{}.jpg'.format(str(time.ctime()).replace(':', '_')), timber)
                    cv2.imwrite('data/timber/{}_pure.jpg'.format(str(time.ctime()).replace(':', '_')), timber_pure)
                    cv2.imwrite('data/timber/{}_bin.jpg'.format(str(time.ctime()).replace(':', '_')), timber_bin)


            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:
                cv2.destroyAllWindows()
                data['stop'] = True

                if self.settings['SAVE_VIDEO']:
                    self.vid_out.release()
                    self.vid_out_2.release()


            elif key == ord('s'):
                bbox = cv2.selectROI('img', result, fromCenter=False, showCrosshair=True)
                if len(bbox) > 0:
                    bbox_rel = (bbox[0]/result.shape[1], bbox[1]/result.shape[0]), ((bbox[0] + bbox[2])/result.shape[1], (bbox[1] + bbox[3])/result.shape[0])
                    print('====================')
                    print('bbox: ', bbox)
                    print('bbox_rel: ', bbox_rel)
                    print('====================')

            elif key ==ord('h'):
                bbox = cv2.selectROI('img', data['interm'], fromCenter=False, showCrosshair=True)
                if bbox[2] != 0 and bbox[3] != 0:
                    part = result[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]
                    hsv_part = cv2.cvtColor(part, cv2.COLOR_BGR2HSV)
                    hue, saturation, value = cv2.split(hsv_part)
                    h1 = np.interp(hue.min(), [0, 255], [0, 360])
                    s1 = np.interp(saturation.min(), [0, 255], [0, 100])
                    v1 = np.interp(value.min(), [0, 255], [0, 100])
                    h2 = np.interp(hue.max(), [0, 255], [0, 360])
                    s2 = np.interp(saturation.max(), [0, 255], [0, 100])
                    v2 = np.interp(value.max(), [0, 255], [0, 100])
                    print('====================')
                    print('H1:', h1, 'S1:', s1, 'V1:', v1)
                    print('H2:', h2, 'S2:', s2, 'V2:', v2)
                    print('====================')
        else:
            if self.settings['SAVE_VIDEO']:
                save_res = cv2.resize(result, (int(self.settings['WIDTH']/4), int(self.settings['HIGHT']/4)), interpolation = cv2.INTER_AREA)
                self.vid_out.write(save_res)

                save_pure = cv2.resize(data['vid_pure'], (int(self.settings['WIDTH']/4), int(self.settings['HIGHT']/4)), interpolation = cv2.INTER_AREA)
                self.vid_out_2.write(save_pure)
            
            
                

            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:
                data['stop'] = True

                if self.settings['SAVE_VIDEO']:
                    self.vid_out.release()
                    self.vid_out_2.release()


        data['result_img'] = None
        self.t = time.time()
        return data
