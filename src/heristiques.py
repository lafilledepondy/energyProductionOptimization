from data import Readingfile

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
        """
        - Low initial stock => urgent refueling
        - High max power => high impact on production
        - Few campaigns => low flexibility
        """
        w_i_tab = []

        for i in range(data.nbpower2()):
            plant = data.accessPower2(i)
            Xi1 = plant.initialstock()          
            Pmax_i = sum(plant.pmax())          
            Ki_size = len(plant.Campaigns())    

            # priority score
            Wi = (1 / (Xi1 + 1e-6)) + Pmax_i + (1 / (Ki_size + 1e-6)) # + 1e-6 pour eviter /0

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