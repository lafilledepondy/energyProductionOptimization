import sys

class power1 :
    def __init__(self, index, S):
        self._name = index
        self._scenario = S
        self._pmin = []
        self._pmax = []
        self._cost = []

    def name(self):
        return self._name
    
    def whichscnario(self):
        return self._scenario
    
    def pmin(self):
        return self._pmin
    
    def pmax(self):
        return self._pmax
    
    def cost(self):
        return self._cost
    
class campaign :
    def __init__(self, index):
        self._name = index
        self._earlieststop = 0
        self._lateststop = 0
        self._durationoutage = 0 
        self._maxrefuel = 0
        self._minrefuel = 0 
        self._maxstock = 0 
        self._refuelingcost = 0

    def name(self):
        return self._name

    def earlieststop(self):
        return self._earlieststop
    
    def lateststop(self):
        return self._lateststop
    
    def durationoutage(self):
        return self._durationoutage
    
    def maxrefuel(self):
        return self._maxrefuel
    
    def minrefuel(self):
        return self._minrefuel
    
    def maxstock(self):
        return self._maxstock
    
    def refuelingcost(self):
        return self._refuelingcost
    
class scenario :
    def __init__(self, index):
        self._name = index
        self._demands= []
        self._Power1 = []

    def addPower1(self, power1):
        self._Power1.append(power1)

    def name(self):
        return self._name

    def demands(self):
        return self._demands
    
    def Power1(self):
        return self._Power1

class power2 :
    def __init__(self, index):
        self._name = index
        self._initialstock = 0
        self._minstock = 0
        self._Campaigns = []
        self._pmax = []
    
    def addCampaign(self, campaign):
        self._Campaigns.append(campaign)

    def name(self):
        return  self._name
    
    def initialstock(self):
        return  self._initialstock
    
    def minstock(self):
        return  self._minstock
    
    def Campaigns(self):
        return  self._Campaigns
    
    def pmax(self):
        return self._pmax

class alldata :
    def __init__(self, name):
        self._name = name
        self._timestep = 0
        self._weeks = 0
        self._nbcampaigns = 0
        self._nbscenario = 0
        self._nbpower1 = 0
        self._nbpower2 = 0
        self._timestepduration = [] 
        self._Scenario = []
        self._Power2 = []
    
    def addScenario(self, scenario):
        self._Scenario.append(scenario)

    def addPower2(self, power2):
        self._Power2.append(power2)

    def name(self):
        return  self._name
    
    def timestep(self):
        return  self._timestep
    
    def weeks(self):
        return  self._weeks
    
    def nbcampaigns(self):
        return  self._nbcampaigns
    
    def nbscenario(self):
        return self._nbscenario
    
    def nbpower1(self):
        return self._nbpower1
    
    def nbpower2(self):
        return self._nbpower2
    
    def timestepduration(self):
        return self._timestepduration
    
    def Scenario(self):
        return self._Scenario
    
    def Power2(self):
        return self._Power2
    
    def accessPower2(self, index_powerplant2):
        return self.Power2()[index_powerplant2]
    
    def accessScenario(self, index_scenario):
        return self.Scenario()[index_scenario]
    
    def accessPower1(self, index_scenario, index_powerplant1):
        return self.Scenario()[index_scenario].Power1()[index_powerplant1]
    
    def accessCampaign(self, index_powerplant2, index_campaign):
        return self.Power2()[index_powerplant2].Campaigns()[index_campaign]
    
    


        


def Readingfile(dataFilePath):
    try:
        
        actuel = "None"
        compte = 0
        type1 = -1
        type2 = -1
        
        with open(dataFilePath, 'r') as dataFile:
            import os
            dataFileName = os.path.splitext(os.path.basename(dataFilePath))[0]
            
            data = alldata(dataFileName)
            
            for ligne in dataFile :
                ligne = ligne.strip()
                if not ligne:
                    continue

                if ligne.startswith("begin main") :
                    actuel = "main"
                if actuel == "main":
                    if ligne.startswith("timestep") :
                        data._timestep = int(ligne.split()[1])
                    if ligne.startswith("weeks") :
                        data._weeks= int(ligne.split()[1])
                    if ligne.startswith("campaigns") :
                        data._nbcampaigns = int(ligne.split()[1])
                    if ligne.startswith("scenario") :
                        data._nbscenario = int(ligne.split()[1])
                    if ligne.startswith("powerplant1") :
                        data._nbpower1 = int(ligne.split()[1])
                    if ligne.startswith("powerplant2") :
                        data._nbpower2 = int(ligne.split()[1])
                    if ligne.startswith("durations"):
                        data._timestepduration = [int(n) for n in ligne.split()[1:]]
                    if ligne.startswith("demand"):
                        index = "scenario_" + str(compte)
                        s = scenario(index)
                        s._demands = [float(n) for n in ligne.split()[1:]]
                        compte += 1
                        data.addScenario(s)
                        
                        

                if ligne.startswith("type 1") :
                    actuel = "type 1"
                    compte = 0
                    type1 += 1
                    index = "powerplant_1_" + str(type1)
                    

                if actuel == "type 1":
                    if ligne.startswith("pmin"):
                        p1 = power1(index, compte)
                        p1._pmin = [float(n) for n in ligne.split()[1:]]
                    if ligne.startswith("pmax"):
                        p1._pmax = [float(n) for n in ligne.split()[1:]]
                    if ligne.startswith("cost"):
                        p1._cost = [float(n) for n in ligne.split()[1:]]
                        
                        data._Scenario[compte].addPower1(p1)
                        compte += 1
                        
                    

                if ligne.startswith("type 2") :
                    actuel = "type 2"
                    compte = 0
                    type2 += 1
                    index = "powerplant_2_" + str(type2)
                    p2 = power2(index)
                if actuel == "type 2":
                    
                    if ligne.startswith("stock") :
                        p2._initialstock = int(ligne.split()[1])
                    if ligne.startswith("stock") :
                        p2._initialstock = int(ligne.split()[1])
                    if ligne.startswith("durations") :
                        duree = ligne.split()[1:]
                        n = len(duree)
                        
                        for i in range(n):
                            index2 = "campaign_" + str(i)
                            camp = campaign(index2)
                            camp._durationoutage = int(duree[i] )
                            p2.addCampaign(camp)
                               
                        
                        
                    if ligne.startswith("max_refuel") :
                        duree = ligne.split()[1:]
                        n = len(duree) 
                        
                        for i in range(n):  
                            p2._Campaigns[i]._maxrefuel = duree[i] 
                        
                        
                    if ligne.startswith("min_refuel") :
                        duree = ligne.split()[1:]
                        n = len(duree) 
                        for i in range(n):
                            p2._Campaigns[i]._minrefuel = duree[i]
                    if ligne.startswith("current_campaign_stock_threshold"):
                        p2._minstock = int(ligne.split()[1])
                    if ligne.startswith("pmax"):
                        p2._pmax = [float(n) for n in ligne.split()[1:]]
                    if ligne.startswith("max_stock_after_refueling") :
                        duree = ligne.split()[1:]
                        n = len(duree) 
                        for i in range(n):
                            p2._Campaigns[i]._maxstock = duree[i]
                    if ligne.startswith("refueling_cost") :
                        duree = ligne.split()[1:]
                        n = len(duree) 
                        for i in range(n):
                            p2._Campaigns[i]._refuelingcost = float(duree[i])
                        data.addPower2(p2)
                        

                if ligne.startswith("type 13") :
                    actuel = "type 13"
                    p = 0
                    c = 0
                    if ligne.startswith("powerplant") :
                        p = int(ligne.split()[1])
                    if ligne.startswith("campaign") :
                        c = int(ligne.split()[1])
                    if ligne.startswith("earliest_stop_time") :
                        e = int(ligne.split()[1])
                        data._Power2[p]._Campaigns[c]._earlieststop = e
                    if ligne.startswith("earliest_stop_time") :
                        e = int(ligne.split()[1])
                        data._Power2[p]._Campaigns[c]._lateststop = e 
            
            return data
                    

    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror), file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Could not convert data to an integer.", file=sys.stderr)
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info()[0], file=sys.stderr)
        sys.exit(1)
