import os

import pandas as pd
from loguru import logger
from dynaconf import settings


def read_credentials_excel(dir_credential_excel, col_index=None):
    """

    FUNÇÃO PARA REALIZAR A LEITURA DO EXCEL
    CONTENDO AS CREDENCIAIS

    # Arguments
        dir_credential_excel      - Required: Diretório do excel de credenciais (Path)
        col_index                 - Required: Nome da coluna contendo o user (String)

    # Returns

    """

    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ AS CREDENCIAIS
    credentials_usernames = {"usernames": ""}

    logger.info("INICIANDO A LEITURA DAS CREDENCIAIS")

    # VERIFICANDO SE O ARQUIVO EXCEL EXISTE
    if os.path.exists(dir_credential_excel):
        # REALIZANDO A LEITURA DO EXCEL
        df = pd.read_excel(dir_credential_excel)

        # VALIDANDO SE É DESEJADO RENOMEAR AS COLUNAS DO DATAFRAME
        if settings.get("VALIDATOR_RENAME_CREDENTIALS"):
            # VERIFICANDO SE O DICT É DIFERENTE DE NONE
            if settings.get("AUTHENTICATION_CREDENTIALS_INDEX_DICT_RENAME"):
                # APLICANDO O DICT RENAME
                df = df.rename(
                    columns=settings.get("AUTHENTICATION_CREDENTIALS_INDEX_DICT_RENAME")
                )

        # OBTENDO O DADO EM FORMATO DICT
        credentials = df.to_dict(orient="records")

        # DEFININDO A COLUNA DE USER
        if col_index is not None and col_index in df.columns:
            # OBTENDO TODAS AS CREDENCIAIS
            credentials = {
                credential[col_index]: credential for credential in credentials
            }

            # ATUALIZANDO O DICT DE CREDENCIAIS
            credentials_usernames = {"usernames": credentials}

    else:
        logger.error("O DIR DE CREDENCIAIS ESTÁ INCORRETO")

    return credentials_usernames
