from demo import *


def main():
    print("=" * (15 - 2) + " TER " + "=" * (15 - 2))

    # read_file_demo()

    # model_demo("toy.txt", 0)
    # model_demo("toyy.txt", 0)
    # model_demo("data0.txt", 0)
    # model_demo("data0.txt", 1)
    # model_demo("data1.txt", 0)
    # model_demo("data1.txt", 1)

    ### data0 has 2 scenatios
    ### data1 has 10 scenatios
    ### data2 has 20 scenatios

    # heuristic_2_demo("toyy.txt", 0, 58651800.0) # gap = -6.85%
    # heuristic_2_demo("data0.txt", 0, 8610050657314.8) # gap = -0.44%
    # heuristic_2_demo("data0.txt", 1, 8846806435123.2) # gap = -0.43%
    # heuristic_2_demo("data1.txt", 0, 170492782000) # gap = -12.24%
    # heuristic_2_demo("data1.txt", 1, ) # gap = ?

    # heuristic_2_2_demo("toy.txt", 0, 58651800.0) # gap = -10.18%
    # heuristic_2_2_demo("toyy.txt", 0, 58651800.0) # gap = -2.30%
    # heuristic_2_2_demo("data0.txt", 0, 8610050657314.8) # gap = -0.17%
    # heuristic_2_2_demo("data0.txt", 1, 8846806435123.2) # gap = -0.16%
    # heuristic_2_2_demo("data1.txt", 0, 170492782000) # gap = -7.39%
    # heuristic_2_2_demo("data1.txt", 1, ) # gap = ?

    # heuristic_2_RF_demo("toy.txt", 0, 58651800.0) # gap = 100% comme V2_basic
    # heuristic_2_RF_demo("toyy.txt", 0, 58651800.0) # gap = -6.85%
    # heuristic_2_RF_demo("data0.txt", 0, 8610050657314.8) # gap = -0.44%
    # heuristic_2_RF_demo("data0.txt", 1, 8846806435123.2) # gap = -0.43%
    # heuristic_2_RF_demo("data1.txt", 0, 170492782000) # gap = -12.24%
    # heuristic_2_RF_demo("data1.txt", 1, ) # gap = ?

if __name__ == "__main__":
    main()    