from GA import *
import copy

class GA_optimistic_left(GA):
    def __init__(self):
        GA.__init__(self)

    def Run(self):
        self.Clear()
        Algorithm.timecounts = 0
        Algorithm.simcounts = 0
        Algorithm.time = time.time()
        for i in range(self.algconf.popNum):
            s = System()
            s.GenerateRandom(True)
            self.population.append(s)
        self.population.sort(key=interval_key_optimistic_left, reverse=True)
        while not self._checkStopCondition():
            self.Step()
            #print self.currentIter, self.currentSolution
        print "Best solution: ", self.currentSolution
        print "--------------------------------------\n"
        Algorithm.time = time.time() - Algorithm.time
        self.stat.AddExecution(Execution(self.currentSolution, self.currentIter, Algorithm.time, Algorithm.timecounts, Algorithm.simcounts))

    def _select(self):
        probabilities = []
        sum = 0.0
        for s in self.population:
            val = s.relL * s.penalty
            sum += val
            probabilities.append(val)
        for p in range(self.algconf.popNum):
            probabilities[p] = probabilities[p] / sum
        nums = range(self.algconf.popNum)
        events = dict(zip(nums, probabilities))
        new_pop = []
        for i in nums:
            new_pop.append(self.population[genEvent(events)])
        self.population = new_pop
        self.population.sort(key=interval_key_optimistic_left, reverse=True)

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
        self.population.sort(key=interval_key_optimistic_left, reverse=True)
        new_pop += self.population[:self.algconf.popNum - notCrossNum]
        self.population = new_pop
        self.population.sort(key=interval_key_optimistic_left, reverse=True)

    def _evalPopulation(self):
        self.currentIter += 1
        self.iterWithoutChange += 1
        self.population.sort(key=interval_key_optimistic_left, reverse=True)
        not_use_metamodel = Algorithm.algconf.metamodel==None or random.random() <= self.algconf.pop_control_percent
        for s in self.population:
            if not_use_metamodel:
                if self.candidate:
                    self.candidate.Update(use_metamodel=False)
                    cand_relC = ( self.candidate.relL + self.candidate.relR ) / 2
                    cand_relW = ( self.candidate.relR - self.candidate.relL )
                    if (self.candidate.CheckConstraints() and
                            (self.currentSolution == None or self.candidate.relL > self.currentSolution.relL
                            )
                    ):
                            self.currentSolution = copy.deepcopy(self.candidate)
                            self.iterWithoutChange = 0
                s.Update(use_metamodel=False)
                s_relC = (s.relL + s.relR) / 2
                s_relW = (s.relR - s.relL)
                if (s.CheckConstraints() and
                        (self.currentSolution == None or s.relL > self.currentSolution.relL
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
                         s.relL > self.candidate.relL
                        )
                ):
                    self.candidate = copy.deepcopy(s)
                    break
        if not_use_metamodel and Algorithm.algconf.metamodel:
            Algorithm.algconf.metamodel.Update()