from pathlib import Path

from data import Readingfile
from model import runMILPModel_1, runMILPModel_2
from solution import recordSolution, Solution

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
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / "data0.txt"

    data = Readingfile(str(data_file))

    sol = runMILPModel_1(data, outputFlag=True, timeLimit=60)
    
    print(f"Solution: {sol.status}, Objective: {sol.value()}")
    print(f"Dual Bound value: {sol.dualBound}, Runtime: {sol.runtime} seconds")