from data import Readingfile
from pathlib import Path

def read_file():
    data_file = Path(__file__).resolve().parents[1] / "data" / "Base_A" / "data0.txt"

    data = Readingfile(str(data_file))

    print(f"Loaded instance: {data.name()}")
    print(f"timesteps={data.timestep()}, weeks={data.weeks()}")
    print(
        f"scenarios={data.nbscenario()}, powerplant1={data.nbpower1()}, powerplant2={data.nbpower2()}"
    )

    if data.Scenario():
        first_scenario = data.accessScenario(0)
        print(f"first scenario id: {first_scenario.name()}")
        print(f"first demand values: {first_scenario.demands()[:5]}")

