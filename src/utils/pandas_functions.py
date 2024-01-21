import streamlit as st
import pandas as pd
from loguru import logger
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


def column_to_uppercase(data):
    # OBTENDO TODAS AS COLNAS DO DATAFRAME
    # APLICANDO UPPERCASE
    newcols = [column.upper() for column in data.columns]

    # FORMATANDO O DATAFRAME
    data.columns = newcols

    # RETORNANDO O DATAFRAME FORMATADO EM UPPERCASE
    return data


def rows_to_uppercase(data, trim=False):
    # OBTENDO TODAS AS COLNAS DO DATAFRAME
    # APLICANDO UPPERCASE
    for column in data.select_dtypes(include="O").columns:
        if trim:
            data[column] = data[column].apply(lambda x: str(x).upper().strip())
        else:
            data[column] = data[column].apply(lambda x: str(x).upper())

    return data


@st.cache_data
def load_data(data_dir,
              header=0,
              column_uppercase=True,
              row_uppercase=True,
              trim_values=True,
              multiindex=False):
    """

    REALIZA A LEITURA DOS DADOS

    # Arguments
        data_dir                 - Required: Dado a ser lido (Path)
        column_uppercase         - Required: Validador para tornar
                                             todas colunas uppercase (Boolean)
        row_uppercase            - Required: Validador para tornar
                                             todas linhas (valores) uppercase (Boolean)
        trim_values              - Required: Validador para remover espaços antes e depois,
                                             em valores strings (Boolean)
        multiindex               - Optional: Se é desejado ler um dataframe multiindex (Boolean)

    # Returns
        df                       - Required: Dado após leitura (DataFrame)

    """

    # INICIANDO O DICT RESULT
    dict_result = {}

    # REALIZANDO A LEITURA DOS DADOS
    if "csv" in data_dir:
        df = pd.read_csv(data_dir, header)
    else:
        df = pd.read_excel(data_dir, header)

    if not multiindex:

        if column_uppercase:
            df = column_to_uppercase(data=df)
        if row_uppercase:
            df = rows_to_uppercase(data=df, trim=trim_values)

    if multiindex:
        df_columns = df.columns.to_numpy()
        df_columns_level0 = df.columns.get_level_values(0)
        df_columns_level1 = df.columns.get_level_values(1)

        df.columns = df_columns_level1

        dict_result["DF_COLUMNS"] = df_columns
        dict_result["DF_COLUMNS_LEVEL0"] = df_columns_level0
        dict_result["DF_COLUMNS_LEVEL1"] = df_columns_level1

        if column_uppercase:
            df = column_to_uppercase(data=df)
        if row_uppercase:
            df = rows_to_uppercase(data=df, trim=trim_values)

    dict_result["DATAFRAME_RESULT"] = df

    return dict_result


def convert_dataframe_to_aggrid(data, validator_all_rows_selected=True):
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_default_column(
        enablePivot=False, enableValue=True, enableRowGroup=True
    )
    gb.configure_pagination(
        paginationAutoPageSize=True, paginationPageSize=10
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


def compare_dataframes(df1, df2):

    validator_diff_dataframes = df1.equals(df2)

    try:
        if not validator_diff_dataframes:
            result = df1.compare(df2)
    except Exception as ex:
        logger.error(ex)

    return validator_diff_dataframes
