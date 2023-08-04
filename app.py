import os
from pathlib import Path

import streamlit as st
from dynaconf import settings
from loguru import logger

from utils.streamlit_functions import add_logo
from app_pages import page_plan_estrategico, page_agencias

# CONFIGURANDO O APP
st.set_page_config(
    page_title="FOOTPRINT - PLANEJAMENTO ESTRATÉGICO",
    page_icon=":world-map:",
    layout="wide",
)


def main(authenticator, username):
    if st.session_state.get("authentication_status"):
        # OBTENDO AS INFOS DO USUÁRIO LOGADO
        infos_username_log = st.session_state["users"]["usernames"][username]

        logger.debug("USUÁRIO LOGADO: {}".format(infos_username_log))

        # ADICIONANDO TITULO DA PÁGINA
        # st.title("APP - PLANEJAMENTO ESTRATÉGICO")

        # OBTENDO O DIRETÓRIO DO LOGO
        dir_logo = settings.get("LOGO_APP")

        # ADICIONANDO LOGO
        add_logo(dir_logo, width=100, location="sidebar", position_image="left")

        with st.sidebar:
            st.markdown("Bem vindo: {}".format(infos_username_log["name"]))

            # CRIANDO UMA LINHA EM BRANCO
            st.divider()

            # ESTUDO DESEJADO
            st.title("Defina o estudo desejado")

            options_estudos = [
                "Plan. Estratégico",
                "Agências",
            ]

            selected_estudo_desejado = st.radio(
                label="Estudo desejado",
                options=options_estudos,
                index=0,
                key=None,
                help="Escolha o estudo desejado e na página central aparecerá novas opções",
                on_change=None,
                disabled=False,
                horizontal=False,
                label_visibility="visible",
            )

            # CRIANDO UMA LINHA EM BRANCO
            st.divider()

            # BOTÃO DE LOGOUT
            authenticator.logout("Sair", "main", key="app_page")

        # DEFININDO A PÁGINA DESEJADA
        if selected_estudo_desejado == "Plan. Estratégico":
            # CARREGANDO A PÁGINA DE AUTOSSERVIÇO
            page_plan_estrategico.load_page_plan_estrategico()

        elif selected_estudo_desejado == "Agências":
            # CARREGANDO A PÁGINA DE AGÊNCIAS
            page_agencias.load_page_agencias()

        else:
            st.empty()
