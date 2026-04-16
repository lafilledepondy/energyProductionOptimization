import time
from xml.parsers.expat import model
import highspy as hp

try:
    from .data import Readingfile
    from .solution import Solution
except ImportError:
    from data import Readingfile
    from solution import Solution

# -----------------------------
# Abstract class
# -----------------------------
class AbstractMaintenanceHeuristic:
    def solve(self, data: Readingfile, scenario: int) -> Solution:
        raise NotImplementedError

# -----------------------------
#  Heuristic 1
# -----------------------------
class MaintenanceHeuristicV1(AbstractMaintenanceHeuristic): 
    def computePriorityScores(self, data: Readingfile) -> list[tuple[int, float]]:
        w_i_tab = []
        I2 = range(data.nbpower2())
        Xi1 = [data.accessPower2(i).initialstock() for i in I2]
        Sth_min = [data.accessPower2(i).minstock() for i in I2]
        campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
        Smax_ik = [
            [
                data.accessCampaign(i, k).maxstock()
                for k in campaign_ids_by_unit[i]
            ]
            for i in I2
        ]
        T = range(data.timestep()) 
        Pmax_2 = [
            [data.accessPower2(i).pmax()[t] for t in T]
            for i in I2
        ]  # Type 2 units: Pmax_2[i][t]
        tot_Pmax_ik = [
            sum(Pmax_2[i][t] for t in T) for i in I2
        ]
        horizon_last_t = data.timestep() - 1
        K_i = []
        for i in I2:
            campaigns_i = []
        
            for k in campaign_ids_by_unit[i]:
                start = max(0, data.accessCampaign(i, k).earlieststop())
                end   = min(horizon_last_t, data.accessCampaign(i, k).lateststop())
            
                k_range = list(range(start, end + 1))
            
                if k_range != [0]:   
                    campaigns_i.append(k_range)
            K_i.append(campaigns_i)

        K_i_simple = {}
        for i in I2:
            K_i_simple[i] = [t for campagne in K_i[i] for t in campagne]
            

        for i in I2:
            if all(v == Smax_ik[i][0] for v in Smax_ik[i]):
                smax_i = Smax_ik[i][0]
            else:
                print(f"Warning: Smax_ik values are not the same for all campaigns of unit {i}.")
                            
            Wi = (Xi1[i] - Sth_min[i]) / (smax_i - Sth_min[i]) # stock (Xi1 - Sth_min_i) / (Smax_ik - Sth_min_i)
            Wi += sum(Pmax_2[i][t] for t in T) / tot_Pmax_ik[i] # puissance
            Wi += 1 - (len(K_i_simple[i])/(data.timestep())) # fenetres de maintenance

            w_i_tab.append((i, Wi))

        return w_i_tab

    def sortPlantsByPriority(self, priorityScores: list[tuple[int, float]]) -> list[tuple[int, float]]:
        return sorted(priorityScores, key=lambda x: x[1], reverse=True) # tri decroissant

    def findFeasibleStartTime(
        self,
        data: Readingfile,
        i: int,
        demand: list[float],
        remaining_capacity: list[float],
    ) -> tuple[int, int] | None:
        plant = data.accessPower2(i)
        T = data.timestep()

        # !(initial stock >= min stock)
        if plant.initialstock() < plant.minstock():
            return None

        for k_index, campaign in enumerate(plant.Campaigns()):
            duration = campaign.durationoutage()
            start_min = max(0, campaign.earlieststop())
            start_max = min(campaign.lateststop(), T - duration)

            if start_min > start_max:
                continue

            for t_start in range(start_min, start_max + 1):
                feasible = True

                for t in range(t_start, t_start + duration):
                    # cdt 1 (demande) et 2 (stock)
                    if remaining_capacity[t] - plant.pmax()[t] < demand[t]:
                        feasible = False
                        break

                if feasible:
                    return k_index, t_start

        return None

    def scheduleMaintenance(self, data: Readingfile) -> tuple[list[list[int]], list[list[tuple[int, int]]]] | None:
        T = data.timestep()
        I2 = data.nbpower2()
        y_it = [[0 for _ in range(T)] for _ in range(I2)]
        x_itk = [[] for _ in range(I2)]

        # etape 1
        scores = self.computePriorityScores(data)
        ordered_plants = self.sortPlantsByPriority(scores)

        # etape 2
        scenario = data.accessScenario(0)
        demand = scenario.demands()[:]

        # generation capacity per timestep before scheduling outages
        remaining_capacity = [0.0 for _ in range(T)]
        for t in range(T):
            total_pmax_type1 = sum(
                data.accessPower1(0, j).pmax()[t] for j in range(data.nbpower1())
            )
            total_pmax_type2 = sum(
                data.accessPower2(j).pmax()[t] for j in range(data.nbpower2())
            )
            remaining_capacity[t] = total_pmax_type1 + total_pmax_type2

        # etape 3
        for (i, _) in ordered_plants:
            result = self.findFeasibleStartTime(data, i, demand, remaining_capacity)

            if result is None:
                return None

            k_index, t_start = result
            plant = data.accessPower2(i)
            duration = plant.Campaigns()[k_index].durationoutage()
            x_itk[i].append((k_index, t_start)) # stock le choix

            for t in range(t_start, t_start + duration):
                y_it[i][t] = 1
                remaining_capacity[t] -= plant.pmax()[t]

        return y_it, x_itk

    def computeProductionPlan(
        self,
        data: Readingfile,
        y_it: list[list[int]],
        x_itk: list[list[tuple[int, int]]],
    ) -> tuple[
        dict[tuple[int, int], float],
        dict[tuple[int, int], float],
        dict[tuple[int, int], float],
        dict[tuple[int, int], float],
    ]:
        T = data.timestep()
        # p1_sol = {
        #     (i, t): float(data.accessPower1(0, i).pmax()[t])
        #     for i in range(data.nbpower1())
        #     for t in range(T)
        # }
        p1_sol: dict[tuple[int, int], float] = {}
        p2_sol: dict[tuple[int, int], float] = {}
        r_sol: dict[tuple[int, int], float] = {}
        s_sol: dict[tuple[int, int], float] = {}

        scheduled_campaign_start = {
            i: {t_start: k_index for k_index, t_start in x_itk[i]}
            for i in range(data.nbpower2())
        }
        productiontot = [0 for t in range(T)]
        for i in range(data.nbpower2()):
            plant = data.accessPower2(i)
            stock = float(plant.initialstock())

            for t in range(T):
                if t in scheduled_campaign_start[i]:
                    campaign = plant.Campaigns()[scheduled_campaign_start[i][t]]
                    target_stock = float(campaign.maxstock())
                    refuel = max(0.0, campaign.maxrefuel()) #target_stock - stock  Modif pour produire que ce qu'on peut
                    if refuel > 0:
                        r_sol[(i, t)] = refuel
                    stock += refuel

                production = 0.0 if y_it[i][t] == 1 else min(float(plant.pmax()[t]), data.accessScenario(0).demands()[t]- productiontot[t]) # Modif pour produire que si on en a besoin sinon on produit max possible
                if stock - plant.minstock()*0.1 - production* float(data.timestepduration()[t]) < 0 :
                    production = (stock - plant.minstock()*0.1)/float(data.timestepduration()[t])
                p2_sol[(i, t)] = production
                stock -= production * float(data.timestepduration()[t])
                s_sol[(i, t)] = stock
                productiontot[t] += production

        for i in range(data.nbpower1()):
            plant = data.accessPower1(0,i)
            for t in range(T):
                reste = data.accessScenario(0).demands()[t]- productiontot[t]
                sep = reste / data.nbpower1()
                p1_sol[(i, t)] = sep

        return p1_sol, p2_sol, r_sol, s_sol

    def solve(self, data: Readingfile, scenario: int) -> Solution:
        start_time = time.time()
        result = self.scheduleMaintenance(data)

        if result is None:
            return None

        y_it, x_itk = result
        p1_sol, p2_sol, r_it, s_it = self.computeProductionPlan(data, y_it, x_itk)

        y_sol = {
            (i, t): 1
            for i in range(data.nbpower2())
            for t in range(data.timestep())
            if y_it[i][t] == 1
        }
        x_sol = {
            (i, k_index, t_start): 1
            for i, campaigns in enumerate(x_itk)
            for k_index, t_start in campaigns
        }

        sol = [p1_sol, p2_sol, y_sol, r_it, s_it, x_sol]

        runtime = time.time() - start_time

        # calcul de la fct obj
        I1 = range(data.nbpower1())   
        I2 = range(data.nbpower2())
        T = range(data.timestep())
        campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
        horizon_last_t = data.timestep() - 1
        K_i = []
        for i in I2:
            campaigns_i = []
        
            for k in campaign_ids_by_unit[i]:
                start = max(0, data.accessCampaign(i, k).earlieststop())
                end   = min(horizon_last_t, data.accessCampaign(i, k).lateststop())
            
                k_range = list(range(start, end + 1))
            
                if k_range != [0]:   
                    campaigns_i.append(k_range)
        
            K_i.append(campaigns_i)
        K_i_simple = {}
        for i in I2:
            K_i_simple[i] = [t for campagne in K_i[i] for t in campagne]
        RefCost_ik = [
                [float(data.accessCampaign(i, k).refuelingcost()) 
                    for k in range(len(data.accessPower2(i).Campaigns()))
                ]
            for i in I2
            ]
        Cost_it = [
        [data.accessPower1(scenario, i).cost()[t] for t in T]
        for i in I1]  # Cost_it[i][t]
        D_t = data.timestepduration()

        obj_value = (
            sum(
                Cost_it[i][t] * p1_sol.get((i, t), 0.0) * D_t[t]
                for i in I1
                for t in T
            )
            +
            sum(
                RefCost_ik[i][k_idx] *
                sum(r_it.get((i, t), 0.0) for t in K_i[i][k_idx])
                for i in I2
                for k_idx in range(len(K_i[i]))
            )
        )

        return Solution("HEURISTIC_1", 
                    obj_value, 
                    float('inf'), runtime, sol)
    
# -----------------------------
#  Heuristic 2
# -----------------------------
class MaintenanceHeuristicV2(AbstractMaintenanceHeuristic): 
    def computePriorityScores(self, data: Readingfile) -> list[tuple[int, float]]:
        w_i_tab = []
        I2 = range(data.nbpower2())
        Xi1 = [data.accessPower2(i).initialstock() for i in I2]
        Sth_min = [data.accessPower2(i).minstock() for i in I2]
        campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
        Smax_ik = [
            [
                data.accessCampaign(i, k).maxstock()
                for k in campaign_ids_by_unit[i]
            ]
            for i in I2
        ]
        T = range(data.timestep()) 
        Pmax_2 = [
            [data.accessPower2(i).pmax()[t] for t in T]
            for i in I2
        ]  # Type 2 units: Pmax_2[i][t]
        tot_Pmax_ik = [
            sum(Pmax_2[i][t] for t in T) for i in I2
        ]
        horizon_last_t = data.timestep() - 1
        K_i = []
        for i in I2:
            campaigns_i = []
        
            for k in campaign_ids_by_unit[i]:
                start = max(0, data.accessCampaign(i, k).earlieststop())
                end   = min(horizon_last_t, data.accessCampaign(i, k).lateststop())
            
                k_range = list(range(start, end + 1))
            
                if k_range != [0]:   
                    campaigns_i.append(k_range)
            K_i.append(campaigns_i)

        K_i_simple = {}
        for i in I2:
            K_i_simple[i] = [t for campagne in K_i[i] for t in campagne]
            

        for i in I2:
            if all(v == Smax_ik[i][0] for v in Smax_ik[i]):
                smax_i = Smax_ik[i][0]
            else:
                print(f"Warning: Smax_ik values are not the same for all campaigns of unit {i}.")
                            
            Wi = (Xi1[i] - Sth_min[i]) / (smax_i - Sth_min[i]) # stock (Xi1 - Sth_min_i) / (Smax_ik - Sth_min_i)
            Wi += sum(Pmax_2[i][t] for t in T) / tot_Pmax_ik[i] # puissance
            Wi += 1 - (len(K_i_simple[i])/(data.timestep())) # fenetres de maintenance

            w_i_tab.append((i, Wi))

        return w_i_tab

    def sortPlantsByPriority(self, priorityScores: list[tuple[int, float]]) -> list[tuple[int, float]]:
        return sorted(priorityScores, key=lambda x: x[1], reverse=True) # tri decroissant

    def scheduleMaintenance(self, data: Readingfile) -> tuple[list[list[int]], list[list[tuple[int, int]]]] | None:
        T = data.timestep()
        I2 = data.nbpower2()
        y_it = [[0 for _ in range(T)] for _ in range(I2)]
        x_itk = [[] for _ in range(I2)]

        # etape 1
        scores = self.computePriorityScores(data)
        ordered_plants = self.sortPlantsByPriority(scores)

        # etape 2
        scenario = data.accessScenario(0)
        demand = scenario.demands()[:]

        # generation capacity per timestep before scheduling outages
        remaining_capacity = [0.0 for _ in range(T)]
        for t in range(T):
            total_pmax_type1 = sum(
                data.accessPower1(0, j).pmax()[t] for j in range(data.nbpower1())
            )
            total_pmax_type2 = sum(
                data.accessPower2(j).pmax()[t] for j in range(data.nbpower2())
            )
            remaining_capacity[t] = total_pmax_type1 + total_pmax_type2      
        return y_it, x_itk   
    
######################

    def solve(self, data: Readingfile, scenario: int) -> Solution:
        result = self.scheduleMaintenance(data)

        if result is None:
            return None

        y_it, x_itk = result
        print("y_it:", y_it)
        print("x_itk:", x_itk)
        
        # etape 3

        # y_sol = {
        #     (i, t): 1
        #     for i in range(data.nbpower2())
        #     for t in range(data.timestep())
        #     if y_it[i][t] == 1
        # }
        # x_sol = {
        #     (i, k_index, t_start): 1
        #     for i, campaigns in enumerate(x_itk)
        #     for k_index, t_start in campaigns
        # }

        # sol = [p1_sol, p2_sol, y_sol, r_it, s_it, x_sol]

        # print(y_sol)
        # print(x_sol)

        return Solution("HEURISTIC_2", float('inf'), float('inf'), 0, [{}, {}, {}, {}, {}, {}])
    
    #     # ======= MODEL =======
    #     model = hp.Highs()
    #     model.setOptionValue('time_limit', timeLimit)
    #     model.setOptionValue('output_flag', outputFlag)

    #     # ======= DONNEES =======
    #     I1 = range(data.nbpower1())   
    #     I2 = range(data.nbpower2())  
    #     T = range(data.timestep())  
    #     W = range(data.weeks()) 
    #     campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
    #     horizon_last_t = data.timestep() - 1
    #     K_i = []
    #     for i in I2:
    #         campaigns_i = []
        
    #         for k in campaign_ids_by_unit[i]:
    #             start = max(0, data.accessCampaign(i, k).earlieststop())
    #             end   = min(horizon_last_t, data.accessCampaign(i, k).lateststop())
            
    #             k_range = list(range(start, end + 1))
            
    #             if k_range != [0]:   
    #                 campaigns_i.append(k_range)
        
    #         K_i.append(campaigns_i)
    #     K_i_simple = {}
    #     for i in I2:
    #         K_i_simple[i] = [t for campagne in K_i[i] for t in campagne]

    #     Dem_t = data.accessScenario(scenario).demands()
    #     Cost_it = [
    #         [data.accessPower1(scenario, i).cost()[t] for t in T]
    #         for i in I1]  # Cost_it[i][t]
    #     RefCost_ik = [
    #         [float(data.accessCampaign(i, k).refuelingcost()) 
    #             for k in range(len(data.accessPower2(i).Campaigns()))
    #         ]
    #         for i in I2
    #     ]
    #     Pmax_1 = [
    #         [data.accessPower1(0, i).pmax()[t] for t in T]
    #         for i in I1]  # Type 1 units: Pmax_1[i][t]
    #     Pmax_2 = [
    #         [data.accessPower2(i).pmax()[t] for t in T]
    #         for i in I2]  # Type 2 units: Pmax_2[i][t]
    #     Rmax = [
    #         [
    #             data.accessCampaign(i, k).maxrefuel()
    #             for k in range(len(K_i[i]))
    #         ]
    #         for i in I2
    #     ]  
    #     Smax = [
    #         [
    #             data.accessCampaign(i, k).maxstock()
    #             for k in range(len(K_i[i]))
    #         ]
    #         for i in I2
    #     ]
    #     Sth_min = [data.accessPower2(i).minstock() for i in I2]
    #     X_i = [data.accessPower2(i).initialstock() for i in I2]  
    #     D_t = data.timestepduration()
    #     DA_ik = [
    #         [
    #             data.accessCampaign(i, k).durationoutage()
    #             for k in range(len(K_i[i]))
    #         ]
    #         for i in I2
    #     ]   

    #     # ======= VARIABLES =======
    """
    #     # y_it
    #     y_it = model.addVariables(I2, T, 
    #                             type=hp.HighsVarType.kInteger, 
    #                             lb=0, ub=1, 
    #                             name_prefix=f"y_{{i}}_{{t}}")
    """
    #     # p_it    
    #     p1_it = model.addVariables(I1, T, 
    #                             type=hp.HighsVarType.kContinuous, 
    #                             lb=0,
    #                             name_prefix=f"p_{{i}}_{{t}}")  
    #     p2_it = model.addVariables(I2, T, 
    #                             type=hp.HighsVarType.kContinuous, 
    #                             lb=0,
    #                             name_prefix=f"p_{{i}}_{{t}}")  
        
    #     # r_it
    #     r_it = model.addVariables(I2, T,
    #                         type=hp.HighsVarType.kContinuous,
    #                         lb=0,
    #                         name_prefix="r_{i}_{t}")

    #     # s_it
    #     s_it = model.addVariables(I2, T,
    #                             type=hp.HighsVarType.kContinuous,
    #                             lb=0,
    #                             name_prefix="s_{i}_{t}")                          
        
    #     max_campaigns = max((len(K_i[i]) for i in I2), default=0)
            
    #     index_set = [
    #     (i, k, t)
    #     for i in I2
    #     for k in range(len(K_i[i]))
    #     for t in K_i[i][k]
    #     ]
    """
    #     x_ikt = model.addVariables(
    #         index_set,
    #         type=hp.HighsVarType.kInteger,
    #         lb=0,
    #         ub=1,
    #         name_prefix="x_{i}_{k}_{t}"
    #     )
    """
    #     # ======= OBJECTIVE =======
    #     model.setObjective(
    #         # production cost
    #         sum(Cost_it[i][t] * p1_it[i, t] * D_t[t] 
    #             for i in I1 for t in T
    #         )
    #         +
    #         # refueling cost (FIXED)
    #         sum(
    #             RefCost_ik[i][k_idx] *
    #             sum(r_it[i, t] for t in K_i[i][k_idx])
    #             for i in I2
    #             for k_idx in range(len(K_i[i]))
    #         ),
    #         sense=hp.ObjSense.kMinimize
    #     )        


    #     # ======= CONSTRAINTS =======
    #     for t in T:
    #         # (2) 
    #         model.addConstr(
    #             sum(p2_it[i, t] for i in I2)
    #                             >= Dem_t[t] - sum(p1_it[i, t] for i in I1),
    #             name=f"Demand_constraint_t{t}"
    #         )
    #         # (3)
    #         for i in I1:
    #             model.addConstr(
    #                 p1_it[i, t] 
    #                         <= Pmax_1[i][t],
    #                 name=f"Pmax1_constraint_i{i}_t{t}"
    #             )
    #         # (4)
    #         for i in I2:
    #             model.addConstr(
    #                 p2_it[i, t] 
    #                         <= Pmax_2[i][t] * (1 - y_it[i, t]),
    #                 name=f"Pmax2_constraint_i{i}_t{t}"
    #             )

    #     # stock 
    #     for i in I2:
    #         for t in T:
    #             if t == 0:
    #                 # (5)
    #                 model.addConstr(
    #                     s_it[i,t] == X_i[i] - p2_it[i,t]*D_t[t],
    #                     name=f"Stock_init_i{i}_t{t}"
    #                 )
    #             else:
    #                 # (6)
    #                 model.addConstr(
    #                     s_it[i,t] == s_it[i,t-1] - p2_it[i,t]*D_t[t] + r_it[i,t],
    #                     name=f"Stock_i{i}_t{t}"
    #                 )

    #             # (7)
    #             model.addConstr(
    #                 s_it[i,t] <= Smax[i][0],
    #                 name=f"Stock_max_i{i}_t{t}"
    #             )
    #             # (8)
    #             model.addConstr(
    #                 s_it[i,t] >= Sth_min[i]*0.1,
    #                 name=f"Stock_min_i{i}_t{t}"
    #             )

    #             # (9)
    #             for k_idx, k in enumerate(K_i[i]):
    #                 if t in k:
    #                     model.addConstr(
    #                         r_it[i,t] <= Rmax[i][k_idx] * x_ikt[i,k_idx,t],
    #                         name=f"Refuel_limit_i{i}_t{t}"
    #                     )
    #             if t not in K_i_simple[i] :
    #                 model.addConstr( r_it[i,t] == 0, name=f"Refuel_limit_i2{i}_t{t}")
        
    #     # (11)
    #     # for i in I2:
    #     #     for k_idx, k in enumerate(K_i[i]):
    #     #         for t in k:
    #     #             for j in range(t, t+DA_ik[i][k_idx]-1):
    #     #                 model.addConstr(
    #     #                     y_it[i][j] >= x_ikt[i][k][t],
    #     #                     name=f""
    #     #                 )

    #         # (12)
    #         model.addConstr(
    #             sum(y_it[i,t] for t in T) 
    #             == 
    #             sum (DA_ik[i][k_idx] * x_ikt[i,k_idx, t] 
    #                 for k_idx, k in enumerate(K_i[i]) 
    #                 for t in k),
    #             name=f"Link_y_x_i{i}"
    #         )
            
    #         for k_idx, k in enumerate(K_i[i]):
    #             # (10) 
    #             model.addConstr(
    #                 sum(x_ikt[i,k_idx, t] for t in k) <= 1,
    #                 name=f"One_refuel_per_campaign_i{i}_k{k_idx}"
    #             )
    #             for t in k:
    #                 # (13)
    #                 if t + DA_ik[i][k_idx] <= len(T):
    #                     model.addConstr(
    #                         sum(y_it[i, _t] for _t in range(t, t + DA_ik[i][k_idx]))
    #                         >= 
    #                         DA_ik[i][k_idx] * x_ikt[i, k_idx, t ],
    #                         name=f"Link_y_xx_i{i}_t{t}_k{k_idx}"
    #                     )
    #                 else:
    #                     model.addConstr(x_ikt[i, k_idx, t] == 0, name=f"Forbid_x_{i}_{k_idx}_{t}")

    #     # ===== EXTRACT SOLUTION =====
    #     start_time = time.time()
    #     #status = model.optimize()
    #     model.run()
    #     end_time = time.time()
    #     runtime = end_time - start_time

    #     print("\n----------------------------------")
    #     info = model.getInfo()
    #     model_status = model.getModelStatus()
    #     print('Status de la résolution par le solveur = ', model.modelStatusToString(model_status))
    #     print("Valeur de la fonction objectif = ", model.getObjectiveValue())
    #     print("Meilleure borne inférieure sur la valeur de la fonction objectif: ", info.mip_dual_bound)
    #     print("Gap: ", info.mip_gap)
    #     print("# de noeuds explorés: ", info.mip_node_count)
    #     print("Temps de résolution (en secondes) = ", runtime)
    #     print("----------------------------------")

    #     # On vérifie si une solution primale exploitable existe (optimale ou faisable)
    #     model_status = model.getModelStatus()
    #     primal_status = model.getInfo().primal_solution_status
    #     if (
    #         model_status == hp.HighsModelStatus.kOptimal
    #         or primal_status == hp.SolutionStatus.kSolutionStatusFeasible
    #     ):
    #         obj_value = model.getObjectiveValue()
    #         # for i in I2:
    #         #     for k in K_i[i]:
    #         #         print(f"i={i}, k={k}, refuel cost={RefCost_ik[i][k]}")

            
    #         p1_solution = {(i,t): model.variableValue(p1_it[i,t]) for i in I1 for t in T}
    #         p2_solution = {(i,t): model.variableValue(p2_it[i,t]) for i in I2 for t in T}
    #         y_solution = {(i,t): model.variableValue(y_it[i,t]) for i in I2 for t in T if model.variableValue(y_it[i,t]) > 0.1}
    #         r_solution = {(i,t): model.variableValue(r_it[i,t]) for i in I2 for t in T if model.variableValue(r_it[i,t]) > 0.1}
    #         s_solution = {(i,t): model.variableValue(s_it[i,t]) for i in I2 for t in T}
    #         x_solution = {
    #             (i, k_idx, t): model.variableValue(x_ikt[i,k_idx, t])
    #             for i in I2
    #             for k_idx, k in enumerate(K_i[i])
    #             for t in k
    #             if model.variableValue(x_ikt[i,k_idx, t]) > 0.1
    #         }

    #         sol = [p1_solution, p2_solution, y_solution, r_solution, r_solution, x_solution]

    #     else:
    #         obj_value = -1
    #         sol = [0,0,0,0,0,0]

        # return Solution((model.modelStatusToString(model_status) + " " + HEURISTIC_2), 
        #                 obj_value, 
        #                 model.getInfo().mip_dual_bound, runtime, sol)

