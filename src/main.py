from demo import *


def main():
    print("=" * (15 - 2) + " TER " + "=" * (15 - 2))

    # read_file_demo()

    # model_demo("toy.txt", 0)
    # model_demo("toyy.txt", 0)
    # model_demo("data0.txt", 0)
    # model_demo("data0.txt", 1)
    # model_demo("data1.txt", 0)
    # model_demo("data4.txt", 0)

    ### data0 has 2 scenatios
    ### data1 has 10 scenatios
    ### data2 has 20 scenatios

    # heuristic_2_demo("toy.txt", 0, 63274200.0) # gap = -6.85%
    #heuristic_2_demo("data0.txt", 0, 8610050657314.8) # gap = -0.44%
    #heuristic_2_demo("data0.txt", 1, 8846806435123.2) # gap = -0.43%
    #heuristic_2_demo("data1.txt", 0, 170492782000) # gap = -12.24%
    #heuristic_2_demo("data5.txt", 0, 113322696311.46948) # gap = ?
    # heuristic_2_demo("data2.txt", 0, 1.4727594e+11) # gap = -16.71%

   # heuristic_2_2_demo("toy.txt", 0, 63274200.0) # gap = -2.13%
    # heuristic_2_2_demo("toyy.txt", 0, 58651800.0) # gap = -2.30%
    #heuristic_2_2_demo("data0.txt", 0, 8610050657314.8) # gap = -0.17%
    #heuristic_2_2_demo("data0.txt", 1, 8846806435123.2) # gap = -0.16%
    #heuristic_2_2_demo("data1.txt", 0, 170492782000) # gap = -7.39%
    #heuristic_2_2_demo("data1.txt", 1, 165495870429.0952) # 
   # heuristic_2_2_demo("data1.txt", 2, 162841643956.18933) # 
   # heuristic_2_2_demo("data1.txt", 3, 150696133283.6359) 
    # heuristic_2_2_demo("data1.txt", 4, 210107150010.10928) 
    #heuristic_2_2_demo("data2.txt", 0, 1.4727594e+11) 
    #heuristic_2_2_demo("data2.txt", 1, 152135839927.7093) 
   # heuristic_2_2_demo("data3.txt", 0, 1.39533299e+11) 
    #heuristic_2_2_demo("data3.txt", 1, 130381283710.15749) 
    #heuristic_2_2_demo("data5.txt", 0, 113322696311.46948) # gap = -3.95%
    # heuristic_2_2_demo("data2.txt", 0, 1.4727594e+11) # gap = -4.44%
    #heuristic_2_2_demo("data4.txt", 0, 115765240184.99612) # gap = -9.44%
    #heuristic_2_2_demo("data4.txt", 1, 100585552199.51825)

    # heuristic_2_2_1demo("data5.txt", 0, 113322696311.46948) # gap = -2.13% 

    # heuristic_2_RF_demo("toy.txt", 0, 58651800.0) # gap = 100% comme V2_basic
    # heuristic_2_RF_demo("toyy.txt", 0, 58651800.0) # gap = -6.85%
    # heuristic_2_RF_demo("data0.txt", 0, 8610050657314.8) # gap = -0.44%
    # heuristic_2_RF_demo("data0.txt", 1, 8846806435123.2) # gap = -0.43%
    # heuristic_2_RF_demo("data1.txt", 0, 170492782000) # gap = -12.24%
    # heuristic_2_RF_demo("data1.txt", 1, ) # gap = ?

    heuristic_3_dichotomie_demo("toy.txt", 0, 63274200.0) # gap = ?
    # heuristic_3_dichotomie_demo("toyy.txt", 0, 58651800.0) # gap = ?
    # heuristic_3_dichotomie_demo("data0.txt", 0, 8610050657314.8) # gap = ?
    # heuristic_3_dichotomie_demo("data0.txt", 1, 8846806435123.2) # gap = ?
    # heuristic_3_dichotomie_demo("data1.txt", 0, 170492782000) # gap = ?
    # heuristic_3_dichotomie_demo("data5.txt", 0, 113322696311.46948) # gap = ?
    # heuristic_3_dichotomie_demo("data2.txt", 0, 1.4727594e+11) # gap = ?
    # heuristic_3_dichotomie_demo("data4.txt", 1, 100585552199.51825) # gap = ?

if __name__ == "__main__":
    main()    