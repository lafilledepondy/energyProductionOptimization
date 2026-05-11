import time
import highspy as hp
import numpy as np
# import joblib

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
            
            solution = model.getSolution().col_value

            p1_solution = {
                (i, t): solution[var.index]
                for (i, t), var in p1_it.items()
            }

            p2_solution = {
                (i, t): solution[var.index]
                for (i, t), var in p2_it.items()
            }

            r_solution = {
                (i, t): solution[var.index]
                for (i, t), var in r_it.items()
                if solution[var.index] > 0.1
            }

            s_solution = {
                (i, t): solution[var.index]
                for (i, t), var in s_it.items()
            }

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
#  Heuristic 2_3
# -----------------------------
class MaintenanceHeuristicV2MultiCampaign_2(MaintenanceHeuristicV2MultiCampaign):
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
        start_time2 = time.time()
        I2 = data.nbpower2()
        T = data.timestep()
        y_it = [[0]*T for _ in range(I2)]

        for i in range(I2):
            x_itk[i] = [(k, t) for (k, t) in x_itk[i] if (i, t) in r_sol]

        for i, campaigns in enumerate(x_itk):
            plant = data.accessPower2(i)
            campaigns_data = plant.Campaigns()  

            for k_index, t_start in campaigns:
                duration = campaigns_data[k_index].durationoutage()
                t_end = min(t_start + duration, T)
                for t in range(t_start, t_end):
                    y_it[i][t] = 1
        production_plan = self.computeProductionPlanLP(data, scenario, y_it, x_itk, start_time2)
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

        return Solution(f"HEURISTIC_2_MultiCampaign_2_{status}", obj_value, dual_bound, total_runtime + lp_runtime, sol)


# -----------------------------
#  Heuristic 2_4
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
# ======= INITIALISATION DES MODÈLES (UNE SEULE FOIS) =======
    def __init__(self, data, scenario):
        super().__init__()
        self.set_data_attrs(data, scenario)
        if self.I1 is None or self.T is None:
            raise ValueError("Les ensembles I1 ou T ne sont pas initialisés par la classe parente !")
        self.model1 = hp.Highs()
        self.model1.setOptionValue("output_flag", False)
        
        self.model2 = hp.Highs()
        self.model2.setOptionValue("output_flag", False)

        # ======= VARIABLES SOUS-PROBLÈME 1 =======
        self.p1_it = self.model1.addVariables(self.I1, self.T, 
                                type=hp.HighsVarType.kContinuous, lb=0)

        # ======= VARIABLES SOUS-PROBLÈME 2 =======
        self.y_it = self.model2.addVariables(self.I2, self.T, 
                                type=hp.HighsVarType.kInteger, lb=0, ub=1)
        self.p2_it = self.model2.addVariables(self.I2, self.T, 
                                type=hp.HighsVarType.kContinuous, lb=0)
        self.r_it = self.model2.addVariables(self.I2, self.T,
                                type=hp.HighsVarType.kContinuous, lb=0)
        self.s_it = self.model2.addVariables(self.I2, self.T,
                                type=hp.HighsVarType.kContinuous, lb=0)
        
        index_set_x = [(i, k, t) for i in self.I2 for k in range(len(self.K_i[i])) for t in self.K_i[i][k]]
        self.x_ikt = self.model2.addVariables(index_set_x, type=hp.HighsVarType.kInteger, lb=0, ub=1)

        # ======= CONTRAINTES STATIQUES (NE CHANGENT JAMAIS) =======
        self._build_static_constraints()

    def _build_static_constraints(self):
        # Contraintes SP1
        for i in self.I1:
            for t in self.T:
                self.model1.addConstr(self.p1_it[i, t] <= self.Pmax_1[i][t])
        
        # Contraintes SP2 (Stock, Maintenance, etc.)
        for i in self.I2:
            for t in self.T:
                # Puissance max avec maintenance
                self.model2.addConstr(self.p2_it[i, t] <= self.Pmax_2[i][t] * (1 - self.y_it[i, t]))
                
                # Équilibre de stock
                if t == 0:
                    self.model2.addConstr(self.s_it[i,t] == self.X_i[i] - self.p2_it[i,t]*self.D_t[t])
                else:
                    self.model2.addConstr(self.s_it[i,t] == self.s_it[i,t-1] - self.p2_it[i,t]*self.D_t[t] + self.r_it[i,t])
                
                # Bornes stock
                self.model2.addConstr(self.s_it[i,t] <= self.Smax_ik[i][0]) # Attention au [0] ici comme discuté
                self.model2.addConstr(self.s_it[i,t] >= self.Sth_min[i]*0.1)

                # Ravitaillement
                for k_idx, k in enumerate(self.K_i[i]):
                    if t in k:
                        self.model2.addConstr(self.r_it[i,t] <= self.Rmax[i][k_idx] * self.x_ikt[i,k_idx,t])
                if t not in self.K_i_simple[i]:
                    self.model2.addConstr(self.r_it[i,t] == 0)

        # Maintenance (Equations 10, 11, 12)
        for i in self.I2:
            for k_idx, k in enumerate(self.K_i[i]):
                self.model2.addConstr(sum(self.x_ikt[i,k_idx, t] for t in k) <= 1)
                for t in k:
                    if t + self.DA_ik[i][k_idx] <= len(self.T):
                        self.model2.addConstr(sum(self.y_it[i, _t] for _t in range(t, t + self.DA_ik[i][k_idx])) 
                                              >= self.DA_ik[i][k_idx] * self.x_ikt[i, k_idx, t])
                    else:
                        self.model2.addConstr(self.x_ikt[i, k_idx, t] == 0)

            self.model2.addConstr(sum(self.y_it[i,t] for t in self.T) == 
                                  sum(self.DA_ik[i][k_idx] * self.x_ikt[i,k_idx, t] 
                                      for k_idx, k in enumerate(self.K_i[i]) for t in k))
    
    def sousPB_typeI1_modelv(self, mu):
        # On ne change QUE l'objectif
        obj = sum((self.Cost_it[i][t]*self.D_t[t] - mu[t]) * self.p1_it[i, t] 
                  for i in self.I1 for t in self.T)
        self.model1.setObjective(obj, sense=hp.ObjSense.kMinimize)
        
        self.model1.run()
        
        if self.model1.getModelStatus() == hp.HighsModelStatus.kOptimal:
            obj_val = self.model1.getObjectiveValue()
            sol = {(i,t): self.model1.variableValue(self.p1_it[i,t]) for i in self.I1 for t in self.T}
            return obj_val, sol
        return 0, {(i,t): 0.0 for i in self.I1 for t in self.T}

    def sousPB_typeI2_modelv(self, mu):
        # 1. Mise à jour de l'objectif (Pénalité de la demande)
        obj = sum(
            sum(self.RefCost_ik[i][k_idx] * sum(self.r_it[i, t] for t in self.K_i[i][k_idx]) 
                for k_idx in range(len(self.K_i[i])))
            - sum(mu[t] * self.p2_it[i, t] for t in self.T)
            for i in self.I2
        )
        self.model2.setObjective(obj, sense=hp.ObjSense.kMinimize)
        
        # 2. Résolution
        self.model2.run()
        
        # 3. Extraction
        model_status = self.model2.getModelStatus()
        
        if model_status == hp.HighsModelStatus.kOptimal:
            obj_value = self.model2.getObjectiveValue()
            
            # Initialisation des structures de retour
            x_ikt_solution = [[] for _ in range(len(self.I2))]
            y_it_solution = [[0.0 for _ in self.T] for _ in self.I2]
            p2_solution = {}
            r_solution = {}
            s_solution = {}

            for i in self.I2:
                # Extraction x (format liste de tuples pour les activations)
                for k_idx, k in enumerate(self.K_i[i]):
                    for t in k:
                        val_x = self.model2.variableValue(self.x_ikt[i, k_idx, t])
                        if val_x > 0.1:
                            x_ikt_solution[i].append((k_idx, t))
                
                for t in self.T:
                    # Extraction y (format matrice)
                    y_it_solution[i][t] = self.model2.variableValue(self.y_it[i, t])
                    
                    # Extraction p, r, s (format dictionnaire pour calcul subgradient)
                    p2_val = self.model2.variableValue(self.p2_it[i, t])
                    p2_solution[(i, t)] = p2_val
                    
                    r_val = self.model2.variableValue(self.r_it[i, t])
                    if r_val > 0.1:
                        r_solution[(i, t)] = r_val
                    
                    s_solution[(i, t)] = self.model2.variableValue(self.s_it[i, t])

            return obj_value, x_ikt_solution, y_it_solution, p2_solution, r_solution, s_solution

        else:
            # En cas d'échec, on renvoie l'infini pour le dual (minimisation)
            # et des structures vides compatibles pour ne pas faire planter la boucle
            p2_empty = {(i, t): 0.0 for i in self.I2 for t in self.T}
            return float('inf'), [], [], p2_empty, {}, {}
    
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
            sum((self.Cost_it[i][t]*self.D_t[t] - mu[t]) * p1_it[i, t] 
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

        # print("\n----------------------------------")
        # info = model.getInfo()
        # model_status = model.getModelStatus()
        # print('Status de la résolution par le solveur = ', model.modelStatusToString(model_status))
        # print("Valeur de la fonction objectif = ", model.getObjectiveValue())
        # print("Meilleure borne inférieure sur la valeur de la fonction objectif: ", info.mip_dual_bound)
        # print("Gap: ", info.mip_gap)
        # print("# de noeuds explorés: ", info.mip_node_count)
        # print("Temps de résolution (en secondes) = ", runtime)
        # print("----------------------------------")
        
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


        return obj_value, p1_solution  

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
                ( 
                sum(self.RefCost_ik[i][k_idx] *
                sum(r_it[i, t] for t in self.K_i[i][k_idx])
                for k_idx in range(len(self.K_i[i])))
                - sum(mu[t] * p2_it[i, t] for t in self.T)
                for i in self.I2
                )
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
                            >= # in the avancement_TER it was == 
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

        return obj_value, x_ikt_solution, y_it_solution, p2_solution, r_solution, s_solution


    def dualLag_function(self, mu, data, scenario):
        total = 0.0
        valP1 , p1_sol = self.sousPB_typeI1_modelv(mu)
        valP2, x_sol, y_sol, p2_sol, r_sol, s_sol = self.sousPB_typeI2_modelv(mu)
        total = valP2 + valP1 + sum(mu[t]*self.Dem_t[t] for t in self.T)

        return total, p1_sol, p2_sol, x_sol, y_sol, r_sol, s_sol
    
    def compute_subgradient(self, p1_sol, p2_sol):
        ssgradient = [self.Dem_t[t] - sum(p1_sol[(i,t)] for i in self.I1) - sum(p2_sol[(i,t)] for i in self.I2) 
                      for t in self.T]
        return ssgradient

    def subgradient_basic( self,data, scenario, time_start : float,
        initial_mu,
        min_step_size: float,
        initial_step_size: float = 2.0,
        alpha: float = 0.95,
        max_iterations: int = 100,
    ):
        mu = initial_mu 

        step_size = float(initial_step_size)

        best_Dualvalue = -float("inf")
      
        p1_best, p2_best, x_best, y_best, r_best, s_best = None , None , None , None , None , None 
        # history = [] # to track

        iteration = 0
        
        while iteration < max_iterations or time.time() - time_start < 7200: #step_size > min_step_size and (max_iterations is None or iteration < max_iterations):
            # solve Lagrangian subproblem
            dual_value, p1_sol, p2_sol, x_sol, y_sol, r_sol, s_sol = self.dualLag_function(mu, data, scenario)

            # keep best
            if dual_value > best_Dualvalue:
                best_Dualvalue = dual_value
    
                p1_best, p2_best, x_best, y_best, r_best, s_best = p1_sol, p2_sol, x_sol, y_sol, r_sol, s_sol

            # subgradient
            ssgradient = self.compute_subgradient(p1_sol, p2_sol)

            # update multipliers
            for t in self.T : 
                if mu[t] + step_size * ssgradient[t] > 0 :
                    mu[t] = mu[t] + step_size * ssgradient[t]
                else :
                    mu[t] = 0

            # update step
            step_size = step_size * alpha

            # update the history
            # history.append({
            #     "dual_value": dual_value,
            #     "mu": np.copy(mu)
            # })
            print(dual_value)
            iteration += 1

        return round(best_Dualvalue, 2), p1_best, p2_best, x_best, y_best, r_best, s_best
    

    def solve(self, data: Readingfile, scenario: int) -> Solution:
        try:
            from .checker import CheckerL
        except ImportError:
            from checker import CheckerL        

        # self.set_data_attrs(data, scenario)

        start_time = time.time()
        mu_initial = [0 for t in self.T]

        best_Dualvalue, p1_sol, p2_sol, x_sol, y_sol, r_sol, s_sol = self.subgradient_basic( data, scenario, start_time, mu_initial, 0.8)


        y_it_solution_sousPB2_ = {
            (i, t): 1
            for i in range(data.nbpower2())
            for t in range(data.timestep())
            if y_sol[i][t] == 1
        }
        x_ikt_solution_sousPB2_ = {
            (i, k_index, t_start): 1
            for i, campaigns in enumerate(x_sol)
            for k_index, t_start in campaigns
        }
        sol_sousPB_list = [p1_sol, p2_sol, y_it_solution_sousPB2_, r_sol, s_sol, x_ikt_solution_sousPB2_] 
        to = time.time() - start_time
        sol_sousPB =Solution("HEURISTIC_3_DICHOTOMY_Dual", best_Dualvalue, 0, to , sol_sousPB_list)

        if CheckerL(data, sol_sousPB, scenario):
            return sol_sousPB
            
        else :
            # list to dict 
            
            # inherited LP production plan
            production_plan = self.computeProductionPlanLP(
                data, scenario, y_sol, x_sol, start_time
            )
            obj_value, dual_bound, lp_runtime, status, p1_sol, p2_sol, r_sol, s_sol = production_plan
            sol = [p1_sol, p2_sol, y_it_solution_sousPB2_, r_sol, s_sol, x_ikt_solution_sousPB2_]

            return Solution("HEURISTIC_3_DICHOTOMY_Realisable", obj_value, dual_bound, lp_runtime, sol), sol_sousPB
          