import base64
from io import BytesIO

import streamlit as st


def add_logo(
    logo_url: str,
    width: int = 50,
    location="sidebar",
    local_form=None,
    position_image="center",
):
    """

    FUNÇÃO CUJO OBJETIVO É ADICIONAR UM LOGO NO SIDEBAR
    DO APP STREAMLIT.

    RECEBE UMA IMAGEM EM:
      URL DA WEB
      PATH DA MÁQUINA

    A IMAGEM PODE SER INSERIDA EM
    USANDO O PARÂMETRO (location):
        1. main
        2. sidebar (default)

    A IMAGEM PODE SER POSICIONADA
    USANDO O PARÂMETRO (position_image):
        1. LEFT
        2. CENTER
        3. RIGHT

    # Arguments
      logo_url             - Required: Local onde está a imagem (String)
      width                - Optional: Largura da imagem (Integer)
      location             - Optional: Local onde a imagem será inserida (String)
      local_form           - Optional: Formulário para a imagem ser inserida.
                                       Caso None, a imagem não é inserida em
                                       nenhum form streamlit (Object)
      position_image         - Optional: Posição da imagem (String)

    """

    # VERIFICANDO SE A IMAGEM ESTÁ EM BYTES
    if isinstance(logo_url, bytes):
        logo_url = BytesIO(base64.b64decode(logo_url))

    if local_form is None:
        if location == "main":
            col1, col2, col3 = st.columns(3)
        else:
            col1, col2, col3 = st.sidebar.columns(3)

        with col1:
            if position_image == "left":
                col1.image(image=logo_url, width=width)
            else:
                st.write(" ")

        with col2:
            if position_image == "center":
                col2.image(image=logo_url, width=width)
            else:
                st.write(" ")

        with col3:
            if position_image == "right":
                col3.image(image=logo_url, width=width)
            else:
                st.write(" ")

    else:
        col1, col2, col3 = local_form.columns(3)
        with col1:
            if position_image == "left":
                col1.image(image=logo_url, width=width)
            else:
                st.write(" ")

        with col2:
            if position_image == "center":
                col2.image(image=logo_url, width=width)
            else:
                st.write(" ")

        with col3:
            if position_image == "right":
                col3.image(image=logo_url, width=width)
            else:
                st.write(" ")
