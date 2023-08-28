from pathlib import Path
from inspect import stack

import pandas as pd
import streamlit as st
from dynaconf import settings
from streamlit_folium import folium_static
from loguru import logger

from utils.pandas_functions import load_data, convert_dataframe_to_aggrid, compare_dataframes
from utils.agstyler import draw_grid
from utils.map.map_functions import load_map, download_folium_map
from utils.dataframe_explorer import dataframe_explorer

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

        return style, convert_dataframe_to_aggrid(data=data, validator_all_rows_selected=True)

    elif style == "dataframe_explorer":

        return style, dataframe_explorer(data,
                                         case=False)

    else:
        logger.warning("OPÇÃO NÃO VÁLIDA - {}".format(stack()[0][3]))

        return style, convert_dataframe_to_aggrid(data=data, validator_all_rows_selected=True)


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

        st.session_state["df_planejamento"] = df_planejamento

    else:
        logger.info("df_planejamento - DADOS RECUPERADOS DO SESSION STATE COM SUCESSO - {} AGÊNCIAS".format(len(st.session_state["df_planejamento"])))
        df_planejamento = st.session_state["df_planejamento"]

    if "selected_df" not in st.session_state.keys():

        # CARREGANDO DATAFRAME
        st.session_state["selected_df"] = st.session_state["df_planejamento"]

    else:
        logger.info("selected_df - DADOS RECUPERADOS DO SESSION STATE COM SUCESSO - {} AGÊNCIAS".format(len(st.session_state["selected_df"])))

    # INCLUINDO O DATAFRAME EM TELA
    # NO MAIN
    st.markdown("# APP - PLANEJAMENTO ESTRATÉGICO")

    # CRIANDO UMA LINHA EM BRANCO
    # st.divider()

    select_column1, select_column2, select_column3 = st.columns(3)

    # OBTENDO TODOS OS MERCADOS, REGIÕES E SUPT
    lista_mercados = list(
        st.session_state["df_planejamento"]["MERCADO"].unique())
    lista_regioes = list(st.session_state["df_planejamento"]["REGIÃO"].unique())
    lista_supt = list(st.session_state["df_planejamento"]["SUPT"].unique())

    logger.info(lista_mercados)
    logger.info(lista_regioes)
    logger.info(lista_supt)

    # CRIANDO O SELECT BOX DE MERCADO
    filtro_mercado = select_column1.selectbox(label="Mercado",
                                              options=lista_mercados,
                                              help="Selecione o mercado desejado")

    filtro_regiao = select_column2.selectbox(label="Região",
                                  options=lista_regioes,
                                  help="Selecione a região desejada")

    filtro_supt = select_column3.selectbox(label="Superintendência",
                                           options=lista_supt,
                                           help="Selecione a superintendência desejada")

    if st.sidebar.button('Redefinir Filtros'):
        filtro_mercado = 'Todos'
        filtro_regiao = 'Todas'
        filtro_supt = 'Todas'

    st.session_state["selected_df"] = []

    print(filtro_mercado, filtro_regiao, filtro_supt)

    for dado in st.session_state["df_planejamento"]:
        # Aplicar filtros
        if (filtro_mercado == 'Todos' or dado['MERCADO'] == filtro_mercado) and \
                (filtro_regiao == 'Todas' or dado[
                    'REGIÃO'] == filtro_regiao) and \
                (filtro_supt == 'Todas' or dado['SUPT'] == filtro_supt):
            st.session_state["selected_df"].append(dado)

    # PLOTANDO O MAPA
    validator, st.session_state["mapobj"], st.session_state["current_map_df"] = load_map(
        data=st.session_state["selected_df"],
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

    logger.info("MAPA ATUALIZADO")

    with st.container():

        # INCLUINDO O MAPA NO APP
        st_data = folium_static(st.session_state["mapobj"],
                                width=900,
                                height=500)

        # OBTENDO O DATAFRAME
        dataframe_explorer_type, dataframe_return = convert_dataframe_explorer(data=st.session_state["selected_df"],
                                                                               style=settings.get("OPTION_DATAFRAME_EXPLORER",
                                                                                                  "aggrid_default"))

        if dataframe_explorer_type in ["agstyle", "aggrid_default"]:

            # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
            st.session_state["selected_df"] = pd.DataFrame(dataframe_return["selected_rows"])
        else:
            # PLOTANDO O DATAFRAME EM TELA
            selected_df = st.dataframe(dataframe_return,
                                       use_container_width=True)
            # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
            st.session_state["selected_df"] = dataframe_return

        print(len(st.session_state["selected_df"]))
        print(len(st.session_state["current_map_df"]))
        print(validator_rerun)

        if not compare_dataframes(df1=st.session_state["selected_df"],
                                  df2=st.session_state["current_map_df"]):
            # REALIZAR NOVO REFRESH NA PÁGINA
            logger.info("ENTROU")
            #st.experimental_rerun()

        st.text("Foram selecionados {} agências".format(
            len(st.session_state["selected_df"])))
        st.text("Mapa: {} agências".format(
            len(st.session_state["current_map_df"])))

if __name__ == "__main__":
    load_page_plan_estrategico()
