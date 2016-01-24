#!/usr/bin/python
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

import pexpect
import socket
import time
import sys
import atexit

stations = {
    "KEXP": "http://live-mp3-128.kexp.org:8000/listen.pls",
    "WFUV": "http://www.wfuv.org/sites/all/files/streams/wfuvmp3high.pls",
    "TSF Jazz": "http://tsfjazz.ice.infomaniak.ch/tsfjazz-high.mp3",
    "Radio FIP": "http://audio.scdn.arkena.com/11016/fip-midfi128.mp3"
}


def cleanExit():
    if lcd is not None:
        time.sleep(0.5)
        lcd.backlight(lcd.OFF)
        lcd.clear()
        lcd.stop()
    if audio is not None:
        audio.terminate()


atexit.register(cleanExit)

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

    if btnSel:
        t = time.time()                        # Start time of button press
        while lcd.buttonPressed(lcd.SELECT):   # Wait for button release
            if (time.time() - t) >= 3:  # Turn off if held for 5 seconds.
                if audio is not None:
                    audio.terminate()
                    print "Killing audio"
                lcd.clear()
                lcd.message('Nighty Night!\n' + s.getsockname()[0])
                lcd.backlight(lcd.RED)
                time.sleep(5)
                lcd.backlight(lcd.OFF)
        # # A short press will fippi turn off in 30 minutes.
        # sleeptime = t + 1800  # 30 minutes
        # lcd.clear()
        # lcd.message('Off in 30 min!\n ' + 
        #             time.strftime('%I:%M:%S %p', time.localtime(sleeptime)))
        # time.sleep(5)
        # lcd.backlight(lcd.OFF)
        # while True:
        #     if time.time() >= sleeptime:
        #         break
        # if audio is not None:
        #     audio.terminate()
        #     print "Killing audio"
        # lcd.clear()
        # lcd.message('Nighty Night!\n' + s.getsockname()[0])
        # lcd.backlight(lcd.RED)
        # time.sleep(5)
        # lcd.backlight(lcd.OFF)

    elif btnUp:
        station_name = "KEXP"
        if audio is not None:
            audio.terminate()
            print "Killing audio"
        lcd.clear()
        lcd.message(station_name)
        lcd.backlight(lcd.GREEN)
        audio = pexpect.spawn('sudo mplayer -quiet -playlist ' +
                              stations[station_name])
        print audio
        audio.logfile = sys.stdout
        print 'Playing ' + station_name + ' at ' + stations[station_name]

    elif btnDown:
        station_name = 'WFUV'
        if audio is not None:
            audio.terminate()
            print "Killing audio"
        lcd.clear()
        lcd.message(station_name)
        lcd.backlight(lcd.GREEN)
        audio = pexpect.spawn('sudo mplayer -quiet -playlist ' +
                              stations[station_name])
        print audio
        audio.logfile = sys.stdout
        print 'Playing ' + station_name + ' at ' + stations[station_name]

    elif btnLeft:
        station_name = 'TSF Jazz'
        if audio is not None:
            audio.terminate()
            print "Killing audio"
        lcd.clear()
        lcd.message(station_name)
        lcd.backlight(lcd.GREEN)
        audio = pexpect.spawn('sudo mplayer -quiet ' + stations[station_name])
        audio.logfile = sys.stdout
        print 'Playing ' + station_name + ' at ' + stations[station_name]

    elif btnRight:
        station_name = 'Radio FIP'
        if audio is not None:
            audio.terminate()
            print "Killing audio"
        lcd.clear()
        lcd.message(station_name)
        lcd.backlight(lcd.GREEN)
        audio = pexpect.spawn('sudo mplayer -quiet ' + stations[station_name])
        print audio
        audio.logfile = sys.stdout
        print 'Playing ' + station_name + ' at ' + stations[station_name]
