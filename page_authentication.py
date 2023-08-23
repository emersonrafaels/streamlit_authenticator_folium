import base64
import yaml
from time import sleep
from pathlib import Path
from yaml.loader import SafeLoader

import streamlit as st
from dynaconf import settings
from loguru import logger

import utils.authenticator.authenticator as stauth
from app import main as main_app
from utils.authenticator.read_credentials import read_credentials_excel


def get_credentials():

    """

        FUNÇÃO PARA OBTER AUXILIAR
        A VERIFICAÇÃO DE CREDENCIAL
        DE UM USUÁRIO AO TENTAR
        LOGAR NO APP

        # Arguments

        # Returns
            authenticator          - Required: Retorna as configurações e
                                               credenciais para funcionamento
                                               da autenticação (stauth)

    """

    logger.info("INICIANDO A OBTENÇÃO DAS CREDENTIAIS")

    # OBTENDO CREDENCIAIS DO ARQUIVO EXCEL
    credentials = read_credentials_excel(
        dir_credential_excel=settings.get("AUTHENTICATION_CREDENTIALS"),
        col_index=settings.get("AUTHENTICATION_CREDENTIALS_INDEX"),
    )

    # OBTENDO AS CONFIGURAÇÕES PARA AS CREDENCIAIS
    with open(settings.AUTHENTICATION_CONFIG) as file:
        config_credentials = yaml.load(file, Loader=SafeLoader)

    # DEFININDO O AUTHENTICATOR
    authenticator = stauth.Authenticate(
        credentials,
        config_credentials["cookie"]["app_name"],
        config_credentials["cookie"]["key"],
        config_credentials["cookie"]["expiry_days"],
        config_credentials["preauthorized"],
    )

    return authenticator


def main_authenticator():

    """

        FUNÇÃO QUE ORQUESTRA A AUTENTICAÇÃO

        # Arguments

        # Returns

    """

    # APLICANDO O STYLE CSS

    # OBTENDO AS CREDENCIAIS
    logger.info("OBTENDO AS CREDENCIAIS")
    authenticator = get_credentials()

    if not st.session_state.get("authentication_status"):

        logger.info("CRIANDO TELA DE LOGIN")

        # OBTENDO OS USUÁRIOS
        st.session_state["users"] = authenticator.credentials

        # OBTENDO O DIRETÓRIO DO LOGO
        dir_logo = str(Path(Path(__file__).absolute().parent,
                            settings.LOGO_APP))

        # CODIFICANDO A IMAGEM EM BASE64
        dir_logo = base64.b64encode(open(dir_logo, "rb").read())

        # CRIANDO O WIDGET DE LOGIN
        name, authentication_status, username = authenticator.login(
            form_name=settings.get("APPNAME_TELA_LOGIN",
                                   "APP - PLANEJAMENTO ESTRATÉGICO"),
            location="main",
            form_name_username=settings.get("FORM_NAME_USERNAME", "Email"),
            form_name_password=settings.get("FORM_NAME_PASSWORD", "Senha"),
            form_name_button=settings.get("FORM_NAME_BUTTON", "Entrar"),
            validator_insert_image=True,
            image=dir_logo,
            width_image=100,
            location_image="main",
            position_image="center",
        )

    # VERIFICANDO SE O USER E O PASSWORD ESTÃO CORRETOS
    if st.session_state.get("authentication_status"):
        logger.debug(
            "LOGIN REALIZADO POR: NOME: {} - USERNAME: {}".format(st.session_state["name"],
                                                                  st.session_state["username"])
        )

        # ENTRANDO NO APP
        main_app(authenticator, st.session_state["username"])

    elif st.session_state["username"] in [None, ""] and authentication_status is False:
        st.warning("Por favor, inserir usuário e senha")

    elif authentication_status is False:
        st.error("Usuário ou senha estão incorretos")

    elif authentication_status is None:
        st.warning("Por favor, inserir usuário e senha")
