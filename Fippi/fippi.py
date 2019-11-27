#!/usr/bin/python
import os
import pexpect
import socket
import time
import sys

import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
from dotenv import load_dotenv
load_dotenv()
stations = [os.getenv("STATION0"), os.getenv("STATION1"),
            os.getenv("STATION2"), os.getenv("STATION3")]
if stations == []:
    stations = ["KEXP|http://live-mp3-128.kexp.org:8000/listen.pls",
                "WFUV|http://www.wfuv.org/sites/all/files/streams/wfuvmp3high.pls",
                "TSF Jazz|http://tsfjazz.ice.infomaniak.ch/tsfjazz-high.mp3",
                "Radio FIP|http://audio.scdn.arkena.com/11016/fip-midfi128.mp3"]


# Initialise I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

# Initialise the LCD class
# Modify this if you have a different sized Character LCD
lcd_columns = 16
lcd_rows = 2
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

# lcd = Adafruit_CharLCDPlate()
lcd.clear()

# Show IP address (if network is available).  System might be freshly
# booted and not have an address yet, so keep trying for a couple minutes
# before reporting failure.
t = time.time()
while True:
    if (time.time() - t) > 120:
        # No connection reached after 2 minutes
        lcd.color = [100, 0, 0]
        lcd.message = "Network is\nunreachable"
        time.sleep(30)
        exit(0)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 0))
        lcd.color = [0, 0, 100]
        lcd.message = ("My IP address is\n" + s.getsockname()[0])
        time.sleep(5)
        break  # Success -- let's hear some music!
    except:
        time.sleep(1)  # Pause a moment, keep trying


# create some custom characters
lcd.create_char(1, [2, 3, 2, 2, 14, 30, 12, 0])
lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])
lcd.create_char(3, [0, 14, 21, 23, 17, 14, 0, 0])
lcd.create_char(4, [31, 17, 10, 4, 10, 17, 31, 0])
lcd.create_char(5, [8, 12, 10, 9, 10, 12, 8, 0])
lcd.create_char(6, [2, 6, 10, 18, 10, 6, 2, 0])
lcd.create_char(7, [31, 17, 21, 21, 21, 21, 17, 31])
lcd.create_char(8, [0, 0, 10, 21, 17, 10, 4, 0])  # Heart
lcd.create_char(9, [2, 3, 2, 2, 14, 30, 12, 0])  # Musical note


# Show button state.
lcd.clear()
lcd.color = [50, 0, 50]
lcd.message = "I \x08 you Jenni!\nPress a button!"


class Fippi:
    def playStation(self, index):
        self.audio = None
        station_name = stations[index].split(sep="|")[0]
        station_url = stations[index].split(sep="|")[1]

        if self.audio is not None:
            self.audio.terminate()
            print("Killing audio")
        lcd.clear()
        lcd.message = station_name
        lcd.color = [0, 0, 100]
        audio = pexpect.spawn(
            "sudo mplayer -quiet -playlist " + station_url)
        print(audio)
        print("Playing " + station_name + " at " + station_url)

    def run(self):
        while True:
            if lcd.up_button:
                self.playStation(0)
            if lcd.down_button:
                self.playStation(1)
            if lcd.left_button:
                self.playStation(2)
            if lcd.right_button:
                self.playStation(3)
            if lcd.select_button:
                t = time.time()  # Start time of button press
                while lcd.select_button:  # Wait for button release
                    # Turn off if held for 5 seconds.
                    if (time.time() - t) >= 3:
                        if self.audio is not None:
                            self.audio.terminate()
                            print("Killing audio")
                        lcd.clear()
                        lcd.message = ("Nighty Night!\n" + s.getsockname()[0])
                        lcd.color = [100, 0, 0]
                        time.sleep(5)
                        lcd.color = [0, 0, 0]

                # Main function
if __name__ == "__main__":
    fippi = Fippi()
    if (not fippi.run()):
        fippi.print_help()
