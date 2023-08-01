from inspect import stack

from geopy.geocoders import Nominatim

class API_GEOPY():

    def __init__(self):

        # INIT GEOPY
        self.geolocator = Nominatim(user_agent="myGeocoder")

    def get_information(self, locations, verbose=False):

        # INICIANDO DICT PARA ARMAZENAR RESULTADOS
        dict_result = {}

        # VERIFICANDO A TIPAGEM
        if isinstance(locations, str):
            locations = [locations]

        # PERCORRENDO CADA UM DOS ENDEREÇOS ENVIADOS
        for location in locations:

            try:
                # CHAMANDO A API
                result_location = geolocator.geocode(location)

                # SALVANDO O RESULTADO
                dict_result[location] = result_location

                if verbose:
                    raw_information = location.raw
                    latitude, longitude = location.latitude, location.longitude
                    print(f"{Endereço}: Latitude {latitude}, Longitude {longitude}")
                    print(raw_information)
            except Exception as ex:
                print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return dict_result