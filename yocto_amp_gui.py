import os,sys,csv,threading
from threading import Thread, Lock
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
import matplotlib.animation as animation
sys.path.append ("yoctolib")
from yocto_api import *
from yocto_current import *

mutex = Lock()
timeList = []
ymAList = []
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

class Window(QtGui.QMainWindow):
    
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50, 100, 500, 300)
        self.setWindowTitle("Graph Plotter")

        sleepCombo = QtGui.QComboBox(self)
        sleepCombo.addItem("1000")
        sleepCombo.addItem("100")
        sleepCombo.addItem("10")
        sleepCombo.addItem("0")
        sleepCombo.move(50, 250)
        sleepCombo.activated[str].connect(worker.sleepTimeSet)
        sleepCombo.setEditable(True)

        timeCombo = QtGui.QComboBox(self)
        timeCombo.addItem("180")
        timeCombo.addItem("120")
        timeCombo.addItem("60")
        timeCombo.addItem("10")
        timeCombo.move(200, 250)
        timeCombo.activated[str].connect(worker.timeLengthSet)
        timeCombo.setEditable(True)

        startBtn = QtGui.QPushButton("Start", self)
        startBtn.clicked.connect(worker.startWork)
        startBtn.resize(100,50)
        startBtn.move(200,20)

        self.displayBtn = QtGui.QPushButton("Display", self)
        self.displayBtn.setDisabled(True)
        self.displayBtn.clicked.connect(worker.plotGraph)
        self.displayBtn.resize(100,50)
        self.displayBtn.move(200,100)

        stopBtn = QtGui.QPushButton("stop", self)
        stopBtn.clicked.connect(worker.stopWork)
        stopBtn.resize(100,50)
        stopBtn.move(350,20)

        liveBtn = QtGui.QPushButton("live", self)
        liveBtn.clicked.connect(go)
        liveBtn.resize(100,50)
        liveBtn.move(350,100)

        self.show()

    def mustStart(self):
        choice = QtGui.QMessageBox.question(self, 'Must be reading amps',
                                            "Do you want to start reading now?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            worker.startWork()
        else:
            pass

    def missing(self):
        plug = QtGui.QMessageBox.critical(self, 'Error',
                                 "Please plug in yotco amp module")

    def displayGrayF(self):
        self.displayBtn.setDisabled(False)

    def displayGrayT(self):
        self.displayBtn.setDisabled(True)

class WorkerThread(threading.Thread):

    def sleepTimeSet(self, text):
        self.sleepTime = int(text)

    def timeLengthSet(self, text):
        self.timeLength = int(text)

    def startWork(self):
        self.go = True
        self.gone = True
        GUI.displayGrayT()

    def stopWork(self):
        if self.gone == False:
            GUI.mustStart()
        else:
            self.go = False
            GUI.displayGrayF()

    def __init__(self):
        self.go = False
        self.gone = False
        self.sleepTime = 1000
        self.timeLength = 180
        self.die = False
        threading.Thread.__init__(self)

    def run(self):
        while not self.die:
            while self.go:
                self.collectValues()
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
            GUI.missing()
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
                mutex.acquire()
                try:
                    timeList.append(timex)
                    ymAList.append(ampval)
                finally:
                    mutex.release()
                f.write('%s, %s\n' % (timex, ampval))
                print ('%s, %s' % (timex, ampval))
                if self.sleepTime > 0:
                    YAPI.Sleep(self.sleepTime, errmsg)
        YAPI.FreeAPI()

    def plotGraph(self):
        stopping = True
        xtime = []
        ymA = []
        with open('data_'+str(int(self.starttime))+'.csv','r') as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            for row in plots:
                xtime.append(float(row[0]))
                ymA.append(float(row[1]))
        plt.plot(xtime,ymA)
        plt.show()

    def kill(self):
        self.die = True

class LiveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def animate(self, i):
        ax1.clear()
        mutex.acquire()
        try:
            ax1.plot(timeList,ymAList)
        finally:
            mutex.release()

    def run(self):
        print ("test")

def run():
    global worker
    global live
    global GUI
    worker = WorkerThread()
    live = LiveThread()
    worker.start()
    live.start()
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    app.exec_()
    worker.kill()

def go():
    print ("test1")
    ani = animation.FuncAnimation(fig, live.animate, interval=500)
    print ("test2")
    plt.show()

run()
