from PyQt4.QtGui import QMainWindow, QFileDialog, QDialog, QMessageBox, qApp
from PyQt4.QtCore import QTranslator
from GUI.Windows.ui_MainWindow import Ui_MainWindow
from GUI.ConfigDialog import ConfigDialog
from Common.SysConfig import SysConfig
from GA.GAConfig import GAConfig
from Common.Constraints import CostConstraints, TimeConstraints
from Common.System import System
from Common.Module import Module
from Common.Algorithm import Algorithm
from Common.AlgConfig import AlgConfig
from GA.GA import GA
from GA.HGA import HGA
from GA.GA_optimistic import GA_optimistic
from GA.GA_optimistic_left import GA_optimistic_left
from GA.GA_Moore import GA_Moore
from GA.HGA_Moore import HGA_Moore
import xml.dom.minidom, time, os

class MainWindow(QMainWindow):
    sysconfig = None
    algconfig = None
    sysconfigfile = None
    algconfigfile = None
    constraints = []

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.sysConfigFilter = self.tr("System Configuration files (*.xml)")
        self.algConfigFilter = self.tr("Algorithm Configuration files (*.xml)")
        self.ui.result_filename.setText("result"+str(time.time())+".csv")
        self.best = None
        translator = QTranslator(qApp)
        translator.load("GUI/Windows/Translations/relopt_ru.qm")
        qApp.installTranslator(translator)
        self.ui.retranslateUi(self)

    def LoadSysConf(self):
        if self.ui.sysconfname.text() == None or self.ui.sysconfname.text() == '':
            return
        self.sysconfig = SysConfig()
        self.sysconfig.loadXML(self.ui.sysconfname.text())
        self.constraints = []
        if self.sysconfig.limitcost != None:
            self.constraints.append(CostConstraints(self.sysconfig.limitcost))

    def LoadAlgConf(self):
        f = open(unicode(self.ui.algconfname.text()), "r")
        dom = xml.dom.minidom.parse(f)
        root = dom.childNodes[0]
        if (self.ui.algorithm.currentIndex()==0 or self.ui.algorithm.currentIndex()==1 or
                self.ui.algorithm.currentIndex() == 2 or self.ui.algorithm.currentIndex()==3 or
                self.ui.algorithm.currentIndex() == 4 or self.ui.algorithm.currentIndex() == 5):
            self.algconfig = GAConfig()
        self.algconfig.LoadFromXmlNode(root)

    def Run(self):
        if self.sysconfig == None:
            QMessageBox.critical(self, "An error occurred", "System configuration must be defined")
            return
        Module.conf = self.sysconfig
        if self.constraints == None:
            QMessageBox.critical(self, "An error occurred", "Constraints must be defined")
            return
        System.constraints = self.constraints
        if self.algconfig == None and self.ui.algorithm.currentIndex() < 2 :
            QMessageBox.critical(self, "An error occurred", "Algorithm configuration must be defined")
            return
        Algorithm.algconf = self.algconfig
        if Algorithm.algconf == None:
            Algorithm.algconf = AlgConfig()

        algidx = self.ui.algorithm.currentIndex()
        if algidx==0:
            algorithm = GA()
        elif algidx==1:
            algorithm = HGA()
        elif algidx==2:
            algorithm = GA_optimistic()
        elif algidx==3:
            algorithm = GA_optimistic_left()
        elif algidx==4:
            algorithm = GA_Moore()
        elif algidx==5:
            algorithm = HGA_Moore()
        Algorithm.result_filename = self.ui.result_filename.text()
        for i in range(self.ui.execNum.value()):
            if algorithm.algconf.metamodel:
                algorithm.algconf.metamodel.Clear()
            algorithm.Run()
            self.best = algorithm.currentSolution
        algorithm.PrintStats()
        try:
            os.remove("sch" + str(os.getpid()) + ".xml")
            os.remove("res" + str(os.getpid()) + ".xml")
        except:
            pass

    def OpenSysConf(self):
        name = unicode(QFileDialog.getOpenFileName(filter=self.sysConfigFilter))
        if name == None or name == '':
            return
        self.sysconfigfile = name
        self.ui.sysconfname.setText(name)
        self.LoadSysConf()
        costrange = self.sysconfig.costInterval()
        timerange = self.sysconfig.timeInterval()
        self.ui.maxcost.setText(str(costrange[1]))
        self.ui.mincost.setText(str(costrange[0]))
        self.ui.maxtime.setText(str(timerange[1]).replace("]","").replace("[",""))
        self.ui.mintime.setText(str(timerange[0]).replace("]","").replace("[",""))
        self.ui.limitcost.setText(str(self.sysconfig.limitcost) if self.sysconfig.limitcost != None else "")

    def OpenAlgConf(self):
        name = unicode(QFileDialog.getOpenFileName(filter=self.algConfigFilter))
        if name == None or name == '':
            return
        self.algconfigfile = name
        self.ui.algconfname.setText(name)
        self.LoadAlgConf()

    def Random(self):
        d = ConfigDialog()
        d.exec_()
        if d.result() == QDialog.Accepted: 
            dict = d.GetResult()
        else:
            return
        self.sysconfig = SysConfig()
        self.sysconfig.generateRandom(dict)
        costrange = self.sysconfig.costInterval()
        timerange = self.sysconfig.timeInterval()
        self.ui.maxcost.setText(str(costrange[1]))
        self.ui.mincost.setText(str(costrange[0]))
        self.ui.maxtime.setText(str(timerange[1]).replace("]","").replace("[",""))
        self.ui.mintime.setText(str(timerange[0]).replace("]","").replace("[",""))
        self.ui.limitcost.setText("")
        self.ui.limittimes.setText("")
        self.ui.sysconfname.setText("")
        self.constraints = []

    def InputTimeLimits(self):
        if self.ui.limittimes.text() == "":
            return
        for constr in self.constraints:
            if isinstance(constr,TimeConstraints):
                self.constraints.remove(constr)
                break
        l = []
        for c in self.ui.limittimes.text().split(","):
            l.append(int(c))
        self.constraints.append(TimeConstraints(l))
        for m,t in zip(self.sysconfig.modules, l):
            m.limittime = t

    def InputCostLimit(self):
        if self.ui.limitcost.text() == "":
            return
        for constr in self.constraints:
            if isinstance(constr,CostConstraints):
                self.constraints.remove(constr)
                break
        c = int(self.ui.limitcost.text())
        self.constraints.append(CostConstraints(c))
        self.sysconfig.limitcost = c

    def SaveSysConf(self):
        name = unicode(QFileDialog.getSaveFileName(filter=self.sysConfigFilter))
        if name == None or name == '':
            return
        self.sysconfig.saveXML(name)

    def no_checked(self):
        if self.ui.checktime_yes.isChecked():
            return
        for constr in self.constraints:
            if isinstance(constr,TimeConstraints):
                self.constraints.remove(constr)
                break
        self.ui.limittimes.setText("")
        self.ui.limittimes.setEnabled(False)

    def yes_checked(self):
        if not self.ui.checktime_yes.isChecked():
            return
        self.ui.limittimes.setEnabled(True)
        if self.sysconfig == None:
            return
        c = self.sysconfig.getLimitTimes()     
        if c != None:
            self.constraints.append(TimeConstraints(c))
            self.ui.limittimes.setText(str(c).replace("]","").replace("[",""))





