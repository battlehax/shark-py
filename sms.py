#!/usr/bin/python
import shark
import requests, binascii, re, json, hashlib, codecs
from time import sleep, gmtime, strftime
shark.do_checkauth()
while 1:
   z = shark.do_recieve_sms()
   if z:
      print(strftime("%d/%m %H:%M:%S", gmtime()) + ' [' + z[0] + '] ' + z[1] )


      '''
      if z[1] == 'Hello':
         print('saying hi to ' + z[0])
         sleep(10) #md380 still kinda craps itself with a delay
         shark.do_send_sms(z[0], 'hi there!')
      '''
   sleep(3)
