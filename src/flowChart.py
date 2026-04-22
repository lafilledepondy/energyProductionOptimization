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

    output_path = g.render('output/heuristic_1_flowchart', view=True)

def main():
    flowChart_heu1()

if __name__ == "__main__":
    main()