from datetime import datetime

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

        print(f'{func.__name__} demorou {delta_time.total_seconds()} segundos.')

        return result

    return nestes_function