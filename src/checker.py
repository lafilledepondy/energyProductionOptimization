from solution import *
from data import *

def Checker(data: alldata, sol: Solution, scenario: int = 0):
    test = True
    for t in range(data.timestep()):
        if data.accessScenario(scenario).demands()[t] > sum(sol._solP1[(i, t)] for i in range(data.nbpower1())) + sum(sol._solP2[(i, t)] for i in range(data.nbpower2())): #Vérif demande
            print("La demande ", t, "n'est pas respectée.")    # On vérifie que la demande est tjs respectée
            test = False

        for i in range(data.nbpower2()):
            if (i,t) not in sol._soly and (i,t) in sol._solr : # On vérifie que la recharge se fait que lors de la panne 
                print("Recharge de ", i, " hors de la panne, à ", t )
                test = False
            if  (i,t) in sol._soly and sol._solP2[(i,t)] > 0 : # On vérifie si il y a de la production lors d'une panne 
                print("Production lors de la panne ", i)
                test = False

            for k in range(data.nbcampaigns()):
                if (i, k, t) in sol._solx and (i,t) not in sol._soly: #Vérification du départ
                    print("Pas de début de panne en", t)
                    test = False
    if test:
        print("Everything is okay")

        