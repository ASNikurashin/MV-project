import snap7

from modules import zmq_module
from modules import mongo_functions
import time
import random
import json

class Send_data:

    def __init__(self, settings):

        self.db_rec = settings['DB_TEMPLATE'].copy()
        self.len_th = settings['LEN_TH']
        self.len_uch = settings['LEN_UCH']
        self.settings = settings
        self.flag = False
        self.counter = 0
        self.buffer = []
        self.buffer_en = None
        self.diam_buf = []
        self.bdl = 0
        self.counter_rec = 0
        self.prev_throw = None
        self.prev_db_rec = None
        self.start_throw = 0

        if self.settings['ENCODER_USE']:
            self.plc = snap7.client.Client()
            self.plc.connect(self.settings['ENCODER_IP'],
                             self.settings['ENCODER_RACK'],
                             self.settings['ENCODER_SLOT'])

        if not self.settings['DEBUG']:
            self.serv = zmq_module.ZMQ_transfer(ip=settings['STREAM_IP'],
                                            port=settings['STREAM_PORT'])
            self.serv.run()
    
        if self.settings['DB_USE']:
            self.db = mongo_functions.DB(port=settings['DB_PORT'],
                                         database=settings['DB_DATABASE'])
            self.DB_THEME = settings['DB_THEME']


    def get_db_rec(self, data):

        if self.settings['ENCODER_USE']:
            contidion = (data['L_encoder'] == None)
        else: 
            contidion = (data['L_encoder'] == None or len(self.diam_buf) == 0)

        print('Diam buffer:', self.diam_buf)
        if contidion:
            return None
        else:
            plc_check = self.plc.db_read(202, 0, 4)
            auto_mode = snap7.util.get_bool(plc_check, 0, 3)
            first_saw = snap7.util.get_bool(plc_check, 0, 4)
            third_saw = snap7.util.get_bool(plc_check, 0, 5)
        
            if (len(self.diam_buf) != 0) and (self.diam_buf[0] != 0):
                self.db_rec['D'] = self.diam_buf[0]
                self.diam_buf.pop(0)
            elif (len(self.diam_buf) != 0) and (self.diam_buf[0] == 0):
                self.db_rec['D'] = self.prev_db_rec['D']
                self.diam_buf.pop(0)
            else:
                if not(self.prev_db_rec is None):
                    self.db_rec['D'] = self.prev_db_rec['D']
                else:
                    self.db_rec['D'] = 0
                   
            # ---------------------------
            self.counter += 1
            print('Counter: ', self.counter)
            # ---------------------------
            self.db_rec['L'] = data['L_encoder']
            # ---------------------------
            #len_th  = [2000, 3200, 3930, 4900, 5360, 6600]
            #len_uch = [1600, 2600, 3200, 3900, 4800, 5200]
            
            if self.db_rec['L'] < self.len_th[0]:
                self.db_rec['L_uch'] = self.len_uch[0]
            elif self.db_rec['L'] < self.len_th[1]:
                self.db_rec['L_uch'] = self.len_uch[1]
            elif self.db_rec['L'] < self.len_th[2]:
                self.db_rec['L_uch'] = self.len_uch[2]
            elif self.db_rec['L'] < self.len_th[3]:
                self.db_rec['L_uch'] = self.len_uch[3]
            elif self.db_rec['L'] < self.len_th[4]:
                self.db_rec['L_uch'] = self.len_uch[4]
            elif self.db_rec['L'] < self.len_th[5]:
                self.db_rec['L_uch'] = self.len_uch[5]
            # ---------------------------
            self.db_rec['date'] = time.strftime("%d.%m.%Y", time.localtime())
            self.db_rec['time'] = time.strftime("%H:%M:%S", time.localtime())
            self.db_rec['sec_time'] = time.mktime(time.strptime('{} {}'.format(self.db_rec['time'], self.db_rec['date']),
                                                                '%H:%M:%S %d.%m.%Y'))
            # ---------------------------
            with open(r'data/current_mode.json', 'r', encoding='utf-8') as f:
                mode = json.load(f)
            self.db_rec['mode'] = mode['name']
            # ---------------------------
            saw = []
            saw_list = [1, 2, 3]
            for i in range(len(saw_list)):
                if self.db_rec['L_uch']/1000 in mode['saw_{}'.format(saw_list[i])]['drop_len']:
                    saw.append(saw_list[i])

            saw_copy = saw.copy()
            for el in saw_copy:
                if self.db_rec['D'] < mode['saw_{}'.format(saw_copy[saw_copy.index(el)])]['d_min'] or self.db_rec['D'] > mode['saw_{}'.format(saw_copy[saw_copy.index(el)])]['d_max']:
                    saw.pop(saw.index(el))

            if len(saw) != 0:
                self.db_rec['saw'] = random.choice(saw)
            else:
                self.db_rec['saw'] = random.choice(saw_list)
            # ---------------------------
            if auto_mode == 1:
                self.db_rec['auto'] = 'Автоматический'
            else:
                self.db_rec['auto'] = 'Ручной'
            # ---------------------------
            if first_saw:
                self.db_rec['plc_saw'] = 1
            elif third_saw:
                self.db_rec['plc_saw'] = 3
            else:
                self.db_rec['plc_saw'] = 2
            # ---------------------------
            rec = self.db_rec
            
            print(self.db_rec)
            #try:
            self.db.add(theme=self.DB_THEME, element=self.db_rec)
            #except:
            #    print('База данных не подключена')
                
            self.db_rec = self.settings['DB_TEMPLATE'].copy()

            print('Diam buffer:', self.diam_buf)
            return rec


    def get_diam(self, data):

        if self.settings['ENCODER_USE']:
            eye_arr = []
            eye_plc = self.plc.db_read(202, 0, 4)
            eye = snap7.util.get_bool(eye_plc, 0, 1) # Значение с датчика о наличии бревна 
            throw = snap7.util.get_bool(eye_plc, 0, 2) # Значение о работе сбрасывателя
            if (throw == False) and (self.prev_throw != None):
                if (throw != self.prev_throw):
                    self.flag = True
                    self.start_throw = 0
            elif (throw == True) and (self.prev_throw != None):
                if (throw != self.prev_throw):
                    self.start_throw = time.time()
                else:
                    self.flag = False
            self.prev_throw = throw

        # print('buffer', self.diam_buf)
        #print(data['diams']);
        if len(data['diams']) != 0: # and (throw == False): # len(data['bbox_coords']) != 0
           if (self.start_throw == 0) or ((time.time() - self.start_throw) < 2):   
               #self.flag = True
               aver_diam = round(sum(data['diams'])/len(data['diams']), 2)

               if data['bbox_coords'][0][0] < (self.settings['WOOD_AREA'][0][0] + self.settings['WOOD_AREA'][1][0])//2:
                   if (aver_diam > 100) and len(self.buffer) <= 100: #10: (aver_diam != 0) and
                       self.buffer.append(aver_diam)
        #else:
        print(' +++', len(self.buffer), ' ',self.start_throw, '+++')
        if self.flag:
            print('===============================')
            #for i in range(len(self.buffer)):
            #    if self.buffer[i] <= 10:
            #        self.buffer.pop(i)
            
            if len(self.buffer) >= 25:
                self.diam_buf.append(int(sum(self.buffer)/len(self.buffer)))
                self.buffer = []
            
            #else:
            #    if not(self.prev_db_rec is None):
            #        self.diam_buf.append(self.prev_db_rec['D'])
            #    else:
            #        self.diam_buf.append(0)
            #    self.buffer = []
            self.flag = False


    def run(self, data):
        if not self.settings['DEBUG']:
            self.serv.put_img(data['result'])
            
        if self.settings['ENCODER_USE']:

            # data1 - проверка на связь с контроллером
            pcl_connection = self.plc.db_read(202, 0, 4)
            pcl_connection_bool = snap7.util.get_bool(pcl_connection, 0, 0)

            if pcl_connection_bool:
                data1 = bytearray(1)
                snap7.util.set_bool(data1,0,0,True)
                self.plc.db_write(201, 0, data1)

            self.get_diam(data)

            data['L_encoder'] = None

            # a,a1,bdl счетчик обновления длины чурака  
            # a = self.plc.db_read(202, 2, 4)
            a = self.plc.db_read(202, 6, 4)
            a1 = snap7.util.get_dint(a, 0)

            if self.bdl == 0:
                self.bdl = a1

            if  a1 != self.bdl:

                print('Counter123: ', self.bdl)
                print('lenght: ', a1)
                self.bdl = a1

                # TODO: Тут нужно ставить проверку что значение в контроллере изменилось, если так то читаем
                lenght = self.plc.db_read(202, 2, 4)
                plc_read = snap7.util.get_dint(lenght, 0)
                buff = plc_read
                # plc_read = round(random.uniform(1000,6500), 2)

                if self.buffer_en != plc_read: 
                    # Тут фиксим фактические длины, если они слишком большие или слишком маленькие
                    if plc_read < 100:
                        data['L_encoder'] = None
                    elif plc_read > self.len_th[5]:
                        data['L_encoder'] = self.prev_db_rec['L']
                    else:
                        data['L_encoder'] = plc_read
                else:
                    # Раскоментить присвоение None, закомментить присвоение plc_read
                    #data['L_encoder'] = plc_read
                    data['L_encoder'] = None
                    self.buffer_en = plc_read

                rec = self.get_db_rec(data)

                if not(rec is None):
                    self.prev_db_rec = rec
                    print('Value to PLC: ', rec['saw'])
    		        # Здесь отправлять значение	
                    # запись счётчика для контроллера 
                    self.counter_rec += 1
                    if self.counter_rec > 10000:
                        self.counter_rec = 0
                    data2 = bytearray (4)
                    snap7.util.set_dint(data2,0,self.counter_rec)
                    print('counter_rec: ', self.counter_rec)                
                    self.plc.db_write(201,6,data2)
                    
                    # запись пилы
                    data3 = bytearray(4)
                    snap7.util.set_dint(data3,0,rec['saw'])
                    self.plc.db_write(201, 10, data3)
                    
        
        else:
            self.get_diam(data)

            data['L_encoder'] = None            
            plc_read = round(random.uniform(1000,6500), 2)

            if self.buffer_en != plc_read:
                data['L_encoder'] = plc_read
            else:
                data['L_encoder'] = plc_read
                self.buffer_en = plc_read

            rec = self.get_db_rec(data)
            if rec is not None: 
                print('Value to PLC: ', rec['saw'])
                self.counter_rec += 1   
                print('counter_rec: ', self.counter_rec)                

        return data
