import os

import pandas as pd
from loguru import logger
from dynaconf import settings


def read_credentials_excel(dir_credential_excel, col_index=None):
    # INICIANDO A VARIÁVEL QUE ARMAZENARÁ AS CREDENCIAIS
    credentials_usernames = {"usernames": ""}

    logger.info("INICIANDO A LEITURA DAS CREDENCIAIS")

    # REALIZANDO A LEITURA DO EXCEL
    if os.path.exists(dir_credential_excel):
        df = pd.read_excel(dir_credential_excel)

        # VALIDANDO SE É DESEJADO RENOMEAR AS COLUNAS DO DATAFRAME
        if settings.get("VALIDATOR_RENAME_CREDENTIALS"):
            # OBTENDO O DICT PARA RENAME
            dict_rename = settings.get("AUTHENTICATION_CREDENTIALS_INDEX_DICT_RENAME")

            # VERIFICANDO SE O DICT É DIFERENTE DE NONE
            if dict_rename:
                # APLICANDO O DICT RENAME
                df = df.rename(columns=dict_rename)

        # OBTENDO O DADO EM FORMATO DICT
        credentials = df.to_dict(orient="records")

        # DEFININDO O INDEX
        if col_index is not None and col_index in df.columns:
            credentials = {
                credential[col_index]: credential for credential in credentials
            }
            credentials_usernames = {"usernames": credentials}

    else:
        logger.error("O DIR DE CREDENCIAIS ESTÁ INCORRETO")

    return credentials_usernames
