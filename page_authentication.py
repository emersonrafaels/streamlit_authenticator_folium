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
    logger.info("INICIANDO A OBTENÇÃO DAS CREDENTIAIS")

    # OBTENDO CREDENCIAIS
    credentials = read_credentials_excel(
        dir_credential_excel=settings.get("AUTHENTICATION_CREDENTIALS"),
        col_index=settings.get("AUTHENTICATION_CREDENTIALS_INDEX"),
    )

    # OBTENDO CONFIG CREDENCIAIS
    with open(settings.AUTHENTICATION_CONFIG) as file:
        config_credentials = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        credentials,
        config_credentials["cookie"]["name"],
        config_credentials["cookie"]["key"],
        config_credentials["cookie"]["expiry_days"],
        config_credentials["preauthorized"],
    )

    return authenticator


def main_authenticator():

    # OBTENDO AS CREDENCIAIS
    logger.info("OBTENDO AS CREDENCIAIS")

    authenticator = get_credentials()

    if not st.session_state.get("authentication_status"):

        logger.info("CRIANDO TELA DE LOGIN")

        st.session_state["users"] = authenticator.credentials

        # OBTENDO O DIRETÓRIO DO LOGO
        dir_logo = str(Path(Path(__file__).absolute().parent, settings.LOGO_APP))
        # CODIFICANDO A IMAGEM EM BASE64
        dir_logo = base64.b64encode(open(dir_logo, "rb").read())

        # CRIANDO O WIDGET
        name, authentication_status, username = authenticator.login(
            form_name="Footprint - Autosserviços",
            location="main",
            form_name_username="Usuário",
            form_name_password="Senha",
            form_name_button="Entrar",
            validator_insert_image=True,
            image=dir_logo,
            width_image=100,
            location_image="main",
            position_image="center",
        )

    # VERIFICANDO O LOGIN
    if st.session_state.get("authentication_status"):
        logger.debug(
            "LOGIN REALIZADO POR: NOME: {} - USERNAME: {}".format(st.session_state["name"],
                                                                  st.session_state["username"])
        )

        # st.success("Login realizado com sucesso")
        # sleep(2)
        main_app(authenticator, st.session_state["username"])
    elif st.session_state["username"] in [None, ""] and authentication_status is False:
        st.warning("Por favor, inserir usuário e senha")
    elif authentication_status is False:
        st.error("Usuário ou senha estão incorretos")
    elif authentication_status is None:
        st.warning("Por favor, inserir usuário e senha")
