# -*- coding: cp1251 -*-
import threading
from ftplib import FTP
import sys

PATH = '\\'.join(sys.argv[0].split('\\')[:-1])

def main_thread():
  ftp = FTP()
  HOST = '46.146.211.38'
  PORT = 56065

  ftp.connect(HOST, PORT)

  print(ftp.login(user='', passwd='9'))

  ftp.cwd('/timber/small/2')

  for i in ['best.pt', 'last.pt', 'F1_curve.png', 'results.png']:
    try:
      with open(i, 'wb') as f:
        ftp.retrbinary('RETR ' + i, f.write)
    except:
      print(i)


main_thread()
