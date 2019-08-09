#!/usr/bin/python
import os,sys,csv,threading
from threading import Thread, Lock
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
import matplotlib.animation as animation
sys.path.append ("yoctolib")
from yocto_api import *
from yocto_current import *


def run():
    timex = 0
    starttime = time.time()
    errmsg = YRefParam()
    target = 'any'
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        print "Failed to register hub (connecting to usb device)"
        sys.exit(1)
    sensor = YCurrent.FirstCurrent()
    print sensor
    m = sensor.get_module()
    print m
    sensorDC = YCurrent.FindCurrent(m.get_serialNumber() + '.current1')
    print (sensorDC)
    while True:
        timex = time.time() - starttime
        ampval = float(sensorDC.get_currentRawValue())
        print ('%s, %s' % (timex, ampval))
    YAPI.FreeAPI()

run()
