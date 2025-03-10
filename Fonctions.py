import sys
from collections import defaultdict, deque


def lire_table(nom_fichier):
    """
    Lit le fichier texte dont chaque ligne est de la forme :
      numéro_tâche durée [prédécesseur1 prédécesseur2 ...]
    Par exemple, la ligne "5 9 4 6 8" signifie que la tâche 5 (de durée 9)
    a pour prédécesseurs les tâches 4, 6 et 8.
    Retourne :
      - tasks : dictionnaire associant chaque tâche à sa durée
      - pred_for_task : dictionnaire associant chaque tâche à la liste de ses prédécesseurs
      - all_pred : ensemble de toutes les tâches qui interviennent comme prédécesseur
      - N : numéro maximum de tâche
    """
    tasks = {}
    pred_for_task = {}
    all_pred = set()
    N = 0
    with open(nom_fichier, "r") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne.startswith('#'):
                continue
            parts = ligne.split()
            if len(parts) < 2:
                print("Format invalide dans la ligne :", ligne)
                continue
            task_id = int(parts[0])
            duration = float(parts[1])
            tasks[task_id] = duration
            N = max(N, task_id)
            if len(parts) > 2:
                preds = list(map(int, parts[2:]))
                pred_for_task[task_id] = preds
                for p in preds:
                    all_pred.add(p)
                    N = max(N, p)
            else:
                pred_for_task[task_id] = []
    return tasks, pred_for_task, all_pred, N


def construire_arcs(tasks, pred_for_task):
    """
    Construit la liste des arcs à partir des contraintes.
    Pour chaque tâche i possédant des prédécesseurs, on crée un arc de chaque prédécesseur p vers i,
    avec pour poids la durée de p.
    Retourne la liste d'arcs sous la forme (p, i, durée(p)).
    """
    arcs = []
    for i, preds in pred_for_task.items():
        if preds:
            for p in preds:
                if p in tasks:
                    arcs.append((p, i, tasks[p]))
                else:
                    print(f"Attention : la tâche prédécesseur {p} n'est pas définie pour la tâche {i}.")
    return arcs


def construire_matrice(arcs, tasks, pred_for_task, all_pred, N):
    """
    Construit la matrice d'adjacence du graphe, en intégrant deux nœuds fictifs :
      - 0 pour le début,
      - N+1 pour la fin.
    La matrice est de taille (N+2)x(N+2) et est initialisée avec None pour indiquer l'absence d'arc,
    et 0 sur la diagonale.
    Les arcs sont ajoutés ainsi :
      - Pour chaque arc (p, i, w) issu des contraintes, M[p][i] = w.
      - Pour toute tâche sans prédécesseurs (liste vide dans pred_for_task), on ajoute un arc de 0 vers i de durée 0.
      - Pour toute tâche qui n'est jamais utilisée comme prédécesseur (donc sans successeur), on ajoute un arc de i vers N+1 avec un poids égal à sa durée.
    """
    taille = N + 2  # indices de 0 à N+1
    M = [[None for _ in range(taille)] for _ in range(taille)]
    for i in range(taille):
        M[i][i] = 0

    # Ajout des arcs définis par les contraintes
    succ_count = defaultdict(int)
    for (p, i, w) in arcs:
        M[p][i] = w
        succ_count[p] += 1

    # Ajout de l'arc fictif de départ : pour chaque tâche sans prédécesseurs, ajouter (0, i) de durée 0
    for i in range(1, N + 1):
        if i not in pred_for_task or (pred_for_task[i] == []):
            M[0][i] = 0

    # Ajout de l'arc fictif de fin : pour chaque tâche qui n'est pas utilisée comme prédécesseur, ajouter (i, N+1) avec poids = durée de la tâche
    for i in range(1, N + 1):
        if i not in all_pred:
            M[i][N + 1] = tasks[i]

    return M


def afficher_matrice(M):
    """
    Affiche la matrice d'adjacence.
    """
    print("Matrice d'adjacence (None indique l'absence d'arc) :")
    for ligne in M:
        print(["{:.1f}".format(x) if x is not None else "None" for x in ligne])


def detection_circuit(M):
    """
    Vérifie l'absence de circuit dans le graphe en effectuant un tri topologique.
    Retourne un tuple (est_acyclique, ordre_topologique).
    """
    taille = len(M)
    deg_ent = [0] * taille
    for i in range(taille):
        for j in range(taille):
            if M[i][j] is not None and i != j:
                deg_ent[j] += 1

    file = deque([i for i in range(taille) if deg_ent[i] == 0])
    ordre = []
    while file:
        u = file.popleft()
        ordre.append(u)
        for v in range(taille):
            if M[u][v] is not None and u != v:
                deg_ent[v] -= 1
                if deg_ent[v] == 0:
                    file.append(v)
    return (len(ordre) == taille), ordre


def verification_arcs_positifs(M):
    """
    Vérifie que tous les arcs présents dans le graphe ont une valeur non négative.
    """
    taille = len(M)
    for i in range(taille):
        for j in range(taille):
            if M[i][j] is not None and M[i][j] < 0:
                return False
    return True


def calcul_calendriers(M, topo):
    """
    Calcule le calendrier au plus tôt (dates_min), le calendrier au plus tard (dates_max)
    et les marges (dates_max - dates_min).
    La date au plus tard du nœud final (N+1) est fixée égale à sa date au plus tôt.
    """
    taille = len(M)
    dates_min = [-float('inf')] * taille
    dates_min[0] = 0
    for u in topo:
        for v in range(taille):
            if M[u][v] is not None:
                dates_min[v] = max(dates_min[v], dates_min[u] + M[u][v])

    dates_max = [float('inf')] * taille
    dates_max[-1] = dates_min[-1]
    for u in reversed(topo):
        for v in range(taille):
            if M[u][v] is not None:
                dates_max[u] = min(dates_max[u], dates_max[v] - M[u][v])
    marges = [dates_max[i] - dates_min[i] for i in range(taille)]
    return dates_min, dates_max, marges


def trouver_chemins_critiques(M, dates_min, dates_max, chemin_actuel=[], noeud=0):
    """
    Recherche récursive des chemins critiques dans le graphe.
    Un chemin critique est une suite de nœuds dont la marge est nulle.
    """
    chemin_actuel = chemin_actuel + [noeud]
    if noeud == len(M) - 1:
        return [chemin_actuel]
    chemins = []
    for v in range(len(M)):
        if M[noeud][v] is not None:
            if dates_min[noeud] + M[noeud][v] == dates_min[v] and (dates_max[v] - dates_min[v] == 0):
                chemins.extend(trouver_chemins_critiques(M, dates_min, dates_max, chemin_actuel, v))
    return chemins


def main():
    # Nom du fichier contenant la table (assurez-vous que le fichier est dans le même répertoire ou indiquez le chemin complet)
    nom_fichier = "table "+ input("Choisissez le nombre du fichier désiré : ") + ".txt"
    try:
        tasks, pred_for_task, all_pred, N = lire_table(nom_fichier)
    except Exception as e:
        print("Erreur lors de la lecture du fichier :", e)
        sys.exit(1)

    arcs = construire_arcs(tasks, pred_for_task)
    # Construction de la matrice d'adjacence avec les nœuds fictifs 0 et N+1
    M = construire_matrice(arcs, tasks, pred_for_task, all_pred, N)
    afficher_matrice(M)

    # Vérification des propriétés nécessaires du graphe
    acyclique, topo = detection_circuit(M)
    if not acyclique:
        print("Erreur : le graphe contient un circuit.")
        sys.exit(1)
    if not verification_arcs_positifs(M):
        print("Erreur : le graphe contient des arcs avec des valeurs négatives.")
        sys.exit(1)
    print("Le graphe est acyclique et tous les arcs ont des valeurs non négatives.")

    # Calcul des calendriers
    dates_min, dates_max, marges = calcul_calendriers(M, topo)
    print("\nCalendrier au plus tôt (dates_min) :")
    for i, d in enumerate(dates_min):
        print(f"Nœud {i} : {d}")

    print("\nCalendrier au plus tard (dates_max) :")
    for i, d in enumerate(dates_max):
        print(f"Nœud {i} : {d}")

    print("\nMarges :")
    for i, m in enumerate(marges):
        print(f"Nœud {i} : {m}")

    # Recherche et affichage des chemins critiques
    chemins_critiques = trouver_chemins_critiques(M, dates_min, dates_max)
    print("\nChemin(s) critique(s) :")
    for chemin in chemins_critiques:
        print(" -> ".join(map(str, chemin)))


if __name__ == "__main__":
    main()
