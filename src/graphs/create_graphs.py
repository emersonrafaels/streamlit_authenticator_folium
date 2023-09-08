from inspect import stack

import sidetable
import plotly.express as px
import plotly.graph_objects as go
from loguru import logger


def get_bar_plot_fill_recomendations(data,
                                     column_status,
                                     width=500,
                                     height=500,
                                     paper_bgcolor=None):
    """

    OBTÉM UM GRÁFICO COM O PERCENTUAL DE PREENCHIMENTO
    DAS RECOMENDAÇÕES
    VERSUS
    O TOTAL DE AGÊNNCIAS DISPONÍVEIS PARA
    PREENCHIMENTO

    # Arguments
        data                    - Required: Dados para plotar (DataFrame)
        column_status			- Required: Coluna de status (String)
        width                   - Optional: Largura da imagem (Integer)
        height                  - Optional: Altura da imagem (Integer)
        paper_bgcolor           - Optional: Cor do background da imagem.
                                            Deve ser um valor rgb ou hex (String)

    # Returns
        fig                     - Required: Figura Plotly (Plotly fig)
    """

    # INICIANDO O GRÁFICO PLOT
    fig = px.bar()

    try:
        # OBTENDO A TABELA DE FREQUÊNCIA
        df_groupby_status = data.stb.freq([column_status])

        # OBTENDO OS VALORES
        total_agencias = df_groupby_status["count"].sum()
        total_inicial = df_groupby_status[
            df_groupby_status[column_status] == "RECOMENDAÇÃO INICIAL"
        ]["count"]
        total_inicial = total_inicial.values[0] if not total_inicial.empty else 0
        total_acao_usuario = df_groupby_status[
            df_groupby_status[column_status] == "ESTRATÉGIA DEFINIDA"
        ]["count"]
        total_acao_usuario = (
            total_acao_usuario.values[0] if not total_acao_usuario.empty else 0
        )

        # OBTENDO OS VALORES PARA PLOTAR
        keys = df_groupby_status["MOMENTO ESTRATÉGIA ATUAL"].values
        values = df_groupby_status["count"].values
        percent = df_groupby_status["percent"].values

        # INICIALIZANDO A FIGURA PARA PLOT
        fig = go.Figure()

        # ADICIONANDO A BARRA DE RECOMENDAÇÃO INICIAL
        fig.add_trace(go.Bar(
            x=[keys[0]],
            y=[values[0]],
            name='Mantida recomendação inicial',
            marker_color='#FFA15A',
            text=[values[0]],
            textposition='outside',
            texttemplate='%{text} agências' if values[
                                                   0] != 1 else '%{text} agência',
            hovertemplate="<br>".join([
                "Mantida a recomendação inicial",
                "Quantidade: %{y}",
                "Percentual: {}%".format(percent[0]),
            ])
        ))

        # ADICIONANDO A BARRA DE ESTRATÉGIA DEFINIDA
        fig.add_trace(go.Bar(
            x=[keys[1]],
            y=[values[1]],
            name='Recomendação alterada',
            marker_color='#00CC96',
            text=[values[1]],
            textposition='outside',
            texttemplate='%{text} agências' if values[
                                                   1] != 1 else '%{text} agência',
            hovertemplate="<br>".join([
                "Recomendação alterada",
                "Quantidade: %{y}",
                "Percentual: {}%".format(percent[1]),
            ])
        ))

        """
        fig = go.Figure([go.Bar(x=keys, 
                                y=values, 
                                text=values, 
                                textposition='outside', 
                                orientation='v')])
        """

        """
        # ATUALIZANDO AS CORES DAS BARRAS
        fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                          marker_line_width=1.5, opacity=0.8)
        """

        # INCLUINDO TÍTULO E LEGENDAS
        fig.update_layout(
            title="Preenchimento realizado para {}/{} agências".format(total_acao_usuario, total_agencias),
            title_x=0.03,
            xaxis_tickfont_size=14,
            yaxis=dict(
                title='Quantidade de agências',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=1.0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ))

        # ATUALIZANDO LAYOUT DA FIGURA
        fig.update_layout(
            autosize=False,
            width=width,
            height=height,
            margin=dict(
                l=100,
                r=50,
                b=100,
                t=100,
                pad=50
            ),
            paper_bgcolor=paper_bgcolor,
        )

        # REMOVENDO O GRID
        fig.update_layout(xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=False)
                          )

    except Exception as ex:
        logger.error("ERRO NA FUNÇÃO - {} - {}".format(stack()[0][3], ex))

    return fig

def get_pie_plot_fill_recomendations_status(data,
                                            column_status,
                                            column_regiao=None,
                                            width=300,
                                            height=300,
                                            paper_bgcolor=None,
                                            layout_showlegend=False):
    """

    OBTÉM UM PIE PLOT
    COM O PERCENTUAL DE DISTRIBUIÇÃO POR STATUS

    # Arguments
        data                    - Required: Dados para plotar (DataFrame)
        column_status			- Required: Coluna de status (String)
        column_regiao           - Optional: Coluna de região (String)
        width                   - Optional: Largura da imagem (Integer)
        height                  - Optional: Altura da imagem (Integer)
        paper_bgcolor           - Optional: Cor do background da imagem.
                                            Deve ser um valor rgb ou hex (String)

    # Returns
        validator               - Required: Validador da função (Boolean)
        fig                     - Required: Figura Plotly (Plotly fig)
    """

    # INICIANDO O VALIDADOR DA FUNÇÃO
    validator = False

    # INICIANDO O GRÁFICO PLOT
    fig = px.bar()

    try:
        if column_regiao is None:
            # OBTENDO A TABELA DE FREQUÊNCIA POR STATUS
            df_groupby = data.stb.freq(
                [column_status])
        else:
            # OBTENDO A TABELA DE FREQUÊNCIA POR STATUS E REGIÃO
            df_groupby = data.stb.freq([column_status, column_regiao])

        # VERIFICANDO SE HÁ VALOR PARA PLOTAR
        if not df_groupby[df_groupby[column_status] != ""].empty:

            # APLICANDO TRATAMENTO NOS DADOS
            df_groupby[column_status] = df_groupby[column_status].replace({"": "Nenhuma alteração"})

            # CRIANDO O PIE PLOT
            fig = px.pie(df_groupby, values='count',
                         names=column_status, color=column_status,
                         color_discrete_map={'VERDE': '#008744',
                                             'AMARELA': '#ffa700',
                                             'VERMELHA': '#d62d20'},
                         hole=.3)

            # ATUALIZANDO O TEXTO DO GRÁFICO
            fig.update_traces(hoverinfo='all',
                              textinfo='label+value+percent',
                              textfont_size=14,
                              textposition='outside')

            # ATUALIZANDO LAYOUT DA FIGURA
            fig.update_layout(
                autosize=False,
                width=width,
                height=height,
                margin=dict(
                    l=50,
                    r=50,
                    b=100,
                    t=100,
                    pad=4
                ),
                paper_bgcolor=paper_bgcolor,
            )

            # ATUALIZANDO A LEGENDA
            fig.update(layout_showlegend=layout_showlegend)

            validator = True

    except Exception as ex:
        logger.error("ERRO NA FUNÇÃO - {} - {}".format(stack()[0][3], ex))

    return validator, fig