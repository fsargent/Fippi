FROM balenalib/raspberry-pi2-python:3.7.4-build

WORKDIR /usr/src/app
RUN install_packages \
  mplayer \
  alsa-utils
RUN pip3 install \
  adafruit-blinka \
  adafruit-circuitpython-charlcd \
  adafruit-circuitpython-busdevice \
  pexpect \
  python-dotenv \
  RPI.GPIO 
COPY ./fippi ./

ENV UDEV=1
CMD modprobe i2c-dev && python3 ./fippi.py