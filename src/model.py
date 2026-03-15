import time
import highspy as hp

from solution import Solution
from data import Readingfile


def runMILPModel_1(data: Readingfile, outputFlag: bool, timeLimit: float):
    # ======= MODEL =======
    model = hp.Highs()
    model.setOptionValue('time_limit', timeLimit)
    model.setOptionValue('output_flag', outputFlag)

    # ======= DONNEES =======
    I1 = range(data.nbpower1())
    I2 = range(data.nbpower2())
    W = range(data.weeks())
    T = range(data.timestep())
    K_i = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
    IK = [(i, k) for i in I2 for k in K_i[i]]

    Dem_t = data.accessScenario(0).demands()
    Cost_it = [
        [data.accessPower1(0, i).cost()[t] for t in T]
        for i in I1]  # Cost_it[i][t]
    RefCost_ik = [
        [float(data.accessCampaign(i, k).refuelingcost()) 
            for k in range(len(data.accessPower2(i).Campaigns()))
        ]
        for i in I2
    ]
    Pmax_1 = [
        [data.accessPower1(0, i).pmax()[t] for t in T]
        for i in I1]  # Type 1 units: Pmax_1[i][t]
    Pmax_2 = [
        [data.accessPower2(i).pmax()[t] for t in T]
        for i in I2]  # Type 2 units: Pmax_2[i][t]
    # Rmax
    # Smax
    # Sth_min
    # X_i1
    D_t = data.timestepduration()
    # Da_ik

    # ======= VARIABLES =======
    # y_it
    y_it = model.addVariables(I2, T, 
                             type=hp.HighsVarType.kInteger, 
                             lb=0, ub=1, 
                             name_prefix=f"y_{{i}}_{{t}}")
    # p_it
    p_it = model.addVariables(list(I1) + list(I2), T,
                            type=hp.HighsVarType.kContinuous,
                            lb=0,
                            name_prefix=f"p_{{i}}_{{t}}")    
    
    # r_it indexed on existing campaigns only: (i, k)
    r_it = model.addVariables(IK,
                            type=hp.HighsVarType.kContinuous,
                            lb=0,
                            name_prefix=f"r_{{ik}}")

    # ======= OBJECTIVE =======
    model.setObjective(
        sum(Cost_it[i][t] * p_it[i, t] * D_t[t] for i in I1 for t in T)
        + sum(RefCost_ik[i][k] * r_it[i, k] for i in I2 for k in K_i[i])
        , sense=hp.ObjSense.kMinimize
    )

    # ======= CONSTRAINTS =======
    # (2)
    # for t in T:
    #     model.addConstr(
    #         sum(p_it[i, t] for i in I2) 
    #                         >= Dem_t[t] - sum(p_it[i, t] for i in I1),
    #         name=f"Demand_constraint_t{t}"
    #     )
    # (3)
    for t in T:
        for i in I1:
            model.addConstr(
                p_it[i, t] 
                        <= Pmax_1[i][t],
                name=f"Pmax1_constraint_i{i}_t{t}"
            )
    # (4)
    # for t in T:
    #     for i in I2:
    #         model.addConstr(
    #             p_it[i, t] 
    #                     <= Pmax_2[i][t] * (1 - y_it[i, t]),
    #             name=f"Pmax2_constraint_i{i}_t{t}"
    #         )
    
    # ===== EXTRACT SOLUTION =====
    start_time = time.time()
    status = model.optimize()
    end_time = time.time()
    runtime = end_time - start_time

    # On vérifie si une solution primale exploitable existe (optimale ou faisable)
    model_status = model.getModelStatus()
    primal_status = model.getInfo().primal_solution_status
    if (
        model_status == hp.HighsModelStatus.kOptimal
        or primal_status == hp.SolutionStatus.kSolutionStatusFeasible
    ):
        obj_value = model.getObjectiveValue()
    else:
        obj_value = -1

    return Solution(model.modelStatusToString(model_status), 
                    obj_value, 
                    model.getInfo().mip_dual_bound, runtime)


def runMILPModel_2(data: Readingfile, outputFlag: bool, timeLimit: float):
    # ======= VARIABLES =======


    # ======= OBJECTIVE =======


    # ======= CONSTRAINTS =======


    # ======= MODEL =======

    
    # ===== EXTRACT SOLUTION =====
 
    # return Solution(status, obj_value, dualBound, runtime)
    pass