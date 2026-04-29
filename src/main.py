from demo import *


def main():
    print("=" * (15 - 2) + " TER " + "=" * (15 - 2))

    # read_file_demo()

    # model_demo("toy.txt", 0)
    # model_demo("data0.txt", 0)
    # model_demo("data0.txt", 1)
    # model_demo("data1.txt", 0)
    # model_demo("data1.txt", 1)

    # heuristic_2_demo("toyy.txt", 0, 58651800.0)
    # heuristic_2_demo("data0.txt", 0, 8610050657314.8)
    # heuristic_2_demo("data1.txt", 0, 170492782000  )
    # heuristic_2_demo("data1.txt", 1, )

    heuristic_2_2_demo("toyy.txt", 0, 58651800.0)
    # heuristic_2_2_demo("data0.txt", 0, 8610050657314.8)
    # heuristic_2_2_demo("data0.txt", 1, 8846806435123.2)
    # heuristic_2_2_demo("data1.txt", 0, 170492782000  )



if __name__ == "__main__":
    main()    