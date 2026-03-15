import time


def runMILPModel(data, toPrint, timeLimit, solverName):
    # ======= VARIABLES =======


    # ======= OBJECTIVE =======


    # ======= CONSTRAINTS =======


    # ======= MODEL =======
    solver = pyo.SolverFactory(solverName)
    
    # Réglage spécifique pour HiGHS (via appsi)
    if solverName == "appsi_highs":
        solver.options['time_limit'] = timeLimit
    else:
        solver.options['time_limit'] = timeLimit
    
    start_time = time.time()

    # tee=True est la CLÉ pour que le log contienne les bornes
    results = solver.solve(model, tee=True) 
    solve_time = time.time() - start_time

    status = results.solver.status
    
    # ===== EXTRACT SOLUTION =====
    sectors = []
    # On vérifie si une solution existe (Optimal ou Feasible)
    if status == SolverStatus.ok or status == SolverStatus.warning:
        for i in range(H):
            for j in range(W):
                try:
                    if pyo.value(model.x[i, j]) > 0.5:
                        sectors.append((i, j))
                except ValueError: # Au cas où la variable n'a pas de valeur
                    continue
        obj_value = pyo.value(model.obj)
    else:
        obj_value = -1

    # On retourne UNIQUEMENT les 4 arguments de votre classe
    return Solution(sectors, obj_value, solve_time, status)
