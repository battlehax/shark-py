# shark-py
Interact with an openSpot SharkRF via the http json api.
For now, only a few options are implemented for changing settings. I will work on adding more or all of the settings.
Make sure you set your password and host/ip address if you've changed it from the default.


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