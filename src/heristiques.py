from data import Readingfile
import data

# -----------------------------
# Abstract class
# -----------------------------
class AbstractMaintenanceHeuristic:
    def solve(self, data: Readingfile) -> dict:
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

        for i in I2:
            if all(v == Smax_ik[i][0] for v in Smax_ik[i]):
                smax_i = Smax_ik[i][0]
            else:
                print(f"Warning: Smax_ik values are not the same for all campaigns of unit {i}.")
                            
            Wi = (Xi1[i] - Sth_min[i]) / (smax_i - Sth_min[i]) # stock (Xi1 - Sth_min_i) / (Smax_ik - Sth_min_i)
            # Wi += # puissance
            # Wi += 1-(sum( for k in Ki)/len(data.timestep())) # fenetres de maintenance

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

    def computeProductionPlan(self, data: Readingfile, y_it: list[list[int]], x_itk: list[list[tuple[int, int]]]) -> tuple[list[list[float]], list[list[float]], list[list[float]]]:
        T = data.timestep()
        I = data.nbpower1() + data.nbpower2()
        p_it = [[0 for _ in range(T)] for _ in range(I)]
        s_it = []
        r_it = []
        return p_it, s_it, r_it

    def solve(self, data: Readingfile) -> dict:
        result = self.scheduleMaintenance(data)

        if result is None:
            return None

        y_it, x_itk = result
        p_it, s_it, r_it = self.computeProductionPlan(data, y_it, x_itk)

        return {
            "y": y_it,   # outage decisions
            "x": x_itk,  # campaign selection
            "p": p_it,   # production plan
            "s": s_it,   # stock evolution
            "r": r_it    # refueling quantities
        }