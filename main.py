import pandas as pd
import folium


def main():

    # -------------------------
    # 1. Lecture des données
    # -------------------------

    pop = pd.read_csv(
        "insee-pop-communes.csv",
        sep=";",
        dtype={"DEPCOM": str}
    )

    correspondance = pd.read_csv(
        "correspondance-code-insee-code-postal.csv",
        sep=";",
        dtype={"Code INSEE": str}
    )


    # -------------------------
    # 2. Garder les données utiles
    # -------------------------

    pop = pop[["DEPCOM", "PTOT"]]

    correspondance = correspondance[
        ["Code INSEE", "Superficie"]
    ]


    # -------------------------
    # 3. Fusion des deux datasets
    # -------------------------

    data = pop.merge(
        correspondance,
        left_on="DEPCOM",
        right_on="Code INSEE",
        how="inner"
    )


    # -------------------------
    # 4. Garder uniquement l'Île-de-France
    # -------------------------

    departements_idf = (
        "75", "77", "78", "91",
        "92", "93", "94", "95"
    )

    data = data[
        data["DEPCOM"].str.startswith(departements_idf)
    ]


    # -------------------------
    # 5. Calcul de la densité
    # -------------------------

    data["densite"] = (
        data["PTOT"] / data["Superficie"]
    )

    print(data[["DEPCOM", "PTOT", "Superficie", "densite"]].head())


    # -------------------------
    # 6. Création de la carte
    # -------------------------

    coords = (48.7453229, 2.5073644)

    carte = folium.Map(
        location=coords,
        tiles=None,
        zoom_start=9
    )


    # -------------------------
    # 7. Choroplèthe
    # -------------------------

    folium.Choropleth(
        geo_data="idf.geojson",
        data=data,

        # DEPCOM = clé
        # densite = valeur à représenter
        columns=["DEPCOM", "densite"],

        # Correspondance avec idf.geojson
        key_on="feature.properties.code_commune",

        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,

        legend_name="Densité de population"
    ).add_to(carte)


    # -------------------------
    # 8. Sauvegarde
    # -------------------------

    carte.save("map.html")


if __name__ == "__main__":
    main()