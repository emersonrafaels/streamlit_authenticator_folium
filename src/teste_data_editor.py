import math

try:
	from config_app.config_app import settings
except ModuleNotFoundError:
	from src.config_app.config_app import settings

import pandas as pd
import streamlit as st

dir_data = settings.get("DATA_DIR_AGENCIAS")

df = pd.read_excel(dir_data)

df["ESTRATÉGIA"] = "Manter estratégia"
options_estrategia = list(settings.get("OPTIONS_ESTRATEGIA"))

# Definindo uma função de formatação
def formata_valor(valor):
    if valor < 0:
        return 'color: red'
    else:
        return 'color: green'

print(df)

# APLICANDO FORMATAÇÃO PARA A COLUNA LAIR
styled_df = df.style.applymap(formata_valor, subset=['LAIR'])

# APLICANDO HEATMAP PARA A COLUNA PB
styled_df = styled_df.background_gradient(subset=['PB'], cmap='YlGn')

column_config = {"CÓDIGO AG": st.column_config.NumberColumn(label="AGÊNCIA",
														  	help="Código da agência",
														  	disabled=True),
				 "UF": st.column_config.TextColumn(label="UF",
													help="UF",
													disabled=True),
				 "PB": st.column_config.NumberColumn(label="PB",
													 help="Produto bruto",
													 format="R$ %d",
													 disabled=True),
				 "LAIR": st.column_config.NumberColumn(label="LAIR",
													  help="Produto bruto",
													  format="R$ %d",
													  disabled=True),
				 "ESTRATÉGIA": st.column_config.SelectboxColumn(label="ESTRATÉGIA",
													  help="Estratégia desejada para a agência",
													  options=options_estrategia,
													  default="Manter estratégia",
													  disabled=None)
				 }

columns_to_display = [value for value in list(styled_df.columns) if value not in ["LATITUDE", "LONGITUDE"]]

edited_df = st.data_editor(data=styled_df,
						   column_config=column_config,
						   hide_index=True,
						   column_order=columns_to_display,
						   disabled=False,
						   key="dataframe_editor")

st.write(st.session_state["dataframe_editor"])