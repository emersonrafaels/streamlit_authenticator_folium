from pathlib import Path

from src.config_app.config_app import settings

import folium
from folium.plugins import MarkerCluster

from src.utils.pandas_functions import load_data
from src.utils.map.map_functions import load_map

dir_root = Path(__file__).absolute().parent.parent.parent

data = load_data(data_dir=str(Path(dir_root, settings.get("DATA_DIR_AGENCIAS"))))


def create_map():
    column_latitude = "LATITUDE"
    column_longitude = "LONGITUDE"
    map_layer_default = "cartodbpositron"
    column_status = "STATUS"
    MAP_COLUMN_TOOLTIP = "CÓDIGO AG"
    MAP_COLUMN_HEADER = "ENDEREÇO"

    # CRIANDO O MAPA
    footprint_map = folium.Map(
        location=[data[column_latitude].mean(), data[column_longitude].mean()],
        zoom_start=4,
        tiles=map_layer_default,
    )

    marker_cluster = MarkerCluster().add_to(footprint_map)

    for idx, row in data.iterrows():
        # OBTENDO O STATUS
        status = row.get(column_status)

        # OBTENDO LATTUDE E LONGITUDE
        lat = row.get(column_latitude)
        long = row.get(column_longitude)

        folium.Marker(
            location=[lat, long],
            lazy=True,
            popup=row[MAP_COLUMN_HEADER],
            tooltip=str(row[MAP_COLUMN_TOOLTIP]),
        ).add_to(marker_cluster)

    footprint_map.save("MAPA.html")


del data["STATUS"]

# PLOTANDO O MAPA
validator, mapobj, _ = load_map(
    data=data,
    map_layer_default=settings.get("MAP_LAYER_DEFAULT", "openstreetmap"),
    circle_radius=0,
    validator_add_layer=settings.get("VALIDATOR_ADD_LAYER", False),
    column_status=settings.get("COLUMN_STATUS", "STATUS"),
    save_figure=settings.get("MAP_SAVE_FIGURE", True),
    map_save_name=settings.get("MAP_SAVE_NAME", "PLOT_MAP.html"),
    dict_icons=None,
    validator_marker_cluster=settings.get("VALIDATOR_MARKER_CLUSTER", True),
    column_marker_cluster=settings.get("COLUMN_MARKER_CLUSTER", "MERCADO"),
    column_latitude=settings.get("COLUMN_LATITUDE", "LATITUDE"),
    column_longitude=settings.get("COLUMN_LONGITUDE", "LONGITUDE"),
    name_column_tooltip=settings.get("MAP_COLUMN_TOOLTIP", "CÓDIGO AG"),
    name_column_header=settings.get("MAP_COLUMN_HEADER", "ENDEREÇO"),
)
