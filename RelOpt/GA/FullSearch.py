from Common.Algorithm import Algorithm
from Common.System import System
from Common.Core import genEvent
from Common.Module import NONE, NVP01, NVP11, RB11, HWRC20, Module
from Common.Statistics import Execution
import random, copy, time


# pessimistic interval comparison extended with optimistic interval comparison
# it seems that despite complex description
# interval is chosen if it has higher value of center
# among intervals with similar centers better are those with lower width/radius
# B left of A - AC is higher - choose A
# B left of A and intersect - AC is higher - choose A
# B embraces A - if AC > BC - choose A
# A embraces B - if AC > BC - choose A by optimism
# B embraces A - if AC = BC and AW < BW - choose A
# in other cases choose B because BC is higher or BC = AC and BW is lower than AW
def interval_key_pessimistic_extended(x):
    return x.penalty * (x.relL + x.relR) / 2, x.penalty * (x.relL - x.relR)


def interval_key_optimistic(x):
    return x.penalty * x.relR


def interval_key_optimistic_left(x):
    return x.penalty * x.relL


# pessimistic interval comparison extended with optimistic interval comparison
def interval_cmp_pessimistic_extended(A, B):
    AC = A.penalty * (A.relL + A.relR) / 2
    BC = B.penalty * (B.relL + B.relR) / 2
    AL = A.penalty * A.relL
    AR = A.penalty * A.relR
    BL = B.penalty * B.relL
    BR = B.penalty * B.relR
    # A is B
    if (AL == BL and AR == BR):
        return 0
    else:
        # A is to the right of B
        # A and B may or may not be intersecting
        # [ B ]   ( A )
        # [   B ( ] A   )
        if ((AL >= BL and AR > BR) or (AL > BL and AR >= BR)):
            return 1
        else:
            # B is to the right of A
            # B and A may or may not be intersecting
            # [ A ]   ( B )
            # [   A ( ] B   )
            if ((AL <= BL and AR < BR) or (AL < BL and AR <= BR)):
                return -1
            else:
                # A is inside of B
                if (AL >= BL and AR <= BR):
                    if (AC >= BC):
                        return 1
                    else:
                        return -1
                else:
                    # B is inside of A
                    if (AL <= BL and AR >= BR):
                        if (AC > BC):
                            return 1
                        else:
                            return -1


class FullSearch(Algorithm):
    def __init__(self):
        Algorithm.__init__(self)
        self.population = []
        self.best = None
        self.recCount = 0

    def recursive_findBest(self, s, k, num):
        if k < num:
            for tool0 in Module.conf.modules[k].tools:
                if tool0 == "none":
                    for hw in Module.conf.modules[k].hw:
                        for sw in Module.conf.modules[k].sw:
                            new = NONE(k,[hw.num],[sw.num])
                            s.modules[k] = new
                            self.recursive_findBest(s, k + 1, num)
                elif tool0 == "nvp01":
                    for hw in Module.conf.modules[k].hw:
                        for sw0 in Module.conf.modules[k].sw:
                            for sw1 in Module.conf.modules[k].sw:
                                if sw1.num != sw0.num:
                                    for sw2 in Module.conf.modules[k].sw:
                                        if sw2.num != sw0.num and sw2.num != sw1.num:
                                            new = NVP01(k, [hw.num], [sw0.num, sw1.num, sw2.num])
                                            s.modules[k] = new
                                            self.recursive_findBest(s, k + 1, num)
                elif tool0 == "nvp11":
                    for hw0 in Module.conf.modules[k].hw:
                        for hw1 in Module.conf.modules[k].hw:
                            for hw2 in Module.conf.modules[k].hw:
                                for sw0 in Module.conf.modules[k].sw:
                                    for sw1 in Module.conf.modules[k].sw:
                                        if sw1.num != sw0.num:
                                            for sw2 in Module.conf.modules[k].sw:
                                                if sw2.num != sw0.num and sw2.num != sw1.num:
                                                    new = NVP11(k, [hw0.num, hw1.num, hw2.num], [sw0.num, sw1.num, sw2.num])
                                                    s.modules[k] = new
                                                    self.recursive_findBest(s, k + 1, num)
                elif tool0 == "rb11":
                    for hw0 in Module.conf.modules[k].hw:
                        for hw1 in Module.conf.modules[k].hw:
                            for sw0 in Module.conf.modules[k].sw:
                                for sw1 in Module.conf.modules[k].sw:
                                    if sw1.num != sw0.num:
                                        new = RB11(k, [hw0.num, hw1.num], [sw0.num, sw1.num])
                                        s.modules[k] = new
                                        self.recursive_findBest(s, k + 1, num)
                else:
                    for hw in Module.conf.modules[k].hw:
                        for sw in Module.conf.modules[k].sw:
                            new = HWRC20(k,[hw0.num],[sw0.num])
                            s.modules[k] = new
                            self.recursive_findBest(s, k + 1, num)
        else:
            #s.Update()
            self.recCount += 1

    def Run(self):
        self.Clear()
        Algorithm.time = time.time()
        print "Assuming direct control" + " "
        s = System()
        s.GenerateRandom(True)
        s.hwrc_cost = 50
        k = 0
        self.recursive_findBest(s, k, 6)
        print self.recCount

        Algorithm.time = time.time() - Algorithm.time