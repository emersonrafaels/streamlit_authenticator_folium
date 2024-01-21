from pathlib import Path
from inspect import stack

import folium
import pandas as pd
import streamlit as st
from loguru import logger
from streamlit_folium import st_folium

from utils.pandas_functions import (
    load_data,
    compare_dataframes,
)
from utils.map.map_functions import load_map
from utils.map.map_functions import folium_static
from utils.dataframe_explorer import dataframe_explorer
from config_app.config_app import settings

dir_root = Path(__file__).absolute().parent


def load_page_plan_estrategico():
    """

    DATAFRAME ORIGINAL - st.session_state["df_planejamento"] = df_planejamento
    DATAFRAME SELECIONADO - st.session_state["selected_df"]

    """

    # INICIANDO UM VALIDADOR DO RERUN AUTOMÁTICO
    validator_rerun = True

    if "df_planejamento" not in st.session_state.keys():
        # CARREGANDO DATAFRAME
        df_planejamento = load_data(
            data_dir=str(Path(dir_root, settings.get("DATA_DIR_AGENCIAS")))
        )

        logger.info("DADOS OBTIDOS COM SUCESSO")

        df_planejamento_formatted = df_planejamento.get("DATAFRAME_RESULT")
        df_planejamento_formatted.columns = df_planejamento_formatted.iloc[0]
        df_planejamento_formatted = df_planejamento_formatted.iloc[1:]

        st.session_state["df_planejamento"] = df_planejamento_formatted

    else:
        logger.info(
            "df_planejamento - DADOS RECUPERADOS DO SESSION STATE COM SUCESSO - {} AGÊNCIAS".format(
                len(st.session_state["df_planejamento"])
            )
        )
        df_planejamento = st.session_state["df_planejamento"]

    if "selected_df" not in st.session_state.keys():
        # CARREGANDO DATAFRAME
        st.session_state["selected_df"] = st.session_state["df_planejamento"]

    else:
        logger.info(
            "selected_df - DADOS RECUPERADOS DO SESSION STATE COM SUCESSO - {} AGÊNCIAS".format(
                len(st.session_state["selected_df"])
            )
        )

    # NO MAIN
    st.markdown("# APP - PLANEJAMENTO ESTRATÉGICO")

    # PLOTANDO O DATAFRAME EM TELA
    selected_df = st.data_editor(
        dataframe_explorer(st.session_state["df_planejamento"]),
        use_container_width=True)

    # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
    st.session_state["selected_df"] = selected_df

    st.multiselect(label="Qualquer", options=["a", "b"])

    with st.container():

        if (not compare_dataframes(
            df1=st.session_state.get("selected_df"), df2=st.session_state.get("current_map_df", pd.DataFrame())
        )) or ("current_map_df" not in st.session_state.keys()):

            # REALIZAR NOVO REFRESH NA PÁGINA
            logger.info("OS DATAFRAMES NÃO SÃO IGUAIS")
            # st.experimental_rerun()

            # OBTENDO O MAPA
            (
                validator,
                st.session_state["mapobj"],
                st.session_state["current_map_df"],
            ) = load_map(
                data=st.session_state["selected_df"],
                map_layer_default=settings.get("MAP_LAYER_DEFAULT",
                                               "openstreetmap"),
                circle_radius=0,
                validator_add_layer=settings.get("VALIDATOR_ADD_LAYER", False),
                column_status=settings.get("COLUMN_STATUS", "STATUS"),
                save_figure=False,
                map_save_name=settings.get("MAP_SAVE_NAME", "PLOT_MAP.html"),
                dict_icons=settings.get("MAP_DICT_ICON_DEFAULT", {}),
                validator_marker_cluster=settings.get("VALIDATOR_MARKER_CLUSTER",
                                                      True),
                column_marker_cluster=settings.get("COLUMN_MARKER_CLUSTER",
                                                   "MERCADO"),
                column_latitude=settings.get("COLUMN_LATITUDE", "LATITUDE"),
                column_longitude=settings.get("COLUMN_LONGITUDE", "LONGITUDE"),
                name_column_tooltip=settings.get("MAP_COLUMN_TOOLTIP", "CÓDIGO AG"),
                name_column_header=settings.get("MAP_COLUMN_HEADER", "ENDEREÇO"),
            )

            logger.info("MAPA CONSTRUIDO COM SUCESSO - LOAD MAP")

            with st.spinner('Mapa sendo atualizado'):

                # INCLUINDO O MAPA NO APP
                st.session_state["folium_map_render"] = folium_static(
                    st.session_state["mapobj"],
                    width=700,
                    height=500,
                    add_categorical_legend=True,
                    title_legend="Legenda",
                    list_categories=["Ag Black", "Ag Blue"],
                    list_colors=["#ffffff", "#3391FF"],
                )

        else:
            logger.info("UTILIZANDO UM MAPA DO SESSION STATE")

            #html = open(r'', 'r').read()

            #folium_static(html, width=900, height=500)

            with st.spinner('Mapa sendo atualizado'):

                # INCLUINDO O MAPA NO APP
                st.session_state["folium_map_render"] = folium_static(
                    st.session_state["mapobj"],
                    width=700,
                    height=500,
                    add_categorical_legend=True,
                    title_legend="Legenda",
                    list_categories=["Ag Black", "Ag Blue"],
                    list_colors=["#ffffff", "#3391FF"],
                )

                logger.info("MAPA CONSTRUIDO COM SUCESSO - IFRAME")

        logger.info("MAPA RENDERIZADO EM TELA")

        st.text(
            "Foram selecionados {} agências".format(
                len(st.session_state["selected_df"])
            )
        )
        st.text("Mapa: {} agências".format(len(st.session_state["current_map_df"])))

load_page_plan_estrategico()
