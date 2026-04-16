from pathlib import Path

try:
    from .data import Readingfile
    from .heristiques import MaintenanceHeuristicV1
except ImportError:
    # Support direct script execution (python src/demo.py)
    from data import Readingfile
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

def model_demo(file_name: str):
    try:
        from .model import runMILPModel_1
        from .checker import Checker
    except ImportError:
        from model import runMILPModel_1
        from checker import Checker

    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    sol = runMILPModel_1(data, outputFlag=True, timeLimit=129600, )
    
    print(f"Solution: {sol._status}, Objective: {sol.value()}")
    print(f"Dual Bound value: {sol._dualBound}, Runtime: {sol._runtime} seconds")
    Checker(data, sol)

def heuristic_demo(file_name: str):
    try:
        from .checker import Checker
        from .solution import print_solution
    except ImportError:
        from checker import Checker
        from solution import print_solution

    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristicV1()
    sol = heuristic.solve(data, 0)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol)

    


