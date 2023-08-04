from pathlib import Path
from inspect import stack

import pandas as pd
import streamlit as st
from dynaconf import settings
from streamlit_folium import st_folium
from loguru import logger

from utils.pandas_functions import load_data, convert_dataframe_to_aggrid
from utils.agstyler import draw_grid
from utils.map.map_functions import load_map, download_folium_map

dir_root = Path(__file__).absolute().parent.parent

def load_page_agencias():

    # INICIALIZANDO AS VARIÁVEIS AUXILIARES
    if "current_map_df" not in st.session_state.keys():
        st.session_state["current_map_df"] = pd.DataFrame()

    if "df_planejamento" not in st.session_state.keys():
        # CARREGANDO DATAFRAME
        df_planejamento = load_data(
            data_dir=str(Path(dir_root, settings.get("DATA_DIR_AGENCIAS")))
        )

        logger.info("DADOS OBTIDOS COM SUCESSO")

        st.session_state["df_planejamento"] = df_planejamento

    else:
        logger.info("DADOS RECUPERADOS DO SESSION STATE COM SUCESSO")
        df_planejamento = st.session_state["df_planejamento"]

	# INCLUINDO O DATAFRAME EM TELA
	# NO MAIN
	st.markdown("# APP - PÁGINA DE AGÊNCIAS")

	# CRIANDO UMA LINHA EM BRANCO
	# st.divider()

	logger.info("{} AGÊNCIAS".format(len(df_planejamento)))