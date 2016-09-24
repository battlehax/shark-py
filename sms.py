#!/usr/bin/python
import shark
import requests, binascii, re, json, hashlib, codecs
from time import sleep
shark.do_checkauth()
while 1:
   z = shark.do_recieve_sms()
   if z:
      print(z)
      print(z[1])
      if z[1] == 'Hello':
         print('saying hi to ' + z[0])
         sleep(2) #md380 still kinda craps itself with a delay
         shark.do_send_sms(z[0], 'hi there!')
   sleep(3)
