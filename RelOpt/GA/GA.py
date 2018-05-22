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
def interval_cmp_pessimistic_extended(A,B):
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

class GA(Algorithm):
    def __init__(self):
        Algorithm.__init__(self)
        self.population = []
        self.iterWithoutChange = 0

    def Step(self):
        self._select()
        self._recombine()
        self._mutate()
        self._evalPopulation()

    def Run(self):
        self.Clear()
        Algorithm.timecounts = 0
        Algorithm.simcounts = 0
        Algorithm.time = time.time()
        for i in range(self.algconf.popNum):
            s = System()
            s.GenerateRandom(True)
            self.population.append(s)
        self.population.sort(cmp=interval_cmp_pessimistic_extended, reverse=True)
        while not self._checkStopCondition():
            self.Step()
            #print self.currentIter, self.currentSolution
        print "Best solution: ", self.currentSolution
        print "--------------------------------------\n"
        Algorithm.time = time.time() - Algorithm.time
        self.stat.AddExecution(Execution(self.currentSolution, self.currentIter, Algorithm.time, Algorithm.timecounts, Algorithm.simcounts))

    def Clear(self):
        Algorithm.Clear(self)
        self.population = []
        self.iterWithoutChange = 0
        self.candidate = None

    def _mutate(self):
        for s in self.population[int((1.0-self.algconf.mutPercent.cur) * self.algconf.popNum):]:
            if random.random() <= self.algconf.Pmut.cur:
                k = random.randint(0, Module.conf.modNum-1)
                if self.currentIter > 500 and self.currentSolution == None:
                    type = "none"
                else:
                    type = random.choice(Module.conf.modules[k].tools)
                if type == "none":
                    new = NONE(k)
                elif type == "nvp01":
                    new = NVP01(k)
                elif type == "nvp11":
                    new = NVP11(k)
                elif type == "rb11":
                    new = RB11(k)
                else:
                    new = HWRC20(k)
                    if s.hwrc_cost <= 0:
                        s.hwrc_cost = 50
                s.modules[k] = new
                s.Update()
            
    def _select(self):
        probabilities = []
        sum = 0.0
        for s in self.population:
            val = (s.relL + s.relR)/2 * s.penalty
            sum += val
            probabilities.append(val)
        for p in range(self.algconf.popNum):
            probabilities[p] = probabilities[p]/sum
        nums = range(self.algconf.popNum)
        events = dict(zip(nums, probabilities))
        new_pop = []
        for i in nums:
            new_pop.append(self.population[genEvent(events)])
        self.population = new_pop
        self.population.sort(cmp=interval_cmp_pessimistic_extended, reverse=True)

    def _recombine(self):
        if Module.conf.modNum == 1:
            return
        new_pop = []
        notCrossNum =  int((1.0 - self.algconf.crossPercent.cur) * self.algconf.popNum)
        for i in range(notCrossNum):
            new_pop.append(copy.deepcopy(self.population[i]))
        for i in range(self.algconf.popNum/2):
            if random.random() <= self.algconf.Pcross.cur:
                parents = random.sample(self.population,  2)
                k = random.randint(1,Module.conf.modNum-1)
                child1 = parents[0].modules[0:k] + parents[1].modules[k:Module.conf.modNum]
                child2 = parents[1].modules[0:k] + parents[0].modules[k:Module.conf.modNum]
                parents[0].modules = child1
                parents[1].modules = child2
                parents[0].Update()
                parents[1].Update()
        self.population.sort(cmp=interval_cmp_pessimistic_extended, reverse=True)
        new_pop += self.population[:self.algconf.popNum - notCrossNum]
        self.population = new_pop
        self.population.sort(cmp=interval_cmp_pessimistic_extended, reverse=True)

    def _evalPopulation(self):
        self.currentIter += 1
        self.iterWithoutChange += 1
        self.population.sort(cmp=interval_cmp_pessimistic_extended, reverse=True)
        not_use_metamodel = Algorithm.algconf.metamodel==None or random.random() <= self.algconf.pop_control_percent
        for s in self.population:
            if not_use_metamodel:
                if self.candidate:
                    self.candidate.Update(use_metamodel=False)
                    cand_relC = ( self.candidate.relL + self.candidate.relR ) / 2
                    cand_relW = ( self.candidate.relR - self.candidate.relL )
                    if (self.candidate.CheckConstraints() and
                            (self.currentSolution == None or
                            cand_relC > (self.currentSolution.relL + self.currentSolution.relR) / 2 or
                            (cand_relC == (self.currentSolution.relL + self.currentSolution.relR) / 2 and
                            cand_relW < (self.currentSolution.relR - self.currentSolution.relL))

                            )
                    ):
                            self.currentSolution = copy.deepcopy(self.candidate)
                            self.iterWithoutChange = 0
                s.Update(use_metamodel=False)
                s_relC = (s.relL + s.relR) / 2
                s_relW = (s.relR - s.relL)
                if (s.CheckConstraints() and
                        (self.currentSolution == None or
                        s_relC > (self.currentSolution.relL + self.currentSolution.relR) / 2 or
                        (s_relC == (self.currentSolution.relL + self.currentSolution.relR) / 2 and
                        s_relW < (self.currentSolution.relR - self.currentSolution.relL))
                        )
                ):
                    self.currentSolution = copy.deepcopy(s)
                    self.iterWithoutChange = 0
                    self.candidate = None
                    break
            else:
                s_relC = (s.relL + s.relR) / 2
                s_relW = (s.relR - s.relL)
                if (s.CheckConstraints() and
                        (self.currentSolution == None or
                         self.candidate == None or
                         s_relC > (self.candidate.relL + self.candidate.relR) / 2 or
                         (s_relC == (self.candidate.relL + self.candidate.relR) / 2 and
                            s_relW < (self.candidate.relR - self.candidate.relL))
                        )
                ):
                    self.candidate = copy.deepcopy(s)
                    break
        if not_use_metamodel and Algorithm.algconf.metamodel:
            Algorithm.algconf.metamodel.Update()

    def _checkStopCondition(self):
        if self.currentSolution != None and self.iterWithoutChange > self.algconf.maxIter:
            self.currentSolution.Update(use_metamodel=False)
            if self.currentSolution.CheckConstraints():
                return True

        if self.currentSolution == None and self.iterWithoutChange >= 1000:
            self.currentSolution = System()
            self.currentSolution.relL = 0
            self.currentSolution.relR = 0
            for m in Module.conf.modules:
                self.currentSolution.modules.append(NONE(m.num))
            return True
        return False