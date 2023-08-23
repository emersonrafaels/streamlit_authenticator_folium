import os
from pathlib import Path

import streamlit as st
from dynaconf import settings
from loguru import logger

from utils.streamlit_functions import add_logo
from app_pages import page_plan_estrategico, page_agencias

# CONFIGURANDO O APP
st.set_page_config(
    page_title=settings.get("APPNAME_TITLE",
                            "FOOTPRINT - PLANEJAMENTO ESTRATÉGICO"),
    page_icon=settings.get("APPNAME_TITLE_ICON",
                            ":world-map:"),
    layout="wide",
)

def main(authenticator, username):

    # APLICANDO O STYLE CSS
    st.markdown('<style>.css-1v0mbdj.ebxwdo61{margin-left: 0px;}</style>',
                unsafe_allow_html=True)

    # VERIFICANDO SE O USUÁRIO ESTÁ AUTENTICADO
    if st.session_state.get("authentication_status"):

        # VERIFICANDO SE O USUÁRIO CONSTA CORRETAMENTE NA LISTA DE USERNAMES
        if username in st.session_state["users"]["usernames"]:

            # OBTENDO AS INFOS DO USUÁRIO LOGADO
            infos_username_log = st.session_state["users"]["usernames"][username]

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
                st.title("Escolha a página desejada")

                options_estudos = [
                    "Plan. Estratégico",
                    "Agências",
                ]

                selected_estudo_desejado = st.radio(
                    label="Visão desejada",
                    options=options_estudos,
                    index=0,
                    key=None,
                    help="Escolha a visão desejado e na página central aparecerão novas informações",
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

        else:
            # CASO OCORRA ALGUM ERRO DE AUTENTICAÇÃO
            st.session_state["authentication_status"] = False

            # APARECE O BOTÃO DE SAIR, PARA PERMITIR LIMPEZA DO COOKIE
            authenticator.logout("Sair", "main", key="app_page")
