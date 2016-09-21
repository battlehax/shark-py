# shark-py
Interact with an openSpot SharkRF via the http json api.
For now, only a few options are implemented for changing settings. I will work on adding more or all of the settings.

Make sure you set your password and host/ip address if you've changed it from the default.

  usage: ./shark.py
   display status and exit

  usage: ./shark.py -g <talkgroup> -m <mode> -f <frequency>
   -m   idle/dmr/c4fm/dstar
   -g   dmr talkgroup number
   -f   frequency in MHz

  ex:
   ./shark.py
   ./shark.py -g 4639 -m c4fm
   ./shark.py -m dmr -f 433.1
   ./shark.py -g 0
