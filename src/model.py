import time
from xml.parsers.expat import model
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
    Sth_min = [data.accessPower2(i).minstock() for i in I2]
    # X_i1
    X_i = [data.accessPower2(i).initialstock() for i in I2]  
    D_t = data.timestepduration()
    # Da_ik

    # ======= VARIABLES =======
    # y_it
    y_it = model.addVariables(I2, T, 
                             type=hp.HighsVarType.kInteger, 
                             lb=0, ub=1, 
                             name_prefix=f"y_{{i}}_{{t}}")
    # p_it
    # p_it = model.addVariables(list(I1) + list(I2), T,
    #                         type=hp.HighsVarType.kContinuous,
    #                         lb=0,
    #                         name_prefix=f"p_{{i}}_{{t}}")    
    p1_it = model.addVariables(I1, T, 
                            type=hp.HighsVarType.kContinuous, 
                            lb=0,
                            name_prefix=f"p_{{i}}_{{t}}")  
    p2_it = model.addVariables(I2, T, 
                            type=hp.HighsVarType.kContinuous, 
                            lb=0,
                            name_prefix=f"p_{{i}}_{{t}}")  
    
    # r_it indexed on existing campaigns only: (i, k)
    r_ik = model.addVariables(IK,
                          type=hp.HighsVarType.kContinuous,
                          lb=0,
                          name_prefix="r_{i}_{k}")

    # x_ik
    x_ik = model.addVariables(IK,
                            type=hp.HighsVarType.kInteger,
                            lb=0, ub=1,
                            name_prefix="x_{ik}")

    # s_it
    s_it = model.addVariables(I2, T,
                            type=hp.HighsVarType.kContinuous,
                            lb=0,
                            name_prefix="s_{i}_{t}")

    # ======= OBJECTIVE =======
    model.setObjective(
        sum(Cost_it[i][t] * p1_it[i, t] * D_t[t] for i in I1 for t in T)
        + sum(RefCost_ik[i][k] * r_ik[i,k] for i in I2 for k in K_i[i])
        , sense=hp.ObjSense.kMinimize
    )

    # ======= CONSTRAINTS =======
    # (2) 
    for t in T:
        model.addConstr(
            sum(p2_it[i, t] for i in I2) + sum(p1_it[i, t] for i in I1)
                            >= Dem_t[t] ,
            name=f"Demand_constraint_t{t}"
        )
    # (3)
    for t in T:
        for i in I1:
            model.addConstr(
                p1_it[i, t] #== 10 pr verifier que les contraintes sont bien prises en compte,
                        <= Pmax_1[i][t],
                name=f"Pmax1_constraint_i{i}_t{t}"
            )
    #(4)
    for t in T:
        for i in I2:
            model.addConstr(
                p2_it[i, t] 
                        <= Pmax_2[i][t] * (1 - y_it[i, t]),
                name=f"Pmax2_constraint_i{i}_t{t}"
            )
    #(5) et (6)
    # stock 
    for i in I2:
        for t in T:
            if t == 0:
                model.addConstr(
                    s_it[i,t] == X_i[i] - p2_it[i,t]*D_t[t] + sum(r_ik[i,k] for k in K_i[i]),
                    name=f"Stock_init_i{i}_t{t}"
                )
            else:
                model.addConstr(
                    s_it[i,t] == s_it[i,t-1] - p2_it[i,t]*D_t[t] + sum(r_ik[i,k] for k in K_i[i]),
                    name=f"Stock_i{i}_t{t}"
                )
            model.addConstr(
                s_it[i,t] >= Sth_min[i],
                name=f"Stock_min_i{i}_t{t}"
            )
        
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
        # for i in I2:
        #     for k in K_i[i]:
        #         print(f"i={i}, k={k}, refuel cost={RefCost_ik[i][k]}")

        
        p1_solution = {(i,t): model.variableValue(p1_it[i,t]) for i in I1 for t in T}
        p2_solution = {(i,t): model.variableValue(p2_it[i,t]) for i in I2 for t in T}
        r_solution = {(i,k): model.variableValue(r_ik[i,k]) for i in I2 for k in K_i[i]}
        s_solution  = {(i,t): model.variableValue(s_it[i,t]) for i in I2 for t in T}
       

        # # ===== Pour verif =====
        # production_cost = 0.0
        # for i in I1:
        #     for t in T:
        #         production_cost += Cost_it[i][t] * p1_solution[i,t] * D_t[t]

        # for i in I2:
        #     for t in T:
        #         production_cost += 0  
                
        # refuel_cost = 0.0
        # for i in I2:
        #     for k in K_i[i]:
        #         refuel_cost += RefCost_ik[i][k] * r_solution[i,k]
        
       

  

        # for t in T:
        #     prod1_t = sum(p1_solution[i,t] for i in I1)
        #     prod2_t = sum(p2_solution[i,t] for i in I2)
        #     total_refuel_t = sum(r_solution[i,k] for i in I2 for k in K_i[i])
        #     stocks_t = {i: s_solution[i,t] for i in I2}
        #     print(f"t={t} : production1={prod1_t}, production2={prod2_t}, total={prod1_t+prod2_t}, demand={Dem_t[t]}, total recharge={total_refuel_t}, stocks={stocks_t}")
        
        # print(f"Total production cost: {production_cost}")
        # print(f"Total refueling cost: {refuel_cost}")


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