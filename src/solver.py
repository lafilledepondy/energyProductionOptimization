# DISCLAIMER : Inspiré par le code du projet d’optimisation ROAD 2026 du Pr PRUNET Thibault

import sys
import time
import argparse
import os
import highspy as hp

from model import *
from data import *
from projectUtils import valid_file, valid_folder, positive_int
from solution import recordSolution

# -----------------------------
# Argument parser
# -----------------------------
parser = argparse.ArgumentParser(description="Process command line arguments.")

# Required arguments
parser.add_argument("-d", "--dataFilePath", type=valid_file, required=True,
                    help="The path to the data file.")
parser.add_argument("-v", "--version", type=int, required=True, choices=[1, 2],
                    help="The version of the problem.")
# Optional arguments
parser.add_argument("-t", "--timeLimit", type=positive_int, default=30,
                    help="The time limit. Default is 30.")
parser.add_argument("-p", "--print", action="store_true",
                    help="Verbose output or not.")
parser.add_argument("-f", "--solutionFolderPath", type=valid_folder, default=None,
                    help="The path to the solution folder. If not provided, ./output_exe is created and used.")

args = parser.parse_args()
solver_name = "appsi_highs"

if args.solutionFolderPath is None:
    args.solutionFolderPath = "output_exe"
    os.makedirs(args.solutionFolderPath, exist_ok=True)

print("----------- ARGUMENTS -----------")
print("Data file path =", args.dataFilePath)
print("Problem version =", args.version)
print("Time limit =", args.timeLimit)
print("Verbose output =", args.print)
print("Solution folder path =", args.solutionFolderPath)
print("Solver name =", solver_name)
print("------------------------------------")


# -----------------------------
# Read data
# -----------------------------
dataFileName = os.path.splitext(os.path.basename(args.dataFilePath))[0]
data = Readingfile(args.dataFilePath)

# -----------------------------
# Solver availability check
# -----------------------------
solver = hp.Highs()
print("Solver", solver_name, "is initialized.")


# -----------------------------
# Solve
# -----------------------------
if args.version == 1:
    if args.print:
        print("TODO")
    solution = runMILPModel_1(
        data, args.print, args.timeLimit
    )
elif args.version == 2:
    if args.print:
        print("TODO")
    solution = runMILPModel_2(
        data, args.print, args.timeLimit
    )
else:
    print("Unknown version of the problem")
    sys.exit(1)

# -----------------------------
# Prepare solution dict for downstream functions expecting a mapping
# -----------------------------
# solution_dict = vars(solution) if solution is not None else None

# -----------------------------
# Output
# -----------------------------
# print("\ndataFileName =", dataFileName)
# print("solutionValue =", solution.value())
# print("cpuTime =", end - begin)

# -----------------------------
# Save data to file
# -----------------------------
# if solution is not None and solution_dict is not None:
#     solution.recordSolution(data, str(args.version), solution_dict, dataFileName)
# else:
#     print("No solution found; nothing saved.")

# if solution is not None:
#     # Check the solution
#     # isFeasible = checkSolution(data, solution, args.version, args.print)
#     # print("isFeasible =", isFeasible)

#     # Write the solution to the file
#     solutionFilePath = dataFileName + "_V" + str(args.version) + ".sol"
#     solutionFilePath = os.path.join(args.solutionFolderPath, solutionFilePath)
#     print("Solution is written in the following file: ", solutionFilePath)
#     recordSolution(data, solution, solutionFilePath)
# else:
#     print("isFeasible =", False)

# print("\nRESULT;", dataFileName, ";", solution.value(), ";", isFeasible, ";", end - begin)

sys.exit(0)
