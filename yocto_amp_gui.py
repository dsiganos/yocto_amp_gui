import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt4 import QtGui, QtCore
import random
import sys
import time
import os
import sys
import csv
import threading

sys.path.append ("yoctolib")
from yocto_api import *
from yocto_current import *

class GraphClosedEvent(QtCore.QEvent):
    """
    Event that will be sent to Qt main loop to inform it of closure of Tk matoplotlib windows
    """
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self):
        super(GraphClosedEvent, self).__init__(self.EVENT_TYPE)

class TkThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.job = None
        self.die = False

    def run(self):
        while not self.die:
            if self.job:
                self.job()
                self.job = None
            else:
                time.sleep(0.1)

    def postjob(self, job):
        self.job = job

    def kill(self):
        self.die = True

class LastGraph:
    def __init__(self, gui, starttime):
        self.gui = gui
        self.starttime = starttime

    def __call__(self):
        xdata, ydata = [], []
        with open('data_%s.csv' % str(int(self.starttime)), 'r') as csvfile:
            cvsreader = csv.reader(csvfile, delimiter=',')
            for row in cvsreader:
                xdata.append(float(row[0]))
                ydata.append(float(row[1]))

        fig, axes = plt.subplots()
        fig.canvas.mpl_connect('close_event', self.handle_close)
        plt.plot(xdata, ydata)
        plt.show()

    def handle_close(self, evt):
        QtGui.QApplication.postEvent(self.gui, GraphClosedEvent())
        print('Closed Display Last Graph!')

class LiveData:
    def __init__(self):
        self.mutex = threading.Lock()
        self.xdata = []
        self.ydata = []
        self.islive = False

    def add_point(self, x, y):
        self.mutex.acquire()
        if self.islive:
            self.xdata.append(x)
            self.ydata.append(y)
        self.mutex.release()

    def get_data(self):
        self.mutex.acquire()
        xdata, ydata = self.xdata, self.ydata
        self.mutex.release()
        return xdata, ydata

    def start_capture(self):
        self.mutex.acquire()
        self.xdata, self.ydata = [], []
        self.islive = True
        self.mutex.release()

    def stop_capture(self):
        self.mutex.acquire()
        self.islive = False
        self.mutex.release()

class LiveGraph:
    def __init__(self, gui, livedata):
        self.gui = gui
        self.livedata = livedata
        self.fig = None
        self.axes = None
        self.line = None

    def animate(self, i):
        xdata, ydata = self.livedata.get_data()
        if len(xdata) > 0:
            self.line.set_xdata(xdata)
            self.line.set_ydata(ydata)
            self.axes.set_xlim(min(xdata), max(xdata))
            self.axes.set_ylim(min(ydata), max(ydata))

    def __call__(self):
        self.livedata.start_capture()
        try:
            self.fig, self.axes = plt.subplots()
            self.fig.canvas.mpl_connect('close_event', self.handle_close)
            self.line, = self.axes.plot([], [])
            self.ani = animation.FuncAnimation(self.fig, self.animate, interval=2000, save_count=1000)
            plt.show()
        finally:
            self.livedata.stop_capture()

    def stop(self):
        self.ani.event_source.stop()

    def handle_close(self, evt):
        QtGui.QApplication.postEvent(self.gui, GraphClosedEvent())
        print('Closed Live Graph!')

class Window(QtGui.QMainWindow):
    def __init__(self, tkthread, worker, livedata):
        super(Window, self).__init__()
        self.tkthread = tkthread
        self.worker = worker
        self.livedata = livedata

        self.setGeometry(50, 100, 500, 300)
        self.setWindowTitle("Graph Plotter")

        self.sleepCombo = QtGui.QComboBox(self)
        self.sleepCombo.addItems(['1000', '100', '10', '0'])
        self.sleepCombo.move(50, 250)
        self.sleepCombo.setEditable(True)

        self.timeCombo = QtGui.QComboBox(self)
        self.timeCombo.addItems(['180', '120', '60', '10'])
        self.timeCombo.move(200, 250)
        self.timeCombo.setEditable(True)

        self.startBtn = QtGui.QPushButton("Start", self)
        self.startBtn.clicked.connect(self.start)
        self.startBtn.resize(100,50)
        self.startBtn.move(200,20)

        self.stopBtn = QtGui.QPushButton("Stop", self)
        self.stopBtn.setDisabled(True)
        self.stopBtn.clicked.connect(self.stop)
        self.stopBtn.resize(100,50)
        self.stopBtn.move(350,20)

        self.displayBtn = QtGui.QPushButton("Display Last", self)
        self.displayBtn.setDisabled(True)
        self.displayBtn.clicked.connect(self.display)
        self.displayBtn.resize(100,50)
        self.displayBtn.move(200,100)

        self.liveBtn = QtGui.QPushButton("Live", self)
        self.liveBtn.clicked.connect(self.live)
        self.liveBtn.resize(100,50)
        self.liveBtn.move(350,100)

        self.show()

    def missing(self):
        plug = QtGui.QMessageBox.critical(self, 'Error',
                                 "Please plug in yocto amp module")

    def start(self):
        self.startBtn.setDisabled(True)
        self.stopBtn.setEnabled(True)
        self.displayBtn.setDisabled(True)
        sleepTime = int(self.sleepCombo.currentText())
        timeLength = int(self.timeCombo.currentText())
        self.worker.startWork(sleepTime, timeLength)

    def stop(self):
        self.startBtn.setEnabled(True)
        self.stopBtn.setDisabled(True)
        self.displayBtn.setEnabled(True ^ (not self.liveBtn.isEnabled()))
        self. worker.stopWork()

    def live(self):
        self.liveBtn.setDisabled(True)
        self.displayBtn.setDisabled(True)
        self.tkthread.postjob(LiveGraph(self, self.livedata))

    def display(self):
        self.liveBtn.setDisabled(True)
        self.displayBtn.setDisabled(True)
        self.tkthread.postjob(LastGraph(self, self.worker.starttime))

    def event(self, event):
        if type(event) != GraphClosedEvent:
            return super(Window, self).event(event)
        event.accept()
        self.liveBtn.setEnabled(True)
        self.displayBtn.setEnabled(True ^ (not self.startBtn.isEnabled()))
        return True

class WorkerThread(threading.Thread):
    def __init__(self, livedata):
        threading.Thread.__init__(self)
        self.go = False
        self.die = False
        self.livedata = livedata

    def startWork(self, sleepTime, timeLength):
        self.sleepTime = sleepTime
        self.timeLength = timeLength
        self.go = True

    def stopWork(self):
        self.go = False

    def run(self):
        while not self.die:
            while self.go:
                self.collectValues()
            time.sleep(0.1)
        print("thread is dead")

    def collectValues(self):
        self.starttime = time.time()
        timex = 0
        errmsg = YRefParam()
        target = 'any'
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            sys.exit("init error" + errmsg.value)
        sensor = YCurrent.FirstCurrent()
        if sensor is None:
            #GUI.missing()
            self.go = False
            return
        else:
            pass
        m = sensor.get_module()
        sensorDC = YCurrent.FindCurrent(m.get_serialNumber() + '.current1')
        print (sensorDC)
        with open('data_'+str(int(self.starttime))+'.csv', "w") as f:
            while sensor.isOnline() and time.time() < (self.starttime + self.timeLength) and self.go == True:
                timex = time.time() - self.starttime
                ampval = float(sensorDC.get_currentRawValue())
                self.livedata.add_point(timex, ampval + random.randint(1,101))
                f.write('%s, %s\n' % (timex, ampval))
                print ('%s, %s' % (timex, ampval))
                if self.sleepTime > 0:
                    YAPI.Sleep(self.sleepTime, errmsg)
        YAPI.FreeAPI()

    def kill(self):
        self.die = True

    def handle_display_last_close(self, evt):
        print('Closed Display Last Graph!')

def main():
    livedata = LiveData()

    tkthread = TkThread()
    tkthread.start()

    worker = WorkerThread(livedata)
    worker.start()

    app = QtGui.QApplication(sys.argv)
    GUI = Window(tkthread, worker, livedata)
    app.exec_()

    worker.kill()
    tkthread.kill()

    worker.join()
    tkthread.join()

if __name__ == "__main__":
    main()
