# Carte de densité de population en Île-de-France

## Présentation

Ce projet génère une carte choroplèthe représentant la densité de population
des communes d'Île-de-France.

Le programme utilise :

- les données de population de l'INSEE ;
- un fichier de correspondance contenant notamment la superficie des communes ;
- un fichier GeoJSON contenant les contours géographiques des communes ;
- Pandas pour manipuler et fusionner les données ;
- Folium pour générer la carte interactive.

La densité est calculée avec la formule :

densité = population / superficie


## Fonctionnement actuel

Le programme suit les étapes suivantes :

1. Lecture du fichier de population.
2. Lecture du fichier contenant les superficies.
3. Conservation des colonnes nécessaires.
4. Fusion des datasets grâce au code INSEE.
5. Filtrage des communes d'Île-de-France.
6. Calcul de la densité de population.
7. Création de la carte avec Folium.
8. Création de la couche choroplèthe.
9. Sauvegarde de la carte dans `map.html`.


## Structure attendue

Le projet doit contenir au minimum :

    projet/
    ├── main.py
    ├── insee-pop-communes.csv
    ├── correspondance-code-insee-code-postal.csv
    ├── idf.geojson
    ├── README.md
    └── map.html


## Dépendances

Le projet utilise :

    pandas
    folium

Installation :

    pip install pandas folium

Il serait préférable d'ajouter un fichier `requirements.txt` :

    pandas
    folium

Puis les dépendances pourraient être installées avec :

    pip install -r requirements.txt


# Améliorations possibles


## 1. Découper le programme en plusieurs fonctions

Actuellement, presque toute la logique se trouve dans `main()`.

Cela fonctionne pour un petit programme, mais rend le code plus difficile à
maintenir et à tester.

On pourrait créer plusieurs fonctions :

    def charger_donnees():
        ...

    def preparer_donnees(pop, correspondance):
        ...

    def calculer_densite(data):
        ...

    def creer_carte(data):
        ...

Puis conserver un `main()` très simple :

    def main():
        pop, correspondance = charger_donnees()
        data = preparer_donnees(pop, correspondance)
        data = calculer_densite(data)
        carte = creer_carte(data)
        carte.save("map.html")


## 2. Définir les chemins et paramètres dans des constantes

Les noms des fichiers sont actuellement écrits directement dans le code.

Par exemple :

    "insee-pop-communes.csv"
    "correspondance-code-insee-code-postal.csv"
    "idf.geojson"
    "map.html"

Ils pourraient être regroupés au début du programme :

    FICHIER_POPULATION = "insee-pop-communes.csv"
    FICHIER_SUPERFICIE = "correspondance-code-insee-code-postal.csv"
    FICHIER_GEOJSON = "idf.geojson"
    FICHIER_SORTIE = "map.html"

Même chose pour les départements :

    DEPARTEMENTS_IDF = (
        "75", "77", "78", "91",
        "92", "93", "94", "95"
    )

Cela facilite les modifications futures.


## 3. Vérifier les données avant le calcul

Le programme suppose actuellement que toutes les valeurs de population et de
superficie sont correctes.

Il faudrait vérifier :

- les valeurs manquantes ;
- les superficies nulles ;
- les superficies négatives ;
- les populations manquantes ;
- les doublons de codes INSEE.

Par exemple :

    print(data.isna().sum())

On peut supprimer les données inutilisables :

    data = data.dropna(
        subset=["PTOT", "Superficie"]
    )

Et éviter une division par zéro :

    data = data[data["Superficie"] > 0]


## 4. Vérifier l'unité de la superficie

Avant de calculer :

    data["densite"] = data["PTOT"] / data["Superficie"]

il faut vérifier l'unité de la colonne `Superficie`.

La densité est généralement exprimée en habitants par km².

Si `Superficie` n'est pas exprimée en km², une conversion doit être effectuée
avant le calcul.


## 5. Vérifier la qualité de la fusion

La fusion est actuellement :

    data = pop.merge(
        correspondance,
        left_on="DEPCOM",
        right_on="Code INSEE",
        how="inner"
    )

Une jointure `inner` supprime automatiquement les communes qui ne trouvent pas
de correspondance.

Cela peut cacher des problèmes dans les données.

Pour analyser la qualité de la fusion, on pourrait temporairement utiliser :

    data = pop.merge(
        correspondance,
        left_on="DEPCOM",
        right_on="Code INSEE",
        how="left",
        indicator=True
    )

Puis :

    print(data["_merge"].value_counts())

Cela permet de repérer les communes qui n'ont pas de superficie associée.


## 6. Gérer les doublons

Le dataset de correspondance peut éventuellement contenir plusieurs lignes
pour un même code INSEE.

Avant le `merge`, il serait intéressant de vérifier :

    print(
        correspondance[
            correspondance["Code INSEE"].duplicated(keep=False)
        ]
    )

Si les doublons représentent plusieurs codes postaux pour une même commune,
une stratégie doit être choisie afin de ne pas dupliquer artificiellement les
données après la fusion.


## 7. Gérer correctement le cas de Paris

Les données géographiques et les données de population ne représentent pas
nécessairement Paris de la même manière.

Le fichier de population peut contenir les arrondissements séparément alors
que le GeoJSON peut contenir Paris comme une seule commune.

Il faut donc vérifier les codes INSEE concernés et éventuellement agréger la
population des arrondissements avant de construire la carte.

Ce problème peut sinon provoquer une zone sans données sur la carte.


## 8. Ajouter un fond de carte

Le programme utilise actuellement :

    tiles=None

Cela évite les problèmes d'accès aux serveurs de tuiles OpenStreetMap mais
produit une carte sans fond.

Un fournisseur compatible avec Folium pourrait éventuellement être utilisé,
par exemple :

    carte = folium.Map(
        location=coords,
        tiles="CartoDB positron",
        zoom_start=9
    )

Il faut néanmoins vérifier les conditions d'utilisation du fournisseur choisi.


## 9. Ajouter des informations au survol

La carte pourrait devenir plus interactive en affichant :

- le nom de la commune ;
- la population ;
- la superficie ;
- la densité.

Une couche `folium.GeoJson` avec `GeoJsonTooltip` pourrait être ajoutée.

L'utilisateur pourrait alors survoler une commune pour obtenir ses
informations.


## 10. Améliorer la légende

La légende actuelle indique :

    "Densité de population"

Elle pourrait préciser l'unité :

    "Densité de population (habitants/km²)"

Cela permet de comprendre immédiatement ce que représentent les couleurs.


## 11. Adapter l'échelle des couleurs

Les densités de population peuvent varier énormément entre les communes
rurales et très urbanisées.

Une échelle linéaire peut donc rendre la majorité des communes presque de la
même couleur.

Il serait intéressant de tester :

- des classes de densité ;
- des quantiles ;
- une échelle logarithmique ;
- différents seuils de couleur.

Cela permettrait de rendre les différences entre communes plus visibles.


## 12. Supprimer les `print()` de debug

Les lignes :

    print(data)
    print(data.dtypes)

sont utiles pendant le développement mais ne sont plus forcément nécessaires
dans la version finale.

Elles pourraient être supprimées ou remplacées par un système de logs.


## 13. Ajouter une gestion des erreurs

Le programme échoue directement si un fichier est absent.

On pourrait gérer cette situation :

    try:
        pop = pd.read_csv(...)
    except FileNotFoundError:
        print("Erreur : fichier de population introuvable.")
        return

Il faudrait également gérer :

- les colonnes absentes ;
- les fichiers CSV invalides ;
- le GeoJSON absent ;
- les valeurs numériques incorrectes.


## 14. Utiliser `pathlib`

Au lieu d'utiliser uniquement des chaînes de caractères pour les chemins,
`pathlib` permet une gestion plus robuste :

    from pathlib import Path

    DATA_DIR = Path("data")

    POPULATION_FILE = DATA_DIR / "insee-pop-communes.csv"

Cela permet également d'organiser le projet :

    projet/
    ├── main.py
    ├── README.md
    ├── requirements.txt
    ├── data/
    │   ├── insee-pop-communes.csv
    │   ├── correspondance-code-insee-code-postal.csv
    │   └── idf.geojson
    └── output/
        └── map.html


## 15. Ajouter des docstrings

Les futures fonctions devraient être documentées.

Exemple :

    def calculer_densite(data):
        """
        Calcule la densité de population de chaque commune.

        La densité est calculée en divisant la population totale
        par la superficie de la commune.

        Parameters
        ----------
        data : pandas.DataFrame
            Données contenant PTOT et Superficie.

        Returns
        -------
        pandas.DataFrame
            DataFrame contenant une colonne densite.
        """
        data["densite"] = data["PTOT"] / data["Superficie"]
        return data


## 16. Respecter davantage le principe de séparation des responsabilités

Le programme réalise actuellement trois tâches différentes :

- chargement des données ;
- traitement statistique ;
- affichage cartographique.

Ces trois parties pourraient être séparées.

Cela permettrait par exemple de modifier la carte sans toucher au calcul de
densité.


## 17. Ajouter des tests

Des tests simples pourraient vérifier le calcul de densité.

Par exemple, pour une commune fictive :

    population = 10000
    superficie = 20

La densité attendue est :

    500 habitants/km²

Des tests pourraient également vérifier :

- le filtrage de l'Île-de-France ;
- l'absence de division par zéro ;
- les codes INSEE ;
- les données manquantes.


# Exemple d'architecture améliorée

Une version plus structurée pourrait suivre cette organisation :

    import pandas as pd
    import folium


    DEPARTEMENTS_IDF = (
        "75", "77", "78", "91",
        "92", "93", "94", "95"
    )


    def charger_donnees():
        pop = pd.read_csv(
            "insee-pop-communes.csv",
            sep=";",
            dtype={"DEPCOM": str}
        )

        superficie = pd.read_csv(
            "correspondance-code-insee-code-postal.csv",
            sep=";",
            dtype={"Code INSEE": str}
        )

        return pop, superficie


    def preparer_donnees(pop, superficie):

        pop = pop[["DEPCOM", "PTOT"]]

        superficie = superficie[
            ["Code INSEE", "Superficie"]
        ]

        data = pop.merge(
            superficie,
            left_on="DEPCOM",
            right_on="Code INSEE",
            how="inner"
        )

        data = data[
            data["DEPCOM"].str.startswith(DEPARTEMENTS_IDF)
        ].copy()

        data = data.dropna(
            subset=["PTOT", "Superficie"]
        )

        data = data[
            data["Superficie"] > 0
        ]

        data["densite"] = (
            data["PTOT"] / data["Superficie"]
        )

        return data


    def creer_carte(data):

        carte = folium.Map(
            location=(48.7453229, 2.5073644),
            tiles=None,
            zoom_start=9
        )

        folium.Choropleth(
            geo_data="idf.geojson",
            data=data,
            columns=["DEPCOM", "densite"],
            key_on="feature.properties.code_commune",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Densité de population (habitants/km²)"
        ).add_to(carte)

        return carte


    def main():

        pop, superficie = charger_donnees()

        data = preparer_donnees(
            pop,
            superficie
        )

        carte = creer_carte(data)

        carte.save("map.html")


    if __name__ == "__main__":
        main()


# Améliorations prioritaires

Pour une prochaine version, les améliorations les plus importantes sont :

1. Vérifier l'unité de `Superficie`.
2. Vérifier les doublons dans le fichier de correspondance.
3. Vérifier les communes perdues pendant le `merge`.
4. Gérer le cas particulier de Paris.
5. Découper `main()` en plusieurs fonctions.
6. Ajouter des informations interactives sur les communes.
7. Améliorer la représentation des fortes différences de densité.
8. Ajouter une gestion des erreurs et des tests.


## Résultat attendu

L'exécution :

    python main.py

doit générer :

    map.html

Ce fichier peut ensuite être ouvert dans un navigateur pour consulter la carte
choroplèthe de la densité de population des communes d'Île-de-France.