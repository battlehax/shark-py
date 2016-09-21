#!/usr/bin/python
import sys, getopt, requests, json
from hashlib import sha256

password = 'openspot'
ip = 'openspot.local'
tmp = '/tmp/.shark.auth'

def show_usage():
 print('''
  usage: ./shark.py
   display status

  usage: ./shark.py -g <talkgroup> -m <mode> -f <frequency>
   -m   idle/dmr/c4fm/dstar
   -g   dmr talkgroup number
   -f   frequency in MHz
  
  ex:
   ./shark.py
   ./shark.py -g 4639 -m c4fm
   ./shark.py -m dmr -f 433.1
   ./shark.py -g 0
  ''')

def do_auth():
 global tok, digest, post
 f = open(tmp, 'r')
 tok = f.readline()
 digest = f.readline()
 post = { 'token': tok, 'digest': digest }
 login = requests.post("http://"+ip+"/checkauth.cgi", json=post)
 if int(json.loads(login.text)['success']) != 1:
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

def get_freq():
 global rx, tx
 rfreq = requests.post("http://"+ip+"/modemfreq.cgi", json=post)
 rx = rfreq.json()["rx_frequency"]
 tx = rfreq.json()["tx_frequency"]
 rx = str(rx / 1000000.0) + "MHz"
 tx = str(tx / 1000000.0) + "MHz"

def get_status():
 global room, status
 rstatus = requests.post("http://"+ip+"/status.cgi", json=post)
 room = rstatus.json()["connected_to"]
 status = rstatus.json()["status"]
 if status == 0:
  status = "Standby"
 elif status == 1:
  status = "In call"
 elif status == 3:
  status = "Connector not set"
 elif status == 4:
  status = "Modem initializing"
 elif status == 5:
  status = "Modem disconnected"
 elif status == 6:
  status = "Modem HW/SW version mismatch"
 elif status == 7:
  status = "Modem firmware upgrade in progress"
 else:
  status = "API ERROR: unknown status code"

def get_mode():
 global mode, submode
 rmode = requests.post("http://"+ip+"/modemmode.cgi", json=post)
 mode = rmode.json()["mode"]
 if mode == 0:
  mode = "Idle"
 elif mode == 1:
  mode = "Raw"
 elif mode == 2:
  mode = "DMR"
 elif mode == 3:
  mode = "D-STAR"
 elif mode == 4:
  mode = "C4FM"
 else:
  mode = "API ERROR: unknown modem mode"
 submode = rmode.json()["submode"]
 if submode == 0:
  submode = "No submode"
 elif submode == 1:
  submode = "DMR Hotspot"
 elif submode == 2:
  submode = "DMR MS"
 elif submode == 3:
  submode = "DMR BS"
 else:
  submode = "API ERROR: unknown sub mode"

def get_connector():
 global connector
 rconnector = requests.post("http://"+ip+"/connector.cgi", json=post)
 connector = rconnector.json()["active_connector"]
 if connector == 0:
  connector = "No connector"
 elif connector == 1:
  connector = "DMRplus"
 elif connector == 2:
  connector = "Homebrew"
 elif connector == 3:
  connector = "TS repeat"
 elif connector == 4:
  connector = "DCS/XLX"
 elif connector == 5:
  connector = "FCS"
 elif connector == 6:
  connector = "SharkRF Client"
 elif connector == 7:
  connector = "SharkRF Server"
 elif connector == 8:
  connector = "DMR calibration"
 elif connector == 9:
  connector = "REF/XRF"
 elif connector == 10:
  connector = "YSF Reflector"
 else:
  connector = "API ERROR: unknown connector type" 

def args(argv):
 try:
  opts, args = getopt.getopt(argv,"hf:m:g:")
 except getopt.GetoptError:
  show_usage()
 for opt, arg in opts:
  if opt == '-h':
   show_usage()
   exit()
  elif opt == '-f':
   set_freq(arg)
  elif opt == '-m':
   set_mode(arg)
  elif opt == '-g':
   set_talkgroup(arg)

def set_talkgroup(argv):
 post = { 'token': tok, 'digest': digest, 'new_autocon_id': argv, 'new_c4fm_dstid': argv, 'new_reroute_id': argv }
 de = requests.post("http://"+ip+"/homebrewsettings.cgi", json=post)
 if int(json.loads(de.text)['changed']) != 1:
  print("TALKGROUP ERROR: make sure " + argv + " is correct")
 else:
  print("Changing to talkgroup " + argv)

def set_freq(argv):
 f = float(argv) * 1000000
 post = { 'token': tok, 'digest': digest, 'new_rx_freq': f, 'new_tx_freq': f }
 dc = requests.post("http://"+ip+"/homebrewsettings.cgi", json=post)
 if int(json.loads(dc.text)['changed']) != 1:
  print("FREQUENCY ERROR: make sure " + argv + " is correct")
 else:
  print("Changing to frequency " + argv)

def set_mode(argv):
 if argv == "dmr":
  newmode = 2
 elif argv == "dstar":
  newmode = 3
 elif argv == "c4fm":
  newmode = 4
 elif argv == "raw":
  newmode = 1
 elif argv == "idle":
  newmode = 0
 else:
  print("MODE ERROR: try one of dmr, dstar, c4fm, raw, idle")
 if newmode == 2:
  post = { 'token': tok, 'digest': digest, 'new_mode': newmode, 'new_submode': '1' }
 else:
  post = { 'token': tok, 'digest': digest, 'new_mode': newmode, 'new_submode': '0' }
 dm = requests.post("http://"+ip+"/modemmode.cgi", json=post)
 if int(json.loads(dm.text)['changed']) != 1:
  print("MODE ERROR: cannot change mode")
 else:
  print("Changing mode to " + argv)

def show_info():
 get_mode()
 get_freq()
 get_connector()
 get_status()
 print("Status: " + status)
 print("Connector: " + connector)
 if rx == tx:
  print("Frequency: " + tx)
 else:
  print("Recieve Freq: " + rx)
  print("Transmit Freq: " + tx)
 print("Mode: " + mode + " (" + submode +")")
 print("Talkgroup: " + room)



do_auth()
args(sys.argv[1:])
if len(sys.argv) <= 1:
 show_info()
