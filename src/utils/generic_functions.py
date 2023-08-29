import typing
from datetime import datetime
from inspect import stack

from loguru import logger


def is_integer_string(value):
    """

    VALIDA SE UM VALOR STRING É POSSÍVEL DE CONVERTER EM INTEGER

    # Arguments
        value             - Required: Valor para verificar (String)

    # Returns
        validador         - Required: Validador. True para é possível
                                                 converter para integer (String)

    """

    try:
        return value.isdigit() or (value[0] == "-" and value[1:].isdigit())
    except Exception as ex:
        return False


def is_float_string(s):
    """

    VALIDA SE UM VALOR STRING É POSSÍVEL DE CONVERTER EM FLOAT

    # Arguments
        value             - Required: Valor para verificar (String)

    # Returns
        validador         - Required: Validador. True para é possível
                                                 converter para Float (String)

    """

    try:
        float(s)
        return True
    except ValueError:
        return False


def validator_convert_number(string):
    """

    VALIDA SE UM VALOR STRING É POSSÍVEL DE CONVERTER EM INTEGER OU FLOAT

    # Arguments
        value             - Required: Valor para verificar (String)

    # Returns
        value_converted   - Required: Valor após conversão.
                                      Retorna None, caso não seja
                                      possível converter (Int | Float)

    """

    if is_float_string(string):
        return float(string)
    elif is_integer_string(string):
        return int(string)
    else:
        return None


def convert_to_number(value_to_convert, type):
    """

    FUNÇÃO PARA CONVERTER UM VALOR PARA
    TIPO NUMÉRICO (integer, float)

    # Arguments
        value_to_convert    - Required: Valor a ser convertido (Object)
        type                - Required: Tipo desejado (typing)

    # Returns
        value_converted     - Required: Valor após conversão (Integer | Float)

    """

    if type in [float, int]:
        if isinstance(value_to_convert, (float, int)):
            return value_to_convert
        elif isinstance(value_to_convert, str):
            return validator_convert_number(value_to_convert)
        else:
            return None
    else:
        logger.error("TIPOS NÃO ACEITOS NA FUNÇÃO - {}".format(stack()[0][3]))


def calculate_time_usage(func):
    def nestes_function(*args, **kwargs):
        # OBTENDO O TEMPO DE INÍCIO
        init_time = datetime.now()

        # EXECUTANDO A FUNÇÃO
        result = func(*args, **kwargs)

        # OBTENDO O TEMPO DE FIM
        end_time = datetime.now()

        # OBTENDO O TEMPO DE EXECUÇÃO DA FUNÇÃO
        delta_time = end_time - init_time

        print(f"{func.__name__} demorou {delta_time.total_seconds()} segundos.")

        return result

    return nestes_function
