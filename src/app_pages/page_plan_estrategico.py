try:
    from config_app.config_app import settings
except Exception as ex:
    from src.config_app.config_app import settings

from pathlib import Path
from inspect import stack

import pandas as pd
import streamlit as st
from loguru import logger

try:
    from utils.pandas_functions import (
        load_data,
        convert_dataframe_to_aggrid,
        compare_dataframes,
    )
    from utils.agstyler import draw_grid
    from utils.map.map_functions import load_map
    from utils.map.map_functions import folium_static
    from utils.dataframe_explorer import dataframe_explorer
    from graphs import get_dataframe_to_plot
    from graphs import create_graphs
except ModuleNotFoundError:
    from src.utils.pandas_functions import (
        load_data,
        convert_dataframe_to_aggrid,
        compare_dataframes,
    )
    from src.utils.agstyler import draw_grid
    from src.utils.map.map_functions import load_map
    from src.utils.map.map_functions import folium_static
    from src.utils.dataframe_explorer import dataframe_explorer
    from src.graphs import get_dataframe_to_plot
    from src.graphs import create_graphs

dir_root = Path(__file__).absolute().parent.parent


def __save_action__(data_planejamento, data_selected, ag_selected, action_selected):
    print(
        "SALVANDO ESTRATÉGIA - AGÊNCIA: {} - ESTRATÉGIA: {}".format(
            ag_selected, action_selected
        )
    )

    # OBTENDO A COLUNA PARA SALVAR AS AÇÕES
    col_save_action = settings.get("COL_SAVE_ACTION", "ESTRATÉGIA SELECIONADA")

    # VERIFICANDO SE A COLUNA EXISTE, CASO NÃO EXISTA
    # CRIA COLUNA PARA SALVAR A ESTRATÉGIA SELECIONADA
    for data in [data_planejamento, data_selected]:
        if not col_save_action in data:
            data[col_save_action] = ""

        logger.info(
            "SALVANDO AÇÃO: AGÊNCIA: {} - ESTRATÉGIA: {}".format(
                ag_selected, action_selected
            )
        )

        # SALVANDO A ESTRATÉGIA PARA A AGÊNCIA
        data.loc[
            data[settings.get("COLUMN_NUM_AGENCIA", "CÓDIGO AG")] == ag_selected,
            col_save_action,
        ] = action_selected


def convert_dataframe_explorer(data, style):
    if style == "agstyle":
        formatter = None
        css = None

        return draw_grid(
            data,
            formatter=formatter,
            fit_columns=True,
            selection="multiple",  # or 'single', or None
            use_filterable=True,  # or False by default
            use_groupable=True,
            use_checkbox=True,
            validator_all_rows_selected=True,
            validator_enable_enterprise_modules=True,
            theme="streamlit",
            max_height=300,
            css=css,
        )

    elif style == "aggrid_default":
        return style, convert_dataframe_to_aggrid(
            data=data, validator_all_rows_selected=True
        )

    elif style == "dataframe_explorer":
        return style, dataframe_explorer(data, case=False)

    else:
        logger.warning("OPÇÃO NÃO VÁLIDA - {}".format(stack()[0][3]))

        return style, convert_dataframe_to_aggrid(
            data=data, validator_all_rows_selected=True
        )


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

    dir_save = str(
        Path(
            dir_root,
            settings.get("DIR_SAVE_RESULT", "resultados/RESULTADO_ESTRATEGICO"),
        )
    )

    # SALVANDO OS DADOS
    data.to_excel(dir_save, index=False)

    logger.info("DADOS SALVOS COM SUCESSO EM: {}".format(dir_save))


def get_dataframe_filter(dataframe, filtro_mercado, filtro_regiao, filtro_supt):
    try:
        logger.info(
            "INICIANDO FILTROS - DATAFRAME COM {} VALORES".format(len(dataframe))
        )
        logger.info(
            "APLICANDO FILTRO DE MERCADO: {} - REGIAO: {} - SUPT: {}".format(
                filtro_mercado, filtro_regiao, filtro_supt
            )
        )

        # APLICANDO FILTROS - MERCADO
        if settings.get("FILTRO_MERCADO_VALUE_DEFAULT", "Todos") not in filtro_mercado:
            dataframe = dataframe[
                dataframe[settings.get("COLUMN_MERCADO", "MERCADO")].isin(
                    filtro_mercado
                )
            ]

        logger.info(
            "FILTRO DE MERCADO - {} - APÓS O FILTRO - DATAFRAME COM {} VALORES".format(
                settings.get("FILTRO_MERCADO_VALUE_DEFAULT", "Todos"), len(dataframe)
            )
        )

        # APLICANDO FILTROS - REGIÃO
        if settings.get("FILTRO_REGIAO_VALUE_DEFAULT", "Todas") not in filtro_regiao:
            dataframe = dataframe[
                dataframe[settings.get("COLUMN_REGIAO", "REGIAO")].isin(filtro_regiao)
            ]

        logger.info(
            "FILTRO DE REGIÃO - {} - APÓS O FILTRO - DATAFRAME COM {} VALORES".format(
                settings.get("FILTRO_REGIAO_VALUE_DEFAULT", "Todas"), len(dataframe)
            )
        )

        # APLICANDO FILTROS - SUPT
        if settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todas") not in filtro_supt:
            dataframe = dataframe[
                dataframe[settings.get("COLUMN_SUPT", "SUPT")].isin(filtro_supt)
            ]

        logger.info(
            "FILTRO DE SUPT - {} - APÓS O FILTRO - DATAFRAME COM {} VALORES".format(
                settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todas"), len(dataframe)
            )
        )

    except Exception as ex:
        logger.error("ERRO NA FUNÇÃO - {} - {}".format(stack()[0][3], ex))

    return dataframe


def redefine_filtros(dataframe, multiselect_change, key):
    """

    APÓS QUALQUER MUDANÇA NOS BOTÕES DE FILTRO (on_change)
    ATUALIZA OS VALORES DO SESSION_STATE
    PARA O RESPECTIVO BOTÃO

    # Arguments
        multiselect_change          - Required: Chave do session
                                                state para ser atualizado (String)
        key                         - Required: Valores para atualização (String)

    """

    # DEFININDO OS VALORES PARA O FILTRO SELECIONADO
    st.session_state[multiselect_change] = st.session_state[key]

    # DEFININDO OS VALORES PARA OS OUTROS FILTROS
    if multiselect_change == "filtro_mercado" and st.session_state[key]:
        dataframe = dataframe[
            dataframe[settings.get("COLUMN_MERCADO", "MERCADO")].isin(
                st.session_state[key]
            )
        ]

        # ATUALIZANDO OS VALORES POSSIVEIS PARA OS CAMPOS REGIÃO E SUPT
        st.session_state["list_regioes"] = [
            settings.get("FILTRO_REGIAO_VALUE_DEFAULT", "Todas")
        ] + list(dataframe[settings.get("COLUMN_REGIAO", "REGIÃO")].unique())

        st.session_state["list_supt"] = [
            settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todas")
        ] + list(dataframe[settings.get("COLUMN_SUPT", "SUPT")].unique())

        # ATUALIZANDO O FILTRO DEFAULT
        st.session_state["filtro_regiao"] = st.session_state["list_regioes"][0]
        st.session_state["filtro_supt"] = st.session_state["list_supt"][0]

    elif multiselect_change == "filtro_regiao" and st.session_state[key]:
        dataframe = dataframe[
            dataframe[settings.get("COLUMN_REGIAO", "REGIÃO")].isin(
                st.session_state[key]
            )
        ]

        # ATUALIZANDO OS VALORES POSSIVEIS PARA OS CAMPOS REGIÃO E SUPT
        st.session_state["list_mercados"] = [
            settings.get("FILTRO_MERCADO_VALUE_DEFAULT", "Todos")
        ] + list(dataframe[settings.get("COLUMN_MERCADO", "MERCADO")].unique())

        st.session_state["list_supt"] = [
            settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todas")
        ] + list(dataframe[settings.get("COLUMN_SUPT", "SUPT")].unique())

        # ATUALIZANDO O FILTRO DEFAULT
        st.session_state["filtro_mercado"] = st.session_state["list_mercados"][0]
        st.session_state["filtro_supt"] = st.session_state["list_supt"][0]


def redefine_filtros_default():
    """

    DEFININDO O VALOR PARA OS FILTROS
    VALORES DEFAULT

    """

    # ATUALIZANDO TODAS AS OPÇÕES
    # OBTENDO TODOS OS MERCADOS, REGIÕES E SUPT
    st.session_state["list_mercados"] = [
        settings.get("FILTRO_MERCADO_VALUE_DEFAULT", "Todos")
    ] + list(
        st.session_state["df_planejamento"][
            settings.get("COLUMN_MERCADO", "MERCADO")
        ].unique()
    )

    st.session_state["list_regioes"] = [
        settings.get("FILTRO_REGIAO_VALUE_DEFAULT", "Todas")
    ] + list(
        st.session_state["df_planejamento"][
            settings.get("COLUMN_REGIAO", "REGIÃO")
        ].unique()
    )

    st.session_state["list_supt"] = [
        settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todas")
    ] + list(
        st.session_state["df_planejamento"][
            settings.get("COLUMN_SUPT", "SUPT")
        ].unique()
    )

    # DEFININDO O VALOR DEFAULT
    st.session_state["filtro_mercado"] = settings.get(
        "FILTRO_MERCADO_VALUE_DEFAULT", "Todos"
    )
    st.session_state["filtro_regiao"] = settings.get(
        "FILTRO_REGIAO_VALUE_DEFAULT", "Todos"
    )
    st.session_state["filtro_supt"] = settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todos")


def load_page_plan_estrategico():
    """

    DATAFRAME ORIGINAL - st.session_state["df_planejamento"] = df_planejamento
    DATAFRAME SELECIONADO - st.session_state["selected_df"]

    """

    # INICIANDO UM VALIDADOR DO RERUN AUTOMÁTICO
    validator_rerun = True

    if "df_planejamento" not in st.session_state.keys():
        # CARREGANDO DATAFRAME
        dict_result = load_data(
            data_dir=str(Path(dir_root, settings.get("DATA_DIR_AGENCIAS"))),
            header=[0, 1]
        )

        df_planejamento = dict_result["DATAFRAME_RESULT"]

        logger.info("DADOS OBTIDOS COM SUCESSO")

        st.session_state["df_planejamento"] = df_planejamento

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

    if "list_mercados" not in st.session_state.keys():
        # OBTENDO TODOS OS MERCADOS, REGIÕES E SUPT
        st.session_state["list_mercados"] = [
            settings.get("FILTRO_MERCADO_VALUE_DEFAULT", "Todos")
        ] + list(
            st.session_state["df_planejamento"][
                settings.get("COLUMN_MERCADO", "MERCADO")
            ].unique()
        )

    if "list_regioes" not in st.session_state.keys():
        st.session_state["list_regioes"] = [
            settings.get("FILTRO_REGIAO_VALUE_DEFAULT", "Todas")
        ] + list(
            st.session_state["df_planejamento"][
                settings.get("COLUMN_REGIAO", "REGIÃO")
            ].unique()
        )

    if "list_supt" not in st.session_state.keys():
        st.session_state["list_supt"] = [
            settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todas")
        ] + list(
            st.session_state["df_planejamento"][
                settings.get("COLUMN_SUPT", "SUPT")
            ].unique()
        )

    # NO MAIN
    st.markdown("# APP - PLANEJAMENTO ESTRATÉGICO")

    # CRIANDO UMA LINHA EM BRANCO
    # st.divider()

    select_column1, select_column2, select_column3, select_column4 = st.columns(4)

    # CRIANDO O SELECT BOX DE MERCADO
    st.session_state["filtro_mercado"] = select_column1.multiselect(
        label="Mercado",
        options=st.session_state["list_mercados"],
        default=st.session_state["filtro_mercado"]
        if "filtro_mercado" in st.session_state.keys()
        else settings.get("FILTRO_MERCADO_VALUE_DEFAULT", "Todos"),
        help="Selecione o mercado desejado",
        key="filtro_mercado_selection",
        on_change=redefine_filtros,
        args=(
            st.session_state["df_planejamento"],
            "filtro_mercado",
            "filtro_mercado_selection",
        ),
    )

    st.session_state["filtro_regiao"] = select_column2.multiselect(
        label="Região",
        options=st.session_state["list_regioes"],
        default=st.session_state["filtro_regiao"]
        if "filtro_regiao" in st.session_state.keys()
        else settings.get("FILTRO_REGIAO_VALUE_DEFAULT", "Todas"),
        help="Selecione a região desejada",
        key="filtro_regiao_selection",
        on_change=redefine_filtros,
        args=(
            st.session_state["df_planejamento"],
            "filtro_regiao",
            "filtro_regiao_selection",
        ),
    )

    st.session_state["filtro_supt"] = select_column3.multiselect(
        label="Superintendência",
        options=st.session_state["list_supt"],
        default=st.session_state["filtro_supt"]
        if "filtro_supt" in st.session_state.keys()
        else settings.get("FILTRO_SUPT_VALUE_DEFAULT", "Todas"),
        help="Selecione a superintendência desejada",
        key="filtro_supt_selection",
        on_change=redefine_filtros,
        args=(
            st.session_state["df_planejamento"],
            "filtro_supt",
            "filtro_supt_selection",
        ),
    )

    # CRIANDO DOIS ESPAÇOS EM BRANCO NO COLUMN4 PARA ALINHAR O BOTÃO
    select_column4.markdown("")
    select_column4.markdown("")
    select_column4.button("Redefinir Filtros", on_click=redefine_filtros_default)

    print(
        st.session_state["filtro_mercado"],
        st.session_state["filtro_regiao"],
        st.session_state["filtro_supt"],
    )

    # SELECIONANDO OS VALORES DO DATAFRAME VIA COMBOBOX
    st.session_state["selected_df"] = get_dataframe_filter(
        dataframe=st.session_state["df_planejamento"],
        filtro_mercado=st.session_state["filtro_mercado"],
        filtro_regiao=st.session_state["filtro_regiao"],
        filtro_supt=st.session_state["filtro_supt"],
    )

    # PLOTANDO O MAPA
    (
        validator,
        st.session_state["mapobj"],
        st.session_state["current_map_df"],
    ) = load_map(
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

    with st.container():
        # INCLUINDO O MAPA NO APP
        st_data = folium_static(
            st.session_state["mapobj"],
            width=900,
            height=500,
            add_categorical_legend=True,
            title_legend="Legenda",
            list_categories=["Ag Black", "Ag Blue"],
            list_colors=["#ffffff", "#3391FF"],
        )

        # OBTENDO O DATAFRAME
        dataframe_explorer_type, dataframe_return = convert_dataframe_explorer(
            data=st.session_state["selected_df"],
            style=settings.get("OPTION_DATAFRAME_EXPLORER", "aggrid_default"),
        )

        # INCLUINDO O DATAFRAME
        if dataframe_explorer_type in ["agstyle", "aggrid_default"]:
            # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
            st.session_state["selected_df"] = pd.DataFrame(
                dataframe_return["selected_rows"]
            )
        else:
            # PLOTANDO O DATAFRAME EM TELA
            selected_df = st.dataframe(dataframe_return, use_container_width=True)
            # OBTENDO O DATAFRAME DAS LINHAS SELECIONADAS
            st.session_state["selected_df"] = dataframe_return

        print(len(st.session_state["selected_df"]))
        print(len(st.session_state["current_map_df"]))
        print(validator_rerun)

        st.text("Mapa: {} agências".format(len(st.session_state["current_map_df"])))


if __name__ == "__main__":
    load_page_plan_estrategico()
