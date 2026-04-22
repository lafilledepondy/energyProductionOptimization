from pathlib import Path
from projectUtils import gapEntreOptHeuriEtMILP

try:
    from .data import Readingfile
    from .heristiques import MaintenanceHeuristicV1
    from .heristiques import MaintenanceHeuristicV2
except ImportError:
    # Support direct script execution (python src/demo.py)
    from data import Readingfile
    from heristiques import MaintenanceHeuristicV1
    from heristiques import MaintenanceHeuristicV2

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

def model_demo(file_name: str, scenario: int):
    try:
        from .model import runMILPModel_1
        from .checker import Checker
    except ImportError:
        from model import runMILPModel_1
        from checker import Checker

    print("Running MILP model on instance:", file_name)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    sol = runMILPModel_1(data, outputFlag=True, timeLimit=129600, scenario=scenario)
    
    print(f"Solution: {sol._status}, Objective: {sol.value()}")
    print(f"Dual Bound value: {sol._dualBound}, Runtime: {sol._runtime} seconds")
    print(sol._sols)
    Checker(data, sol, scenario)
    return sol.value()

def heuristic_1_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .checker import Checker
        from .solution import print_solution
    except ImportError:
        from checker import Checker
        from solution import print_solution

    print("Running heuristic 1 on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristicV1()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")

def heuristic_2_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .checker import Checker
        from .solution import print_solution
    except ImportError:
        from checker import Checker
        from solution import print_solution

    print("Running heuristic 2 on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))
    # scenario = 1

    heuristic = MaintenanceHeuristicV2()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")

