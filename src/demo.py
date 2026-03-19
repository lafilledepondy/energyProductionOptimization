from pathlib import Path

from data import Readingfile
from model import runMILPModel_1, runMILPModel_2
from solution import Solution

def read_file_demo():
    # TODO: properly 
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / "data0.txt"

    data = Readingfile(str(data_file))

    print(f"Loaded instance: {data.name()}")
    print(f"timesteps={data.timestep()}, weeks={data.weeks()}")
    print(f"scenarios={data.nbscenario()}, powerplant1={data.nbpower1()}, powerplant2={data.nbpower2()}")

    if data.Scenario():
        first_scenario = data.accessScenario(0)
        print(f"first scenario id: {first_scenario.name()}")
        print(f"first demand values: {first_scenario.demands()[:5]}")

    # all powerplant2 units
    for i, p2 in enumerate(data.Power2()):
        print(f"Pmax for powerplant2[{i}] ({p2.name()}): {p2.pmax()[:10]}")

def model_demo():  
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / "data3.txt"

    data = Readingfile(str(data_file))


    sol = runMILPModel_1(data, outputFlag=True, timeLimit=3600)
    
    print(f"Solution: {sol._status}, Objective: {sol.value()}")
    print(f"Dual Bound value: {sol._dualBound}, Runtime: {sol._runtime} seconds")

    # I2 = range(data.nbpower2()) 
    # campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]

    # K_i = [ # 3D [ [ [range k_e à k_l] [...] by campagne ] [ []  [] ] by units]
    #         [
    #             list(
    #                 range(
    #                     data.accessCampaign(i, k).earlieststop(),
    #                     data.accessCampaign(i, k).lateststop() + 1,
    #                 )
    #             )
    #             for k in campaign_ids_by_unit[i]
    #         ]
    #         for i in I2
    #     ]

    # k_K_i = [ [k] for i in I2 for k in K_i[i]]
    # index_set = [
    # (i, k, t)
    # for i in I2
    # for k in range(len(K_i[i]))
    # for t in K_i[i][k]
    # ]

    # print(K_i[1][1])
    # # print(index_set[0])
