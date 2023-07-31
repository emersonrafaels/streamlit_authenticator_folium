import os
from pathlib import Path

import streamlit as st
from dynaconf import settings

from utils.streamlit_functions import add_logo

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

        # ADICIONANDO TITULO DA PÁGINA
        st.title("APP - FOOTPRINT - GESTÃO DO PARQUE DE AGÊNCIAS")

        # OBTENDO O DIRETÓRIO DO LOGO
        dir_logo = settings.get("LOGO_APP")

        # ADICIONANDO LOGO
        add_logo(dir_logo, width=100, location='sidebar', position_image='left')

        with st.sidebar:

            st.markdown("Bem vindo: {}".format(infos_username_log["name"]))

            authenticator.logout('Sair', 'main', key='unique_key')

