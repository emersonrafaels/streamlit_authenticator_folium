from inspect import stack

from geopy.geocoders import Nominatim


class API_GEOPY:

    """

    PERMITE OBTER INFORMAÇÕES
    DE LOCALIZAÇÃO
    USANDO ENDEREÇO
    OU LATITUDE E LONGITUDE.

    1. USANDO ENDEREÇO PARA
       OBTER INFORMAÇÕES: get_information_using_address
    2. USANDO LATITUDE E LONGITUDE
       PARA OBTER INFORMAÇÕES: get_information_using_lat_long

    """

    def __init__(self):
        # INIT GEOPY
        self.geolocator = Nominatim(user_agent="myGeocoder")

    def get_information_using_address(self, locations, verbose=False):
        """

        PERMITE OBTER INFORMAÇÕES
        DE LOCALIZAÇÃO
        USANDO ENDEREÇO

        # Arguments
            locations        - Required: Endereço ou
                                         lista de Endereços (String | Tuple | List)

        # Returns
            dict_result      - Required: Dict contendo a lista de endereços (Dict)

        """

        # INICIANDO DICT PARA ARMAZENAR RESULTADOS
        dict_result = {}

        # VERIFICANDO A TIPAGEM
        if isinstance(locations, str):
            locations = [locations]

        # PERCORRENDO CADA UM DOS ENDEREÇOS ENVIADOS
        for location in locations:
            try:
                # CHAMANDO A API
                result_location = self.geolocator.geocode(location)

                # SALVANDO O RESULTADO
                dict_result[location] = result_location

                if verbose:
                    raw_information = location.raw
                    latitude, longitude = location.latitude, location.longitude
                    print(f"{location}: Latitude {latitude}, Longitude {longitude}")
                    print(raw_information)
            except Exception as ex:
                print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return dict_result

    def get_information_using_lat_long(self, lat, long, verbose=False):
        """

        PERMITE OBTER INFORMAÇÕES
        DE LOCALIZAÇÃO
        USANDO LATITUDE E LONGITUDE

        # Arguments
            lat              - Required: Valor da latitude (Float)
            long             - Required: Valor da longitude (Float)

        # Returns
            dict_result      - Required: Dict contendo a lista de endereços (Dict)

        """

        # INICIANDO DICT PARA ARMAZENAR RESULTADOS
        dict_result = {}

        # VERIFICANDO A TIPAGEM
        if isinstance(lat, float) and isinstance(long, float):
            location = [lat, long]

        try:
            # CHAMANDO A API
            result_location = self.geolocator.reverse(location)

            # SALVANDO O RESULTADO
            dict_result[location] = result_location

            if verbose:
                raw_information = location.raw
                endereco = location.address
                print(f"{location}: Endereço {endereco}")
                print(raw_information)
        except Exception as ex:
            print("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        return dict_result
