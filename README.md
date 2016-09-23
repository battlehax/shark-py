# shark-py
Interact with an openSpot SharkRF via the http json api.
For now, only a few options are implemented for changing settings. I will work on adding more or all of the settings.
Make sure you set your password and host/ip address if you've changed it from the default.

Currently implemented:

- shark.do_checkauth() - run this to auth and set some needed vars
- shark.get_freq() - returns the rx and tx frequencies as a dict
- shark.get_status() - returns modem status and room as a dict
- shark.get_mode() - returns the modem mode and submode as a dict
- shark.get_connector() - returns the current connector as a string
- shark.set_talkgroup(new_group) - changes the room
- shark.set_freq(new_rx_freq, new_tx_freq) - set the frequency in MHz. set both with just new_rx_freq
- shark.set_mode(new_mode) - change the modem mode
- shark.do_recieve_sms() - if there is an unread, show sender and message as list
- shark.do_send_sms(dstid, msg) - send sms to radio

There is an example script:

./info.py

display status of the openSpot and exit

./info.py -h

show command line arguments to change some options

Here is another example:

```
#!/usr/bin/python
import re, binascii, shark
shark.do_checkauth()
shark.do_send_sms( '3120022', 'hey there' )
```