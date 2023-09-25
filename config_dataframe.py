import random
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

def get_dataframe():

	# Criando uma lista de números inteiros aleatórios entre 0 e 200 para a coluna 'sales'
	sales = [random.randint(0, 200) for _ in range(10)]

	# Criando uma lista de estratégias atuais ('vermelho', 'amarelo', 'verde')
	estrategia_atual = [random.choice(['vermelho', 'amarelo', 'verde']) for _ in range(10)]

	data_inicial = datetime(2023, 1, 1)
	datas = [data_inicial + timedelta(days=i) for i in range(10)]

	# Criando o dataframe
	df = pd.DataFrame({'sales': sales, 'estrategia_atual': estrategia_atual, 'datas': datas})

	# Exibindo o dataframe
	return df

def get_column_config_default():

	column_config={
			"sales": st.column_config.ProgressColumn(
				"Sales volume",
				help="The sales volume in USD",
				format="$%f",
				min_value=0,
				max_value=1000,
			),
			"estrategia atual": st.column_config.TextColumn(
						"Estrategia atual",
						help="The strategy",
			),
		}

	return column_config

def get_describe_dataframe(dataframe, column,
						   min_default=0,
						   max_default=100,
						   options_default=[]):

	# CRIANDO O DICT PARA SALVAR OS INDICADORES DO DATAFRAME
	dict_indicator = {}

	# VERIFICANDO SE A COLUNA EXISTE NO DATAFRAME
	if column in dataframe:
		try:
			# TENTANDO OBTER O VALOR MIN
			dict_indicator["MIN"] = dataframe[column].min()
		except Exception as ex:
			dict_indicator["MIN"] = min_default

		try:
			# TENTANDO OBTER O VALOR MAX
			dict_indicator["MAX"] = dataframe[column].max()
		except Exception as ex:
			dict_indicator["MAX"] = max_default

		try:
			# TENTANDO OBTER AS OPÇÕES DISPONÍVEIS
			dict_indicator["UNIQUE"] = dataframe[column].unique()
		except Exception as ex:
			dict_indicator["UNIQUE"] = options_default

	return dict_indicator

# OBTENDO O DATAFRAME
df = get_dataframe()

# OBTENDO AS CONFIGS DO MODELO
column_config_model={
        "sales": st.column_config.ProgressColumn(
            "Sales volume",
            help="The sales volume in USD",
            format="$%f",
            min_value=get_describe_dataframe(dataframe=df,
											 column="sales",
											 min_default=0,
											 max_default=1000).get("MIN", 0),
            max_value=get_describe_dataframe(dataframe=df,
											 column="sales",
											 min_default=0,
											 max_default=1000).get("MAX", 0),
        ),
		"estrategia atual": st.column_config.SelectboxColumn(
					label="Estrategia atual",
					help="The sales volume in USD",
					options=get_describe_dataframe(dataframe=df,
												   column="estrategia_atual",
												   options_default=["Azul"]).get("UNIQUE", []),
		),
		"estrategia atual": st.column_config.SelectboxColumn(
							label="Estrategia atual",
							help="The sales volume in USD",
							options=get_describe_dataframe(dataframe=df,
														   column="estrategia_atual",
														   options_default=["Azul"]).get("UNIQUE", []),
				),
    }


"""
if isinstance(column_config, (list, tuple)):

	for value in column_config[0]:
		if "sales" in value:
			column_config[0]["sales"]['type_config']["min_value"] = 15

if isinstance(column_config, (dict)):

	for value in column_config.keys():
		if "sales" in value:
			column_config["sales"]['type_config']["min_value"] = 15]
			
"""

print(column_config_model)