from pathlib import Path

import streamlit as st
from PIL import Image

from src.utils.streamlit_functions import add_logo

# OBTENDO O DIRETÓRIO DO LOGO
dir_logo = Image.open(str(Path(Path(__file__).parent, "src/assets/itau.png")))


with st.form("my_form"):

	# ADICIONANDO LOGO
	column_left, column_center, column_right = st.columns(3)
	with column_center:
		st.image(image=dir_logo, width=100)

	st.write("Login")

	st.text_input(label="Username :",
				 value="",
				 key="user")
	st.text_input(label="Password :",
				 value="",
				 key="pwd",
				 type="password")

	# Every form must have a submit button.
	submitted = st.form_submit_button("Entrar")

	if submitted:
	   print("Logado")