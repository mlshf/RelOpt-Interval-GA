from GA_Moore import *
import copy

class HGA_Moore(GA_Moore):
    def __init__(self):
        GA_Moore.__init__(self)
        self.prevSolution = None
        self.prevAvgC = -1
        self.prevAvgL = -1
        self.prevAvgR = -1
        self.currentAvgC = -1
        self.currentAvgL = -1
        self.currentAvgR = -1

    def Step(self):
        self._select()
        self._recombine()
        self._mutate()
        self._evalPopulation()
        self._fuzzyLogic()

    def Clear(self):
        GA.Clear(self)
        self.prevSolution = None
        self.prevAvgC = -1
        self.prevAvgL = -1
        self.prevAvgR = -1
        self.currentAvgC = -1
        self.currentAvgL = -1
        self.currentAvgR = -1
        self.algconf.crossPercent.cur = self.algconf.crossPercent.norm
        self.algconf.Pcross.cur = self.algconf.Pcross.norm

    def _fuzzyLogic(self):
        # if no prev solution, there's nothing to compare
        if self.prevSolution == None:
            self.algconf.crossPercent.cur = self.algconf.crossPercent.max
            self.algconf.Pcross.cur = self.algconf.Pcross.max
            self.algconf.mutPercent.cur = self.algconf.mutPercent.max
            self.algconf.Pmut.cur = self.algconf.Pmut.max
            # if curr solution exists, save it as prev solution
            if self.currentSolution != None:
                self.prevSolution = copy.deepcopy(self.currentSolution)
                self.currentAvgC = reduce(lambda a, b: a + (b.relL + b.relR) / 2, self.population, 0) / len(self.population)
                self.currentAvgL = reduce(lambda a, b: a + b.relL, self.population, 0) / len(self.population)
                self.currentAvgR = reduce(lambda a, b: a + b.relR, self.population, 0) / len(self.population)
                self.prevAvgC = self.currentAvgC
                self.prevAvgL = self.currentAvgL
                self.prevAvgR = self.currentAvgR
        # else prevSollution != None
        # and of currentSolution != None
        elif self.currentSolution != None:
            self.currentAvgC = reduce(lambda a, b: a + (b.relL + b.relR) / 2, self.population, 0) / len(self.population)
            self.currentAvgL = reduce(lambda a, b: a + b.relL, self.population, 0) / len(self.population)
            self.currentAvgR = reduce(lambda a, b: a + b.relR, self.population, 0) / len(self.population)
            if self.currentIter > 1:
                curr_relC = (self.currentSolution.relL + self.currentSolution.relR) / 2
                curr_relL = self.currentSolution.relL
                curr_relR = self.currentSolution.relR
                prev_relC = (self.prevSolution.relL + self.prevSolution.relR) / 2
                prev_relL = self.prevSolution.relL
                prev_relR = self.prevSolution.relR
                bestDiff = ((curr_relL - prev_relL)/curr_relL + (curr_relR - prev_relR)/curr_relR + (curr_relC - prev_relC)/curr_relC)/3
                avgDiff = ((self.currentAvgR - self.prevAvgR) / self.currentAvgR + (self.currentAvgL - self.prevAvgL) / self.currentAvgL + (self.currentAvgC - self.prevAvgC) / self.currentAvgC)/3
                if bestDiff >= 0.01:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.max
                    self.algconf.Pcross.cur = self.algconf.Pcross.max
                else:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.min
                    self.algconf.Pcross.cur = self.algconf.Pcross.min
                if avgDiff >= 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.min
                    self.algconf.Pmut.cur = self.algconf.Pmut.min
                elif avgDiff > -0.03 and avgDiff < 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.norm
                    self.algconf.Pmut.cur = self.algconf.Pmut.norm
                elif avgDiff <= -0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.max
                    self.algconf.Pmut.cur = self.algconf.Pmut.max
            self.prevSolution = copy.deepcopy(self.currentSolution)
            self.prevAvgC = self.currentAvgC
            self.prevAvgL = self.currentAvgL
            self.prevAvgR = self.currentAvgR
        # somehow prev != None, curr == None
        else:
            self.algconf.crossPercent.cur = self.algconf.crossPercent.max
            self.algconf.Pcross.cur = self.algconf.Pcross.max
            self.algconf.mutPercent.cur = self.algconf.mutPercent.max
            self.algconf.Pmut.cur = self.algconf.Pmut.max

