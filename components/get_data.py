import random


class Get_data:
    def __init__(self, settings):
        self.settings = settings
        #self.buffer = None
        '''
        if self.settings['ENCODER_USE']:
            import snap7
            self.plc = snap7.client.Client()
            self.plc.connect(self.settings['ENCODER_IP'], 
                             self.settings['ENCODER_RACK'], 
                             self.settings['ENCODER_SLOT'])
        '''

    def run(self, data):
        '''
        data['L_encoder'] = None

        # Тут нужно ставить проверку что значение в контроллере изменилось, если так то читаем
        #plc_read = plc.db_read(6, 0, 4)
        plc_read = round(random.uniform(1000,6500), 2)

        if self.buffer != plc_read:
            data['L_encoder'] = plc_read
            data['plc_connect'] = plc.get_connected()
        else:
            # Раскоментить присвоение None 
            data['L_encoder'] = plc_read # None
            #data['L_encoder'] = None
            self.buffer = plc_read
        '''
        return data
