from graphviz import Digraph
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def flowChart_heu_basic():

    g = Digraph(format='png')
    g.attr(rankdir='TB')

    # --- Configuration des Styles ---

    # Vert pour le début et la fin (Cercles/Ellipses)
    g.attr('node', style='filled', color='seagreen', fillcolor='honeydew', shape='ellipse')
    g.node('A', 'Début Heuristique basique')
    g.node('J', 'Solution finale')

    # Orange pour les questions (Losanges)
    g.attr('node', color='darkorange', fillcolor='papayawhip', shape='diamond')
    g.node('E', 'Date d\'interruption réalisable?')
    g.node('H', 'Plus de centrales?')

    # Bleu pour les actions (Rectangles)
    g.attr('node', color='steelblue', fillcolor='aliceblue', shape='box')
    g.node('B', 'Calculer scores de priorité Wi')
    g.node('C', 'Trier les centrales par Wi décroissant')
    g.node('D', 'Sélectionner la première centrale') # REDO the french
    g.node('F', 'Planifier l\'interruption\nMettre à jour y, x')
    g.node('G', 'Rien planifier')
    g.node('I', 'Résoudre le PL pour p, s, r')

    # --- Définition des Arêtes ---
    g.edges([('A','B'), ('B','C'), ('C','D'), ('D','E')])
    g.edge('E', 'F', label='Yes')
    g.edge('E', 'G', label='No')
    g.edge('G', 'H')
    g.edge('F', 'H')
    g.edge('H', 'D', label='Yes')
    g.edge('H', 'I', label='No')
    g.edge('I', 'J')

    g.render(str(OUTPUT_DIR / 'heuristic_basic_flowchart'), view=True)

from graphviz import Digraph

def flowChart_heu_campaign_multiple():

    g = Digraph(format='png')
    g.attr(rankdir='TB')

    # --- Configuration des Styles ---

    # Vert pour le début et la fin (Cercles/Ellipses)
    g.attr('node', style='filled', color='seagreen', fillcolor='honeydew', shape='ellipse')
    g.node('A', 'Début Heuristique basique améliorée\nMulti-campagnes')
    g.node('K', 'Solution finale')

    # Orange pour les questions (Losanges)
    g.attr('node', color='darkorange', fillcolor='papayawhip', shape='diamond')
    g.node('E', 'Date d\'interruption réalisable?')
    g.node('H', 'Plus de centrales?')
    g.node('I', 'cpt < |I_2| ?')

    # Bleu pour les actions (Rectangles)
    g.attr('node', color='steelblue', fillcolor='aliceblue', shape='box')
    g.node('B', 'Calculer scores de priorité Wi\nET\nTrier les centrales par Wi décroissant')
    g.node('C', 'Unité sans créneau réalisable : cpt=0')
    g.node('D', 'Sélectionner la première centrale')
    g.node('F', 'Planifier l\'interruption\nMettre à jour y, x')
    g.node('G', 'Rien planifier ; cpt+1')
    g.node('J', 'Résoudre le PL pour p, s, r')

    # --- Définition des Arêtes ---

    g.edges([
        ('A', 'B'),
        ('B', 'C')
    ])

    # Partie identique à la version précédente → en pointillés
    g.edge('C', 'D',)
    g.edge('D', 'E', style='dashed')

    g.edge('E', 'F', label='Yes', style='dashed')
    g.edge('E', 'G', label='No', style='dashed')

    g.edge('G', 'H', style='dashed')
    g.edge('F', 'H', style='dashed')

    g.edge('H', 'D', label='Yes', style='dashed')

    # Partie spécifique multi-campagnes
    g.edge('H', 'I', label='No')
    g.edge('I', 'C', label='Yes')
    g.edge('I', 'J', label='No')

    g.edge('J', 'K')

    g.render(str(OUTPUT_DIR / 'heuristic_campaign_multiple_flowchart'), view=True)

def flowChart_heu_RF():

    g = Digraph(format='png')
    g.attr(rankdir='TB')

    # --- Start / End ---
    g.attr('node', style='filled', color='seagreen', fillcolor='honeydew', shape='ellipse')
    g.node('A', 'Début Heuristique améliorée\nRandom Forest')
    # g.node('N', 'Solution finale')

    # --- Decisions ---
    g.attr('node', color='darkorange', fillcolor='papayawhip', shape='diamond')
    g.node('B', 'Modèle priorité en cache ?')
    g.node('F', 'Modèle dates en cache ?')
    g.node('K', 'Créneau faisable trouvé ?')

    # --- Actions ---
    g.attr('node', color='steelblue', fillcolor='aliceblue', shape='box')
    g.node('C', 'Construction features centrales type 2')
    g.node('D', 'Entraînement RandomForestRegressor')
    g.node('E', 'Prédiction scores W_i et tri centrales')

    g.node('G', 'Construction dataset dates maintenance')
    g.node('H', 'Entraînement RandomForestClassifier')
    g.node('I', 'Prédiction meilleurs t_start candidats')

    g.node('J', 'Test capacité restante / faisabilité')
    g.node('L', '(pareil que heuristique basic...)')
    # g.node('L', 'Fixer x_itk et y_it')
    # g.node('M', 'Résolution PL production + recharge (HiGHS)')

    # --- Edges ---
    g.edge('A', 'B')

    # Priority model
    g.edge('B', 'E', label='Oui')
    g.edge('B', 'C', label='Non')
    g.edge('C', 'D')
    g.edge('D', 'E')

    # Start-date model
    g.edge('E', 'F')
    g.edge('F', 'I', label='Oui')
    g.edge('F', 'G', label='Non')
    g.edge('G', 'H')
    g.edge('H', 'I')

    # Scheduling loop
    g.edge('I', 'J')
    g.edge('J', 'K')
    g.edge('K', 'L', label='Oui')
    g.edge('K', 'I', label='Non')

    # Final LP
    # g.edge('L', 'M')
    # g.edge('M', 'N')

    g.render(str(OUTPUT_DIR / 'heuristic_basic+MILP_flowchart'), view=True)   

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw_maintenance_schedule_production():
    # --- Configuration ---
    # Production values (normalized to fit within the unit's vertical space)
    # Max height for curve will be ~0.4 units above the baseline
    # prod_data = {
    #     4: [70, 90, 100, 100, 100, 60, 100, 100, 100, 0, 100, 100, 100, 100, 70, 90, 100, 0, 100, 60, 100, 100, 100, 100, 100, 100, 100, 100, 70, 90, 100, 100, 100, 60, 100, 100, 100, 100, 100, 100, 100, 100, 70, 90, 100, 100, 100, 60, 100, 100, 100],       # Gaz
    #     3: [80]*51,     # Charbon
    #     2: [0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 47.0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50, 30, 10, 0, 40, 10, 20, 50, 60, 70, 50, 10, 0, 0, 50, 30, 10, 0, 40, 10, 20],        # Nucl 1
    #     1: [0, 0, 50, 30, 10, 0, 40, 10, 20, 140, 60, 70, 2.916, 0, 0, 0, 50, 130, 10, 0, 40, 10, 20, 50, 60, 70, 50, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],       # Nucl 2
    # }

    prod_data = {
        4: [70.0, 90.0, 100.0, 100.0, 100.0, 60.0, 100.0, 100.0, 100.0, 0.0, 100.0, 100.0, 100.0, 100.0, 70.0, 90.0, 100.0, 0.0, 100.0, 60.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 70.0, 90.0, 100.0, 100.0, 100.0, 60.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 70.0, 90.0, 100.0, 100.0, 100.0, 60.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 70.0, 90.0, 100.0, 0.0, 100.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 0.0, 90.0, 100.0, 100.0, 100.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 0.0, 90.0, 100.0, 100.0, 100.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 70.0, 90.0, 100.0, 100.0, 100.0, 60.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 70.0, 90.0, 100.0, 100.0, 100.0, 60.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 0.0, 70.0, 90.0, 100.0, 100.0, 100.0, 60.0, 0.0, 100.0, 35.0, 10.0, 100.0, 30.0, 100.0],
        3: [80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0, 80.0],
        2: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 47.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 50.0, 30.0, 10.0, 0.0, 40.0, 10.0, 20.0, 50.0, 60.0, 70.0, 50.0, 10.0, 0.0, 0.0, 50.0, 30.0, 10.0, 0.0, 40.0, 10.0, 20.0, 50.0, 60.0, 70.0, 50.0, 10.0, 0.0, 0.0, 50.0, 130.0, 10.0, 60.0, 0.0, 10.0, 20.0, 50.0, 60.0, 70.0, 50.0, 10.0, 0.0, 0.0, 0.0, 0.0, 10.0, 60.0, 40.0, 0.0, 20.0, 0.0, 60.0, 37.92, 50.0, 10.0, 70.0, 0.0, 50.0, 30.0, 10.0, 60.0, 40.0, 10.0, 20.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 60.0, 70.0, 50.0, 10.0, 0.0, 0.0, 50.0, 30.0, 10.0, 0.0, 40.0, 10.0, 20.0, 50.0, 60.0, 70.0, 50.0, 110.0, 0.0, 0.0, 50.0, 30.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        1: [0.0, 0.0, 50.0, 30.0, 10.0, 0.0, 40.0, 10.0, 20.0, 140.0, 60.0, 70.0, 2.916, 0.0, 0.0, 0.0, 50.0, 130.0, 10.0, 0.0, 40.0, 10.0, 20.0, 50.0, 60.0, 70.0, 50.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 40.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 70.0, 0.0, 50.0, 30.0, 0.0, 0.0, 0.0, 10.0, 0.0, 50.0, 0.0, 32.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 60.0, 70.0, 50.0, 10.0, 0.0, 0.0, 50.0, 30.0, 10.0, 0.0, 40.0, 10.0, 20.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 140.0, 10.0, 85.0, 140.0, 60.0, 140.0, 50.0],
    }

    lengths = {key: len(value) for key, value in prod_data.items()}
    print("Summary of lengths:", lengths)

        
    units = [
        # (6, "Panneau solaire ($i=1$)"),
        # (5, "Éolienne ($i=2$)"),
        (4, "Gaz ($i=3$)"),
        (3, "Charbon ($i=4$)"),
        (2, "Nucléaire 1 ($i=5$)"),
        (1, "Nucléaire 2 ($i=6$)")
    ]
    
    t_max = 139
    x_limit = t_max + 10
    weeks_ticks = range(0, 134, 7)

    fig, ax = plt.subplots(figsize=(9, 5))

    # --- Draw Axes and Labels ---
    for y, name in units:
        ax.arrow(0, y, x_limit, 0, head_width=0.12, head_length=2, 
                 fc='black', ec='black', length_includes_head=True)
        ax.text(x_limit + 2, y, "jours", va='center', fontsize=9)
        ax.plot([0, 0], [y - 0.5, y + 0.5], color='black', linewidth=1)
        ax.text(-5, y, name, ha='right', va='center', fontsize=10)
        
        for t in weeks_ticks:
            ax.plot([t, t], [y - 0.08, y + 0.08], color='black', linewidth=0.8)

        if y in prod_data:
            vals = np.array(prod_data[y])
            n = len(vals)
            # x coordinates matching the number of samples in this series
            # Start at integer days (0,1,2,...) so curves align with rectangles/ticks
            x_vals = np.arange(0, n, 1.0)
            max_val = max(vals) if max(vals) > 0 else 1
            # Scaling: 0.4 is the peak height, y is the baseline
            norm_vals = y + (vals / max_val) * 0.4
            ax.plot(x_vals, norm_vals, color='blue', linewidth=1.5, alpha=0.85, zorder=4)
            # Label "prod." like in the reference image
            # ax.text(-2, y + 0.45, "prod.", fontsize=8, ha='right')

    # --- Unit 5 (Nucléaire 1) Maintenance ---
    ax.add_patch(patches.Rectangle((7, 2 - 0.25), 21, 0.5, color='#e0e0e0', zorder=1)) 
    ax.add_patch(patches.Rectangle((98, 2 - 0.25), 35, 0.5, color='#e0e0e0', zorder=1))
    ax.add_patch(patches.Rectangle((14, 2 - 0.25), 14, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(21, 2.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)

    # Bloc 2 : t=94 à 107 (14 jours)
    ax.add_patch(patches.Rectangle((94, 2 - 0.25), 13, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(101, 2.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)    

    # --- Unit 6 (Nucléaire 2) Maintenance ---
    ax.add_patch(patches.Rectangle((14, 1 - 0.25), 42, 0.5, color='#e0e0e0', zorder=1))
    ax.add_patch(patches.Rectangle((105, 1 - 0.25), 28, 0.5, color='#e0e0e0', zorder=1))
    ax.add_patch(patches.Rectangle((42, 1 - 0.25), 14, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(49, 1.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)

    # Bloc 2 : t=118 à 131 (14 jours)
    ax.add_patch(patches.Rectangle((112, 1 - 0.25), 14, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(119, 1.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)    

    # --- Legend ---
    ax.add_patch(patches.Rectangle((10, -0.2), 5, 0.3, facecolor='#e0e0e0', edgecolor='black'))
    ax.text(17, -0.05, "Fenêtres de début $K_i$", va='center', fontsize=10)
    ax.add_patch(patches.Rectangle((70, -0.2), 5, 0.3, facecolor='#99ff99', edgecolor='black'))
    ax.text(77, -0.05, "Maintenance choisie ($y_{it}=1$)", va='center', fontsize=10)
    ax.plot([10, 15], [-0.28, -0.28], color='blue', linewidth=2)
    ax.text(17, -0.28, "Courbe de production", va='center', fontsize=10)

    # --- Formatting ---
    ax.set_xlim(-30, x_limit + 8)
    ax.set_ylim(-0.6, 4.7)
    ax.axis('off')
    plt.title("Solution réalisable : Planning des arrêts et Courbes de Production", 
    # plt.title("Diagramme illustrant les périodes de maintenance possibles pour chaque unité (i)",
              y=0.98, fontsize=13, fontweight='bold')

    plt.savefig(OUTPUT_DIR / 'solution maintenance solution.png', bbox_inches='tight', dpi=300)
    plt.show()
    
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class TERPlots:
    """
    Generate comparison plots from LaTeX result tables.

    INPUTS
    ------
    milp_tex_file : str
        Path to LaTeX file containing MILP table.

    heuristic_tex_file : str
        Path to LaTeX file containing heuristic comparison table.

    The heuristic table must contain columns like:
        Data | S | VAL | Gap | CPU

    The MILP table must contain:
        Data | S | BD | CPU_1

    Gap formula assumed:
        Gap(%) = (VAL - BD)/BD * 100

    OUTPUT
    ------
    Saves:
        - gap_comparison.png
        - cpu_comparison.png
        - quality_vs_runtime.png
    """

    def __init__(self, milp_tex_file: str, heuristic_tex_file: str):
        self.milp_tex_file = milp_tex_file
        self.heuristic_tex_file = heuristic_tex_file

        self.milp_df = None
        self.heuristic_df = None

    # =========================================================
    # ---------------- LATEX TABLE PARSING --------------------
    # =========================================================

    def _clean_value(self, x):
        x = str(x).strip()

        x = x.replace("\\", "")
        x = x.replace("%", "")
        x = x.replace("s", "")
        x = x.replace("--", "")
        x = x.replace("Irréal.", "")
        x = x.replace("inf", "")
        x = x.replace(" ", "")

        try:
            return float(x)
        except:
            return np.nan

    def _extract_rows(self, text):
        rows = []

        for line in text.splitlines():

            if "&" not in line:
                continue

            if "\\hline" in line:
                continue

            if "textbf" in line:
                continue

            line = line.replace("\\\\", "")
            parts = [p.strip() for p in line.split("&")]

            rows.append(parts)

        return rows

    # =========================================================
    # ---------------------- MILP -----------------------------
    # =========================================================

    def parse_milp_table(self):

        with open(self.milp_tex_file, "r", encoding="utf-8") as f:
            text = f.read()

        rows = self._extract_rows(text)

        data = []

        for row in rows:

            if len(row) < 8:
                continue

            instance = row[0]
            scenario = row[1]

            bd = self._clean_value(row[3])
            cpu = self._clean_value(row[7])

            data.append({
                "Instance": f"{instance}-S{scenario}",
                "BD": bd,
                "MILP_CPU": cpu
            })

        self.milp_df = pd.DataFrame(data)

    # =========================================================
    # ------------------- HEURISTICS --------------------------
    # =========================================================

    def parse_heuristic_table(self):

        with open(self.heuristic_tex_file, "r", encoding="utf-8") as f:
            text = f.read()

        table_blocks = re.findall(
            r"\\begin\{table\}.*?\\end\{table\}",
            text,
            flags=re.DOTALL
        )

        data = []

        for block in table_blocks:
            rows = self._extract_rows(block)

            heuristic_names = re.findall(
                r"\\textbf\{([^}]*)\}",
                block
            )

            heuristic_names = [
                h for h in heuristic_names
                if "Instances" not in h
                and "Data" not in h
                and "S" not in h
                and "VAL" not in h
                and "Gap" not in h
                and "CPU" not in h
            ]

            if len(heuristic_names) < 2:
                continue

            h1_name, h2_name = heuristic_names[:2]

            heuristic_pairs = [
                (h1_name, 3, 4),
                (h2_name, 6, 7),
            ]

            for row in rows:

                if len(row) < 8:
                    continue

                instance = row[0]
                scenario = row[1]

                instance_name = f"{instance}-S{scenario}"

                for heuristic_name, gap_idx, cpu_idx in heuristic_pairs:
                    if "RF" in heuristic_name.upper():
                        continue

                    data.append({
                        "Instance": instance_name,
                        "Heuristic": heuristic_name,
                        "Gap": self._clean_value(row[gap_idx]),
                        "CPU": self._clean_value(row[cpu_idx])
                    })

        self.heuristic_df = pd.DataFrame(data)
        # Assign consistent colors for heuristics using matplotlib default cycle
        heuristics = list(self.heuristic_df["Heuristic"].unique()) if not self.heuristic_df.empty else []
        prop_colors = plt.rcParams.get('axes.prop_cycle').by_key().get('color', [])
        self.colors = {h: prop_colors[i % len(prop_colors)] for i, h in enumerate(heuristics)}

    # =========================================================
    # ------------------- FIGURE 1 ----------------------------
    # =========================================================

    def plot_gap_comparison(self):
        # Compute mean gap per heuristic (average across instances)
        if self.heuristic_df is None or self.heuristic_df.empty:
            print("No heuristic data to plot GAPs")
            return

        # Mean gap per heuristic
        mean_gap = self.heuristic_df.groupby("Heuristic")["Gap"].mean()

        # If any mean is non-positive, fall back to mean absolute gap
        use_abs = False
        if (mean_gap <= 0).any():
            mean_gap = self.heuristic_df.groupby("Heuristic")["Gap"].apply(lambda x: np.nanmean(np.abs(x)))
            ylabel = "Moyen |Gap| (%) [log scale]"
            use_abs = True
        else:
            ylabel = "Gap Moyen (%) [log scale]"

        # use consistent heuristic colors
        colors = [self.colors.get(h, None) for h in mean_gap.index]
        ax = mean_gap.plot(kind="bar", figsize=(12, 6), color=colors)

        # Log scale (use absolute means when necessary to ensure positivity)
        ax.set_yscale("log")
        ax.set_ylabel(ylabel)
        ax.set_title("Moyenne des GAPs par heuristique")
        ax.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / "gap_comparison.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

    # =========================================================
    # ------------------- FIGURE 2 ----------------------------
    # =========================================================

    def plot_cpu_comparison(self):

        cpu_df = self.heuristic_df.pivot_table(
            index="Instance",
            columns="Heuristic",
            values="CPU"
            , aggfunc="first"
        )

        milp_cpu = self.milp_df.set_index("Instance")["MILP_CPU"]

        cpu_df["MILP"] = milp_cpu

        ax = cpu_df.plot(
            kind="bar",
            figsize=(14, 6)
        )

        # set colors for each column (heuristics + MILP)
        col_colors = []
        for col in cpu_df.columns:
            if col == "MILP":
                col_colors.append('gray')
            else:
                col_colors.append(self.colors.get(col, None))
        # replot with colors to ensure consistent palette
        ax = cpu_df.plot(kind="bar", figsize=(14,6), color=col_colors)

        ax.set_yscale("log")
        ax.set_ylabel("CPU Time (s) [log scale]")
        ax.set_title("Comparaison des temps CPU")
        ax.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / "cpu_comparison.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

    # =========================================================
    # ------------------- FIGURE 3 ----------------------------
    # =========================================================

    def plot_quality_vs_runtime(self):

        plt.figure(figsize=(10, 7))

        heuristics = self.heuristic_df["Heuristic"].unique()

        for h in heuristics:

            subset = self.heuristic_df[
                self.heuristic_df["Heuristic"] == h
            ]

            plt.scatter(
                subset["CPU"],
                subset["Gap"],
                s=80,
                label=h
            )

        plt.xlabel("CPU Time (s)")
        plt.ylabel("Gap (%)")
        plt.title("Qualité vs Temps de calcul")

        plt.grid(True)
        plt.legend()

        plt.tight_layout()

        plt.savefig(
            OUTPUT_DIR / "quality_vs_runtime.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

    # =========================================================
    # -------------------- MAIN PIPELINE ----------------------
    # =========================================================

    def generate_all_plots(self):

        self.parse_milp_table()
        self.parse_heuristic_table()

        self.plot_gap_comparison()
        self.plot_cpu_comparison()
        self.plot_quality_vs_runtime()

        print("Plots generated successfully.")

    

def main():
    # flowChart_heu_basic()
    # flowChart_heu_campaign_multiple()
    # flowChart_heu_RF()
    draw_maintenance_schedule_production()

    # base_dir = Path(__file__).resolve().parent
    # output_dir = base_dir.parent / "output"
    # plots = TERPlots(
    #     milp_tex_file=str(output_dir / "tableau_milp_resultats.tex"),
    #     heuristic_tex_file=str(output_dir / "tableaux_heur_resultats.tex")
    # )
    # plots.generate_all_plots()    

if __name__ == "__main__":
    main()