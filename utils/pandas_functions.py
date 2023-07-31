import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


@st.cache_data
def load_data(data_dir):
    # REALIZANDO A LEITURA DOS DADOS
    df = pd.read_excel(data_dir)

    return df


def convert_dataframe_to_aggrid(data, validator_all_rows_selected=True):
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_default_column(
        enablePivot=False, enableValue=True, enableRowGroup=True
    )
    gb.configure_pagination(
        paginationAutoPageSize=True, paginationPageSize=5
    )  # Add pagination
    gb.configure_side_bar(
        filters_panel=True, columns_panel=True, defaultToolPanel=""
    )  # Add a sidebar
    gb.configure_selection(
        "multiple",
        use_checkbox=True,
        groupSelectsChildren="Group checkbox select children",
    )  # Enable multi-row selection

    # VALIDANDO SE É DESEJADO QUE TODAS AS LINHAS INICIEM SELECIONADAS
    if validator_all_rows_selected:
        gb.configure_selection("multiple", pre_selected_rows=list(range(len(data))))

    gridOptions = gb.build()

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.VALUE_CHANGED
        | GridUpdateMode.SELECTION_CHANGED
        | GridUpdateMode.FILTERING_CHANGED
        | GridUpdateMode.SORTING_CHANGED,
        fit_columns_on_grid_load=False,
        theme="light",
        enable_enterprise_modules=True,
        height=350,
        width="100%",
        reload_data=False,
        header_checkbox_selection_filtered_only=True,
        use_checkbox=True,
    )

    return grid_response


def get_indicators_before_versus_after(
    df1, df2, column_on="CÓDIGO AG", name_column_indicator="CRUZAMENTO"
):
    # REALIZANDO O JOIN ENTRE OS DATAFRAMES
    df_join = pd.merge(
        df1, df2, on=column_on, how="inner", suffixes=("_antes", "_depois")
    )

    return df_join


def filter_columns_multiselect(colunas_desejadas, df_columns):
    colunas_desejadas_antes_depois = []

    for column in colunas_desejadas:
        colunas_desejadas_antes_depois.append(str(column))
        colunas_desejadas_antes_depois.append("{}{}".format(str(column), "_antes"))
        colunas_desejadas_antes_depois.append("{}{}".format(str(column), "_depois"))

    colunas_desejadas_filter = list(
        filter(lambda x: x in df_columns, colunas_desejadas_antes_depois)
    )
    return colunas_desejadas_filter
