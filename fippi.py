#!/usr/bin/python
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

import pexpect
import socket
import time

stations = {
    "KEXP": "http://live-mp3-128.kexp.org:8000/listen.pls",
    "WFUV": "http://www.wfuv.org/sites/all/files/streams/wfuvmp3high.pls",
    "TSF Jazz": "http://tsfjazz.ice.infomaniak.ch/tsfjazz-high.mp3",
    "Radio FIP": "http://audio.scdn.arkena.com/11016/fip-midfi128.mp3"
}


lcd = Adafruit_CharLCDPlate()
lcd.begin(16, 2)
lcd.clear()

log = file('/var/log/fippy.log', 'w')

# Show IP address (if network is available).  System might be freshly
# booted and not have an address yet, so keep trying for a couple minutes
# before reporting failure.
t = time.time()
while True:
    if (time.time() - t) > 120:
        # No connection reached after 2 minutes
        lcd.backlight(lcd.RED)
        lcd.message('Network is\nunreachable')
        time.sleep(30)
        exit(0)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        lcd.backlight(lcd.GREEN)
        lcd.backlight(lcd.ON)
        lcd.message('My IP address is\n' + s.getsockname()[0])
        time.sleep(5)
        break         # Success -- let's hear some music!
    except:
        time.sleep(1)  # Pause a moment, keep trying


# create some custom characters
lcd.createChar(1, [2, 3, 2, 2, 14, 30, 12, 0])
lcd.createChar(2, [0, 1, 3, 22, 28, 8, 0, 0])
lcd.createChar(3, [0, 14, 21, 23, 17, 14, 0, 0])
lcd.createChar(4, [31, 17, 10, 4, 10, 17, 31, 0])
lcd.createChar(5, [8, 12, 10, 9, 10, 12, 8, 0])
lcd.createChar(6, [2, 6, 10, 18, 10, 6, 2, 0])
lcd.createChar(7, [31, 17, 21, 21, 21, 21, 17, 31])
lcd.createChar(8, [0, 0, 10, 21, 17, 10, 4, 0])  # Heart
lcd.createChar(9, [2, 3, 2, 2, 14, 30, 12, 0])  # Musical note


# Show button state.
lcd.clear()
lcd.backlight(lcd.VIOLET)
lcd.message('I \x08 you Jenni!\nPress a button!')

audio = None

while True:
    # Poll all buttons once, avoids repeated I2C traffic for different cases
    b = lcd.buttons()
    btnUp = b & (1 << lcd.UP)
    btnDown = b & (1 << lcd.DOWN)
    btnLeft = b & (1 << lcd.LEFT)
    btnRight = b & (1 << lcd.RIGHT)
    btnSel = b & (1 << lcd.SELECT)

    def playStream(station_name):
        lcd.clear()
        lcd.message(station_name)
        lcd.backlight(lcd.GREEN)
        audio = pexpect.spawn(
            'sudo mplayer -quiet -playlist ' + stations[station_name])
        # print audio
        audio.logfile_read = log
        print 'Playing ' + station_name

    if btnSel:
        if audio is not None:
            audio.terminate()
        lcd.clear()
        lcd.message('Nighty Night!\n' + s.getsockname()[0])
        lcd.backlight(lcd.RED)
        time.sleep(5)
        lcd.backlight(lcd.OFF)

    elif btnUp:
        if audio is not None:
            audio.terminate()
        playStream("KEXP")

    elif btnDown:
        if audio is not None:
            audio.terminate()
        lcd.clear()
        playStream('WFUV')

    elif btnLeft:
        if audio is not None:
            audio.terminate()
        lcd.clear()
        playStream('TSF Jazz')

    elif btnRight:
        if audio is not None:
            audio.terminate()
        lcd.clear()
        playStream('Radio FIP')
