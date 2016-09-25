#!/usr/bin/python
import json, requests
import shark

# gets info about your node reported by your brandmeister server

shark.do_checkauth()

server = shark.get_homebrew()['server_host']
my_id = shark.get_homebrew()['repeater_id']

print("getting status from " + server )

r = requests.get("http://"+server+"/status/status.php")
jr = json.loads(r.text)
t = requests.get("http://"+server+"/status/list.php")
tr = json.loads(t.text)

for i in jr:
   if i['number'] == my_id:
      index = i
      room = str(i['values'][18])
      permroom = str(i['values'][19])
for i in tr:
    if i['number'] == my_id:
      hw = i['hardware']
      fw = i['firmware']
      call = i['name']

print(call + " " + hw + " ver: " + fw )
print("Current Room: " + room )
print("Always on: " + permroom )
