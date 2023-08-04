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


def __save_action__(data, ag_selected, action_selected):

    # OBTENDO A COLUNA PARA SALVAR AS AÇÕES
    col_save_action = settings.get("COL_SAVE_ACTION", "ESTRATÉGIA SELECIONADA")

    # VERIFICANDO SE A COLUNA EXISTE, CASO NÃO EXISTA
    # CRIA COLUNA PARA SALVAR A ESTRATÉGIA SELECIONADA
    if not col_save_action in data:
        data[col_save_action] = ""

    logger.info(
        "SALVANDO AÇÃO: AGÊNCIA: {} - ESTRATÉGIA: {}".format(ag_selected,
                                                             action_selected))

    # SALVANDO A ESTRATÉGIA PARA A AGÊNCIA
    data.loc[data[settings.get("COLUMN_NUM_AGENCIA",  "CÓDIGO AG")] == ag_selected,
             col_save_action] = action_selected

    # SALVANDO NO OBJETO GLOBAL
    st.session_state["df_planejamento"] = data

def convert_dataframe_explorer(data, style):

    if style == 'agstyle':

        formatter = None
        css = None

        return draw_grid(
            data,
            formatter=formatter,
            fit_columns=True,
            selection='multiple',  # or 'single', or None
            use_filterable=True,  # or False by default
            use_groupable=True,
            use_checkbox=True,
            validator_all_rows_selected=True,
            validator_enable_enterprise_modules=True,
            theme='streamlit',
            max_height=300,
            css=css,
        )

    elif style == "aggrid_default":

        return convert_dataframe_to_aggrid(data=data, validator_all_rows_selected=True)

    else:
        logger.warning("OPÇÃO NÃO VÁLIDA - {}".format(stack()[0][3]))

        return convert_dataframe_to_aggrid(data=data, validator_all_rows_selected=True)


def __save_excel__(data):

    """

        SALVA O DATAFRAME ATUAL

        COMO O DATAFRAME É ATUALIZADO
        COM AS AÇÕES DO USÁRIO
        ESSE DATAFRAME REPRESENTA AS
        ESTRATÉGIAS ADOTADAS

        # Arguments
            data            - Required: Dados em tela (DataFrame)

        # Returns

    """

    dir_save = str(Path(dir_root,
                    settings.get("DIR_SAVE_RESULT",
                                 "resultados/RESULTADO_ESTRATEGICO")))

    # SALVANDO OS DADOS
    data.to_excel(dir_save, index=False)

    logger.info("DADOS SALVOS COM SUCESSO EM: {}".format(dir_save))

def load_page_plan_estrategico():

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
    st.markdown("# APP - PLANEJAMENTO ESTRATÉGICO")

    # CRIANDO UMA LINHA EM BRANCO
    # st.divider()

    # OBTENDO O DATAFRAME
    dataframe_aggrid = convert_dataframe_explorer(data=df_planejamento,
                                                  style=settings.get("OPTION_DATAFRAME_EXPLORER",
                                                                     "aggrid_default"))

    # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
    selected_df = pd.DataFrame(dataframe_aggrid["selected_rows"])

    if not selected_df.empty:
        df_map = selected_df
    else:
        df_map = df_planejamento

    # PLOTANDO O MAPA
    validator, st.session_state["mapobj"], st.session_state["current_map_df"] = load_map(
        data=df_map,
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

    # INCLUINDO O MAPA NO APP
    st_data = st_folium(st.session_state["mapobj"], width=1000, height=500)

    # INCLUINDO A POSSIBILIDADE DE SELECIONAR UMA AÇÃO PARA UMA DETERMINADA AGÊNCIA
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            ag_selected = st.selectbox(label="Agência",
                                       options=df_planejamento[settings.get("COLUMN_NUM_AGENCIA",
                                                                            "CÓDIGO AG")].unique(),
                                       help="Selecione o número da agência desejada")
        with col2:
            ag_action = st.selectbox(label="Estratégia",
                                       options=settings.get("OPTIONS_ESTRATEGIA",
                                                            ["ENCERRAR", "MANTER", "ESPAÇO ITAÚ"]),
                                       help="Selecione a estratégia desejada para a agência")

        with col3:
            st.markdown("")
            st.markdown("")
            bt_action = st.button(label="Aplicar estratégia",
                                                           help="Ao clicar no botão, os dados serão salvos na atualizados",
                                  on_click=__save_action__, args=(df_planejamento,
                                                                  ag_selected,
                                                                  ag_action))

    # SALVAR RESULTADOS
    with st.container():
        col1_save, col2_save, col3_save = st.columns(3)
        with col2_save:
            st.download_button(
                label="Download mapa (html)",
                data=download_folium_map(st.session_state["mapobj"]),
                file_name="FOOTPRINT_MAPA.html",
                mime="text/html",
            )
            pass

        with col3_save:
            validator_save_estrategia = st.button(label="Salvar estratégia",
                                                  help="Ao clicar no botão, os dados serão salvos na planilha auxiliar",
                                                  on_click=__save_excel__, args=(df_planejamento,))
            if validator_save_estrategia:
                logger.info("ESTRATÉGIA SALVA: {}".format(validator_save_estrategia))
                st.success("Estratégia salva com sucesso", icon="")

if __name__ == "__main__":
    load_page_plan_estrategico()
