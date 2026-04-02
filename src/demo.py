from pathlib import Path

from data import Readingfile
from model import runMILPModel_1
from solution import Solution
from heristiques import MaintenanceHeuristicV1

# TODO: handle when the file path doesn't exist

def read_file_demo(file_name: str = "toy.txt"):
    # TODO: properly 
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
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

def model_demo(file_name: str = "data2.txt"):
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    sol = runMILPModel_1(data, outputFlag=True, timeLimit=3600, )
    
    print(f"Solution: {sol._status}, Objective: {sol.value()}")
    print(f"Dual Bound value: {sol._dualBound}, Runtime: {sol._runtime} seconds")

def heuristic_demo(file_name: str):
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristicV1()
    result = heuristic.solve(data)

    print(result)
    #valeur de fct objecti, temps de resoluation

    # if result is None:
    #     print(f"Heuristic failed to find a solution for {data_file.name}.")
    #     return

    # y_it = result.get("y", [])
    # x_itk = result.get("x", [])
    # total_outage_slots = sum(sum(row) for row in y_it) if y_it else 0
    # total_selected_campaigns = sum(len(choices) for choices in x_itk) if x_itk else 0

    # print(f"Heuristic found a solution for {data_file.name}:")
    # print(f"- selected campaigns: {total_selected_campaigns}")
    # print(f"- outage slots used: {total_outage_slots}")

    # for i in range(min(3, len(x_itk))):
    #     print(f"- unit {i} campaign choices: {x_itk[i]}")


