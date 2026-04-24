from graphviz import Digraph

def flowChart_heu1():

    g = Digraph(format='png')
    g.attr(rankdir='TB')

    # --- Configuration des Styles ---

    # Vert pour le début et la fin (Cercles/Ellipses)
    g.attr('node', style='filled', color='seagreen', fillcolor='honeydew', shape='ellipse')
    g.node('A', 'Début Heuristique 1')
    g.node('J', 'Solution finale')

    # Orange pour les questions (Losanges)
    g.attr('node', color='darkorange', fillcolor='papayawhip', shape='diamond')
    g.node('E', 'Date d\'interruption réalisable?')
    g.node('H', 'Plus de centrales?')

    # Bleu pour les actions (Rectangles)
    g.attr('node', color='steelblue', fillcolor='aliceblue', shape='box')
    g.node('B', 'Calculer scores de priorité Wi')
    g.node('C', 'Trier les centrales par Wi')
    g.node('D', 'Sélectionner la première centrale')
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

    g.render('output/heuristic_1_flowchart', view=True)


def flowChart_heu3():

    g = Digraph(format='png')
    g.attr(rankdir='TB')

    # --- Start / End ---
    g.attr('node', style='filled', color='seagreen', fillcolor='honeydew', shape='ellipse')
    g.node('A', 'Début Heuristique V3')
    g.node('J', 'Solution finale')

    # --- Decision / ML block ---
    g.attr('node', color='darkorange', fillcolor='papayawhip', shape='diamond')
    g.node('D', 'Modèle Random Forest chargé ?')

    # --- Actions ---
    g.attr('node', color='steelblue', fillcolor='aliceblue', shape='box')
    g.node('B', 'Extraction features centrales type 2')
    g.node('C', 'Calcul W_i via RandomForestRegressor')
    g.node('E', 'Chargement mémoire (joblib)')
    g.node('F', 'Entraînement modèle si absent')
    g.node('G', 'Tri des centrales selon W_i')
    g.node('H', 'Planification maintenances (V2 identique)')
    g.node('I', 'Résolution PL (HiGHS)')

    # --- Edges ---
    g.edge('A', 'D')

    g.edge('D', 'E', label='Oui')
    g.edge('D', 'B', label='Non')

    g.edge('E', 'G')
    g.edge('B', 'F')
    g.edge('F', 'C')
    g.edge('C', 'G')

    g.edge('G', 'H')
    g.edge('H', 'I')
    g.edge('I', 'J')

    g.render('output/heuristic_ML+MILP_flowchart', view=True)    

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_maintenance_schedule():
    # --- Configuration ---
    # (y-coordinate, Label)
    units = [
        (6, "Panneau solaire ($i=1$)"),
        (5, "Éolienne ($i=2$)"),
        (4, "Gaz ($i=3$)"),
        (3, "Charbon ($i=4$)"),
        (2, "Nucléaire 1 ($i=5$)"),
        (1, "Nucléaire 2 ($i=6$)")
    ]
    
    t_max = 139
    x_limit = t_max + 10
    weeks = range(0, 134, 7)  # Graduations every 7 days

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # --- Draw Axes and Labels ---
    for y, name in units:
        # Horizontal arrow for the timeline (jours)
        ax.arrow(0, y, x_limit, 0, head_width=0.12, head_length=2, 
                 fc='black', ec='black', length_includes_head=True)
        ax.text(x_limit + 2, y, "jours", va='center', fontsize=9)
        
        # Vertical axis start line
        ax.plot([0, 0], [y - 0.5, y + 0.5], color='black', linewidth=1)
        
        # Unit label on the left
        ax.text(-5, y, name, ha='right', va='center', fontsize=10)
        
        # Weekly tick marks (similar to TikZ \foreach)
        for t in weeks:
            ax.plot([t, t], [y - 0.08, y + 0.08], color='black', linewidth=0.8)

    # --- Unit 5 (Nucléaire 1) Maintenance Data ---
    # Gray background windows (Fenêtres de début)
    # Rectangle( (x, y), width, height )
    ax.add_patch(patches.Rectangle((7, 2 - 0.25), 21, 0.5, color='#e0e0e0', zorder=1)) 
    ax.add_patch(patches.Rectangle((98, 2 - 0.25), 35, 0.5, color='#e0e0e0', zorder=1))
    
    # Green maintenance block (Arrêt choisi)
    ax.add_patch(patches.Rectangle((14, 2 - 0.25), 14, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(21, 2.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)

    # --- Unit 6 (Nucléaire 2) Maintenance Data ---
    # Gray background windows
    ax.add_patch(patches.Rectangle((14, 1 - 0.25), 42, 0.5, color='#e0e0e0', zorder=1))
    ax.add_patch(patches.Rectangle((91, 1 - 0.25), 28, 0.5, color='#e0e0e0', zorder=1))
    
    # Green maintenance block
    ax.add_patch(patches.Rectangle((35, 1 - 0.25), 14, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(42, 1.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)

    # --- Legend ---
    # Window legend
    ax.add_patch(patches.Rectangle((10, -0.2), 5, 0.3, facecolor='#e0e0e0', edgecolor='black'))
    ax.text(17, -0.05, "Fenêtres de début $K_i$", va='center', fontsize=10)
    
    # Maintenance legend
    ax.add_patch(patches.Rectangle((70, -0.2), 5, 0.3, facecolor='#99ff99', edgecolor='black'))
    ax.text(77, -0.05, "Maintenance choisie ($y_{it}=1$)", va='center', fontsize=10)

    # --- Formatting ---
    ax.set_xlim(-45, x_limit + 15)
    ax.set_ylim(-0.5, 7.5)
    ax.axis('off')  # Hide standard matplotlib frame
    plt.title("Solution réalisable : Planning des arrêts sur 20 semaines", 
              y=0.95, fontsize=13, fontweight='bold')

    # Save to file
    plt.savefig('output/solExample_maintenanceSchedule.png', bbox_inches='tight', dpi=300)
    plt.show()

import numpy as np

def draw_maintenance_schedule_production():
    # --- Configuration ---
    # Production values (normalized to fit within the unit's vertical space)
    # Max height for curve will be ~0.4 units above the baseline
    prod_data = {
        4: [
            70, 90, 100, 100, 100, 60, 100, 100, 100, 0,
            100, 100, 100, 100, 70, 90, 100, 0, 100, 60,
            100, 100, 100, 100, 100, 100, 100, 100, 70, 90,
            100, 100, 100, 60, 100, 100, 100, 100, 100, 100,
            100, 100, 70, 90, 100, 100, 100, 60, 100, 100, 100
        ],       # Gaz
        3: [80]*51,     # Charbon
        2: [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 10,
            0, 0, 47.0, 10, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            50, 30, 10, 0, 40, 10, 20, 50, 60, 70,
            50, 10, 0, 0, 50, 30, 10, 0, 40, 10, 20
        ],        # Nucl 1
        1: [
            0, 0, 50, 30, 10, 0, 40, 10, 20, 140,
            60, 70, 2.916, 0, 0, 0, 50, 130, 10, 0,
            40, 10, 20, 50, 60, 70, 50, 10, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ],       # Nucl 2
    }
        
    units = [
        (6, "Panneau solaire ($i=1$)"),
        (5, "Éolienne ($i=2$)"),
        (4, "Gaz ($i=3$)"),
        (3, "Charbon ($i=4$)"),
        (2, "Nucléaire 1 ($i=5$)"),
        (1, "Nucléaire 2 ($i=6$)")
    ]
    
    t_max = 139
    x_limit = t_max + 10
    weeks_ticks = range(0, 134, 7)

    # --- Time steps for the 51 production samples ---
    # Use one x-coordinate per sample so every production series plots correctly.
    week_x = np.arange(0.5, 51.5, 1.0)

    fig, ax = plt.subplots(figsize=(12, 8))

    # --- Draw Axes and Labels ---
    for y, name in units:
        ax.arrow(0, y, x_limit, 0, head_width=0.12, head_length=2, 
                 fc='black', ec='black', length_includes_head=True)
        ax.text(x_limit + 2, y, "jours", va='center', fontsize=9)
        ax.plot([0, 0], [y - 0.5, y + 0.5], color='black', linewidth=1)
        ax.text(-5, y, name, ha='right', va='center', fontsize=10)
        
        for t in weeks_ticks:
            ax.plot([t, t], [y - 0.08, y + 0.08], color='black', linewidth=0.8)

        # --- NEW: Add Production Curves (Courbes) ---
        if y in prod_data:
            vals = np.array(prod_data[y])
            max_val = max(vals) if max(vals) > 0 else 1
            # Scaling: 0.4 is the peak height, y is the baseline
            norm_vals = y + (vals / max_val) * 0.4 
            ax.plot(week_x, norm_vals, color='blue', linewidth=1.5, alpha=0.85, zorder=4)
            # Label "prod." like in the reference image
            # ax.text(-2, y + 0.45, "prod.", fontsize=8, ha='right')

    # --- Unit 5 (Nucléaire 1) Maintenance ---
    ax.add_patch(patches.Rectangle((7, 2 - 0.25), 21, 0.5, color='#e0e0e0', zorder=1)) 
    ax.add_patch(patches.Rectangle((98, 2 - 0.25), 35, 0.5, color='#e0e0e0', zorder=1))
    ax.add_patch(patches.Rectangle((14, 2 - 0.25), 14, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(21, 2.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)

    # --- Unit 6 (Nucléaire 2) Maintenance ---
    ax.add_patch(patches.Rectangle((14, 1 - 0.25), 42, 0.5, color='#e0e0e0', zorder=1))
    ax.add_patch(patches.Rectangle((91, 1 - 0.25), 28, 0.5, color='#e0e0e0', zorder=1))
    ax.add_patch(patches.Rectangle((35, 1 - 0.25), 14, 0.5, facecolor='#99ff99', 
                                   edgecolor='black', linewidth=1, zorder=2))
    ax.text(42, 1.3, "Arrêt (14j)", ha='center', va='bottom', fontsize=8)

    # --- Legend ---
    ax.add_patch(patches.Rectangle((10, -0.2), 5, 0.3, facecolor='#e0e0e0', edgecolor='black'))
    ax.text(17, -0.05, "Fenêtres de début $K_i$", va='center', fontsize=10)
    ax.add_patch(patches.Rectangle((70, -0.2), 5, 0.3, facecolor='#99ff99', edgecolor='black'))
    ax.text(77, -0.05, "Maintenance choisie ($y_{it}=1$)", va='center', fontsize=10)
    ax.plot([10, 15], [-0.28, -0.28], color='blue', linewidth=2)
    ax.text(17, -0.28, "Courbe de production", va='center', fontsize=10)

    # --- Formatting ---
    ax.set_xlim(-45, x_limit + 15)
    ax.set_ylim(-0.5, 7.5)
    ax.axis('off')
    plt.title("Solution réalisable : Planning des arrêts et Courbes de Production", 
              y=0.95, fontsize=13, fontweight='bold')

    plt.savefig('output/solExample_maintenanceSchedule_production.png', bbox_inches='tight', dpi=300)
    plt.show()
    
def main():
    # flowChart_heu1()
    # flowChart_heu3()
    # draw_maintenance_schedule()
    draw_maintenance_schedule_production()

if __name__ == "__main__":
    main()