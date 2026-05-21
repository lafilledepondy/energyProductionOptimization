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
    return data, sol

def heuristic_basic_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristic_basic
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristic_basic

    print("Running heuristic basic on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristic_basic()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return
    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")

    return data, sol

def heuristic_multiCamp_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristic_MultiCampaign
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristic_MultiCampaign

    print("Running heuristic multi-campagne on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristic_MultiCampaign()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")
    
    return data, sol

def heuristic_optXandY_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristic_OptXandY
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristic_OptXandY

    print("Running heuristic optXandY on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristic_OptXandY()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")

    return data, sol

def heuristic_RF_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristic_RF
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristic_RF

    print("Running heuristic RF on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))

    heuristic = MaintenanceHeuristic_RF()
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")


def heuristic_relaxLagrange_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristic_relaxLagrange
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristic_relaxLagrange

    print("Running heuristic relaxLagrange on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))
    
    heuristic = MaintenanceHeuristic_relaxLagrange(data, scheme)
    sol , soldual = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print("------------------------------------------")
    print_solution(soldual)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, soldual._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")
    print("------------------------------------------")
    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")

    return data, sol

def heuristic_relaxLP_relaxLag_MILP_demo(file_name: str, scheme:int, optimal_value: float = None):
    try:
        from .data import Readingfile
        from .checker import Checker
        from .solution import print_solution
        from .heristiques import MaintenanceHeuristic_relaxLP_relaxLag_milp
    except ImportError:
        from data import Readingfile
        from checker import Checker
        from solution import print_solution
        from heristiques import MaintenanceHeuristic_relaxLP_relaxLag_milp

    print("Running heuristic relaxLP_relaxLagrange_milp on instance:", file_name, "with scenario", scheme)
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / file_name
    data = Readingfile(str(data_file))
    
    heuristic = MaintenanceHeuristic_relaxLP_relaxLag_milp(data, scheme)
    sol = heuristic.solve(data, scheme)

    if sol is None:
        print("Heuristic failed: no feasible solution found.")
        return

    print_solution(sol)
    Checker(data, sol, scheme)
    if optimal_value is not None:
        gap = gapEntreOptHeuriEtMILP(optimal_value, sol._obj_value)
        print(f"Gap between optimal and heuristic solutions: {gap:.2f}%")