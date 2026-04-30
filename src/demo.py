from pathlib import Path
from projectUtils import gapEntreOptHeuriEtMILP


def read_file_demo(file_name: str = "toy.txt"):
    try:
        from .data import Readingfile
    except ImportError:
        from data import Readingfile   
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
        from .data import Readingfile
        from .model import runMILPModel_1
        from .checker import Checker
    except ImportError:
        from data import Readingfile
        from model import runMILPModel_1
        from checker import Checker

    print("Running MILP model on instance:", file_name)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    sol = runMILPModel_1(data, outputFlag=True, timeLimit=7200, scenario=scenario)
    
    print(f"Solution: {sol._status}, Objective: {sol.value()}")
    print(f"Dual Bound value: {sol._dualBound}, Runtime: {sol._runtime} seconds")
    print(sol._solx)
    print(sol._soly)
    Checker(data, sol, scenario)

def heuristic_2_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristicV2_basic
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristicV2_basic

    print("Running heuristic 2 on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristicV2_basic()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return
    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")

def heuristic_2_2_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristicV2MultiCampaign
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristicV2MultiCampaign

    print("Running heuristic 2_2 on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristicV2MultiCampaign()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")

def heuristic_2_RF_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristicV2_RF
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristicV2_RF

    print("Running heuristic 2_RF on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristicV2_RF()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")


def heuristic_3_dichotomie_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristicV3_dichotomie
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristicV3_dichotomie

    print("Running heuristic 2_RF on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))
    
    heuristic = MaintenanceHeuristicV3_dichotomie()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")