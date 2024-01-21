from typing import Union
import pandas as pd
import numpy as np
from src.utils.pandas_functions import column_to_uppercase, rows_to_uppercase

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

    if not multiindex:

        # REALIZANDO A LEITURA DOS DADOS
        if "csv" in data_dir:
            df = pd.read_csv(data_dir, header)
        else:
            df = pd.read_excel(data_dir, header)

        if column_uppercase:
            df = column_to_uppercase(data=df)
        if row_uppercase:
            df = rows_to_uppercase(data=df, trim=trim_values)

    else:

        # REALIZANDO A LEITURA DOS DADOS
        if "csv" in data_dir:
            df = pd.read_csv(data_dir, header=[header, header + 1])
        else:
            df = pd.read_excel(data_dir, header=[header, header + 1])

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

data_dir = r'C:\Users\Emerson\Desktop\Analytics\MATERIAIS POR TEMA\STREAMLIT\APP_FOOTPRINT_PLANEJAMENTO_ESTRATEGICO\src\data\FOOTPRINT_PLANEJAMENTO_ESTRATEGICO_UNNAMED_V2.xlsx'

dict_result = load_data(data_dir,
					    header=0,
					    column_uppercase=True,
					    row_uppercase=True,
					    trim_values=True,
					    multiindex=True)

def get_column_by_level_0(list_columns_level, list_columns_level0):

    list_columns_result = []

    print(type(list_columns_level))

    if isinstance(list_columns_level, (tuple, list, np.ndarray)) and isinstance(list_columns_level0, (tuple, list)):
        # PERCORRENDO AS COLUNAS LEVEL0 E LEVEL1 DO DATAFRAME:
        for column_level0, column_level1 in list_columns_level:
            # VERIFICANDO SE A COLUNA LEVEL0 CONSTA NA LISTA DE COLUNAS DESEJADAS:
            if column_level0 in list_columns_level0:
                # ARMAZENANDO A COLUNA LEVEL1 RESPECTIVA
                list_columns_result.append(column_level1)

    return list_columns_result


list_columns_result = get_column_by_level_0(list_columns_level=dict_result.get("DF_COLUMNS"),
                                            list_columns_level0=['Informações Financeiras'])

print(dict_result.get("DF_COLUMNS"))
print(list_columns_result)