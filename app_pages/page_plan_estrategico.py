from pathlib import Path

import pandas as pd
import streamlit as st
from dynaconf import settings
from streamlit_folium import st_folium

from utils.pandas_functions import load_data, convert_dataframe_to_aggrid
from utils.map.map_functions import load_map

dir_root = Path(__file__).absolute().parent.parent


def load_page_plan_estrategico():
    # CARREGANDO DATAFRAME
    df_planejamento = load_data(
        data_dir=str(Path(dir_root, settings.get("DATA_DIR_AGENCIAS")))
    )

    # INCLUINDO O DATAFRAME EM TELA
    # NO MAIN
    st.markdown("# APP - PLANEJAMENTO ESTRATÉGICO")

    # CRIANDO UMA LINHA EM BRANCO
    # st.divider()

    # OBTENDO O DATAFRAME
    dataframe_aggrid = convert_dataframe_to_aggrid(data=df_planejamento)

    # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
    selected_df = pd.DataFrame(dataframe_aggrid["selected_rows"])

    # PLOTANDO O MAPA
    validator, map = load_map(
        data=df_planejamento,
        map_layer_default="openstreetmap",
        circle_radius=0,
        validator_add_layer=False,
        column_status=settings.get("COLUMN_STATUS", "STATUS"),
        save_figure=settings.get("MAP_SAVE_FIGURE", True),
        map_save_name=settings.get("MAP_SAVE_NAME", "PLOT_MAP.html"),
        dict_icons=None,
        column_latitude=settings.get("COLUMN_LATITUDE", "LATITUDE"),
        column_longitude=settings.get("COLUMN_LONGITUDE", "LONGITUDE"),
        name_column_tooltip=settings.get("MAP_COLUMN_TOOLTIP", "CÓDIGO AG"),
        name_column_header=settings.get("MAP_COLUMN_HEADER", "ENDEREÇO"),
    )


if __name__ == "__main__":
    load_page_plan_estrategico()
