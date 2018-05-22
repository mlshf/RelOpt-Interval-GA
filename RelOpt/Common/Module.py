import random
import math
from Common.Schedule import Task, Link

class Module:
    '''Base class for system module.
    :param num: Number of module.
    :param hw: List of used HW versions. DO NOT USE -1 FOR ABSENT VERSIONS!
    :param sw: List of used SW versions. DO NOT USE -1 FOR ABSENT VERSIONS!
    '''
    conf = None
    def __init__(self, num, hw, sw):
        self.num = num
        self.hw = hw
        self.sw = sw
        self.time = -1
        self.cost = -1
        self.relL = -1.0
        self.relR = -1.0
        self._computeRel()
        self._computeCost()
        self._computeExecTime()
        self.conf.modules[self.num].type = self.__class__.__name__

    def __eq__(self, other):
        '''Operator ==
        '''
        return self.num ==  other.num and self.hw == other.hw and self.sw == other.sw

class NONE(Module):
    '''Class for module with NONE mechanism.
    :param num: number of module
    :param hw: List of used HW versions. DO NOT USE -1 FOR ABSENT VERSIONS! MUST CONTAIN 0 OR 1 ELEMENT.
    :param sw: List of used SW versions. DO NOT USE -1 FOR ABSENT VERSIONS! MUST CONTAIN 0 OR 1 ELEMENT.

    If len(hw) == 0  and len(sw) == 0 module is generated randomly.
    '''
    def __init__(self, num, hw = [], sw = []):
        if hw == [] and sw == []:
            hw = [random.randint(0, len(self.conf.modules[num].hw)-1)]
            sw = [random.randint(0, len(self.conf.modules[num].sw)-1)]
        Module.__init__(self, num, hw, sw)

    def toSchedule(self, schedule):
        '''Adds elements, corresponding to module to schedule.
        :param schedule: object of class 'Schedule'.
        '''
        schedule.tasks.append(Task("t"+str(self.num), self.execTime, "p"+str(self.num), 0))

    def _computeRel(self):
        self.relL = self.conf.modules[self.num].hw[self.hw[0]].relL * self.conf.modules[self.num].sw[self.sw[0]].relR
        self.relR = self.conf.modules[self.num].hw[self.hw[0]].relR * self.conf.modules[self.num].sw[self.sw[0]].relR

    def _computeCost(self):
        self.cost = self.conf.modules[self.num].hw[self.hw[0]].cost + self.conf.modules[self.num].sw[self.sw[0]].cost

    def _computeExecTime(self):
        self.execTime = self.conf.modules[self.num].times[self.sw[0]][self.hw[0]]

    def __str__(self):
        '''Converts module to string. So we can 'print module'
        '''
        return "\t"+str(self.num)+ ". None:" + str(self.hw) + str(self.sw) + "\n"

class NVP01(Module):
    def __init__(self, num, hw=[], sw=[]):
        if hw == [] and sw == []:
            hw = [random.randint(0, len(self.conf.modules[num].hw)-1)]
            sw1 = random.randint(0, len(self.conf.modules[num].sw)-3)
            sw2 = random.randint(sw1+1, len(self.conf.modules[num].sw)-2)
            sw = [sw1, sw2, random.randint(sw2+1, len(self.conf.modules[num].sw)-1)]
        Module.__init__(self, num, hw, sw)

    def _computeRel(self):
        QhwL = self.conf.modules[self.num].hw[self.hw[0]].relL
        QhwR = self.conf.modules[self.num].hw[self.hw[0]].relR
        PhwL = 1 - QhwR
        PhwR = 1 - QhwL
        Qsw0L = self.conf.modules[self.num].sw[self.sw[0]].relL
        Qsw0R = self.conf.modules[self.num].sw[self.sw[0]].relR
        Psw0L = 1 - Qsw0R
        Psw0R = 1 - Qsw0L
        Qsw1L = self.conf.modules[self.num].sw[self.sw[1]].relL
        Qsw1R = self.conf.modules[self.num].sw[self.sw[1]].relR
        Psw1L = 1 - Qsw1R
        Psw1R = 1 - Qsw1L
        Qsw2L = self.conf.modules[self.num].sw[self.sw[2]].relL
        Qsw2R = self.conf.modules[self.num].sw[self.sw[2]].relR
        Psw2L = 1 - Qsw2R
        Psw2R = 1 - Qsw2L
        QrvL = self.conf.modules[self.num].qrvL
        QrvR = self.conf.modules[self.num].qrvR
        PrvL = 1 - QrvR
        PrvR = 1 - QrvL
        QdL = self.conf.modules[self.num].qdL
        QdR = self.conf.modules[self.num].qdR
        PdL = 1 - QdR
        PdR = 1 - QdL
        QallL = self.conf.modules[self.num].qallL
        QallR = self.conf.modules[self.num].qallR
        PallL = 1 - QallR
        PallR = 1 - QallL

        PL = (PrvL +
              QrvL * PrvL +
              QrvL * QrvL * PrvL +
              QrvL * QrvL * QrvL * PdL +
              QrvL * QrvL * QrvL * QdL * PallL +
              QrvL * QrvL * QrvL * QdL * QallL * PhwL +
              QrvL * QrvL * QrvL * QdL * QallL * QhwL * Psw0L * Psw1L +
              QrvL * QrvL * QrvL * QdL * QallL * QhwL * Qsw0L * Psw1L * Psw2L +
              QrvL * QrvL * QrvL * QdL * QallL * QhwL * Qsw1L * Psw0L * Psw2L)

        PR = (PrvR +
              QrvR * PrvR +
              QrvR * QrvR * PrvR +
              QrvR * QrvR * QrvR * PdR +
              QrvR * QrvR * QrvR * QdR * PallR +
              QrvR * QrvR * QrvR * QdR * QallR * PhwR +
              QrvR * QrvR * QrvR * QdR * QallR * QhwR * Psw0R * Psw1R +
              QrvR * QrvR * QrvR * QdR * QallR * QhwR * Qsw0R * Psw1R * Psw2R +
              QrvR * QrvR * QrvR * QdR * QallR * QhwR * Qsw1R * Psw0R * Psw2R)
        
        self.relL = 1 - PR
        self.relR = 1 - PL

    def _computeCost(self):
        self.cost = (self.conf.modules[self.num].hw[self.hw[0]].cost +
                     self.conf.modules[self.num].sw[self.sw[0]].cost +
                     self.conf.modules[self.num].sw[self.sw[1]].cost +
                     self.conf.modules[self.num].sw[self.sw[2]].cost)
        
    def _computeExecTime(self):
        self.execTime = (self.conf.modules[self.num].times[self.sw[0]][self.hw[0]] +
                         self.conf.modules[self.num].times[self.sw[1]][self.hw[0]] +
                         self.conf.modules[self.num].times[self.sw[2]][self.hw[0]] +
                         self.conf.modules[self.num].tvote)

    def toSchedule(self, schedule):
        schedule.tasks.append(Task("t"+str(self.num), self.execTime, "p"+str(self.num), 0))

    def __str__(self):
        return "\t"+str(self.num)+ ". NVP01:" + str(self.hw) + str(self.sw) + "\n"


class NVP11(Module):
    def __init__(self, num, hw = [], sw = []):
        if hw == [] and sw == []:
            hw = [random.randint(0, len(self.conf.modules[num].hw)-1),
                  random.randint(0, len(self.conf.modules[num].hw)-1),
                  random.randint(0, len(self.conf.modules[num].hw)-1)]
            sw1 = random.randint(0, len(self.conf.modules[num].sw)-3)
            sw2 = random.randint(sw1+1, len(self.conf.modules[num].sw)-2)
            sw = [sw1, sw2, random.randint(sw2+1, len(self.conf.modules[num].sw)-1)]
        Module.__init__(self, num, hw, sw)

    def _computeRel(self):
        Qhw0L = self.conf.modules[self.num].hw[self.hw[0]].relL
        Qhw0R = self.conf.modules[self.num].hw[self.hw[0]].relR
        Phw0L = 1 - Qhw0R
        Phw0R = 1 - Qhw0L
        Qhw1L = self.conf.modules[self.num].hw[self.hw[1]].relL
        Qhw1R = self.conf.modules[self.num].hw[self.hw[1]].relR
        Phw1L = 1 - Qhw1R
        Phw1R = 1 - Qhw1L
        Qhw2L = self.conf.modules[self.num].hw[self.hw[2]].relL
        Qhw2R = self.conf.modules[self.num].hw[self.hw[2]].relR
        Phw2L = 1 - Qhw2R
        Phw2R = 1 - Qhw2L
        Qsw0L = self.conf.modules[self.num].sw[self.sw[0]].relL
        Qsw0R = self.conf.modules[self.num].sw[self.sw[0]].relR
        Psw0L = 1 - Qsw0R
        Psw0R = 1 - Qsw0L
        Qsw1L = self.conf.modules[self.num].sw[self.sw[1]].relL
        Qsw1R = self.conf.modules[self.num].sw[self.sw[1]].relR
        Psw1L = 1 - Qsw1R
        Psw1R = 1 - Qsw1L
        Qsw2L = self.conf.modules[self.num].sw[self.sw[2]].relL
        Qsw2R = self.conf.modules[self.num].sw[self.sw[2]].relR
        Psw2L = 1 - Qsw2R
        Psw2R = 1 - Qsw2L
        QrvL = self.conf.modules[self.num].qrvL
        QrvR = self.conf.modules[self.num].qrvR
        PrvL = 1 - QrvR
        PrvR = 1 - QrvL
        QdL = self.conf.modules[self.num].qdL
        QdR = self.conf.modules[self.num].qdR
        PdL = 1 - QdR
        PdR = 1 - QdL
        QallL = self.conf.modules[self.num].qallL
        QallR = self.conf.modules[self.num].qallR
        PallL = 1 - QallR
        PallR = 1 - QallL
        Qrv3L = QrvL ** 3
        Qrv3R = QrvR ** 3

        PL = (PrvL +
              QrvL * PrvL +
              QrvL * QrvL * PrvL +
              Qrv3L * PdL +
              Qrv3L * QdL * PallL +
              Psw0L * Psw1L * Qrv3L * QdL * QallL +
              Psw0L * Psw2L * Qsw1L * Qrv3L * QdL * QallL +
              Psw2L * Psw1L * Qsw0L * Qrv3L * QdL * QallL +
              Psw0L * Phw0L * Phw1L * Qsw1L * Qsw2L * Qrv3L * QdL * QallL * Qhw2L +
              Qrv3L * QdL * QallL * Phw0L * Phw2L * Qhw1L * Qsw2L * (1 - Psw0L * Psw1L) +
              Psw2L * Phw0L * Phw2L * Qsw0L * Qsw1L * Qrv3L * QdL * QallL * Qhw1L +
              Qrv3L * QdL * QallL * Phw1L * Phw2L * Qhw0L * Qsw1L * (1 - Psw0L * Psw2L) +
              Psw1L * Phw1L * Phw2L * Qsw0L * Qsw2L * Qrv3L * QdL * QallL * Qhw0L +
              Qrv3L * QdL * QallL * Phw0L * Phw1L * Qhw2L * Qsw0L * (1 - Psw2L * Psw1L) +
              Qrv3L * QdL * QallL * Psw0L * Qhw0L * Qsw1L * Qhw1L * Qsw2L * Phw2L +
              Qrv3L * QdL * QallL * Psw0L * Qhw0L * Qsw1L * Phw1L * Qsw2L * Qhw2L +
              Qrv3L * QdL * QallL * Qsw0L * Qhw0L * Psw1L * Qhw1L * Qsw2L * Phw2L +
              Qrv3L * QdL * QallL * Qsw0L * Phw0L * Psw1L * Qhw1L * Qsw2L * Qhw2L +
              Qrv3L * QdL * QallL * Qsw0L * Qhw0L * Qsw1L * Phw1L * Psw2L * Qhw2L +
              Qrv3L * QdL * QallL * Qsw0L * Phw0L * Qsw1L * Qhw1L * Psw2L * Qhw2L)

        PR = (PrvR +
              QrvR * PrvR +
              QrvR * QrvR * PrvR +
              Qrv3R * PdR +
              Qrv3R * QdR * PallR +
              Psw0R * Psw1R * Qrv3R * QdR * QallR +
              Psw0R * Psw2R * Qsw1R * Qrv3R * QdR * QallR +
              Psw2R * Psw1R * Qsw0R * Qrv3R * QdR * QallR +
              Psw0R * Phw0R * Phw1R * Qsw1R * Qsw2R * Qrv3R * QdR * QallR * Qhw2R +
              Qrv3R * QdR * QallR * Phw0R * Phw2R * Qhw1R * Qsw2R * (1 - Psw0R * Psw1R) +
              Psw2R * Phw0R * Phw2R * Qsw0R * Qsw1R * Qrv3R * QdR * QallR * Qhw1R +
              Qrv3R * QdR * QallR * Phw1R * Phw2R * Qhw0R * Qsw1R * (1 - Psw0R * Psw2R) +
              Psw1R * Phw1R * Phw2R * Qsw0R * Qsw2R * Qrv3R * QdR * QallR * Qhw0R +
              Qrv3R * QdR * QallR * Phw0R * Phw1R * Qhw2R * Qsw0R * (1 - Psw2R * Psw1R) +
              Qrv3R * QdR * QallR * Psw0R * Qhw0R * Qsw1R * Qhw1R * Qsw2R * Phw2R +
              Qrv3R * QdR * QallR * Psw0R * Qhw0R * Qsw1R * Phw1R * Qsw2R * Qhw2R +
              Qrv3R * QdR * QallR * Qsw0R * Qhw0R * Psw1R * Qhw1R * Qsw2R * Phw2R +
              Qrv3R * QdR * QallR * Qsw0R * Phw0R * Psw1R * Qhw1R * Qsw2R * Qhw2R +
              Qrv3R * QdR * QallR * Qsw0R * Qhw0R * Qsw1R * Phw1R * Psw2R * Qhw2R +
              Qrv3R * QdR * QallR * Qsw0R * Phw0R * Qsw1R * Qhw1R * Psw2R * Qhw2R)
        
        self.relL = 1 - PR
        self.relR = 1 - PL

    def _computeCost(self):
        self.cost = (self.conf.modules[self.num].hw[self.hw[0]].cost +
                     self.conf.modules[self.num].hw[self.hw[1]].cost +
                     self.conf.modules[self.num].hw[self.hw[2]].cost +
                     self.conf.modules[self.num].sw[self.sw[0]].cost +
                     self.conf.modules[self.num].sw[self.sw[1]].cost +
                     self.conf.modules[self.num].sw[self.sw[2]].cost)
        
    def _computeExecTime(self):
        self.execTime = (max([self.conf.modules[self.num].times[self.sw[0]][self.hw[0]],
                         self.conf.modules[self.num].times[self.sw[1]][self.hw[1]],
                         self.conf.modules[self.num].times[self.sw[2]][self.hw[2]]]) +
                         self.conf.modules[self.num].tvote)

    def toSchedule(self, schedule):
        schedule.tasks.append(Task("t"+str(self.num)+"_rcv", 0, "p"+str(self.num)+"_1", 0))
        schedule.tasks.append(Task("t"+str(self.num)+"_1",
            self.conf.modules[self.num].times[self.sw[0]][self.hw[0]],
            "p"+str(self.num)+"_1", 1))
        schedule.tasks.append(Task("t"+str(self.num)+"_2",
            self.conf.modules[self.num].times[self.sw[1]][self.hw[1]],
            "p"+str(self.num)+"_2", 0))
        schedule.tasks.append(Task("t"+str(self.num)+"_3",
            self.conf.modules[self.num].times[self.sw[2]][self.hw[2]],
            "p"+str(self.num)+"_3", 0))
        schedule.tasks.append(Task("t"+str(self.num)+"_snd",
            self.conf.modules[self.num].tvote,
            "p"+str(self.num)+"_1", 2))
        schedule.links.append(Link("t"+str(self.num)+"_rcv", "t"+str(self.num)+"_2", self.conf.modules[self.num].input))
        schedule.links.append(Link("t"+str(self.num)+"_rcv", "t"+str(self.num)+"_3", self.conf.modules[self.num].input))
        schedule.links.append(Link("t"+str(self.num)+"_2", "t"+str(self.num)+"_snd", self.conf.modules[self.num].output))
        schedule.links.append(Link("t"+str(self.num)+"_3", "t"+str(self.num)+"_snd", self.conf.modules[self.num].output))


    def __str__(self):
        return "\t"+str(self.num)+ ". NVP11:" + str(self.hw) + str(self.sw) + "\n"


class RB11(Module):
    def __init__(self, num, hw = [], sw = []):
        if hw == [] and sw == []:
            hw = [random.randint(0, len(self.conf.modules[num].hw)-1),
                  random.randint(0, len(self.conf.modules[num].hw)-1)]
            sw1 = random.randint(0, len(self.conf.modules[num].sw)-2)
            sw = [sw1, random.randint(sw1+1, len(self.conf.modules[num].sw)-1)]
        Module.__init__(self, num, hw, sw)

    def _computeRel(self):
        Qhw0L = self.conf.modules[self.num].hw[self.hw[0]].relL
        Qhw0R = self.conf.modules[self.num].hw[self.hw[0]].relR
        Phw0L = 1 - Qhw0R
        Phw0R = 1 - Qhw0L
        Qhw1L = self.conf.modules[self.num].hw[self.hw[1]].relL
        Qhw1R = self.conf.modules[self.num].hw[self.hw[1]].relR
        Phw1L = 1 - Qhw1R
        Phw1R = 1 - Qhw1L
        Qsw0L = self.conf.modules[self.num].sw[self.sw[0]].relL
        Qsw0R = self.conf.modules[self.num].sw[self.sw[0]].relR
        Psw0L = 1 - Qsw0R
        Psw0R = 1 - Qsw0L
        Qsw1L = self.conf.modules[self.num].sw[self.sw[1]].relL
        Qsw1R = self.conf.modules[self.num].sw[self.sw[1]].relR
        Psw1L = 1 - Qsw1R
        Psw1R = 1 - Qsw1L
        QrvL = self.conf.modules[self.num].qrvL
        QrvR = self.conf.modules[self.num].qrvR
        PrvL = 1 - QrvR
        PrvR = 1 - QrvL
        QdL = self.conf.modules[self.num].qdL
        QdR = self.conf.modules[self.num].qdR
        PdL = 1 - QdR
        PdR = 1 - QdL
        QallL = self.conf.modules[self.num].qallL
        QallR = self.conf.modules[self.num].qallR
        PallL = 1 - QallR
        PallR = 1 - QallL
        Qrv3L = QrvL ** 3
        Qrv3R = QrvR ** 3

        PL = (PrvL +
              QrvL * PdL +
              QrvL * QdL * PallL +
              QrvL * QdL * QallL * Phw0L * Phw1L +
              QrvL * QdL * QallL * (1 - Phw0L * Phw1L) * Psw0L * Psw1L)

        PR = (PrvR +
              QrvR * PdR +
              QrvR * QdR * PallR +
              QrvR * QdR * QallR * Phw0R * Phw1R +
              QrvR * QdR * QallR * (1 - Phw0R * Phw1R) * Psw0R * Psw1R)
        
        self.relL = 1 - PR
        self.relR = 1 - PL

    def _computeCost(self):
        self.cost = (self.conf.modules[self.num].hw[self.hw[0]].cost +
                     self.conf.modules[self.num].hw[self.hw[1]].cost +
                     2 * self.conf.modules[self.num].sw[self.sw[0]].cost +
                     2 * self.conf.modules[self.num].sw[self.sw[1]].cost)
        
    def _computeExecTime(self):
        self.execTime = (max([self.conf.modules[self.num].times[self.sw[0]][self.hw[0]] +
                             self.conf.modules[self.num].times[self.sw[1]][self.hw[0]],
                             self.conf.modules[self.num].times[self.sw[0]][self.hw[1]] +
                             self.conf.modules[self.num].times[self.sw[1]][self.hw[1]]]) +
                             2 * self.conf.modules[self.num].ttest +
                             self.conf.modules[self.num].trecov)

    def toSchedule(self, schedule):
        schedule.tasks.append(Task("t"+str(self.num)+"_rcv", 0, "p"+str(self.num)+"_1", 0))
        schedule.tasks.append(Task("t"+str(self.num)+"_1",
            self.conf.modules[self.num].times[self.sw[0]][self.hw[0]] +
            self.conf.modules[self.num].times[self.sw[1]][self.hw[0]] +
            2 * self.conf.modules[self.num].ttest +
            self.conf.modules[self.num].trecov,
            "p"+str(self.num)+"_1", 1))
        schedule.tasks.append(Task("t"+str(self.num)+"_2",
            self.conf.modules[self.num].times[self.sw[0]][self.hw[1]] +
            self.conf.modules[self.num].times[self.sw[1]][self.hw[1]] +
            2 * self.conf.modules[self.num].ttest +
            self.conf.modules[self.num].trecov,
            "p"+str(self.num)+"_2", 0))
        schedule.tasks.append(Task("t"+str(self.num)+"_snd", 0, "p"+str(self.num)+"_1", 2))
        schedule.links.append(Link("t"+str(self.num)+"_rcv", "t"+str(self.num)+"_2", self.conf.modules[self.num].input))
        schedule.links.append(Link("t"+str(self.num)+"_2", "t"+str(self.num)+"_snd", self.conf.modules[self.num].output))

    def __str__(self):
        return "\t"+str(self.num)+ ". RB11:" + str(self.hw) + str(self.sw) + "\n"

# reconfiguration for module
# survives initial self fault and then fault of first reserve module
# if second reserve fails there's no reconfiguration
class HWRC20(Module):
    def __init__(self, num, hw=[], sw=[]):
        if hw == [] and sw == []:
            hw = [random.randint(0, len(self.conf.modules[num].hw)-1)]
            sw = [random.randint(0, len(self.conf.modules[num].sw)-1)]
        Module.__init__(self, num, hw, sw)

    def _computeRel(self):
        QhwrcL = self.conf.hwrc_relL
        QhwrcR = self.conf.hwrc_relR
        PhwrcL = 1 - QhwrcR
        PhwrcR = 1 - QhwrcL
        QhwL = self.conf.modules[self.num].hw[0].relL
        QhwR = self.conf.modules[self.num].hw[0].relR
        PhwL = 1 - QhwR
        PhwR = 1 - QhwL
        QswL = self.conf.modules[self.num].sw[0].relL
        QswR = self.conf.modules[self.num].sw[0].relR

        # modules that partake in reconfiguration after initial fault (self fault)
        zone_0 = []
        for i in self.conf.modules:
            if ((i != self.conf.modules[self.num]) and
                    (self.__class__.__name__ == i.type) and
                    (i.hwrc_zone_num == self.conf.modules[self.num].hwrc_zone_num)):
                zone_0.append(i)
        # probability of failure after initial reconfiguration
        P_post_reconf_1L = 0.0
        P_post_reconf_1R = 0.0
        if len(zone_0) > 0:
            for j in zone_0:
                # modules that partake in reconfiguration after second fault (j fault)
                zone_1 = []
                for i in zone_0:
                    if ((i != j) and
                            (i != self.conf.modules[self.num]) and
                            (j.type == i.type) and
                            (i.hwrc_zone_num == j.hwrc_zone_num)):
                        zone_1.append(i)
                # probability of failure after second reconfiguration
                P_post_reconf_2L = 0.0
                P_post_reconf_2R = 0.0
                if len(zone_1) > 0:
                    for k in zone_1:
                        P_post_reconf_2L += 1 - k.hw[0].relR
                        P_post_reconf_2R += 1 - k.hw[0].relL
                    P_post_reconf_2L /= len(zone_1)
                    P_post_reconf_2R /= len(zone_1)
                else:
                    P_post_reconf_2L = 1.0
                    P_post_reconf_2R = 1.0
                P_post_reconf_1L += (1 - j.hw[0].relR) * (PhwrcL + QhwrcL * P_post_reconf_2L)
                P_post_reconf_1R += (1 - j.hw[0].relL) * (PhwrcR + QhwrcR * P_post_reconf_2R)
            P_post_reconf_1L /= len(zone_0)
            P_post_reconf_1R /= len(zone_0)
        else:
            P_post_reconf_1L = 1.0
            P_post_reconf_1R = 1.0
        PL = PhwL * (PhwrcL + QhwrcL * P_post_reconf_1L)
        PR = PhwR * (PhwrcR + QhwrcR * P_post_reconf_1R)
        QL = 1 - PR
        QR = 1 - PL
        self.relL = QL * QswL
        self.relR = QR * QswR

    def toSchedule(self, schedule):
        '''Adds elements, corresponding to module to schedule.
        :param schedule: object of class 'Schedule'.
        '''
        schedule.tasks.append(Task("t"+str(self.num), self.execTime, "p"+str(self.num), 0))

    def _computeCost(self):
        self.cost = self.conf.modules[self.num].hw[self.hw[0]].cost + self.conf.modules[self.num].sw[self.sw[0]].cost

    def _computeExecTime(self):
        self.execTime = self.conf.modules[self.num].times[self.sw[0]][self.hw[0]]

    def __str__(self):
        return "\t" + str(self.num) + ". HWRC20:" + str(self.hw) + str(self.sw) + "\n"