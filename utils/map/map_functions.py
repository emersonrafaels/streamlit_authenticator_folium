import numbers
from os import path
from pathlib import Path
from inspect import stack

import branca
import pandas as pd
import folium
import streamlit as st
from folium.plugins import MarkerCluster
from dynaconf import settings
from loguru import logger

from utils.generic_functions import calculate_time_usage, convert_to_number


dir_root = Path(__file__).absolute().parent.parent.parent

def download_folium_map(mapobj):

    """

        REALIZA O DOWNLOAD DE UM OBJETO FOLIUM (MAP)
        EM FORMATO HTML

        # Arguments
            mapobj          - Required: Objeto (Map) folium para realizar download (Object)

        # Returns
            processed_map   - Reqired: Mapa em formato HTML (HTML)

    """

    processed_map = mapobj._repr_html_()

    return processed_map


def convert_df_html(
    row_df,
    col_header=None,
    left_col_color="#140083",
    right_col_color="#140083",
    left_text_color="#FFFFFF",
    right_text_color="#FFFFFF",
):
    # INICIANDO A VARIÁVEL DE RETORNO
    html = ""

    # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ AS TABLES
    html_table = ""

    html_header = (
        """<!DOCTYPE html>
      <html>
      <head>
        <h4 style="margin-bottom:10"; width="200px">{}</h4>""".format(
            row_df.get(col_header)
        )
        + """
        <style>
      table {
        border:1px solid #b3adad;
        border-collapse:collapse;
        padding:5px;
        font-family: inherit;
      }
      table th {
        border:1px solid #b3adad;
        padding:5px;
        background: #f0f0f0;
        color: #313030;
      }
      table td {
        border:1px solid #b3adad;
        text-align:center;
        padding:5px;
        background: #ffffff;
        color: #313030;
      }
    </style>
      </head>
          <table style="height: 126px; width: 350px;">
      <tbody>
    """
    )

    # VERIFICANDO SE O ARGUMENTO É UM DICT
    if isinstance(row_df, (dict, pd.Series)):
        # PERCORRENDO O DICT
        for key, value in row_df.items():
            html_table += (
                """
        <tr>
        <td style="background-color: """
                + left_col_color
                + ";font-weight: bold"
                """;"><span style="color: text_left_color_to_replace;">key_to_replace</span></td>
        <td style="width: 150px;background-color: """
                + right_col_color
                + """;"><span style="color: right_left_color_to_replace;">value_to_replace</span></td>
        </tr>
      """
            )
            html_table = html_table.replace("key_to_replace", str(key)).replace(
                "value_to_replace", str(value)
            )
            html_table = html_table.replace(
                "text_left_color_to_replace", str(left_text_color)
            ).replace("right_left_color_to_replace", str(right_text_color))

        # UNINDO OS HTML
        html = "{}{}".format(html_header, html_table)

    return html


def get_icon(dict_icons=None, status=None):
    """

    FUNÇÃO PARA OBTER O ICON QUE SERÁ MARCADO NO MAPA

    A FUNÇÃO PODE RECEBER UM DICT DE ICONS, ESSE DICT DE ICONS TEM:

    1. CHAVE: DETERMINADO TIPO
    2. VALOR: A IMAGEM PARA A RESPECTIVA CHAVE

    # Arguments
        dict_icons         - Required: Dicionário contendo os icons (Dict)
        status             - Required: Status desejado para
                                       condicinar a escolha do icon (String)

    # Returns
        current_icon       - Required: Icon definido (Folium Object)

    """

    try:
        # INICIALIZANDO O ICON DEFAULT
        icon_default = str(
            Path(dir_root, settings.get("MAP_ICON_DEFALT", "assets/itau.logo"))
        )

        # VERIFICANDO SE O ICON DEFAULT EXISTE
        if not path.exists(icon_default):
            icon_default = "ok-sign"

        if dict_icons:
            # VERIFICANDO SE O STATUS CONSTA NO DICT DE ICONS
            if str(status) in dict_icons() and path.exists(dict_icons.get(str(status))):
                current_icon = folium.features.CustomIcon(
                    icon_image=dict_icons.get(str(status), icon_size=(16, 16))
                )

                return current_icon

        if str(status).upper() in settings.get("MAP_DICT_ICON_DEFAULT", {}):
            current_icon = folium.features.CustomIcon(
                icon_image=str(
                    Path(
                        dir_root, settings.get("MAP_DICT_ICON_DEFAULT").get(str(status))
                    )
                ),
                icon_size=(16, 16),
            )

        else:
            current_icon = folium.features.CustomIcon(
                icon_image=icon_default, icon_size=(16, 16)
            )

    except Exception as ex:
        logger.error("ERRO NA FUNÇÃO: {} - {}".format(stack()[0][3], ex))

        current_icon = folium.features.CustomIcon(
            icon_image=icon_default, icon_size=(16, 16)
        )

    return current_icon


def get_name_tooltip(data, name_column_tooltip, sep=" - "):
    """
    DEFINE O NOME QUE SERÁ APRESENTADO NO TOOLTIP.

    CASO:
        1. name_column_tooltip seja string, é esperado que
           seja apenas uma coluna do Dataframe)

        2. name_column_tooltip seja list ou tuple, é esperado que
           seja apenas mais de uma coluna do Dataframe e portanto
           será obtido uma junção dessas colunas, separados pelo char
           definido pela variável 'sep'.


    # Arguments
        data                    - Required: Dataframe contendo os dados (DataFrame)
        name_column_tooltip     - Required: Lista de colunas desejadas
                                            para ser tooltip (String | List | Tuple)
        sep                     - Required: Separador usado caso o
                                            name_column_tooltip seja iterável (String)

    # Returns
        value_tooltip           - Required: Tooltip obtido (String)

    """

    # VERIFICANDO SE O NOME DA COLUNA DESEJADA PARA SER TOOLTIP É STRING
    if isinstance(name_column_tooltip, str):
        # VERIFICANDO SE A COLUNA CONSTA NO DATAFRAME
        if name_column_tooltip in data.keys():
            return data[name_column_tooltip]

    # VERIFICANDO SE O NOME DA COLUNA DESEJADA PARA SER TOOLTIP É ITERÁVEL
    elif isinstance(name_column_tooltip, (tuple, list)):
        # VERIFICANDO SE A COLUNA CONSTA NO DATAFRAME
        return sep.join(
            [str(value) for value in data.filter(items=name_column_tooltip)]
        )
    else:
        return name_column_tooltip


@calculate_time_usage
def load_map(
    data=None,
    map_layer_default="openstreetmap",
    circle_radius=0,
    validator_add_layer=False,
    column_status=None,
    save_figure=True,
    map_save_name="PLOT_MAP.html",
    dict_icons=None,
    validator_marker_cluster=False,
    column_marker_cluster=None,
    column_latitude="LATITUDE",
    column_longitude="LONGITUDE",
    name_column_tooltip="AGENCIA",
    name_column_header="NOME AG",
):
    def add_layers_control(mapobj, validator_add_layer=False):
        if validator_add_layer:
            # ADICIONANDO OS LAYERS
            folium.TileLayer("openstreetmap").add_to(mapobj)
            folium.TileLayer("Stamen Terrain").add_to(mapobj)
            folium.TileLayer("Stamen Toner").add_to(mapobj)
            folium.TileLayer("Cartodb dark_matter").add_to(mapobj)
            folium.TileLayer("cartodbpositron").add_to(mapobj)

            # ADICIONANDO LAYER CONTROL
            folium.LayerControl().add_to(mapobj)

        return mapobj

    def add_markers(mapobj, data=None, circle_radius=0):
        # VERIFICANDO SE HÁ UM DATAFRAME ENVIADO COMO ARGUMENTO
        if data is not None:
            # VERIFICANDO SE HÁ UM SOMBREAMENTO A SER DESENHADO
            if circle_radius > 0:
                """
                CONVERTENDO O RAIO DE SOMBREAMENTO PARA M
                NO INPUT DA TELA, O COLABORADOR INCLUI EM KM
                PARA REFLETIR NO CIRCLEMARKER
                É NECESSÁRIO CONVERTER PARA M
                1km = 1000m
                """
                circle_radius = circle_radius * 1000

                # OBTENDO O TEXTO DO TOOLTIP QUE VAI SER COLOCADO NO SOMBREAMENTO
                name_tooltip_sombreamento = settings.get(
                    "NAME_TOOLTIP_SOMBREAMENTO", ""
                )

                logger.info(
                    "ATUALIZANDO O MAPA - SOMBREAMENTO - {} m".format(circle_radius)
                )

            if validator_marker_cluster:
                # CRIANDO O CLUSTER
                marker_cluster = MarkerCluster(name="CLUSTER",
                                               overlay=True,
                                               control=True).add_to(mapobj)

                # OS MARCADORES SÃO ADICIONADOS AO CLUSTER
                obj_marker = marker_cluster

            else:
                # OS MARCADORES SÃO ADICIONADOS AO MAPA
                obj_marker = mapobj

            # PERCORRENDO O DATAFRAME
            for idx, row in data.iterrows():
                # OBTENDO O STATUS
                status = row.get(column_status)

                # OBTENDO LATTUDE E LONGITUDE
                lat = row.get(column_latitude)
                long = row.get(column_longitude)

                if (isinstance(lat, numbers.Number) and not pd.isna(lat)) and (
                    isinstance(long, numbers.Number) and not pd.isna(long)
                ):
                    # OBTENDO O HTML DO ICON
                    html = convert_df_html(
                        row_df=row,
                        col_header=name_column_header,
                        left_col_color="#140083",
                        right_col_color="#140083",
                        left_text_color="#FF7200",
                        right_text_color="#FFFFFF",
                    )

                    iframe = branca.element.IFrame(html=html, width=510, height=280)
                    popup = folium.Popup(iframe, max_width=500)

                    current_icon = get_icon(dict_icons, status)

                    folium.Marker(
                        location=[lat, long],
                        popup=popup,
                        icon=current_icon,
                        tooltip=get_name_tooltip(
                            data=row, name_column_tooltip=name_column_tooltip, sep=" - "
                        ),
                        lazy=True,
                    ).add_to(obj_marker)

                    # VALIDANDO SE É DESEJADO ADICIONAR CIRCLEMARKER
                    if circle_radius > 0:
                        folium.CircleMarker(
                            location=[lat, long],
                            radius=circle_radius,
                            color="crimson",
                            fill="orange",
                            opacity=0.3,
                            tooltip="{}{}".format(
                                name_tooltip_sombreamento, row[name_column_header]
                            ),
                        ).add_to(obj_marker)

        if validator_marker_cluster:
            # ADICIONANDO O CLUSTER AO MAPA
            obj_marker.add_to(mapobj)

        return mapobj

    if column_latitude in data.columns and column_longitude in data.columns:

        logger.info("INICIANDO A CONSTRUÇÃO DO MAPA COM {} DADOS".format(len(data)))

        # GARANTINDO COLUNAS DE LATITUDE E LONGITUDE EM FORMATO FLOAT
        for column in [column_latitude, column_longitude]:
            data[column] = data[column].apply(lambda x: convert_to_number(value_to_convert=x,
                                                                          type=float))

        # REMOVENDO VALORES NONE DA COLUNA DE LATITUDE E LONGITUDE
        data = data[(~data[column_latitude].isna()) & (~data[column_longitude].isna())]

        logger.info(
            "VALIDAÇÃO PARA CONSTRUÇÃO DO MAPA: {} DADOS".format(len(data)))

        # CRIANDO O MAPA
        footprint_map = folium.Map(
            location=[data[column_latitude].mean(),
                      data[column_longitude].mean()],
            zoom_start=4,
            tiles=map_layer_default,
        )

        # ADICIONANDO LAYERS
        footprint_map = add_layers_control(
            mapobj=footprint_map, validator_add_layer=validator_add_layer
        )

        # ADICIONANDO MAKERS
        footprint_map = add_markers(
            mapobj=footprint_map, data=data, circle_radius=circle_radius
        )

        if save_figure:
            footprint_map.save(map_save_name)
            logger.info("MAPA SALVO COM SUCESSO")

        validator = True

        return validator, footprint_map, data

    return False, None, None
