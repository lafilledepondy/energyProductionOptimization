from demo import (model_demo, heuristic_basic_demo, 
    heuristic_basic_demo, heuristic_multiCamp_demo, 
    heuristic_optXandY_demo, heuristic_RF_demo, 
    heuristic_relaxLagrange_demo
    )
from helperPlots import (
    draw_cumulative_production_stack,
    extract_visualization_data_from_solution,
    draw_maintenance_schedule_production,
    save_stack_legend
    )

### data0 has 2 scenatios
### data1 has 10 scenatios
### data2 has 20 scenatios
### dara3 has 20 scenatios
### data4 has 30 scenatios
### data5 has 30 scenatios
TEST_CASES = {
    # ("FileName", Scenario): OptimalValue
    # ("toy.txt", 0): 63274200.0,
    ("toyy.txt", 0): 58651800.0,
    # ("data0.txt", 0): 8610050657314.8,
    # ("data0.txt", 1): 8846806435123.2,
    # ("data1.txt", 0): 170492782000,
    # ("data1.txt", 1): 165495870429.0952,
    # ("data1.txt", 2): 162841643956.18933,
    # ("data1.txt", 3): 150696133283.6359,
    # ("data1.txt", 4): 210107150010.10928,
    # ("data2.txt", 0): 1.4727594e+11,
    # ("data2.txt", 1): 152135839927.7093,
    # ("data3.txt", 0): 1.39533299e+11,
    # ("data3.txt", 1): 130381283710.15749,
    # ("data4.txt", 0): 115765240184.99612,
    # ("data4.txt", 1): 100585552199.51825,
    # ("data5.txt", 0): 113322696311.46948,
}

HEURISTICS = {
    # "heuristic": True or False,
    "heuristic_basic": False,
    "heuristic_multiCamp": False,
    "heuristic_optXandY": False,
    "heuristic_RF": False,
    "heuristic_relaxLagrange": False,
}

def main():
    print("=" * (15 - 2) + " TER " + "=" * (15 - 2))

    # read_file_demo()

    # model_demo("toy.txt", 0)
    # model_demo("toyy.txt", 0)

    for (filename, scenario), gap_value in TEST_CASES.items():
        for heuristic, enabled in HEURISTICS.items():
            if enabled:
                demo_func = globals()[f"{heuristic}_demo"]
                demo_func(filename, scenario, gap_value)
                print("\n" + "#" * 60)
                print("#" * 60)
                print("#" * 60 + "\n")

    ####### PLOTS #######
    # dataFile = "toyy.txt"
    # scheme = 0
    # data, sol = heuristic_2_demo(dataFile, scheme, 58651800.0)
    # title_stack = "Heuristique basique Solution - toy"
    # title_stack = "Plan de production réalisable - Heuristique basique - toy"

    # data, sol = heuristic_2_2_demo(dataFile, scheme, 58651800.0)
    # title_stack = "Heuristique multi-campagnes Solution - toy"

    # data, sol = heuristic_2_2_1demo(dataFile, scheme, 58651800.0)
    # title_stack = "Heuristique améliorée Solution - toy"
    # title_stack = "Plan de production réalisable - Heuristique améliorée - toy"

    # data, sol = heuristic_3_dichotomie_demo(dataFile, scheme, 58651800.0)
    # title_stack = "Relax. Lag. Solution - toy"
    # title_stack = "Plan de production réalisable - Relax. Lag. - toy"

    # data, sol = model_demo(dataFile, scheme)
    # title_stack = "Solution réalisable"
    # title_stack = "Plan de production réalisable - MILP - toy"

    # prod_data, maintenance_blocks, units, recharge_blocks, sols_blocks = extract_visualization_data_from_solution(sol, data)
    # draw_maintenance_schedule_production(prod_data, units, title_stack, maintenance_blocks, recharge_blocks, sols_blocks)

    # draw_cumulative_production_stack(prod_data, data, scheme, units, title_stack)
    # labels, colors = draw_cumulative_production_stack(prod_data, data, scheme, units, title_stack)
    # save_stack_legend(labels, colors, f"{title_stack.replace(' ', '_')}_legend.png")


    # title = "Période de maintenance possible pour chaque unité (i) - toy"
    # draw_maintenance_schedule_production([], units, title, maintenance_blocks, [])



if __name__ == "__main__":
    main()    