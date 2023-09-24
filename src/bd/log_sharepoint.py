try:
    from config_app.config_app import settings
except Exception as ex:
    from src.config_app.config_app import settings

import sqlite3
from pathlib import Path

from loguru import logger

dir_root = Path(__file__).parent.parent

def execute_log_sharepoint(username, password):

	# Conectar ao banco de dados

	if 1 == 2:
		conn = sqlite3.connect(str(Path(dir_root,
										settings.get("BD_SHAREPOINT"))))

		# Criar um cursor para executar comandos SQL
		cursor = conn.cursor()

		# Executar a consulta SELECT
		cursor.execute("""SELECT *
	  FROM USERS
	 WHERE USERNAME = {email} AND 
		   PASSWORD = {password};
	""".format(email=username, password=password))

		# Obter os resultados
		resultados = cursor.fetchall()

		# Fechar a conexão com o banco de dados
		conn.close()

		if len(resultados) > 0:
			return True
		else:
			return False
	else:
		return True
