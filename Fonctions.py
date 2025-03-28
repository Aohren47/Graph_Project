import sys
from collections import defaultdict, deque


def lire_table(nom_fichier):
    """
    Lit le fichier de contraintes.
    Chaque ligne doit être de la forme :
       numéro_tâche durée [prédécesseur1 prédécesseur2 ...]
    Retourne :
       tasks : dictionnaire {numéro_tâche: durée}
       pred_for_task : dictionnaire {numéro_tâche: liste des prédécesseurs}
    """
    tasks = {}
    pred_for_task = {}
    try:
        with open(nom_fichier, 'r') as f:
            for ligne in f:
                ligne = ligne.strip()
                if ligne == '' or ligne.startswith('#'):
                    continue
                parts = ligne.split()
                if len(parts) < 2:
                    print("Format invalide dans la ligne :", ligne)
                    continue
                task = int(parts[0])
                duration = float(parts[1])
                tasks[task] = duration
                if len(parts) > 2:
                    preds = list(map(int, parts[2:]))
                else:
                    preds = []
                pred_for_task[task] = preds
    except Exception as e:
        raise Exception(f"Erreur de lecture : {e}")
    return tasks, pred_for_task


def afficher_table_contraintes(tasks, pred_for_task):
    print("\n--- Tableau de contraintes ---")
    for task in sorted(tasks.keys()):
        duration = tasks[task]
        preds = pred_for_task.get(task, [])
        print(f"Tâche {task} : durée = {duration}, prédécesseurs = {preds}")


def construire_arcs(tasks, pred_for_task):
    """
    Construit la liste des arcs issus des contraintes.
    Pour chaque tâche i avec un prédécesseur p, crée l'arc (p, i) de poids = durée de p.
    """
    arcs = []
    for i, preds in pred_for_task.items():
        for p in preds:
            if p in tasks:
                arcs.append((p, i, tasks[p]))
            else:
                print(f"Attention : le prédécesseur {p} de la tâche {i} n'est pas défini.")
    return arcs


def construire_graphe(tasks, pred_for_task, arcs):
    """
    Construit la matrice d’adjacence du graphe d’ordonnancement.
    On ajoute les deux nœuds fictifs : 0 (début) et N+1 (fin), où N est le maximum des tâches.
    Pour chaque arc (p, i) issu des contraintes, la matrice M[p][i] prend la valeur = durée de p.
    Pour chaque tâche sans prédécesseur, on ajoute un arc de 0 vers la tâche de poids 0.
    Pour chaque tâche qui n'est jamais utilisée comme prédécesseur, on ajoute un arc vers N+1 de poids = durée de la tâche.
    """
    N = max(tasks.keys())
    nb_sommets = N + 2  # de 0 à N+1
    # Initialisation de la matrice avec None (absence d'arc) et 0 sur la diagonale
    M = [[None for _ in range(nb_sommets)] for _ in range(nb_sommets)]
    for i in range(nb_sommets):
        M[i][i] = 0

    # Ajout des arcs définis par les contraintes
    for (p, i, w) in arcs:
        M[p][i] = w

    # Ajout de l'arc fictif de départ : pour chaque tâche sans prédécesseur, ajouter (0, i) de durée 0
    for i in range(1, N + 1):
        if not pred_for_task.get(i):  # liste vide ou inexistante
            M[0][i] = 0

    # Ajout de l'arc fictif de fin : pour chaque tâche qui n'est pas utilisée comme prédécesseur
    all_predecesseurs = set()
    for preds in pred_for_task.values():
        all_predecesseurs.update(preds)
    for i in range(1, N + 1):
        if i not in all_predecesseurs:
            M[i][N + 1] = tasks[i]

    return M


def afficher_graphe_arcs(M):
    print("\n--- Création du graphe d'ordonnancement ---")
    nb_sommets = len(M)
    nb_arcs = 0
    for i in range(nb_sommets):
        for j in range(nb_sommets):
            if i != j and M[i][j] is not None:
                nb_arcs += 1
    print(f"{nb_sommets} sommets")
    print(f"{nb_arcs} arcs")
    for i in range(nb_sommets):
        for j in range(nb_sommets):
            if i != j and M[i][j] is not None:
                print(f"{i} -> {j} = {M[i][j]}")


def afficher_matrice(M):
    nb_sommets = len(M)
    header = "      " + " ".join([f"{j:>8}" for j in range(nb_sommets)])
    print("\n--- Matrice des valeurs ---")
    print(header)
    for i in range(nb_sommets):
        ligne = f"{i:>4}  " + " ".join([f"{('*' if val is None else f'{val:.1f}'):>8}" for val in M[i]])
        print(ligne)


def detection_circuit(M):
    """
    Vérifie l'absence de circuit avec l'algorithme de Kahn.
    Affiche les étapes (points d'entrée et sommets restants) et retourne :
       (True, ordre_topologique) si le graphe est acyclique,
       (False, ordre_topologique_partiel) sinon.
    """
    nb_sommets = len(M)
    indegree = [0] * nb_sommets
    for i in range(nb_sommets):
        for j in range(nb_sommets):
            if M[i][j] is not None and i != j:
                indegree[j] += 1

    print("\n--- Détection de circuit ---")
    entree = [i for i in range(nb_sommets) if indegree[i] == 0]
    print("Points d'entrée initiaux :", entree)

    queue = deque(entree)
    topo_order = []
    iteration = 1
    while queue:
        print(f"Iteration {iteration} - Points d'entrée :", list(queue))
        u = queue.popleft()
        topo_order.append(u)
        for v in range(nb_sommets):
            if M[u][v] is not None and u != v:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)
        remaining = [i for i in range(nb_sommets) if indegree[i] > 0]
        print("Sommets restants :", remaining if remaining else "Aucun")
        iteration += 1

    if len(topo_order) == nb_sommets:
        print("-> Il n'y a pas de circuit")
        return True, topo_order
    else:
        print("-> Il y a un circuit")
        return False, topo_order


def verification_arcs_positifs(M):
    nb_sommets = len(M)
    for i in range(nb_sommets):
        for j in range(nb_sommets):
            if M[i][j] is not None and M[i][j] < 0:
                return False
    return True


def calcul_calendriers(M, topo):
    """
    Calcule :
      - Le calendrier au plus tôt (dates_min)
      - Le calendrier au plus tard (dates_max)
      - Les marges (dates_max - dates_min)
    Pour le calcul du calendrier au plus tard, on fixe la date au plus tard du nœud final égale à sa date au plus tôt.
    """
    nb_sommets = len(M)
    # Calendrier au plus tôt
    dates_min = [-float('inf')] * nb_sommets
    dates_min[0] = 0
    for u in topo:
        for v in range(nb_sommets):
            if M[u][v] is not None:
                dates_min[v] = max(dates_min[v], dates_min[u] + M[u][v])

    # Calendrier au plus tard (nœud final = dernière case)
    dates_max = [float('inf')] * nb_sommets
    dates_max[-1] = dates_min[-1]
    for u in reversed(topo):
        for v in range(nb_sommets):
            if M[u][v] is not None:
                dates_max[u] = min(dates_max[u], dates_max[v] - M[u][v])

    marges = [dates_max[i] - dates_min[i] for i in range(nb_sommets)]
    return dates_min, dates_max, marges


def afficher_calendriers(dates_min, dates_max, marges):
    print("\n--- Calendriers ---")
    print("Calendrier au plus tôt (dates_min) :")
    for i, d in enumerate(dates_min):
        print(f"  Nœud {i} : {d}")
    print("\nCalendrier au plus tard (dates_max) :")
    for i, d in enumerate(dates_max):
        print(f"  Nœud {i} : {d}")
    print("\nMarges :")
    for i, m in enumerate(marges):
        print(f"  Nœud {i} : {m}")


def trouver_chemins_critiques(M, dates_min, dates_max, chemin_actuel=[], noeud=0):
    chemin_actuel = chemin_actuel + [noeud]

    if noeud == len(M) - 1:
        return [chemin_actuel]

    chemins = []
    for v in range(len(M)):
        if M[noeud][v] is not None:
            if (abs(dates_min[noeud] + M[noeud][v] - dates_min[v]) < 1e-6 and
                    abs(dates_max[v] - dates_min[v]) < 1e-6 and
                    v not in chemin_actuel):  # empêche les boucles infinies
                chemins.extend(trouver_chemins_critiques(M, dates_min, dates_max, chemin_actuel, v))
    return chemins


def main():
    while True:
        print("\n=== Ordonnancement ===")
        nom_fichier = input("Entrez le nom du fichier de contraintes (ex: contraintes.txt) : ").strip()
        try:
            tasks, pred_for_task = lire_table(nom_fichier)
        except Exception as e:
            print("Erreur lors de la lecture du fichier :", e)
            continue

        # 1. Affichage du tableau de contraintes
        afficher_table_contraintes(tasks, pred_for_task)

        # 2. Construction du graphe correspondant
        arcs = construire_arcs(tasks, pred_for_task)
        M = construire_graphe(tasks, pred_for_task, arcs)
        afficher_graphe_arcs(M)
        afficher_matrice(M)

        # 3. Vérification des propriétés nécessaires du graphe
        acyclique, topo = detection_circuit(M)
        if not acyclique:
            print("Le graphe contient un circuit. Veuillez choisir un autre tableau de contraintes.")
            if input("Voulez-vous tester un autre tableau ? (o/n) : ").lower() != 'o':
                break
            else:
                continue

        if not verification_arcs_positifs(M):
            print("Le graphe contient des arcs à valeur négative. Veuillez choisir un autre tableau de contraintes.")
            if input("Voulez-vous tester un autre tableau ? (o/n) : ").lower() != 'o':
                break
            else:
                continue

        print("\n-> Le graphe est un graphe d'ordonnancement valide.")

        # 4. Calcul des rangs (ordre topologique déjà obtenu via detection_circuit)
        print("\nOrdre topologique (rangs des sommets) :", topo)

        # 5. Calcul des calendriers et des marges
        dates_min, dates_max, marges = calcul_calendriers(M, topo)
        afficher_calendriers(dates_min, dates_max, marges)

        # 6. Calcul du(s) chemin(s) critique(s)
        chemins_critiques = trouver_chemins_critiques(M, dates_min, dates_max)
        print("\n--- Chemin(s) critique(s) ---")
        for chemin in chemins_critiques:
            print(" -> ".join(map(str, chemin)))

        # Durée totale du projet : date au plus tôt du nœud final
        print("\nDurée totale du projet :", dates_min[-1])

        # Proposition de tester un autre tableau de contraintes
        if input("\nVoulez-vous tester un autre tableau de contraintes ? (o/n) : ").lower() != 'o':
            print("Fin du programme.")
            break


if __name__ == "__main__":
    main()
