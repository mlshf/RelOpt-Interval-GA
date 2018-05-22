from Common.Constraints import CostConstraints, RelConstraints, TimeConstraints

class Execution:
    '''Class for statistics of one execution'''
    def __init__(self, solution, iter, time, timecounts, simcounts):
        self.solution = solution
        self.iter = iter
        self.time = time
        self.timecounts = timecounts
        self.simcounts = simcounts

class Statistics:
    def __init__(self):
        self.execs = []

    def AddExecution(self, ex):
        self.execs.append(ex)

    def ExportToCsv(self, filename):
        '''Print statistics to csv-file'''
        if self.execs==[]:
            return
        f = open(filename, "w")
        for c in self.execs[0].solution.constraints:
            if isinstance(c, CostConstraints):
                f.write("Limit Cost:;%d;\n" % c.limitCost)
            elif isinstance(c, RelConstraints):
                f.write("Limit Rel:;%d;\n" % c.limitRel)
            elif isinstance(c, TimeConstraints):
                f.write("Limit Times:;")
                f.write(str(c.limitTimes))
        f.write("\nNum;RelL;RelR;Cost;Times;IterNum;Time(sec);GetTime_num;Sim_num;\n")
        num = 0
        minRelL = maxRelL = self.execs[0].solution.relL
        sumRelL = 0.0
        minRelR = maxRelR = self.execs[0].solution.relR
        sumRelR = 0.0
        minIter = maxIter = self.execs[0].iter
        sumIter = 0
        mintc = maxtc = self.execs[0].timecounts
        sumtc = 0
        minsc = maxsc = self.execs[0].simcounts
        sumsc = 0
        mintime = maxtime = self.execs[0].time
        sumtime = 0
        for e in self.execs:
            sumRelL += e.solution.relL
            sumRelR += e.solution.relR
            sumIter += e.iter
            sumtc += e.timecounts
            sumsc += e.simcounts
            sumtime += e.time
            if e.solution.relL > maxRelL:
                maxRelL = e.solution.relL
            elif e.solution.relL < minRelL:
                minRelL = e.solution.relL
            if e.solution.relR > maxRelR:
                maxRelR = e.solution.relR
            elif e.solution.relR < minRelR:
                minRelR = e.solution.relR
            if e.iter > maxIter:
                maxIter = e.iter
            elif e.iter < minIter:
                minIter = e.iter
            if e.simcounts > maxsc:
                maxsc = e.simcounts
            elif e.simcounts < minsc:
                minsc = e.simcounts
            if e.timecounts > maxtc:
                maxtc = e.timecounts
            elif e.timecounts < mintc:
                mintc = e.timecounts
            if e.time > maxtime:
                maxtime = e.time
            elif e.time < mintime:
                mintime = e.time
            f.write(str(num)+";")
            f.write(str(e.solution.relL)+";")
            f.write(str(e.solution.relR) + ";")
            f.write(str(e.solution.cost)+";")
            s = "["
            for m in e.solution.modules:
                s+= str(m.time) + ","
            s = s[:-1]+"]"
            f.write(s+";")
            f.write(str(e.iter)+";")
            f.write(str(e.time)+";")
            f.write(str(e.timecounts)+";")
            f.write(str(e.simcounts)+";\n")
            num += 1
        f.write(";\nMin relL:;Max relL:;Avg relL:;Min relR:;Max relR:;Avg relR:;Min iter:;Max iter:;Avg iter:;Min tc:;Max tc:;Avg tc:;Min sc:;Max sc:;Avg sc:;Min time:;Max time:;Avg time:;\n")
        f.write(str(minRelL)+";"+str(maxRelL)+";"+str(sumRelL/num)+";"+
                str(minRelR) + ";" + str(maxRelR) + ";" + str(sumRelR / num) + ";" +
                str(minIter)+";"+str(maxIter)+";"+str(sumIter/num)+";"+
                str(mintc)+";"+str(maxtc)+";"+str(sumtc/num)+";"+
                str(minsc)+";"+str(maxsc)+";"+str(sumsc/num)+";"+
                str(mintime)+";"+str(maxtime)+";"+str(sumtime/num)+";")
        f.close()