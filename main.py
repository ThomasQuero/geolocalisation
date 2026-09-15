import pandas as pd
import folium


def main():

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


    pop = pop[["DEPCOM", "PTOT"]]

    correspondance = correspondance[
        ["Code INSEE", "Superficie"]
    ]


    data = pop.merge(
        correspondance,
        left_on="DEPCOM",
        right_on="Code INSEE",
        how="inner"
    )


    departements_idf = (
        "75", "77", "78", "91",
        "92", "93", "94", "95"
    )

    data = data[
        data["DEPCOM"].str.startswith(departements_idf)
    ]

    data["densite"] = (
        data["PTOT"] / data["Superficie"]
    )

    print(data[["DEPCOM", "PTOT", "Superficie", "densite"]].head())

    coords = (48.7453229, 2.5073644)

    carte = folium.Map(
        location=coords,
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

        legend_name="Densité de population"
    ).add_to(carte)

    print(data)
    print(data.dtypes)

    carte.save("map.html")


if __name__ == "__main__":
    main()