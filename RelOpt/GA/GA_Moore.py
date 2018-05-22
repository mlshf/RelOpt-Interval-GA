from GA import *
import copy

global g_currSolution
g_currSolution = None
# Moore interval distance
def moore_distance(A, B):
    return max(abs(A.relL - B.relL), abs(A.relR - B.relR))

# intervals inside one another are equal
def interval_cmp_inclusion_equality(A, B):
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
                if (AL >= BL and AR <= BR) or (AL <= BL and AR >= BR):
                    return 0

# of 2 intervals that are included in one another best is the one with biggest distance from best solution
def interval_cmp_moore(A, B):
    # in case there is no curr Solution, compare with inclusion equality
    global g_currSolution
    if g_currSolution == None:
        return interval_cmp_inclusion_equality(A, B)
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
                if (AL >= BL and AR <= BR) or (AL <= BL and AR >= BR):
                    if moore_distance(A, g_currSolution) >= moore_distance(B, g_currSolution):
                        return 1
                    else:
                        return -1

class GA_Moore(GA):
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
        # if intervals are included in one another they are equal
        global g_currSolution
        g_currSolution = copy.deepcopy(self.currentSolution)
        self.population.sort(cmp=interval_cmp_moore, reverse=True)
        while not self._checkStopCondition():
            self.Step()
            #print self.currentIter, self.currentSolution
        print "Best solution: ", self.currentSolution
        print "--------------------------------------\n"
        Algorithm.time = time.time() - Algorithm.time
        self.stat.AddExecution(Execution(self.currentSolution, self.currentIter, Algorithm.time, Algorithm.timecounts,
                                         Algorithm.simcounts))

    def Clear(self):
        Algorithm.Clear(self)
        self.population = []
        self.iterWithoutChange = 0
        self.candidate = None

    def _mutate(self):
        for s in self.population[int((1.0 - self.algconf.mutPercent.cur) * self.algconf.popNum):]:
            if random.random() <= self.algconf.Pmut.cur:
                k = random.randint(0, Module.conf.modNum - 1)
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
        # find solution with best center
        best_solution = None
        bestval = 0.0
        sum = 0.0
        for s in self.population:
            val = (s.relL + s.relR) / 2 * s.penalty
            width = s.relR - s.relL
            if val > bestval:
                bestval = val
                best_solution = copy.deepcopy(s)
            elif val == bestval and width < best_solution.relR - best_solution.relL:
                best_solution = copy.deepcopy(s)
        # found solution with the best center
        # now find probabilities
        global g_currSolution
        g_currSolution = copy.deepcopy(best_solution)
        # sort population according to the best solution found in the population
        self.population.sort(cmp=interval_cmp_moore)
        # val is number of solution in sorted temporary population multiplied by its penalty
        i = 1.0
        prev_s = None
        for s in self.population:
            if prev_s != None and (s.relL != prev_s.relL or s.relR != prev_s.relR):
                i += 1.0
            val = s.penalty * i
            sum += i
            probabilities.append(val)
            prev_s = copy.deepcopy(s)
        # return current solution back to normal
        g_currSolution = copy.deepcopy(self.currentSolution)
        for p in range(self.algconf.popNum):
            probabilities[p] = probabilities[p] / sum
        nums = range(self.algconf.popNum)
        events = dict(zip(nums, probabilities))
        new_pop = []
        for i in nums:
            new_pop.append(self.population[genEvent(events)])
        self.population = new_pop
        g_currSolution = copy.deepcopy(self.currentSolution)
        self.population.sort(cmp=interval_cmp_moore, reverse=True)

    def _recombine(self):
        if Module.conf.modNum == 1:
            return
        new_pop = []
        notCrossNum = int((1.0 - self.algconf.crossPercent.cur) * self.algconf.popNum)
        for i in range(notCrossNum):
            new_pop.append(copy.deepcopy(self.population[i]))
        for i in range(self.algconf.popNum / 2):
            if random.random() <= self.algconf.Pcross.cur:
                parents = random.sample(self.population, 2)
                k = random.randint(1, Module.conf.modNum - 1)
                child1 = parents[0].modules[0:k] + parents[1].modules[k:Module.conf.modNum]
                child2 = parents[1].modules[0:k] + parents[0].modules[k:Module.conf.modNum]
                parents[0].modules = child1
                parents[1].modules = child2
                parents[0].Update()
                parents[1].Update()
        global g_currSolution
        g_currSolution = copy.deepcopy(self.currentSolution)
        self.population.sort(cmp=interval_cmp_moore, reverse=True)
        new_pop += self.population[:self.algconf.popNum - notCrossNum]
        self.population = new_pop
        g_currSolution = copy.deepcopy(self.currentSolution)
        self.population.sort(cmp=interval_cmp_moore, reverse=True)

    def _evalPopulation(self):
        global g_currSolution
        self.currentIter += 1
        self.iterWithoutChange += 1
        g_currSolution = copy.deepcopy(self.currentSolution)
        self.population.sort(cmp=interval_cmp_moore, reverse=True)
        not_use_metamodel = Algorithm.algconf.metamodel == None or random.random() <= self.algconf.pop_control_percent
        for s in self.population:
            if not_use_metamodel:
                if self.candidate:
                    self.candidate.Update(use_metamodel=False)
                    if (self.candidate.CheckConstraints() and
                            (self.currentSolution == None or
                             interval_cmp_pessimistic_extended(self.candidate, self.currentSolution) >= 0
                            )
                    ):
                        self.currentSolution = copy.deepcopy(self.candidate)
                        self.iterWithoutChange = 0
                s.Update(use_metamodel=False)
                if (s.CheckConstraints() and
                        (self.currentSolution == None or
                            interval_cmp_pessimistic_extended(s, self.currentSolution) >= 0
                        )
                ):
                    self.currentSolution = copy.deepcopy(s)
                    self.iterWithoutChange = 0
                    self.candidate = None
                    break
            else:
                g_currSolution = copy.deepcopy(self.currentSolution)
                if (s.CheckConstraints() and
                        (self.currentSolution == None or
                         self.candidate == Nonde or
                         interval_cmp_moore(s, self.candidate) >= 0
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