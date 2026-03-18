from pathlib import Path
import sys
import subprocess
import os

from demo import *
from gui import gui_main

def _print_banner(title, subtitle=None, width=60):
    border = "+" + "=" * (width - 2) + "+"
    body_width = width - 4
    print(border)
    print(f"| {title.center(body_width)} |")
    if subtitle:
        print(f"| {subtitle.center(body_width)} |")
    print(border)

def pseudo_main():
    """
        * if no arguments are provided, launch the GUI
        * else call solver.py with the given arguments
    """
    if len(sys.argv) == 1:
        gui_main()
        return
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    solver_path = os.path.join(script_dir, "solver.py")

    cmd = [sys.executable, solver_path] + sys.argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

def main():
    _print_banner(
        title="TODO",
        subtitle="TER",
        width=66,
    )

    # === Uncomment to run the GUI or the solver with command-line arguments ===
    # pseudo_main()

    # === Uncomment to run a specific demo === 
    # read_file()
    model_demo()

if __name__ == "__main__":
    main()    