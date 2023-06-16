# -*- coding: cp1251 -*-
from ftplib import FTP
import sys
fl = []
if len(sys.argv) > 1:
  for i in range(1, len(sys.argv)):
    print(sys.argv[i])
    fl.append(sys.argv[i])
else:
  fl.append('web_interface_2.py')


for j in range(len(fl)):
  print(fl[j])

  ftp = FTP()
  HOSTS = ['46.229.132.100']
  PORT = 21
  for i in range(len(HOSTS)):
    ftp.connect(HOSTS[i], PORT)
    print(ftp.login(user='ur_rs_1', passwd='238238'))

    ftp.cwd('RS_Project_2/components')

    with open(fl[j], 'rb') as f:
        ftp.storbinary('STOR ' + fl[j].split('\\')[-1], f, 1024)

    print('Done!')
