from pathlib import Path
import sys
import subprocess
import os

from demo import *

def _print_banner(title, subtitle=None, width=60):
    border = "+" + "=" * (width - 2) + "+"
    body_width = width - 4
    print(border)
    print(f"| {title.center(body_width)} |")
    if subtitle:
        print(f"| {subtitle.center(body_width)} |")
    print(border)

def main():
    _print_banner(
        title="TODO",
        subtitle="TER",
        width=66,
    )

    # === Uncomment to run the GUI or the solver with command-line arguments ===
    # pseudo_main()

    # === Uncomment to run a specific demo === 
    # read_file_demo()

    # model_demo("toy.txt", 0)
    # model_demo("data0.txt", 0)
    # model_demo("data0.txt", 1)
    # model_demo("data1.txt", 0)
    # model_demo("data1.txt", 1)

    # heuristic_2_demo("toyy.txt", 0, 58651800.0)
    # heuristic_2_2_demo("toyy.txt", 0, 58651800.0)
    # heuristic_2_demo("data0.txt", 0, 8610050657314.8)
    # heuristic_2_2_demo("data0.txt", 0, 8610050657314.8)
    # heuristic_2_2_demo("data0.txt", 1, 8846806435123.2)
    heuristic_2_demo("data1.txt", 0, 170492782000  )
    heuristic_2_2_demo("data1.txt", 0, 170492782000  )
    # heuristic_2_demo("data1.txt", 1, )



if __name__ == "__main__":
    main()    