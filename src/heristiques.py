import time
import highspy as hp
import numpy as np
import joblib

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
    def __init__(self):
        self.I1 = None
        self.I2 = None
        self.T = None
        self.W = None
        self.campaign_ids_by_unit = None
        self.horizon_last_t = None
        self.K_i = None
        self.K_i_simple = None
        self.Dem_t = None
        self.Cost_it = None
        self.RefCost_ik = None
        self.Pmax_1 = None
        self.Pmax_2 = None
        self.Rmax = None
        self.Smax_ik = None
        self.Sth_min = None
        self.X_i = None
        self.D_t = None
        self.DA_ik = None

    def set_data_attrs(self, data: Readingfile, scenario: int):
        self.I1 = range(data.nbpower1())
        self.I2 = range(data.nbpower2())
        self.T = range(data.timestep()) 
        self.W = range(data.weeks()) 
        self.campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in self.I2]
        self.horizon_last_t = data.timestep() - 1
        self.K_i = []
        for i in self.I2:
            campaigns_i = []
        
            for k in self.campaign_ids_by_unit[i]:
                start = max(0, data.accessCampaign(i, k).earlieststop())
                end   = min(self.horizon_last_t, data.accessCampaign(i, k).lateststop())
            
                k_range = list(range(start, end + 1))
            
                if k_range != [0]:   
                    campaigns_i.append(k_range)
        
            self.K_i.append(campaigns_i)
        self.K_i_simple = {}
        for i in self.I2:
            self.K_i_simple[i] = [t for campagne in self.K_i[i] for t in campagne]
        self.Dem_t = data.accessScenario(scenario).demands()
        self.Cost_it = [ [data.accessPower1(scenario, i).cost()[t] for t in self.T] for i in self.I1]  # Cost_it[i][t]
        self.RefCost_ik = [
            [float(data.accessCampaign(i, k).refuelingcost()) 
                for k in range(len(data.accessPower2(i).Campaigns()))
            ]
            for i in self.I2
        ]
        self.Pmax_1 = [
            [data.accessPower1(scenario, i).pmax()[t] for t in self.T]
            for i in self.I1]  # Type 1 units: Pmax_1[i][t] 
        self.Pmax_2 = [
            [data.accessPower2(i).pmax()[t] for t in self.T]
            for i in self.I2]  # Type 2 units: Pmax_2[i][t]        
        self.Rmax = [
            [
                data.accessCampaign(i, k).maxrefuel()
                for k in range(len(self.K_i[i]))
            ]
            for i in self.I2
        ]  
        self.Smax_ik = [
            [
                data.accessCampaign(i, k).maxstock()
                for k in self.campaign_ids_by_unit[i]
            ]
            for i in self.I2
        ]
        self.Sth_min = [data.accessPower2(i).minstock() for i in self.I2]
        self.X_i = [data.accessPower2(i).initialstock() for i in self.I2]  
        self.D_t = data.timestepduration()
        self.DA_ik = [
            [
                data.accessCampaign(i, k).durationoutage()
                for k in range(len(self.K_i[i]))
            ]
            for i in self.I2
        ]   

    def solve(self, data: Readingfile, scenario: int) -> Solution:
        raise NotImplementedError

# # -----------------------------
# #  Heuristic 1
# # -----------------------------
# class MaintenanceHeuristicV1(AbstractMaintenanceHeuristic): 
#     def computePriorityScores(self, data: Readingfile) -> list[tuple[int, float]]:
#         w_i_tab = []
#         I2 = range(data.nbpower2())
#         Xi1 = [data.accessPower2(i).initialstock() for i in I2]
#         Sth_min = [data.accessPower2(i).minstock() for i in I2]
#         campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
#         Smax_ik = [
#             [
#                 data.accessCampaign(i, k).maxstock()
#                 for k in campaign_ids_by_unit[i]
#             ]
#             for i in I2
#         ]
#         T = range(data.timestep()) 
#         Pmax_2 = [
#             [data.accessPower2(i).pmax()[t] for t in T]
#             for i in I2
#         ]  # Type 2 units: Pmax_2[i][t]
#         tot_Pmax_ik = [
#             sum(Pmax_2[i][t] for t in T) for i in I2
#         ]
#         horizon_last_t = data.timestep() - 1
#         K_i = []
#         for i in I2:
#             campaigns_i = []
        
#             for k in campaign_ids_by_unit[i]:
#                 start = max(0, data.accessCampaign(i, k).earlieststop())
#                 end   = min(horizon_last_t, data.accessCampaign(i, k).lateststop())
            
#                 k_range = list(range(start, end + 1))
            
#                 if k_range != [0]:   
#                     campaigns_i.append(k_range)
#             K_i.append(campaigns_i)

#         K_i_simple = {}
#         for i in I2:
#             K_i_simple[i] = [t for campagne in K_i[i] for t in campagne]
            

#         for i in I2:
#             if all(v == Smax_ik[i][0] for v in Smax_ik[i]):
#                 smax_i = Smax_ik[i][0]
#             else:
#                 print(f"Warning: Smax_ik values are not the same for all campaigns of unit {i}.")
                            
#             Wi = (Xi1[i] - Sth_min[i]) / (smax_i - Sth_min[i]) # stock (Xi1 - Sth_min_i) / (Smax_ik - Sth_min_i)
#             Wi += sum(Pmax_2[i][t] for t in T) / tot_Pmax_ik[i] # puissance
#             Wi += 1 - (len(K_i_simple[i])/(data.timestep())) # fenetres de maintenance

#             w_i_tab.append((i, Wi))

#         return w_i_tab

#     def sortPlantsByPriority(self, priorityScores: list[tuple[int, float]]) -> list[tuple[int, float]]:
#         return sorted(priorityScores, key=lambda x: x[1], reverse=True) # tri decroissant

#     def findFeasibleStartTime(
#         self,
#         data: Readingfile,
#         i: int,
#         demand: list[float],
#         remaining_capacity: list[float],
#     ) -> tuple[int, int] | None:
#         plant = data.accessPower2(i)
#         T = data.timestep()

#         # !(initial stock >= min stock)
#         if plant.initialstock() < plant.minstock():
#             return None

#         for k_index, campaign in enumerate(plant.Campaigns()):
#             duration = campaign.durationoutage()
#             start_min = max(0, campaign.earlieststop())
#             start_max = min(campaign.lateststop(), T - duration)

#             if start_min > start_max:
#                 continue

#             for t_start in range(start_min, start_max + 1):
#                 feasible = True

#                 for t in range(t_start, t_start + duration):
#                     # cdt 1 (demande) et 2 (stock)
#                     if remaining_capacity[t] - plant.pmax()[t] < demand[t]:
#                         feasible = False
#                         break

#                 if feasible:
#                     return k_index, t_start

#         return None

#     def scheduleMaintenance(self, data: Readingfile) -> tuple[list[list[int]], list[list[tuple[int, int]]]] | None:
#         T = data.timestep()
#         I2 = data.nbpower2()
#         y_it = [[0 for _ in range(T)] for _ in range(I2)]
#         x_itk = [[] for _ in range(I2)]

#         # etape 1
#         scores = self.computePriorityScores(data)
#         ordered_plants = self.sortPlantsByPriority(scores)

#         # etape 2
#         scenario = data.accessScenario(0)
#         demand = scenario.demands()[:]

#         # generation capacity per timestep before scheduling outages
#         remaining_capacity = [0.0 for _ in range(T)]
#         for t in range(T):
#             total_pmax_type1 = sum(
#                 data.accessPower1(0, j).pmax()[t] for j in range(data.nbpower1())
#             )
#             total_pmax_type2 = sum(
#                 data.accessPower2(j).pmax()[t] for j in range(data.nbpower2())
#             )
#             remaining_capacity[t] = total_pmax_type1 + total_pmax_type2

#         # etape 3
#         for (i, _) in ordered_plants:
#             result = self.findFeasibleStartTime(data, i, demand, remaining_capacity)

#             if result is None:
#                 return None

#             k_index, t_start = result
#             plant = data.accessPower2(i)
#             duration = plant.Campaigns()[k_index].durationoutage()
#             x_itk[i].append((k_index, t_start)) # stock le choix

#             for t in range(t_start, t_start + duration):
#                 y_it[i][t] = 1
#                 remaining_capacity[t] -= plant.pmax()[t]

#         return y_it, x_itk

#     def computeProductionPlan(
#         self,
#         data: Readingfile,
#         y_it: list[list[int]],
#         x_itk: list[list[tuple[int, int]]],
#     ) -> tuple[
#         dict[tuple[int, int], float],
#         dict[tuple[int, int], float],
#         dict[tuple[int, int], float],
#         dict[tuple[int, int], float],
#     ]:
#         T = data.timestep()
#         # p1_sol = {
#         #     (i, t): float(data.accessPower1(0, i).pmax()[t])
#         #     for i in range(data.nbpower1())
#         #     for t in range(T)
#         # }
#         p1_sol: dict[tuple[int, int], float] = {}
#         p2_sol: dict[tuple[int, int], float] = {}
#         r_sol: dict[tuple[int, int], float] = {}
#         s_sol: dict[tuple[int, int], float] = {}

#         scheduled_campaign_start = {
#             i: {t_start: k_index for k_index, t_start in x_itk[i]}
#             for i in range(data.nbpower2())
#         }
#         productiontot = [0 for t in range(T)]
#         for i in range(data.nbpower2()):
#             plant = data.accessPower2(i)
#             stock = float(plant.initialstock())

#             for t in range(T):
#                 if t in scheduled_campaign_start[i]:
#                     campaign = plant.Campaigns()[scheduled_campaign_start[i][t]]
#                     target_stock = float(campaign.maxstock())
#                     refuel = max(0.0, campaign.maxrefuel()) #target_stock - stock  Modif pour produire que ce qu'on peut
#                     if refuel > 0:
#                         r_sol[(i, t)] = refuel
#                     stock += refuel

#                 production = 0.0 if y_it[i][t] == 1 else min(float(plant.pmax()[t]), data.accessScenario(0).demands()[t]- productiontot[t]) # Modif pour produire que si on en a besoin sinon on produit max possible
#                 if stock - plant.minstock()*0.1 - production* float(data.timestepduration()[t]) < 0 :
#                     production = (stock - plant.minstock()*0.1)/float(data.timestepduration()[t])
#                 p2_sol[(i, t)] = production
#                 stock -= production * float(data.timestepduration()[t])
#                 s_sol[(i, t)] = stock
#                 productiontot[t] += production

#         for i in range(data.nbpower1()):
#             plant = data.accessPower1(0,i)
#             for t in range(T):
#                 reste = data.accessScenario(0).demands()[t]- productiontot[t]
#                 sep = reste / data.nbpower1()
#                 p1_sol[(i, t)] = sep

#         return p1_sol, p2_sol, r_sol, s_sol

#     def solve(self, data: Readingfile, scenario: int) -> Solution:
#         start_time = time.time()
#         result = self.scheduleMaintenance(data)

#         if result is None:
#             return None

#         y_it, x_itk = result
#         p1_sol, p2_sol, r_it, s_it = self.computeProductionPlan(data, y_it, x_itk)

#         y_sol = {
#             (i, t): 1
#             for i in range(data.nbpower2())
#             for t in range(data.timestep())
#             if y_it[i][t] == 1
#         }
#         x_sol = {
#             (i, k_index, t_start): 1
#             for i, campaigns in enumerate(x_itk)
#             for k_index, t_start in campaigns
#         }

#         sol = [p1_sol, p2_sol, y_sol, r_it, s_it, x_sol]

#         runtime = time.time() - start_time

#         # calcul de la fct obj
#         I1 = range(data.nbpower1())   
#         I2 = range(data.nbpower2())
#         T = range(data.timestep())
#         campaign_ids_by_unit = [range(len(data.accessPower2(i).Campaigns())) for i in I2]
#         horizon_last_t = data.timestep() - 1
#         K_i = []
#         for i in I2:
#             campaigns_i = []
        
#             for k in campaign_ids_by_unit[i]:
#                 start = max(0, data.accessCampaign(i, k).earlieststop())
#                 end   = min(horizon_last_t, data.accessCampaign(i, k).lateststop())
            
#                 k_range = list(range(start, end + 1))
            
#                 if k_range != [0]:   
#                     campaigns_i.append(k_range)
        
#             K_i.append(campaigns_i)
#         K_i_simple = {}
#         for i in I2:
#             K_i_simple[i] = [t for campagne in K_i[i] for t in campagne]
#         RefCost_ik = [
#                 [float(data.accessCampaign(i, k).refuelingcost()) 
#                     for k in range(len(data.accessPower2(i).Campaigns()))
#                 ]
#             for i in I2
#             ]
#         Cost_it = [
#         [data.accessPower1(scenario, i).cost()[t] for t in T]
#         for i in I1]  # Cost_it[i][t]
#         D_t = data.timestepduration()

#         obj_value = (
#             sum(
#                 Cost_it[i][t] * p1_sol.get((i, t), 0.0) * D_t[t]
#                 for i in I1
#                 for t in T
#             )
#             +
#             sum(
#                 RefCost_ik[i][k_idx] *
#                 sum(r_it.get((i, t), 0.0) for t in K_i[i][k_idx])
#                 for i in I2
#                 for k_idx in range(len(K_i[i]))
#             )
#         )

#         return Solution("HEURISTIC_1", 
#                     obj_value, 
#                     float('inf'), runtime, sol)
    
# -----------------------------
#  Heuristic 2 basic
# -----------------------------
class MaintenanceHeuristicV2_basic(AbstractMaintenanceHeuristic):
    def computePriorityScores(self, data: Readingfile) -> list[tuple[int, float]]:
        w_i_tab = []
        tot_Pmax_ik = [
            sum(self.Pmax_2[i][t] for t in self.T) for i in self.I2
        ]

        for i in self.I2:
            if all(v == self.Smax_ik[i][0] for v in self.Smax_ik[i]):
                smax_i = self.Smax_ik[i][0]
            else:
                print(f"Warning: Smax_ik values are not the same for all campaigns of unit {i}.")
                            
            Wi = (self.X_i[i] - self.Sth_min[i]) / (smax_i - self.Sth_min[i]) # stock (Xi1 - Sth_min_i) / (Smax_ik - Sth_min_i)
            Wi += sum(self.Pmax_2[i][t] for t in self.T) / tot_Pmax_ik[i] # puissance
            Wi += 1 - (len(self.K_i_simple[i])/(data.timestep())) # fenetres de maintenance

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
                print(f"ÉCHEC : Pas de créneau trouvé pour la centrale {i}. Sortie de fonction.")
                continue

            k_index, t_start = result
            plant = data.accessPower2(i)
            duration = plant.Campaigns()[k_index].durationoutage()
            x_itk[i].append((k_index, t_start))

            for t in range(t_start, t_start + duration):
                y_it[i][t] = 1
                remaining_capacity[t] -= plant.pmax()[t]
            print(f"Succès pour centrale {i}")

        return y_it, x_itk

    def computeProductionPlanLP(self, data: Readingfile, scenario: int, y_it: list[list[int]], x_itk: list[list[tuple[int, int]]], start_time : float) :
        # ======= MODEL =======
        model = hp.Highs()
        model.setOptionValue("output_flag", False)

        selected_start = {
            i: {t_start: k_idx for k_idx, t_start in x_itk[i]}
            for i in self.I2
        }
        smax_i = {
            i: (self.Smax_ik[i][0] if len(self.Smax_ik[i]) > 0 else float("inf"))
            for i in self.I2
        }
    
        # ======= VARIABLES =======
        # p_it    
        p1_it = model.addVariables(self.I1, self.T, 
                                type=hp.HighsVarType.kContinuous, 
                                lb=0,
                                name_prefix=f"p_{{i}}_{{t}}")  
        p2_it = model.addVariables(self.I2, self.T, 
                                type=hp.HighsVarType.kContinuous, 
                                lb=0,
                                name_prefix=f"p_{{i}}_{{t}}")  
    
        # r_it
        r_it = model.addVariables(self.I2, self.T,
                            type=hp.HighsVarType.kContinuous,
                            lb=0,
                            name_prefix="r_{i}_{t}")

        # s_it
        s_it = model.addVariables(self.I2, self.T,
                                type=hp.HighsVarType.kContinuous,
                                lb=0,
                                name_prefix="s_{i}_{t}")                          
        
        # ======= OBJECTIVE =======
        model.setObjective(
            # production cost
            sum(self.Cost_it[i][t] * p1_it[i, t] * self.D_t[t] 
                for i in self.I1 for t in self.T
            )
            +
            # refueling cost (FIXED)
            sum(
                self.RefCost_ik[i][k_idx] *
                r_it[i, t_start]
                for i in self.I2
                for k_idx, t_start in x_itk[i]
            ),
            sense=hp.ObjSense.kMinimize
        ) 

        # ======= CONSTRAINTS =======
        for t in self.T:
            # (2) 
            model.addConstr(
                sum(p2_it[i, t] for i in self.I2)
                                >= self.Dem_t[t] - sum(p1_it[i, t] for i in self.I1),
                name=f"Demand_constraint_t{t}"
            )
            # (3)
            for i in self.I1:
                model.addConstr(
                    p1_it[i, t] 
                            <= self.Pmax_1[i][t],
                    name=f"Pmax1_constraint_i{i}_t{t}"
                )
            # (4)
            for i in self.I2:
                model.addConstr(
                    p2_it[i, t] 
                            <= self.Pmax_2[i][t] * (1 - y_it[i][t]),
                    name=f"Pmax2_constraint_i{i}_t{t}"
                )

        # stock 
        for i in self.I2:
            for t in self.T:
                if t == 0:
                    # (5)
                    model.addConstr(
                        s_it[i,t] == self.X_i[i] - p2_it[i,t]*self.D_t[t],
                        name=f"Stock_init_i{i}_t{t}"
                    )
                else:
                    # (6)
                    model.addConstr(
                        s_it[i,t] == s_it[i,t-1] - p2_it[i,t]*self.D_t[t] + r_it[i,t],
                        name=f"Stock_i{i}_t{t}"
                    )

                # (7)
                model.addConstr(
                    s_it[i,t] <= smax_i[i],
                    name=f"Stock_max_i{i}_t{t}"
                )
                # (8)
                model.addConstr(
                    s_it[i,t] >= self.Sth_min[i]*0.1,
                    name=f"Stock_min_i{i}_t{t}"
                )

                if t in selected_start[i]:
                    k_idx = selected_start[i][t]
                    rmax_value = self.Rmax[i][k_idx] if k_idx < len(self.Rmax[i]) else data.accessCampaign(i, k_idx).maxrefuel()
                    model.addConstr(
                        r_it[i, t] <= rmax_value,
                        name=f"Refuel_i{i}_t{t}",
                    )
                else:
                    model.addConstr(r_it[i, t] == 0, name=f"No_refuel_i{i}_t{t}")
        
        # ===== EXTRACT SOLUTION =====
        model.run()
        runtime = time.time() - start_time

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
            
            p1_solution = {(i,t): model.variableValue(p1_it[i,t]) for i in self.I1 for t in self.T}
            p2_solution = {(i,t): model.variableValue(p2_it[i,t]) for i in self.I2 for t in self.T}
            r_solution = {(i,t): model.variableValue(r_it[i,t]) for i in self.I2 for t in self.T if model.variableValue(r_it[i,t]) > 0.1}
            s_solution = {(i,t): model.variableValue(s_it[i,t]) for i in self.I2 for t in self.T}

        else:
            obj_value = -1
            p1_solution = {(i,t): 0.0 for i in self.I1 for t in self.T}
            p2_solution = {(i,t): 0.0 for i in self.I2 for t in self.T}
            r_solution = {}
            s_solution = {(i,t): float(self.X_i[i]) for i in self.I2 for t in self.T}

        return obj_value, obj_value, runtime, model.modelStatusToString(model_status), p1_solution, p2_solution, r_solution, s_solution

    
    def solve(self, data: Readingfile, scenario: int) -> Solution:
        self.set_data_attrs(data, scenario)
        start_time = time.time()
        result = self.scheduleMaintenance(data)

        if result is None:
            return None

        y_it, x_itk = result
        production_plan = self.computeProductionPlanLP(data, scenario, y_it, x_itk, start_time)
        if production_plan is None:
            return None

        obj_value, dual_bound, lp_runtime, status, p1_sol, p2_sol, r_sol, s_sol = production_plan

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

        sol = [p1_sol, p2_sol, y_sol, r_sol, s_sol, x_sol]
        total_runtime = time.time() - start_time

        return Solution(f"HEURISTIC_2_{status}", obj_value, dual_bound, total_runtime + lp_runtime, sol)

# -----------------------------
#  Heuristic 2_2 
# -----------------------------
class MaintenanceHeuristicV2MultiCampaign(MaintenanceHeuristicV2_basic):
    def findFeasibleStartTime(
        self,
        data: Readingfile,
        i: int,
        demand: list[float],
        remaining_capacity: list[float], x
    ) -> tuple[int, int] | None:
        plant = data.accessPower2(i)
        T = data.timestep()

        if plant.initialstock() < plant.minstock():
            return None

        for k_index, campaign in enumerate(plant.Campaigns()):
            if k_index in x[i] :
                continue
            duration = campaign.durationoutage()
            start_min = max(0, campaign.earlieststop())
            start_max = min(campaign.lateststop(), T - duration)

            if start_min > start_max:
                continue

            for t_start in range(start_min, start_max + 1):
                feasible = True
                for t in range(t_start, t_start + duration):
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
        x = [[] for _ in range(I2)]

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
        while True :
            somme = 0
            for (i, _) in ordered_plants:
                result = self.findFeasibleStartTime(data, i, demand, remaining_capacity, x)

                if result is None:
                    print(f"ÉCHEC : Pas de créneau trouvé pour la centrale {i}. Sortie de fonction.")
                    somme += 1
                    continue

                k_index, t_start = result
                
                plant = data.accessPower2(i)
                duration = plant.Campaigns()[k_index].durationoutage()
                x_itk[i].append((k_index, t_start))
                x[i].append(k_index)

                for t in range(t_start, t_start + duration):
                    y_it[i][t] = 1
                    remaining_capacity[t] -= plant.pmax()[t]
                print(f"Succès pour centrale {i}")
            print(somme)
            if somme == I2 :
                break

        return y_it, x_itk
    
    def solve(self, data: Readingfile, scenario: int) -> Solution:
        self.set_data_attrs(data, scenario)
        start_time = time.time()
        result = self.scheduleMaintenance(data)

        if result is None:
            return None

        y_it, x_itk = result
        production_plan = self.computeProductionPlanLP(data, scenario, y_it, x_itk, start_time)
        if production_plan is None:
            return None

        obj_value, dual_bound, lp_runtime, status, p1_sol, p2_sol, r_sol, s_sol = production_plan

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

        sol = [p1_sol, p2_sol, y_sol, r_sol, s_sol, x_sol]
        total_runtime = time.time() - start_time

        return Solution(f"HEURISTIC_2_MultiCampaign_{status}", obj_value, dual_bound, total_runtime + lp_runtime, sol)

# -----------------------------
#  Heuristic 2_1
# -----------------------------
class MaintenanceHeuristicV2_RF(MaintenanceHeuristicV2_basic):
    """
    heuristic improved version using Random Forest models
    Pipeline:
    1) Predict priority order of type-2 plants (RandomForestRegressor)
    2) Predict promising maintenance start dates (RandomForestClassifier)
    3) ... same as V2_basic

    joblib Memory is used so models are trained once and reused aiming to reduce runtile
    """

    def __init__(self):
        from joblib import Memory
        self.memory = Memory(location=".rf_cache", verbose=0)

    def buildPriorityFeatures(self, data: Readingfile):
        """
        building one row of features per plant
        features:
        - stock ratio            -> urgency of refuel
        - avg pmax              -> production importance
        - nb campaigns          -> planning complexity
        - total window size     -> flexibility
        """
        X = []

        for i in self.I2:
            plant = data.accessPower2(i)
            Xi1 = plant.initialstock()
            Smin = plant.minstock()
            campaigns = plant.Campaigns()

            smax = campaigns[0].maxstock() if len(campaigns) > 0 else Xi1

            stock_ratio = (Xi1 - Smin) / max(1.0, (smax - Smin))

            avg_pmax = np.mean(plant.pmax())

            nb_campaigns = len(campaigns)

            total_window = 0
            for c in campaigns:
                total_window += max(0, c.lateststop() - c.earlieststop() + 1)

            X.append([stock_ratio, avg_pmax, nb_campaigns, total_window])

        return np.array(X)

    def buildPriorityTargets(self, data: Readingfile):
        """
        since we dont have dataset to train on, we create our own dataset by using V2_basic
        priorityScore (formule) as pseudo-label
        """
        scores = self.computePriorityScores(data)
        y = np.array([score for (_, score) in scores])
        return y
    
    def trainPriorityModel(self, data: Readingfile):
        from sklearn.ensemble import RandomForestRegressor
        X = self.buildPriorityFeatures(data)
        y = self.buildPriorityTargets(data)

        # n_estimators=100: good bias/variance compromise
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,        # avoid overfitting
            random_state=42,
            n_jobs=-1           # use all CPU cores
        )
        model.fit(X, y)
        return model    

    def predictPriorityOrder(self, data: Readingfile):
        model = self.memory.cache(self.trainPriorityModel)(data)
        X = self.buildPriorityFeatures(data)
        preds = model.predict(X)
        ranking = [(i, preds[i]) for i in range(data.nbpower2())]
        ranking.sort(key=lambda x: x[1], reverse=True) # highest score first
        return ranking

    def buildStartDateDataset(self, data: Readingfile, i: int):
        """
        Label:
        1 if feasible according to capacity screening
        0 otherwise
        """
        plant = data.accessPower2(i)
        T = data.timestep()
        demand = data.accessScenario(0).demands()
        X = []
        y = []
        total_capacity = []

        for t in range(T):
            cap1 = sum(
                data.accessPower1(0, j).pmax()[t]
                for j in range(data.nbpower1())
            )
            cap2 = sum(
                data.accessPower2(j).pmax()[t]
                for j in range(data.nbpower2())
            )
            total_capacity.append(cap1 + cap2)

        for k_index, campaign in enumerate(plant.Campaigns()):
            duration = campaign.durationoutage()
            start_min = max(0, campaign.earlieststop())
            start_max = min(campaign.lateststop(), T - duration)

            for t_start in range(start_min, start_max + 1):

                # feature values
                local_demand = np.mean(demand[t_start:t_start + duration]    )

                slack = np.mean(total_capacity[t_start:t_start + duration]) - local_demand

                X.append([k_index, t_start, duration, local_demand, slack])

                # simple feasibility label
                feasible = 1
                for t in range(t_start, t_start + duration):
                    if total_capacity[t] - plant.pmax()[t] < demand[t]:
                        feasible = 0
                        break

                y.append(feasible)

        return np.array(X), np.array(y)

    def trainStartDateModel(self, data: Readingfile, i: int):
        from sklearn.ensemble import RandomForestClassifier
        X, y = self.buildStartDateDataset(data, i)

        if len(np.unique(y)) <= 1: # in case all labels same are 1 same model would be unstable
            return None

        model = RandomForestClassifier(
            n_estimators=80,   # enough trees, still fast
            max_depth=8,
            random_state=42,
            n_jobs=-1 
        )

        model.fit(X, y)
        return model
    
    def predictBestStartDates(self, data: Readingfile, i: int):
        model = self.memory.cache(self.trainStartDateModel)(data, i)
        X, _ = self.buildStartDateDataset(data, i)

        if model is None:  # fallback if only one class in labels
            ranked = list(range(len(X)))
            return ranked, X

        proba = model.predict_proba(X)[:, 1]
        ranked = list(range(len(X)))
        ranked.sort(key=lambda idx: proba[idx], reverse=True)
        return ranked, X    
    
    def scheduleMaintenance(self, data: Readingfile):
        T = data.timestep()
        I2 = data.nbpower2()

        y_it = [[0 for _ in range(T)] for _ in range(I2)]
        x_itk = [[] for _ in range(I2)]

        demand = data.accessScenario(0).demands()[:]

        remaining_capacity = [0.0 for _ in range(T)]
        for t in range(T):
            cap1 = sum(
                data.accessPower1(0, j).pmax()[t]
                for j in range(data.nbpower1())
            )
            cap2 = sum(
                data.accessPower2(j).pmax()[t]
                for j in range(data.nbpower2())
            )
            remaining_capacity[t] = cap1 + cap2

        # 1. RF ranking
        ordered_plants = self.predictPriorityOrder(data)

        # 2. schedule each plant
        for (i, _) in ordered_plants:

            ranked_rows, X = self.predictBestStartDates(data, i)

            plant = data.accessPower2(i)
            placed = False

            # test only top candidates first
            for row_id in ranked_rows[:10]:

                k_index = int(X[row_id][0])
                t_start = int(X[row_id][1])
                duration = int(X[row_id][2])

                feasible = True

                for t in range(t_start, t_start + duration):
                    if remaining_capacity[t] - plant.pmax()[t] < demand[t]:
                        feasible = False
                        break

                if feasible:
                    x_itk[i].append((k_index, t_start))

                    for t in range(t_start, t_start + duration):
                        y_it[i][t] = 1
                        remaining_capacity[t] -= plant.pmax()[t]

                    placed = True
                    break

            if not placed:
                print(f"RF failed to place plant {i}")

        return y_it, x_itk    

    def solve(self, data: Readingfile, scenario: int) -> Solution:
        self.set_data_attrs(data, scenario)
        start_time = time.time()

        # scheduling by RF
        y_it, x_itk = self.scheduleMaintenance(data)

        # inherited LP production plan
        production_plan = self.computeProductionPlanLP(
            data, scenario, y_it, x_itk, start_time
        )

        obj_value, dual_bound, lp_runtime, status, \
        p1_sol, p2_sol, r_sol, s_sol = production_plan

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

        total_runtime = time.time() - start_time

        return Solution(
            f"HEURISTIC_2_RF{status}",
            obj_value,
            dual_bound,
            total_runtime + lp_runtime,
            [p1_sol, p2_sol, y_sol, r_sol, s_sol, x_sol]
        )

# -----------------------------
#  Heuristic 3 (dichotomie)
# -----------------------------
class MaintenanceHeuristicV3_dichotomie(MaintenanceHeuristicV2_basic):
    def initial_ab(self, data):
        a = 0.0
        b = 0.0

        for i in self.I1:
            for t in self.T:
                b = max(b, self.Cost_it[i][t] * self.D_t[t])

        for i_idx, i in enumerate(self.I2):
            for k in range(len(self.RefCost_ik[i_idx])):
                b = max(b, self.RefCost_ik[i_idx][k])

        return a, b   
    
    #  Dichotomie 7.2.1 cours de remediation de Optim
    @staticmethod # this is added or else it will throw error since we call it without self in solve method
    def dichotomie(f, a, b, l, epsilon, max_iter):
        # TODO: remove the max_itere
        k = 0
        ak, bk = a, b
        sequence = [(ak, bk)]
        
        while (bk - ak) > l and k <= max_iter:
            mid = (ak + bk) / 2.0
            x1 = mid - epsilon
            x2 = mid + epsilon
            
            if f(x1) < f(x2):
                bk = x2
            else:
                ak = x1
                
            sequence.append((round(ak, 3), round(bk, 3)))
            k += 1
            
        return ((ak + bk)/2.0), sequence
    
    def dualLag_function(self, mu, data, scenario):
        total = 0.0

        for i in self.I1:
            for t in self.T:
                gain = self.Cost_it[i][t] * self.D_t[t] - mu

                if gain < 0:
                    p = data.accessPower1(scenario, i).pmax()[t]
                else:
                    p = 0.0

                total += gain * p

        for i in self.I2:
            pmax = data.accessPower2(i).pmax()
            for t in self.T:
                gain = -mu
                if gain < 0:
                    p = pmax[t]
                else:
                    p = 0.0

                total += gain * p

            for k in range(len(data.accessPower2(i).Campaigns())):
                camp = data.accessCampaign(i, k)
                ref_cost = float(camp.refuelingcost())
                incentive = mu * camp.durationoutage()

                if incentive > ref_cost:
                    r = camp.maxrefuel()
                else:
                    r = 0.0

                total += ref_cost * r

        for t in self.T:
            total += mu * self.Dem_t[t]

        return total
    
    def sousPB_typeI1_model(self, data, scenario, mu, start_time : float):
        # ======= MODEL =======
        model = hp.Highs()
        model.setOptionValue("output_flag", False)

        # ======= VARIABLES =======
        # p_it    
        p1_it = model.addVariables(self.I1, self.T, 
                                type=hp.HighsVarType.kContinuous, 
                                lb=0,
                                name_prefix=f"p_{{i}}_{{t}}")  
        
        # ======= OBJECTIVE =======
        model.setObjective(
            # production cost
            sum((self.Cost_it[i][t]*self.D_t[t] - mu) * p1_it[i, t] 
                for i in self.I1 for t in self.T
            ),
            sense=hp.ObjSense.kMinimize
        )        

        # ======= CONSTRAINTS =======
        for t in self.T:
            # (3)
            for i in self.I1:
                model.addConstr(
                    p1_it[i, t] 
                            <= self.Pmax_1[i][t],
                    name=f"Pmax1_constraint_i{i}_t{t}"
                )
        # ===== EXTRACT SOLUTION =====  
        model.run()
        runtime = time.time() - start_time

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
            
            p1_solution = {(i,t): model.variableValue(p1_it[i,t]) for i in self.I1 for t in self.T}

        else:
            obj_value = -1
            p1_solution = {(i,t): 0.0 for i in self.I1 for t in self.T}


        return obj_value, runtime, model.modelStatusToString(model_status), p1_solution  

    def sousPB_typeI2_model(self, data, scenario, mu, start_time : float):
        # ======= MODEL =======
        model = hp.Highs()
        model.setOptionValue("output_flag", False)

        # ======= VARIABLES =======
        # y_it
        y_it = model.addVariables(self.I2, self.T, 
                                type=hp.HighsVarType.kInteger, 
                                lb=0, ub=1, 
                                name_prefix=f"y_{{i}}_{{t}}")
        # p_it  
        p2_it = model.addVariables(self.I2, self.T, 
                                type=hp.HighsVarType.kContinuous, 
                                lb=0,
                                name_prefix=f"p_{{i}}_{{t}}")  
        
        # r_it
        r_it = model.addVariables(self.I2, self.T,
                            type=hp.HighsVarType.kContinuous,
                            lb=0,
                            name_prefix="r_{i}_{t}")

        # s_it
        s_it = model.addVariables(self.I2, self.T,
                                type=hp.HighsVarType.kContinuous,
                                lb=0,
                                name_prefix="s_{i}_{t}")                          
        
        max_campaigns = max((len(self.K_i[i]) for i in self.I2), default=0)
            
        index_set = [
        (i, k, t)
        for i in self.I2
        for k in range(len(self.K_i[i]))
        for t in self.K_i[i][k]
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
            # refueling cost (FIXED)
            sum(
                self.RefCost_ik[i][k_idx] *
                sum(r_it[i, t] for t in self.K_i[i][k_idx])
                for i in self.I2
                for k_idx in range(len(self.K_i[i]))
            ),
            sense=hp.ObjSense.kMinimize
        )         

        # ======= CONSTRAINTS =======
        for t in self.T:
            # (4)
            for i in self.I2:
                model.addConstr(
                    p2_it[i, t] 
                            <= self.Pmax_2[i][t] * (1 - y_it[i, t]),
                    name=f"Pmax2_constraint_i{i}_t{t}"
                )     

        # stock 
        for i in self.I2:
            for t in self.T:
                if t == 0:
                    # (5)
                    model.addConstr(
                        s_it[i,t] == self.X_i[i] - p2_it[i,t]*self.D_t[t],
                        name=f"Stock_init_i{i}_t{t}"
                    )
                else:
                    # (6)
                    model.addConstr(
                        s_it[i,t] == s_it[i,t-1] - p2_it[i,t]*self.D_t[t] + r_it[i,t],
                        name=f"Stock_i{i}_t{t}"
                    )

                # (7)
                model.addConstr(
                    s_it[i,t] <= self.Smax_ik[i][0],
                    name=f"Stock_max_i{i}_t{t}"
                )
                # (8)
                model.addConstr(
                    s_it[i,t] >= self.Sth_min[i]*0.1,
                    name=f"Stock_min_i{i}_t{t}"
                )

                # (9)
                for k_idx, k in enumerate(self.K_i[i]):
                    if t in k:
                        model.addConstr(
                            r_it[i,t] <= self.Rmax[i][k_idx] * x_ikt[i,k_idx,t],
                            name=f"Refuel_limit_i{i}_t{t}"
                        )
                if t not in self.K_i_simple[i] :
                    model.addConstr( r_it[i,t] == 0, name=f"Refuel_limit_i2{i}_t{t}")

        
            for k_idx, k in enumerate(self.K_i[i]):
                # (10) 
                model.addConstr(
                    sum(x_ikt[i,k_idx, t] for t in k) <= 1,
                    name=f"One_refuel_per_campaign_i{i}_k{k_idx}"
                )
                for t in k:
                    # (13) --> (12) in the report
                    if t + self.DA_ik[i][k_idx] <= len(self.T):
                        model.addConstr(
                            sum(y_it[i, _t] for _t in range(t, t + self.DA_ik[i][k_idx]))
                            == # in the avancement_TER it was == 
                            self.DA_ik[i][k_idx] * x_ikt[i, k_idx, t ],
                            name=f"Link_y_xx_i{i}_t{t}_k{k_idx}"
                        )
                    else:
                        model.addConstr(x_ikt[i, k_idx, t] == 0, name=f"Forbid_x_{i}_{k_idx}_{t}")

            # (12) --> (11) in the report 
            model.addConstr(
                sum(y_it[i,t] for t in self.T) 
                == 
                sum (self.DA_ik[i][k_idx] * x_ikt[i,k_idx, t] 
                    for k_idx, k in enumerate(self.K_i[i]) 
                    for t in k),
                name=f"Link_y_x_i{i}"
            )                       

        # ===== EXTRACT SOLUTION =====
        model.run()
        runtime = time.time() - start_time

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
            x_ikt_solution = [[] for _ in range(len(self.I2))]
            for i in self.I2 :
                for k_idx, k in enumerate(self.K_i[i]) :
                    for t in k :
                        if model.variableValue(x_ikt[i,k_idx, t]) > 0.1 :
                            x_ikt_solution[i].append((k_idx, t))
                   
            # y_it_solution = {(i,t): model.variableValue(y_it[i,t]) for i in self.I2 for t in self.T}
            y_it_solution = [[model.variableValue(y_it[i,t]) for t in self.T] for i in range(len(self.I2))]
            # y_it_solution = {(i,t): model.variableValue(y_it[i,t]) for i in self.I2 for t in self.T}
            p2_solution = {(i,t): model.variableValue(p2_it[i,t]) for i in self.I2 for t in self.T}
            r_solution = {(i,t): model.variableValue(r_it[i,t]) for i in self.I2 for t in self.T if model.variableValue(r_it[i,t]) > 0.1}
            s_solution = {(i,t): model.variableValue(s_it[i,t]) for i in self.I2 for t in self.T}

        else:
            obj_value = -1
            x_ikt_solution = {(i, k_idx, t): 0.0 for i in self.I2 for k_idx in range(len(self.K_i[i])) for t in self.K_i[i][k_idx]}
            y_it_solution = {(i,t): 0.0 for i in self.I2 for t in self.T}
            p2_solution = {(i,t): 0.0 for i in self.I2 for t in self.T}
            r_solution = {}
            s_solution = {(i,t): float(self.X_i[i]) for i in self.I2 for t in self.T}

        return obj_value, runtime, model.modelStatusToString(model_status), x_ikt_solution, y_it_solution, p2_solution, r_solution, s_solution


    def solve(self, data: Readingfile, scenario: int) -> Solution:
        try:
            from .checker import Checker
        except ImportError:
            from checker import Checker        

        self.set_data_attrs(data, scenario)

        start_time = time.time()
        a, b = self.initial_ab(data)
        f = lambda mu: self.dualLag_function(mu, data, scenario)

        mu_star, _ = self.dichotomie(f, a, b, l=1e-3, epsilon=1e-3, max_iter=10)

        dualLag_value = f(mu_star)

        obj_value_sousPB1, runtime_sousPB1, model_status_sousPB1, p1_solution_sousPB1 = self.sousPB_typeI1_model(data, scenario, mu_star, start_time=start_time)

        obj_value_sousPB2, runtime_sousPB2, model_status_sousPB2, x_ikt_solution_sousPB2, y_it_solution_sousPB2, p2_solution_sousPB2, r_solution_sousPB2, s_solution_sousPB2 = self.sousPB_typeI2_model(data, scenario, mu_star, start_time=runtime_sousPB1)

        sol_sousPB_list = [p1_solution_sousPB1, p2_solution_sousPB2, y_it_solution_sousPB2, r_solution_sousPB2, s_solution_sousPB2, x_ikt_solution_sousPB2] 
        sol_sousPB =Solution("HEURISTIC_3_DICHOTOMY_Realisable", obj_value_sousPB1+obj_value_sousPB2, 0, 0 , sol_sousPB_list)

        if Checker(data, sol_sousPB, scenario):
            return sol_sousPB  # dual_bound, total_runtime + lp_runtime, sol)
            
        else :
            # list to dict 
            
            # inherited LP production plan
            production_plan = self.computeProductionPlanLP(
                data, scenario, y_it_solution_sousPB2, x_ikt_solution_sousPB2, start_time
            )
            obj_value, dual_bound, lp_runtime, status, p1_sol, p2_sol, r_sol, s_sol = production_plan
            sol = [p1_sol, p2_sol, y_it_solution_sousPB2, r_sol, s_sol, x_ikt_solution_sousPB2]

            return Solution("HEURISTIC_3_DICHOTOMY_Realisable", obj_value, dual_bound, lp_runtime, sol)
          