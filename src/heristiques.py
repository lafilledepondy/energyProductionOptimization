import time

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
        p1_sol = {
            (i, t): float(data.accessPower1(0, i).pmax()[t])
            for i in range(data.nbpower1())
            for t in range(T)
        }

        p2_sol: dict[tuple[int, int], float] = {}
        r_sol: dict[tuple[int, int], float] = {}
        s_sol: dict[tuple[int, int], float] = {}

        scheduled_campaign_start = {
            i: {t_start: k_index for k_index, t_start in x_itk[i]}
            for i in range(data.nbpower2())
        }

        for i in range(data.nbpower2()):
            plant = data.accessPower2(i)
            stock = float(plant.initialstock())

            for t in range(T):
                if t in scheduled_campaign_start[i]:
                    campaign = plant.Campaigns()[scheduled_campaign_start[i][t]]
                    target_stock = float(campaign.maxstock())
                    refuel = max(0.0, target_stock - stock)
                    if refuel > 0:
                        r_sol[(i, t)] = refuel
                    stock += refuel

                production = 0.0 if y_it[i][t] == 1 else float(plant.pmax()[t])
                p2_sol[(i, t)] = production
                stock -= production * float(data.timestepduration()[t])
                s_sol[(i, t)] = stock

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

        return Solution("HEURISTIC", 
                    obj_value, 
                    float('inf'), runtime, sol)