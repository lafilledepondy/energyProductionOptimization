import os

class Solution: 
    def __init__(self, status: str, obj_value: float, dualBound: float, runtime: float, sol: list):
        self._obj_value = obj_value
        self._runtime = runtime
        self._status = status
        self._dualBound = dualBound
        self._solP1 = sol[0]
        self._solP2 = sol[1]
        self._soly = sol[2]
        self._solr = sol[3]
        self._sols = sol[4]
        self._solx = sol[5]

    def value(self):
        return self._obj_value
    
def print_solution(solution: Solution):
    print_solution_summary(solution)


def _format_mapping_preview(name: str, mapping: dict, max_items: int = 5) -> str:
    items = list(mapping.items())
    preview = ", ".join(f"{k}: {v}" for k, v in items[:max_items])
    suffix = ", ..." if len(items) > max_items else ""

    if not items:
        return f"{name}: 0 entries"

    return f"{name}: {len(items)} entries -> {{{preview}{suffix}}}"


def print_solution_summary(solution: Solution, detailed: bool = False, max_items: int = 5):
    print(f"Solution status: {solution._status}")
    print(f"Objective value: {solution._obj_value}")
    print(f"Dual bound: {solution._dualBound}")
    print(f"Runtime: {solution._runtime:.3f} seconds")

    if detailed:
        print(f"solP1: {solution._solP1}")
        print(f"solP2: {solution._solP2}")
        print(f"soly: {solution._soly}")
        print(f"solr: {solution._solr}")
        print(f"sols: {solution._sols}")
        print(f"solx: {solution._solx}")
        return

    print(_format_mapping_preview("solP1", solution._solP1, max_items))
    print(_format_mapping_preview("solP2", solution._solP2, max_items))
    print(_format_mapping_preview("soly", solution._soly, max_items))
    print(_format_mapping_preview("solr", solution._solr, max_items))
    print(_format_mapping_preview("sols", solution._sols, max_items))
    print(_format_mapping_preview("solx", solution._solx, max_items))

def saveDataToFile(solution, dataFileName):
    import csv
    print("Saving to file ", dataFileName)

    outfile = open(dataFileName, 'w')
    writer = csv.writer(outfile, delimiter=";")
    writer.writerow([solution._status])
    writer.writerow([solution._obj_values])
    writer.writerow([solution._dualBound])
    writer.writerow([solution._runtime])
    writer.writerow(solution._solP1)
    writer.writerow(solution._solP2)
    writer.writerow(solution._soly)
    writer.writerow(solution._solr)
    writer.writerow(solution._sols)
    outfile.close()