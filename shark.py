#!/usr/bin/python
import requests, json, re, binascii, hashlib

password = 'openspot'
ip = 'openspot.local'
tmp = '/tmp/.shark.auth'

def do_checkauth():
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
   digest = hashlib.sha256(tok + password).hexdigest()
   post = { 'token': tok, 'digest': digest }
   login = requests.post("http://"+ip+"/login.cgi", json=post)
   if int(json.loads(login.text)['success']) != 1:
      print("AUTH ERROR: check password and ip")
      exit()
   else:
      f = open(tmp, 'w')
      f.write(tok + "\n" + digest)
      f.close

def get_freq():
   rfreq = requests.post("http://"+ip+"/modemfreq.cgi", json=post)
   rx = rfreq.json()["rx_frequency"]
   tx = rfreq.json()["tx_frequency"]
   rx = str(rx / 1000000.0) + "MHz"
   tx = str(tx / 1000000.0) + "MHz"
   return{ 'rx': rx, 'tx': tx }

def get_status():
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
   return{ 'status': status, 'room': room }

def get_mode():
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
   return{ 'mode': mode, 'submode': submode }

def get_connector():
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
   return(connector)

def set_talkgroup(new_group):
   post = { 'token': tok, 'digest': digest, 'new_autocon_id': new_group, 'new_c4fm_dstid': new_group, 'new_reroute_id': new_group }
   de = requests.post("http://"+ip+"/homebrewsettings.cgi", json=post)
   return(json.loads(de.text)['changed'])

def set_freq( new_rx_freq, new_tx_freq = 1 ):
   new_rx_freq = float(new_rx_freq) * 1000000
   if new_tx_freq == 1:
      new_tx_freq = new_rx_freq
   else:
      new_tx_freq = float(new_tx_freq) * 1000000
   post = { 'token': tok, 'digest': digest, 'new_rx_freq': new_rx_freq, 'new_tx_freq': new_tx_freq }
   dc = requests.post("http://"+ip+"/homebrewsettings.cgi", json=post)
   return( int(json.loads(dc.text)['changed']) ) 

def set_mode( new_mode ):
   if new_mode == "dmr":
      newmode = 2
   elif new_mode == "dstar":
      newmode = 3
   elif new_mode == "c4fm":
      newmode = 4
   elif new_mode == "raw":
      newmode = 1
   elif new_mode == "idle":
      newmode = 0
   else:
      return("MODE ERROR: try one of dmr, dstar, c4fm, raw, idle")
   if newmode == 2:
      post = { 'token': tok, 'digest': digest, 'new_mode': newmode, 'new_submode': '1' }
   else:
      post = { 'token': tok, 'digest': digest, 'new_mode': newmode, 'new_submode': '0' }
   dm = requests.post("http://"+ip+"/modemmode.cgi", json=post)
   if int(json.loads(dm.text)['changed']) != 1:
      return("MODE ERROR: cannot change mode")

def do_send_sms( dstid, msg ):
    send_calltype = "0"
    send_srcid = "9998"
    send_format = "1" #MD-380/390
    send_tdma_channel = "0"
    encoded = "".join([str('00' + x) for x in re.findall('..',binascii.hexlify(msg))] )
    if len(encoded) > 150:
      return("Message too long")
    post = { 'token': tok, 'digest': digest, 'send_dstid': dstid, 'send_calltype': send_calltype, 'send_srcid': send_srcid, 'send_format': send_format, 'send_tdma_channel': send_tdma_channel, 'send_msg': encoded.upper() }
    requests.post("http://"+ip+"/status-dmrsms.cgi", json=post)

def do_recieve_sms():
   post = { 'token': tok, 'digest': digest }
   r = requests.post("http://"+ip+"/status-dmrsms.cgi", json=post)
   sms_sender = str(json.loads(r.text)['rx_msg_srcid'])
   sms_message = ''.join(json.loads(r.text)['rx_msg'].split('00')).decode('hex')
   if sms_message != '':
      return([ sms_sender, sms_message ])
