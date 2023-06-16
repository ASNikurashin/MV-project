import time
import snap7
import struct
from snap7.exceptions import Snap7Exception

# client = snap7.client.Client()
#IP = '10.12.36.4'
IP = '10.12.38.165'
RACK = 0
SLOT = 1

def ConnectPLC(IP,RACK,SLOT):
    PLC = snap7.client.Client()

    connect = False
    while True:
        if not connect:
            try:
                PLC.connect(IP, RACK, SLOT)
                time.sleep(1)
                connect = PLC.get_connected()
                print('plc connect ', connect)
            except Snap7Exception as e:
                connect = False
                continue
        else:
            try:
                if connect:
                    print('connect')
                    print( PLC.db_read(6, 0, 4))
                    # factLength = snap7.util.get_dint(Length, 0)
                    # print(factLength)
                    # print('connection')

            except Snap7Exception as e:
                PLC.destroy()
                print('error ', e)
                connect = False
                continue


ConnectPLC(IP,RACK,SLOT)

