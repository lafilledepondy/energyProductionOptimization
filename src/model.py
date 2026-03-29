import time
from xml.parsers.expat import model
import highspy as hp

from solution import *
from data import *


def runMILPModel_1(data: Readingfile, outputFlag: bool, timeLimit: float):
    # ======= MODEL =======
    model = hp.Highs()
    model.setOptionValue('time_limit', timeLimit)
    model.setOptionValue('output_flag', outputFlag)

    # ======= DONNEES =======
    I1 = range(data.nbpower1())   
    I2 = range(data.nbpower2())  
    T = range(data.timestep())  
    W = range(data.weeks()) 
    campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
    horizon_last_t = data.timestep() - 1
    K_i = [  # 3D [ [ [range k_e à k_l] [...] by campagne ] [ []  [] ] by units]
        [
            list(
                range(
                    max(0, data.accessCampaign(i, k).earlieststop()), # j'ai ajoute le max pour eviter les valeurs negatives bcse it was giving me errors
                    min(horizon_last_t, data.accessCampaign(i, k).lateststop()) + 1, # same here
                )
            )
            for k in campaign_ids_by_unit[i]
        ]
        for i in I2
    ]

    K_i_simple = {}
    for i in I2:
        K_i_simple[i] = [t for campagne in K_i[i] for t in campagne]

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
    Rmax = [
        [
            data.accessCampaign(i, k).maxrefuel()
            for k in campaign_ids_by_unit[i]
        ]
        for i in I2
    ]  
    Smax = [
        [
            data.accessCampaign(i, k).maxstock()
            for k in campaign_ids_by_unit[i]
        ]
        for i in I2
    ]
    Sth_min = [data.accessPower2(i).minstock() for i in I2]
    X_i = [data.accessPower2(i).initialstock() for i in I2]  
    D_t = data.timestepduration()
    DA_ik = [
        [
            data.accessCampaign(i, k).durationoutage()
            for k in range(data.nbcampaigns())
        ]
        for i in I2
    ]   

    # ======= VARIABLES =======
    # y_it
    y_it = model.addVariables(I2, T, 
                             type=hp.HighsVarType.kInteger, 
                             lb=0, ub=1, 
                             name_prefix=f"y_{{i}}_{{t}}")
    # p_it    
    p1_it = model.addVariables(I1, T, 
                            type=hp.HighsVarType.kContinuous, 
                            lb=0,
                            name_prefix=f"p_{{i}}_{{t}}")  
    p2_it = model.addVariables(I2, T, 
                            type=hp.HighsVarType.kContinuous, 
                            lb=0,
                            name_prefix=f"p_{{i}}_{{t}}")  
    
    # r_it
    r_it = model.addVariables(I2, T,
                          type=hp.HighsVarType.kContinuous,
                          lb=0,
                          name_prefix="r_{i}_{t}")

    # s_it
    s_it = model.addVariables(I2, T,
                            type=hp.HighsVarType.kContinuous,
                            lb=0,
                            name_prefix="s_{i}_{t}")                          
    
    # TODO : ne prends pas en compte les k in K_i et t in k 
    # x_ikt indexed by (unit i, start time t, campaign index k_idx)
    max_campaigns = max((len(K_i[i]) for i in I2), default=0)
        
    index_set = [
    (i, k, t)
    for i in I2
    for k in range(len(K_i[i]))
    for t in K_i[i][k]
    ]

    x_ikt = model.addVariables(
        index_set,
        type=hp.HighsVarType.kInteger,
        lb=0,
        ub=1,
        name_prefix="x_{i}_{k}_{t}"
    )

    # ======= OBJECTIVE =======
    model.setObjective(
        sum(Cost_it[i][t] * p1_it[i, t] * D_t[t] 
            for i in I1 for t in T
        )
        +
        sum(
            RefCost_ik[i][k_idx] *
            sum(r_it[i, t] for t in T)
            for i in I2
            for k_idx in range(len(K_i[i]))
        )
        ,
        sense=hp.ObjSense.kMinimize
    )

    # ======= CONSTRAINTS =======
    for t in T:
        # (2) 
        model.addConstr(
            sum(p2_it[i, t] for i in I2)
                            >= Dem_t[t] - sum(p1_it[i, t] for i in I1),
            name=f"Demand_constraint_t{t}"
        )
        # (3)
        for i in I1:
            model.addConstr(
                p1_it[i, t] 
                        <= Pmax_1[i][t],
                name=f"Pmax1_constraint_i{i}_t{t}"
            )
        # (4)
        for i in I2:
            model.addConstr(
                p2_it[i, t] 
                        <= Pmax_2[i][t] * (1 - y_it[i, t]),
                name=f"Pmax2_constraint_i{i}_t{t}"
            )

    # stock 
    for i in I2:
        for t in T:
            if t == 0:
                # (5)
                model.addConstr(
                    s_it[i,t] == X_i[i] - p2_it[i,t]*D_t[t],
                    name=f"Stock_init_i{i}_t{t}"
                )
            else:
                # (6)
                model.addConstr(
                    s_it[i,t] == s_it[i,t-1] - p2_it[i,t]*D_t[t] + r_it[i,t],
                    name=f"Stock_i{i}_t{t}"
                )

            # (7)
            model.addConstr(
                s_it[i,t] <= Smax[i][0],
                name=f"Stock_max_i{i}_t{t}"
            )
            # (8)
            model.addConstr(
                s_it[i,t] >= Sth_min[i],
                name=f"Stock_min_i{i}_t{t}"
            )

    # (9)
    for i in I2:
        for t in T:
            for k_idx, k in enumerate(K_i[i]):
                if t in k:
                    model.addConstr(
                        r_it[i,t] <= Rmax[i][k_idx] * x_ikt[i,k_idx,t],
                        name=f"Refuel_limit_i{i}_t{t}"
                    )
            if t not in K_i_simple[i] :
                model.addConstr( r_it[i,t] == 0, name=f"Refuel_limit_i2{i}_t{t}")
                
    # (10) 
    for i in I2:
        for k_idx, k in enumerate(K_i[i]):
            model.addConstr(
                sum(x_ikt[i,k_idx, t] for t in k) <= 1,
                name=f"One_refuel_per_campaign_i{i}_k{k_idx}"
            )
    
    # (11)
    # for i in I2:
    #     for k_idx, k in enumerate(K_i[i]):
    #         for t in k:
    #             for j in range(t, t+DA_ik[i][k_idx]-1):
    #                 model.addConstr(
    #                     y_it[i][j] >= x_ikt[i][k][t],
    #                     name=f""
    #                 )

    # (12)
    for i in I2:
        model.addConstr(
            sum(y_it[i,t] for t in T) 
            == 
            sum (DA_ik[i][k_idx] * x_ikt[i,k_idx, t] 
                 for k_idx, k in enumerate(K_i[i]) 
                 for t in k),
            name=f"Link_y_x_i{i}"
        )

    # (13)
    for i in I2:
        for k_idx, k in enumerate(K_i[i]):
            for t in k:
                if t + DA_ik[i][k_idx] <= len(T):
                    model.addConstr(
                        sum(y_it[i, _t] for _t in range(t, t + DA_ik[i][k_idx]))
                        >= 
                        DA_ik[i][k_idx] * x_ikt[i, k_idx, t ],
                        name=f"Link_y_xx_i{i}_t{t}_k{k_idx}"
                    )
                else:
                    model.addConstr(x_ikt[i, k_idx, t] == 0, name=f"Forbid_x_{i}_{k_idx}_{t}")
        
    # ===== EXTRACT SOLUTION =====
    start_time = time.time()
    #status = model.optimize()
    model.run()
    end_time = time.time()
    runtime = end_time - start_time

    print("\n----------------------------------")
    info = model.getInfo()
    model_status = model.getModelStatus()
    print('Status de la résolution par le solveur = ', model.modelStatusToString(model_status))
    print("Valeur de la fonction objectif = ", model.getObjectiveValue())
    print("Meilleure borne inférieure sur la valeur de la fonction objectif: ", info.mip_dual_bound)
    print("Gap: ", info.mip_gap)
    print("# de noeuds explorés: ", info.mip_node_count)
    print("Temps de résolution (en secondes) = ", runtime)
    print("----------------------------------")

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
        y_solution = {(i,t): model.variableValue(y_it[i,t]) for i in I2 for t in T if model.variableValue(y_it[i,t]) > 0.1}
        r_solution = {(i,t): model.variableValue(r_it[i,t]) for i in I2 for t in T if model.variableValue(r_it[i,t]) > 0.1}
        s_solution = {(i,t): model.variableValue(s_it[i,t]) for i in I2 for t in T}
        x_solution = {
            (i, k_idx, t): model.variableValue(x_ikt[i,k_idx, t])
            for i in I2
            for k_idx, k in enumerate(K_i[i])
            for t in k
            if model.variableValue(x_ikt[i,k_idx, t]) > 0.1
        }

        sol = [p1_solution, p2_solution, y_solution, r_solution, s_solution, x_solution]
       

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
        #     for k_idx, k in enumerate(K_i[i]):
        #         refuel_cost += RefCost_ik[i][k_idx] * sum(r_solution[i, t] for t in k)
  

        # for t in T:
        #     prod1_t = sum(p1_solution[i,t] for i in I1)
        #     prod2_t = sum(p2_solution[i,t] for i in I2)
        #     total_refuel_t = sum(r_solution[i, t] for i in I2)
        #     stocks_t = {i: s_solution[i,t] for i in I2}
        #     print(f"t={t} : production1={prod1_t}, production2={prod2_t}, total={prod1_t+prod2_t}, demand={Dem_t[t]}, total recharge={total_refuel_t}, stocks={stocks_t}")
        
        # print(f"Total production cost: {production_cost}")
        # print(f"Total refueling cost: {refuel_cost}")
        # print(sol[2])
        # print(sol[5])


    else:
        obj_value = -1
        sol = [0,0,0,0,0,0]

    return Solution(model.modelStatusToString(model_status), 
                    obj_value, 
                    model.getInfo().mip_dual_bound, runtime, sol)


def runMILPModel_2(data: Readingfile, outputFlag: bool, timeLimit: float):
    # ======= VARIABLES =======


    # ======= OBJECTIVE =======


    # ======= CONSTRAINTS =======


    # ======= MODEL =======

    
    # ===== EXTRACT SOLUTION =====
 
    # return Solution(status, obj_value, dualBound, runtime)
    pass