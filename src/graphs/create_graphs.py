from inspect import stack

import sidetable
import plotly.express as px
from loguru import logger

def get_graph_fill_recomendations(data,
								  column_status):

	# INICIANDO O GRÁFICO PLOT
	fig = px.bar()

	try:
		# OBTENDO A TABELA DE FREQUÊNCIA
		df_groupby_status = data.stb.freq([column_status])

		# OBTENDO OS VALORES
		total_agencias = df_groupby_status["count"].sum()
		total_inicial = df_groupby_status[df_groupby_status[
							  "MOMENTO ESTRATÉGIA ATUAL"] == "RECOMENDAÇÃO INICIAL"][
			"count"]
		total_inicial = total_inicial.values[0] if not total_inicial.empty else 0
		total_acao_usuario = df_groupby_status[df_groupby_status[
							  "MOMENTO ESTRATÉGIA ATUAL"] == "ESTRATÉGIA DEFINIDA"][
			"count"]
		total_acao_usuario = total_acao_usuario.values[0] if not total_acao_usuario.empty else 0

		# OBTENDO A FIGURA PLOTLY
		fig = px.bar(df_groupby_status,
					 x="count", y=column_status,
					 color=column_status, orientation='h',
					 hover_data=["percent"],
					 height=400,
					 title="Preenchimento atual: {}/{} agências".format(total_acao_usuario, total_agencias))

	except Exception as ex:
		logger.error("ERRO NA FUNÇÃO - {} - {}".format(stack()[0][3], ex))

	return fig