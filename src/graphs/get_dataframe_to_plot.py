from dynaconf import settings


def get_current_status(status_atual, status_recomendacao):
    return_status_recomendacao = ("RECOMENDAÇÃO INICIAL", status_recomendacao)
    return_status_atual = ("ESTRATÉGIA DEFINIDA", status_atual)

    if isinstance(status_atual, str):
        if status_atual == "" or status_atual is None:
            return return_status_recomendacao
    elif isinstance(status_atual, float):
        if np.isnan(status_atual):
            return return_status_recomendacao

    return return_status_atual


def get_fill_recomendation(data):
    """

    OBTÉM UM DADOS PARA PLOTAR O GRÁFICO
    COM O PERCENTUAL DE PREENCHIMENTO
    DAS RECOMENDAÇÕES
    VERSUS
    O TOTAL DE AGÊNNCIAS DISPONÍVEIS PARA
    PREENCHIMENTO

    # Arguments
            data                    - Required: Dados para plotar (DataFrame)

    """

    # OBTENDO UMA CÓPIA DO DATAFRAME ORIGINAL
    df_plot = data.copy()

    # CRIANDO DUAS COLUNAS AUXILIARES
    # A PRIMEIRA CONTÉM SE A RECOMENDAÇÃO ATUAL É A INICIAL OU ALTERADA PELO USUÁRIO
    # A SEGUNDA CONTÉM QUAL A ESTRATÉGIA ATUAL PARA A AGÊNCIA
    df_plot["MOMENTO ESTRATÉGIA ATUAL"], df_plot["ESTRATÉGIA ATUAL"] = zip(
        *df_plot.apply(
            lambda x: get_current_status(
                x[settings.get("COL_SAVE_ACTION", "ESTRATÉGIA SELECIONADA")],
                x[settings.get("COLUMN_STATUS", "STATUS")],
            ),
            axis=1,
        )
    )

    return df_plot
