import os,sys,csv
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
sys.path.append ("yoctolib")
from yocto_api import *
from yocto_current import *
import threading

start = False
stopping = False
End = False
xtime = []
ymA = []

class Window(QtGui.QMainWindow):
    
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("Graph Plotter")


        comboBox = QtGui.QComboBox(self)
        comboBox.addItem("1000")
        comboBox.addItem("100")
        comboBox.addItem("10")
        comboBox.addItem("0")
        comboBox.move(50, 250)
        comboBox.activated[str].connect(worker.sleepChoice)
        comboBox.setEditable(True)

        comboBox1 = QtGui.QComboBox(self)
        comboBox1.addItem("180")
        comboBox1.addItem("120")
        comboBox1.addItem("60")
        comboBox1.addItem("10")
        comboBox1.move(200, 250)
        comboBox1.activated[str].connect(worker.timeChoice)
        comboBox1.setEditable(True)
        
        self.home()

    def home(self):
        btn1 = QtGui.QPushButton("Start", self)
        btn1.clicked.connect(worker.startWork)
        btn1.resize(100,50)
        btn1.move(200,20)

        btn2 = QtGui.QPushButton("Display", self)
        btn2.clicked.connect(worker.ampPlot)
        btn2.resize(100,50)
        btn2.move(50,100)

        btns = QtGui.QPushButton("stop", self)
        btns.clicked.connect(worker.stop)
        btns.resize(100,50)
        btns.move(200,100)

        btn3 = QtGui.QPushButton("Quit", self)
        btn3.clicked.connect(QtCore.QCoreApplication.instance().quit)
        btn3.resize(100,50)
        btn3.move(200,180)
        
        self.show()

        
class workerThread(threading.Thread):

    def sleepChoice(self, text):
        self.sleepTime = int(text)

    def timeChoice(self, text):
        self.timeLength = int(text)
        
    def startWork(self):
        self.go = True
        
    def stop(self):
        self.go = False
        
    def __init__(self):
        self.go = False
        self.sleepTime = 1000
        self.timeLength = 10
        threading.Thread.__init__(self)

    def run(self):
        while True:
            while self.go:
                self.ampCounter()

    def ampCounter(self):
        self.starttime = time.time()
        timex = 0
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
        with open('data_'+str(int(self.starttime))+'.csv', "w") as f:
            while sensor.isOnline() and time.time() < (self.starttime + self.timeLength):
                while self.go:
                    timex = time.time() - self.starttime
                    ampval = float(sensorDC.get_currentRawValue())
                    f.write('%s, %s\n' % (timex, ampval))
                    print ('%s, %s' % (timex, ampval))
                    YAPI.Sleep(self.sleepTime, errmsg)
        YAPI.FreeAPI()


    def ampPlot(self):
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
    
    def starting(self):
        start = True
        
    def stoping(self):
        start = False

    def over(self):
        end = True
        start = False

    
    
def run():
    #print ("test")
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    app.exec_()

#p = Window(self)
#makeT = threading.Thread(target= run,args=())
#plotT = threading.Thread(target= p.ampPlot,args=())
#plotT.start
#makeT.start
run()

    

