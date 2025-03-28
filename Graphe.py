
def LectureTable(fichier):
    taches = {}
    predecesseurs = {}
    try:
        with (open(fichier, 'r') as f):
            for line in f:
                line = line.strip()
                if line == '' :
                    continue
                partie = line.split()
                if len(partie) < 2: #là ça vérifie qu'il y ait au moins la tache et la duree dans chaque lignes
                    print('format invalide dans la ligne',line)
                    continue
                tache = int(partie[0])
                duree = float(partie[1])
                taches[tache] = duree
                if len(partie) > 2: #là ça veut dire qu'il y aura peut-être des predecesseurs
                    preds = list(map(int, partie[2:]))
                else:
                    preds=[]
                predecesseurs[tache]=preds
    except FileNotFoundError:
        print('Le fichier est introuvable ou inexistant')
    return taches, predecesseurs


def TableauContrainte (taches, predecesseurs):
    print("  Tableau De Contrainte  ")
    for taches in sorted(taches.keys()):
        duration = taches[taches]
        preds = predecesseurs.get[taches, []]
        print(f"Tâche {taches} : durée = {duration}, prédécesseurs = {preds}")

def ConstruireArc(taches, predecesseurs):
    arcs=[]
    for i, preds in predecesseurs.items():
        for p in preds:
            if p in taches:
                arcs.append(p,i,taches[p])
            else:
                print(f"le prédécesseur de {p} et de la tâche {i} , n'existent pas ")
            return arcs

def GrapheEnMatrice():



def DetectionCircuit(Matrice):


def main():
