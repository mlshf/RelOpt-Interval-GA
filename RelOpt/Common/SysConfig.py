import xml.dom.minidom, random, math

class Component:
    def __init__(self, num, relL=0.0, relR=0.0, cost=0):
        self.num = num
        self.relL = relL
        self.relR = relR
        self.cost = cost

    def generateRandom(self, param):
        self.relL = random.uniform(param["minrel"], param["maxrel"])
        self.relR = random.uniform(relL, param["maxrel"])
        self.cost = random.randint(param["mincost"], param["maxcost"])

class ModConfig:
    def __init__(self):
        self.sw = []
        self.hw = []
        self.tools = []
        self.times = []
        self.limittime = None
        self.num = -1
        self.qrvL = -1.0
        self.qdL = -1.0
        self.qallL = -1.0
        self.qrvR = -1.0
        self.qdR = -1.0
        self.qallR = -1.0
        self.hwrc_zone_num = -1
        self.type = ""
        self.tvote = 0
        self.ttest = 0
        self.trecov = 0
        self.src = []
        self.dst = []
        self.dep = []
        self.input = 0
        self.output = 0

    def GetConfigsNum(self):
        res = 0
        hw_num = len(self.hw)
        sw_num = len(self.sw)
        if "none" in self.tools:
            res += hw_num * sw_num
        if "hwrc20" in self.tools:
            res += hw_num * sw_num
        if "nvp01" in self.tools:
            res += hw_num * math.factorial(sw_num) /(6 * math.factorial(sw_num - 3))
        if "nvp11" in self.tools:
            res += hw_num**3 * math.factorial(sw_num) /(6 * math.factorial(sw_num - 3))
        if "rb11" in self.tools:
            res += hw_num**2 * math.factorial(sw_num) /(2 * math.factorial(sw_num - 2))
        return res

    def timeInterval(self):
        '''Computes minimum and maximum execution times for module.
        Maximum time is estimated approximately.
        Method is needed for configuration generator.
        FIXME: all tools are considered to be used.'''
        times = []
        for i in range(len(self.times)):
                for j in range(len(self.times[i])):
                    times.append(self.times[i][j])
        times.sort()
        mintime = times[0]
        maxtime = max(2*times[len(times)-1]+2*self.ttest+self.trecov,
                      3*times[len(times)-1]+3*self.tvote)
        return (mintime,maxtime)

    def costInterval(self):
        '''Computes minimum and maximum costs for module.'''
        minhw = min(self.hw, key=lambda x: x.cost).cost
        maxhw = max(self.hw, key=lambda x: x.cost).cost
        costs = []
        for i in self.sw:
            costs.append(i.cost)
        costs.sort()
        minCost = costs[0] + min(self.hw, key=lambda x: x.cost).cost
        size = len(costs)
        maxCost = 0
        if "nvp11" in self.tools:
            maxCost = costs[size-1] + costs[size-2] + costs[size-3] + 3*maxhw
        if "rb11" in self.tools:
            maxCost = max(maxCost, 2 * costs[size-1] + 2 * costs[size-2] + 2 * maxhw)
        if "nvp01" in self.tools:
            maxCost = max(maxCost, costs[size-1] + costs[size-2] + costs[size-3] + maxhw)
        if "none" in self.tools:
            maxCost = max(maxCost, costs[size-1] + maxhw)
        if "hwrc20" in self.tools:
            maxCost = max(maxCost, costs[size-1] + maxhw)
        return (minCost, maxCost)

    def LoadFromXmlNode(self, node):
        '''Loading from node with tag 'module'.'''
        self.num = int(node.getAttribute("num"))
        self.qrvL = float(node.getAttribute("qrvL"))
        self.qdL = float(node.getAttribute("qdL"))
        self.qallL = float(node.getAttribute("qallL"))
        self.qrvR = float(node.getAttribute("qrvR"))
        self.qdR = float(node.getAttribute("qdR"))
        self.qallR = float(node.getAttribute("qallR"))
        if (node.hasAttribute("limittime")):
            self.limittime=int(node.getAttribute("limittime"))
        self.sw = []
        self.hw = []
        self.tools = []
        for child in node.childNodes:
            if isinstance(child, xml.dom.minidom.Text):
                continue
            if child.nodeName == "time":
                continue
            if child.nodeName == "tool":
                name = child.getAttribute("name")
                self.tools.append(name)
                if name =="hwrc20":
                        self.hwrc_zone_num = float(node.getAttribute("hwrczonenum"))
            else:
                num = int(child.getAttribute("num"))
                relL = float(child.getAttribute("relL"))
                relR = float(child.getAttribute("relR"))
                cost = int(child.getAttribute("cost"))
                if child.nodeName == "sw":
                    self.sw.append(Component(num, relL, relR, cost))
                else:
                    self.hw.append(Component(num, relL, relR, cost))
        '''[!!!] Sort lists in order not to search elements by field 'num',
        but to refer them by index.'''
        self.sw.sort(key=lambda x: x.num)
        self.hw.sort(key=lambda x: x.num)
        self.times = range(len(self.sw))
        for i in range(len(self.sw)):
            self.times[i] = range(len(self.hw))
        for child in node.childNodes:
            if isinstance(child, xml.dom.minidom.Text):
                continue
            if child.nodeName != "time":
                continue
            swnum = int(child.getAttribute("swnum"))
            hwnum = int(child.getAttribute("hwnum"))
            time = int(child.getAttribute("t"))
            self.times[swnum][hwnum] = time
            
    def generateRandom(self, param):
        self.qrvL = param["qrvL"]
        self.qdL = param["qdL"]
        self.qallL = param["qallL"]
        self.qrvR = param["qrvR"]
        self.qdR = param["qdR"]
        self.qallR = param["qallR"]
        if param["hwrczonenum"]:
            self.hwrc_zone_num = param["hwrczonenum"]
        self.tools = []
        if param["none"]:
            self.tools.append("none")
        if param["nvp01"]:
            self.tools.append("nvp01")
        if param["nvp11"]:
            self.tools.append("nvp11")
        if param["rb11"]:
            self.tools.append("rb11")
        if param["hwrc20"]:
            self.tools.append("hwrc20")
        self.tvote = param["tvote"]
        self.ttest = param["ttest"]
        self.trecov = param["trecov"]
        self.sw = []
        self.hw = []
        for i in range(param["swnum"]):
            sw = Component(i)
            sw.generateRandom(param)
            self.sw.append(sw)
        for i in range(param["hwnum"]):
            hw = Component(i)
            hw.generateRandom(param)
            self.hw.append(hw)
        self.times = range(param["swnum"])
        for i in self.times:
            self.times[i] = range(param["hwnum"])
            for j in self.times[i]:
                self.times[i][j] = random.randint(param["mintime"], param["maxtime"])

class Link:
    def __init__(self, src, dst, vol):
        self.src = src
        self.dst = dst
        self.vol = vol

class SysConfig:
    def __init__(self):
        self.modNum = 0 #use it instead of len(self.modules)
        self.modules = []
        self.links = []
        self.limitcost = []
        self.limitrel = []
        self.terminals = []

    def findLink(self, src, dst):
        for l in self.links:
            if l.src == src and l.dst == dst:
                return l

    def costInterval(self):
        '''Computes minimum and maximum system costs (is needed for generator)'''
        min = 0
        max = 0
        for m in self.modules:
            range = m.costInterval();
            min += range[0]
            max += range[1]
        return (min, max)

    def modTimeInterval(self, num, l):
        '''Computes minimum and maximum times for module 'num'.
        Module time depends from other modules times. That's why we compute it in this class.
        l -- service list for recursion. l must contain modNum 'False' elements in method call'''
        if l[num]:
            return
        start_min = 0
        start_max = 0
        for m1 in self.modules[num].src:
            self.modTimeInterval(m1.num,l)
            if start_min < self.modules[m1.num].min_time:
                start_min = self.modules[m1.num].min_time
            if start_max < self.modules[m1.num].max_time:
                start_max = self.modules[m1.num].max_time
        range = self.modules[num].timeInterval()
        transfer = 0
        for d in self.modules[num].dst:
            transfer += d[1]
        self.modules[num].min_time = start_min + range[0] + transfer
        self.modules[num].max_time = start_max + range[1] + transfer
        l[num]=True

    def timeInterval(self):
        '''Returns tuple of two arrays: min_time and max_time.
        Every array contains min(max) times for every module.
        Method is needed for generator.'''
        min_time = []
        max_time = []
        l = []
        for m in self.modules:
            l.append(False)
        for m in self.modules:
            self.modTimeInterval(m.num, l)
            min_time.append(m.min_time)
            max_time.append(m.max_time)
        return (min_time, max_time)

    def loadXML(self, fileName):
        self.modules = []
        self.links = []
        f = open(fileName, "r")
        dom = xml.dom.minidom.parse(f)
        for root in dom.childNodes:
            if root.tagName == "system":
                if root.hasAttribute("limitcost"):
                    self.limitcost = int(root.getAttribute("limitcost"))
                if root.hasAttribute("costhwrc"):
                    self.hwrc_cost = int(root.getAttribute("costhwrc"))
                if root.hasAttribute("qhwrcL"):
                    self.hwrc_relL = float(root.getAttribute("qhwrcL"))
                if root.hasAttribute("qhwrcR"):
                    self.hwrc_relR = float(root.getAttribute("qhwrcR"))
                for node in root.childNodes:
                    if isinstance(node, xml.dom.minidom.Text):
                        continue
                    if node.tagName == "module":
                        m = ModConfig()
                        m.LoadFromXmlNode(node)
                        self.modules.append(m)
                    elif node.tagName == "link":
                        continue
                #[!!!]Sort list in order not to search elements by num, but refer them by index
                self.modules.sort(key=lambda x: x.num)
                self.modNum = len(self.modules)
        for root in dom.childNodes:
            if root.tagName == "system":
                for node in root.childNodes:
                    if isinstance(node, xml.dom.minidom.Text):
                        continue
                    if node.tagName == "module":
                        continue
                    elif node.tagName == "link":
                        src = int(node.getAttribute("src"))
                        dst = int(node.getAttribute("dst"))
                        vol = int(node.getAttribute("vol"))
                        self.links.append(Link(self.modules[src],self.modules[dst],vol))
        self.__buildConfig()
        
    def generateRandom(self, param):
        self.modules = []
        self.links = []
        self.modNum = param["modnum"]
        for i in range(param["modnum"]):
            m = ModConfig()
            m.generateRandom(param)
            m.num = i
            self.modules.append(m)
        for m1 in self.modules:
            for m2 in self.modules:
                if m1.num < m2.num and random.random() < param["linkprob"]:
                    l = Link(m1,m2,random.randint(param["minvol"], param["maxvol"]))
                    self.links.append(l)
        self.__buildConfig()


    def saveXML(self, filename):
        dom = xml.dom.minidom.Document()
        system = dom.createElement("system")
        system.setAttribute("limitcost", str(self.limitcost))
        if self.hwrc_cost >= 0.0:
            system.setAttribute("costhwrc", str(self.hwrc_cost))
        if self.hwrc_relL >= 0.0:
            system.setAttribute("qhwrcL", str(self.hwrc_relL))
        if self.hwrc_relR >= 0.0:
            system.setAttribute("qhwrcR", str(self.hwrc_relR))
        for mod in self.modules:
            m = dom.createElement("module")
            m.setAttribute("num", str(mod.num))
            m.setAttribute("qrvL", str(mod.qrvL))
            m.setAttribute("qdL", str(mod.qdL))
            m.setAttribute("qallL", str(mod.qallL))
            m.setAttribute("qrvR", str(mod.qrvR))
            m.setAttribute("qdR", str(mod.qdR))
            m.setAttribute("qallR", str(mod.qallR))
            m.setAttribute("tvote", str(mod.tvote))
            m.setAttribute("ttest", str(mod.ttest))
            m.setAttribute("trecov", str(mod.trecov))
            if mod.hwrc_zone_num >= 0:
                m.setAttribute("hwrczonenum", str(mod.hwrc_zone_num))
            if mod.limittime != None:
                m.setAttribute("limittime", str(mod.limittime))
            for tool in mod.tools:
                t = dom.createElement("tool")
                t.setAttribute("name", tool)
                m.appendChild(t)
            for sw in mod.sw:
                s = dom.createElement("sw")
                s.setAttribute("num", str(sw.num))
                s.setAttribute("cost", str(sw.cost))
                s.setAttribute("relL", str(sw.relL))
                s.setAttribute("relR", str(sw.relR))
                m.appendChild(s)
            for hw in mod.hw:
                h = dom.createElement("hw")
                h.setAttribute("num", str(hw.num))
                h.setAttribute("cost", str(hw.cost))
                h.setAttribute("relL", str(hw.relL))
                h.setAttribute("relR", str(hw.relR))
                m.appendChild(h)
            for i in range(len(mod.times)):
                for j in range(len(mod.times[i])):
                    t = dom.createElement("time")
                    t.setAttribute("swnum", str(i))
                    t.setAttribute("hwnum", str(j))
                    t.setAttribute("t", str(mod.times[i][j]))
                    m.appendChild(t)
            system.appendChild(m)
        for link in self.links:
            l = dom.createElement("link")
            l.setAttribute("src", str(link.src.num))
            l.setAttribute("dst", str(link.dst.num))
            l.setAttribute("vol", str(link.vol))
            system.appendChild(l)
        dom.appendChild(system)
        f = open(filename, "w")
        f.write(dom.toprettyxml())
        f.close()

    def __getSrc(self, dst):
        '''For 'dst' module finds all previous modules'''
        res = []
        for l in self.links:
            if l.dst == dst:
                res.append(l.src)
        return res

    def __getDst(self, src):
        '''For 'src' module finds all next modules'''
        res=[]
        for l in self.links:
            if l.src == src:
                res.append((l.dst, l.vol))
        return res

    def __getTerminals(self):
        '''Find all modules without 'next' modules'''
        res = []
        for m in self.modules:
            if m.dst == []:
                res.append(m.num)
        return res

    def getLimitTimes(self):
        '''Returns time constraints'''
        res = []
        for m in self.modules:
            if m.limittime != None:
                res.append(m.limittime)
            else:
                return None
        return res

    def __getModDependencies(self, mod):
        '''Finds for module all previous modules (for metamodels-approach)'''
        res = []
        for m in mod.src:
            res.append(m)
            res.extend(self.__getModDependencies(m))
        mod.dep = list(set(res)) #delete duplicates
        return mod.dep

    def __buildConfig(self):
        '''Prepares some service data'''
        for m in self.modules:
            m.src = self.__getSrc(m)
            m.dst = self.__getDst(m)
            self.__getModDependencies(m)
            m.input = 0
            for m1 in m.src:
                m.input += self.findLink(m1,m).vol
            m.output = 0
            for m1 in m.dst:
                m.output += m1[1]
        self.terminals = self.__getTerminals()


