from solution import *
from data import *


def Checker(data: alldata, sol: Solution, scenario: int):
    test = True
    for t in range(data.timestep()):
        if data.accessScenario(scenario).demands()[t] > 0.1+sum(sol._solP1[(i, t)] for i in range(data.nbpower1())) + sum(sol._solP2[(i, t)] for i in range(data.nbpower2())): #Vérif demande
            print("La demande ", t, "n'est pas respectée.")    # On vérifie que la demande est tjs respectée #2
            test = False

        for i in range(data.nbpower1()):
            plant = data.accessPower1(scenario, i)
            if sol._solP1[(i,t)] > plant.pmax()[t] :                              #3
                print("Production de la centrale de type 1 trop élevée", t )
                test = False
        for i in range(data.nbpower2()):
            plant = data.accessPower2(i)
            if sol._solP2[(i,t)] > plant.pmax()[t] :                              #4
                print("Production de la centrale de type 2 trop élevée", i )
                test = False
            if (i,t) not in sol._soly and (i,t) in sol._solr : # On vérifie que la recharge se fait que lors de la panne 
                print("Recharge de ", i, " hors de la panne, à ", t )
                test = False
            if  (i,t) in sol._soly and sol._solP2[(i,t)] > 0.2 : # On vérifie si il y a de la production lors d'une panne 
                print("Production lors de la panne ", i)
                test = False
            if sol._sols[(i,t)] > data.accessCampaign(i,0).maxstock() : # On vérifie qu'on ne dépasse pas le stock maximale
                print("Stock dépassé ! ", i)
                test = False
            if t == 0:                                                                                          #Calcul des stocks
                if sol._sols[(i,t)] != plant.initialstock() - sol._solP2[(i,t)]*data.timestepduration()[t] :
                    print("Mauvais Stock départ ", i, t)
                    test = False
                elif (i,t) in sol._solr and sol._sols[(i,t)] != sol._sols[(i,t-1)] - sol._solP2[(i,t)]*data.timestepduration()[t] + sol._solr[(i,t)] :
                    print("Mauvais calscul Stock  ", t)
                    test = False

            if sol._sols[(i,t)]+0.1 < plant.minstock()*0.1 : # On vérifie qu'on ne dépasse pas le stock min
                print("Stock min dépassé ! ", i)
                test = False
            
            for k in range(data.nbcampaigns()):
                if (i, k, t) in sol._solx and (i,t) not in sol._soly: #Vérification du départ
                    print("Pas de début de panne en", t)
                    test = False
                if  (i,t) in sol._solr and (i, k, t) in sol._solx and sol._solr[(i,t)]*sol._solx[(i, k, t)] > data.accessCampaign(i,k).maxrefuel() : # On vérifie que la recharge n'est pas dépasser
                    print("dépassement de la recharge autorisée ", i)
                    test = False

    if test:
        print("Everything is okay :)")

        