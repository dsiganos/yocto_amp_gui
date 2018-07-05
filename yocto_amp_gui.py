import os,sys,csv
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
sys.path.append ("yoctolib")
from yocto_api import *
from yocto_current import *

start = True
stopping = False
End = False

class Window(QtGui.QMainWindow):
    def slow(self):
        self.sleepTime = 1000
    def med(self):
        self.sleepTime = 100
    def fast(self):
        self.sleepTime = 10
    def inf(self):
        self.sleepTime = 0
        
    def Tslow(self):
        self.timeLength = 180
    def Tmed(self):
        self.timeLength = 120
    def Tfast(self):
        self.timeLength = 60
    def Tinf(self):
        self.timeLength = 10
        
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("Graph Plotter")
        self.slow()
        self.Tfast()

        extractAction = QtGui.QAction("1000", self)
        extractAction.triggered.connect(self.slow)
        extractAction1 = QtGui.QAction("100", self)
        extractAction1.triggered.connect(self.med)
        extractAction2 = QtGui.QAction("10", self)
        extractAction2.triggered.connect(self.fast)
        extractAction3 = QtGui.QAction("0", self)
        extractAction3.triggered.connect(self.inf)

        extractActionT = QtGui.QAction("180", self)
        extractActionT.triggered.connect(self.Tslow)
        extractActionT1 = QtGui.QAction("120", self)
        extractActionT1.triggered.connect(self.Tmed)
        extractActionT2 = QtGui.QAction("60", self)
        extractActionT2.triggered.connect(self.Tfast)
        extractActionT3 = QtGui.QAction("10", self)
        extractActionT3.triggered.connect(self.Tinf)
        
        self.statusBar()
        mainMenu = self.menuBar()
        sleepMenu = mainMenu.addMenu('&Sleep')
        sleepMenu.addAction(extractAction)
        sleepMenu.addAction(extractAction1)
        sleepMenu.addAction(extractAction2)
        sleepMenu.addAction(extractAction3)
        
        TimeMenu = mainMenu.addMenu('&Time')
        TimeMenu.addAction(extractActionT)
        TimeMenu.addAction(extractActionT1)
        TimeMenu.addAction(extractActionT2)
        TimeMenu.addAction(extractActionT3)
        self.home()

    def home(self):
        btn1 = QtGui.QPushButton("Start", self)
        btn1.clicked.connect(self.ampCounter)
        btn1.resize(100,50)
        btn1.move(200,80)

        btn2 = QtGui.QPushButton("Display", self)
        btn2.clicked.connect(self.ampPlot)
        btn2.resize(100,50)
        btn2.move(200,160)
        
        btn3 = QtGui.QPushButton("Quit", self)
        btn3.clicked.connect(QtCore.QCoreApplication.instance().quit)
        #btn3.clicked.connect(self.over)
        btn3.resize(100,50)
        btn3.move(200,240)

        #self.progress = QtGui.QProgressBar(self)
        #self.progress.setGeometry(200,80,250,20)
        

        self.show()

    def ampCounter(self):
        starttime = time.time()
        timex = 0
        with open("test.csv", "w") as f:
            thewriter = csv.writer(f)
        errmsg = YRefParam()
        target = 'any'
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            sys.exit("init error" + errmsg.value)
        if target == 'any':
            sensor = YCurrent.FirstCurrent()
            if sensor is None:
                print('No module connected')
        else:
            sensor = YCurrent.FindCurrent(target + '.current1')
        if not sensor.isOnline():
            print('Module not connected')
        m = sensor.get_module()
        sensorDC = YCurrent.FindCurrent(m.get_serialNumber() + '.current1')
        print (sensorDC)
        with open("test.csv", "w") as f:
            while sensor.isOnline() and time.time() < (starttime + self.timeLength):
            #while stopping == False:
                timex = time.time() - starttime
                ampval = sensorDC.get_currentValue()
                f.write('%s, %s\n' % (timex, ampval))
                print ('%s, %s' % (timex, ampval))
                YAPI.Sleep(self.sleepTime, errmsg)
                #print ("test" + str(self.timeLength))
        YAPI.FreeAPI()


    def ampPlot(self):
        stopping = True
        #self.ampCounter()
        xtime = []
        ymA = []
        with open('test.csv','r') as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            for row in plots:
                xtime.append(float(row[0]))
                ymA.append(float(row[1]))
        plt.plot(xtime,ymA)
        plt.show()
    
    def starting(self):
        start = True
        
    def stoping(self):
        start = False

    def over(self):
        end = True
        start = False
        
    
def run():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    app.exec_()

run()

    

