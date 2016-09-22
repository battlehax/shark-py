#!/usr/bin/python
import sys, getopt, requests, json, re, binascii
from hashlib import sha256

password = 'openspot'
ip = 'openspot.local'
tmp = '/tmp/.shark.auth'

def do_auth():
 global tok, digest, post
 try:
   f = open(tmp, 'r')
   tok = f.readline()
   digest = f.readline()
   post = { 'token': tok, 'digest': digest }
   login = requests.post("http://"+ip+"/checkauth.cgi", json=post)
   if int(json.loads(login.text)['success']) != 1:
    do_login()
 except:
    do_login()

def do_login():
 global tok, digest, post
 r = requests.post("http://"+ip+"/gettok.cgi")
 tok = str(r.json()['token'])
 digest = sha256(tok + password).hexdigest()
 post = { 'token': tok, 'digest': digest }
 login = requests.post("http://"+ip+"/login.cgi", json=post)
 if int(json.loads(login.text)['success']) != 1:
  print("AUTH ERROR: check password and ip")
  exit()
 else:
  f = open(tmp, 'w')
  f.write(tok + '\n' + digest)
  f.close

do_auth()

####

send_msg = "msg"
send_dstid = "3120022"
send_calltype = "0"
send_srcid = "9998"
send_format = "1"
send_tdma_channel = "0"

def do_send_sms():
 encoded = "".join([str('00' + x) for x in re.findall('..',binascii.hexlify(send_msg))] )

 if len(encoded) > 150:
  print("Message too long")
  exit()

 post = { 'token': tok, 'digest': digest, 'send_dstid': send_dstid, 'send_calltype': send_calltype, 'send_srcid': send_srcid, 'send_format': send_format, 'send_tdma_channel': send_tdma_channel, 'send_msg': encoded.upper() }
 r = requests.post("http://"+ip+"/status-dmrsms.cgi", json=post)
 if int(json.loads(r.text)['send_success']) != 1:
  print("not sent")


def do_recieve_sms():
 post = { 'token': tok, 'digest': digest }
 r = requests.post("http://"+ip+"/status-dmrsms.cgi", json=post)
 if int(json.loads(r.text)['rx_msg_valid']) == 1:
  print("Message recieved from: " + str(json.loads(r.text)['rx_msg_srcid']) )
  print("Encoded message: " + json.loads(r.text)['rx_msg'] )

if len(sys.argv) > 2:
 print(sys.argv[1:])
 send_dstid = str(sys.argv[1])
 send_msg = str(sys.argv[2:])
 do_send_sms()
else:
 do_recieve_sms()
