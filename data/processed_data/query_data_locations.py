from pathlib import Path

import pandas as pd

from utils.api import api_geopy

# DEFININDO DIRETÓRIO CONTENDO OS DADOS DESEJADOS
dir_root = Path(__file__).absolute().parent.parent
dir_data = str(Path(dir_root, "footprint_agencias.xlsx"))

# REALIZANDO A LEITURA DO DATAFRAME
df = pd.read_excel(dir_data)
# OBTENDO A LISTA DE ENDEREÇOS
list_locations = list(df["ENDEREÇO"])

# INSTANCIANDO A API
api = api_geopy.API_GEOPY()

# OBTENDO AS INFORMAÇÕES DE LAT E LONG USANDO OS ENDEREÇOS
result = api.get_information_using_address(locations=list_locations)

# ATUALIZANDO OS ENDEREÇOS
# LATITUDE, LONGITUDE
lat_long = [value[1] if value is not None else (0, 0) for key, value in result.items()]
df["LATITUDE"] = [value[0] for value in lat_long]
df["LONGITUDE"] = [value[1] for value in lat_long]