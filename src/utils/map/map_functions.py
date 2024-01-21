import numbers
from os import path
from pathlib import Path
from inspect import stack

import branca
import pandas as pd
import folium
import streamlit as st
import streamlit.components.v1 as components
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from loguru import logger

try:
    from utils.generic_functions import calculate_time_usage, convert_to_number
    from config_app.config_app import settings
except ModuleNotFoundError:
    from src.utils.generic_functions import calculate_time_usage, convert_to_number
    from src.config_app.config_app import settings

dir_root = Path(__file__).absolute().parent.parent.parent

from branca.element import Template, MacroElement


def add_caterical_legend_draggable(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))

    template = """
  {% macro html(this, kwargs) %}

  <!doctype html>
  <html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>jQuery UI Draggable - Default functionality</title>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

    <script>
    $( function() {
      $( "#maplegend" ).draggable({
                      start: function (event, ui) {
                          $(this).css({
                              right: "auto",
                              top: "auto",
                              bottom: "auto"
                          });
                      }
                  });
  });

    </script>
  </head>
  <body>

  <div id='maplegend' class='maplegend'
      style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
      border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>"""

    template2 = f"""
  <div class='legend-title'>{title}</div>
  <div class='legend-scale'>
    <ul class='legend-labels'>"""

    for label, color in color_by_label.items():
        template2 = (
            template2
            + f"<li><span style='background:{color};opacity:0.7;'></span>{label}</li>"
        )

    template2 = (
        template2
        + """
    </ul>
  </div>
  </div>
  """
    )

    template3 = """
  </body>
  </html>

  <style type='text/css'>
    .maplegend .legend-title {
      text-align: left;
      margin-bottom: 5px;
      font-weight: bold;
      font-size: 90%;
      }
    .maplegend .legend-scale ul {
      margin: 0;
      margin-bottom: 5px;
      padding: 0;
      float: left;
      list-style: none;
      }
    .maplegend .legend-scale ul li {
      font-size: 80%;
      list-style: none;
      margin-left: 0;
      line-height: 18px;
      margin-bottom: 2px;
      }
    .maplegend ul.legend-labels li span {
      display: block;
      float: left;
      height: 16px;
      width: 30px;
      margin-right: 5px;
      margin-left: 0;
      border: 1px solid #999;
      }
    .maplegend .legend-source {
      font-size: 80%;
      color: #777;
      clear: both;
      }
    .maplegend a {
      color: #777;
      }
  </style>
  {% endmacro %}"""

    html_result = template + template2 + template3

    macro = MacroElement()
    macro._template = Template(html_result)

    folium_map.get_root().add_child(macro)

    return folium_map, html_result


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


def folium_static(
    fig,
    width: int = 700,
    height: int = 500,
    add_categorical_legend=False,
    title_legend="Legenda",
    list_categories=[],
    list_colors=[],
):
    """
    Renders `folium.Figure` or `folium.Map` in a Streamlit app. This method is
    a static Streamlit Component, meaning, no information is passed back from
    Leaflet on browser interaction.
    Parameters
    ----------
    fig  : folium.Map or folium.Figure
        Geospatial visualization to render
    width : int
        Width of result
    Height : int
        Height of result
    Note
    ----
    If `height` is set on a `folium.Map` or `folium.Figure` object,
    that value supersedes the values set with the keyword arguments of this function.

    Example
    -------
    >>> m = folium.Map(location=[45.5236, -122.6750])
    >>> folium_static(m)
    """

    # if Map, wrap in Figure
    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)

        if add_categorical_legend:
            fig, _ = add_caterical_legend_draggable(
                folium_map=fig,
                title=title_legend,
                labels=list_categories,
                colors=list_colors,
            )

        return components.html(
            fig.render(), height=(fig.height or height) + 10, width=width
        )

    # if DualMap, get HTML representation
    elif isinstance(fig, folium.plugins.DualMap) or isinstance(
        fig, branca.element.Figure
    ):
        return components.html(fig._repr_html_(), height=height + 10, width=width)

    if add_categorical_legend:
        fig, _ = add_caterical_legend_draggable(
            folium_map=fig,
            title=title_legend,
            labels=list_categories,
            colors=list_colors,
        )

    return st_folium(fig, width=width, height=height, returned_objects=[])


def convert_df_html(
    row_df,
    col_header=None,
    left_col_color="#140083",
    right_col_color="#140083",
    left_text_color="#FFFFFF",
    right_text_color="#FFFFFF",
):
    # INICIANDO A VARIÁVEL DE RETORNO
    html_table = html_init = html_header = html = ""

    # INICIANDO A VARIÁVEL AUXILIAR QUE ARMAZENARÁ AS TABLES
    value_li = ""

    html_init = (
        """<!DOCTYPE html>
      <html>
      <head>
        """
        + """
        <style>
        @import url('https://fonts.googleapis.com/css?family=Open+Sans');

        * {
          box-sizing: border-box;
        }
        
        body {
          background-color: #f6f5f7;
          font-family: 'Open Sans', sans-serif;
          margin-bottom: 50px;
          font-size: 12px;
          max-width: 500px;
        }
        
        .text-center {
          text-align: center;
          min-width: 100px;
          max-width: 500px;
        }
        
        .pricing-box-container {
          display: flex;
          align-items: center;
          justify-content: center;
          flex-wrap: wrap;
        }
        
        .pricing-box {
          background-color: #ffffff;
          box-shadow: 0px 2px 15px 0px rgba(0,0,0,0.5);
          border-radius: 4px;
          flex: 1;
          padding: 0 30px 30px;
          margin: 2%;
          min-width: 100px;
          max-width: 250px;
        }
        
        .pricing-box h5 {
          text-transform: uppercase;
        }
        
        .price {
          margin: 24px 0;
          font-size: 36px;
          font-weight: 900;
        }
        
        .price sub, .price sup {
          font-size: 16px;
          font-weight: 100;
        }
        
        .features-list {
          padding: 0;
          list-style-type: none;
        }
        
        .features-list li {
          font-weight: 100;
          padding: 12px 0;
          font-weight: 100;
        }
        
        .features-list li:not(:last-of-type) {
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .btn-primary {
          border-radius: 25px;
          border: none;
          background-color: #EC1362;
          color: #ffffff;
          cursor: pointer;
          padding: 10px 15px;
          margin-top: 20px;
          text-transform: uppercase;
          transition: all 0.1s ease-in-out;
        }
        
        .btn-primary:hover {
          box-shadow: 0px 2px 15px 0px rgba(0,0,0,0.5);
          transform: translateY(-3px);
        }
        
        .pricing-box-bg-image {
          background-image: url('https://images.unsplash.com/photo-1550029402-226115b7c579?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=701&q=80');
          background-size: cover;
          background-position: center center;
          color: #ffffff;
        }
        
        .pricing-box-bg-image .features-list li {
          border-bottom-color: rgba(255, 255, 255, 1);
        }
        
        .pricing-box-bg-image .btn-primary {
          background-color: #ffffff;
          color: #000;
        }
        
        footer {
          background-color: #222;
          color: #fff;
          font-size: 14px;
          bottom: 0;
          position: fixed;
          left: 0;
          right: 0;
          text-align: center;
        }
        
        footer p {
          margin: 10px 0;
        }
        
        footer i {
          color: red;
        }
        
        footer a {
          color: #3C97BF;
          text-decoration: none;
        }
        </style>
      </head>
      <tbody>
    """
    )

    html_header = """
        <h1 class="text-center">NOME_AGENCIA</h1>
        """.replace("NOME_AGENCIA", str(row_df.get(col_header)))

    # VERIFICANDO SE O ARGUMENTO É UM DICT
    if isinstance(row_df, (dict, pd.Series)):
        # PERCORRENDO O DICT
        for key, value in row_df.items():
            value_li += "<li><strong>{}</strong>: {}</li>\n".format(key, value)

        html_table += (
                """
       <div class="pricing-box-container">
      <div class="pricing-box text-center">
        <h5>Platinum</h5>
        <p class="price"><sup>$</sup>89<sub>/mo</sub></p>
        <ul class="features-list">
          values_li
        </ul>
      </div>
    </div>""".replace("values_li", str(value_li)))


    # UNINDO OS HTML
    html = "{}{}{}".format(html_init, html_header, html_table)

    return html


def convert_df_htmlx(
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
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
      }
      table th {
        padding: 12px 15px;
      }
      table td {
        padding: 12px 15px;
      }
      table tr {
        background-color: #009879;
        color: #ffffff;
        text-align: left;
      }
      tbody tr {
        border-bottom: 1px solid #dddddd;
      }
      tbody tr:nth-of-type(even) {
          background-color: #f3f3f3;
      }
      tbody tr:last-of-type {
          border-bottom: 2px solid #009879;
      }
      tbody tr.active-row {
        font-weight: bold;
        color: #009879;
      }
      leaflet-popup-content{
        width: 400px;
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

def get_icon(dict_icons=None, status=None, return_default=False):
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

    dict_icons = {"VERMELHA": "assets/itau_vermelho.png",
                  "AMARELA": "assets/itau_amarelo.png",
                  "VERDE": "assets/itau_verde.png"}

    try:
        # INICIALIZANDO O ICON DEFAULT
        icon_default = str(
            Path(dir_root, settings.get("MAP_ICON_DEFAULT", "assets/itau.logo"))
        )

        # VERIFICANDO SE O ICON DEFAULT EXISTE
        if not path.exists(icon_default):
            return folium.Icon("ok-sign")

        if return_default:

            current_icon = folium.features.CustomIcon(
                icon_image=icon_default, icon_size=(16, 16)
            )

            return current_icon

        if dict_icons:
            # VERIFICANDO SE O STATUS CONSTA NO DICT DE ICONS
            if str(status) in dict_icons and path.exists(dict_icons[str(status)]):
                current_icon = folium.features.CustomIcon(
                    icon_image=dict_icons.get(str(status), icon_size=(16, 16))
                )

                return current_icon

        if str(status).upper() in dict_icons:
            current_icon = folium.features.CustomIcon(
                icon_image=str(
                    Path(
                        dir_root, dict_icons.get(str(status))
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
                marker_cluster = MarkerCluster(
                    name="CLUSTER", overlay=True, control=True
                ).add_to(mapobj)

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

                    iframe = branca.element.IFrame(html=html, width=400, height=280)
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

    # SALVANDO O DATAFRAME DE INPUT
    original_data = data.copy()

    if column_latitude in data.columns and column_longitude in data.columns:
        logger.info("INICIANDO A CONSTRUÇÃO DO MAPA COM {} DADOS".format(len(data)))

        # GARANTINDO COLUNAS DE LATITUDE E LONGITUDE EM FORMATO FLOAT
        for column in [column_latitude, column_longitude]:
            data[column] = data[column].apply(
                lambda x: convert_to_number(value_to_convert=x, type=float)
            )

        # REMOVENDO VALORES NONE DA COLUNA DE LATITUDE E LONGITUDE
        data = data[(~data[column_latitude].isna()) & (~data[column_longitude].isna())]

        logger.info(
            "APÓS VALIDAÇÃO PARA CONSTRUÇÃO DO MAPA: {} DADOS".format(len(data))
        )

        # CRIANDO O MAPA
        footprint_map = folium.Map(
            location=[data[column_latitude].mean(), data[column_longitude].mean()],
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

        # ADICIONANDO O EXPANDIR
        folium.plugins.Fullscreen(
            position="topright",
            title="Expand me",
            title_cancel="Exit me",
            force_separate_button=True,
        ).add_to(footprint_map)

        # ADICIONANDO O GEOCODER
        folium.plugins.Geocoder().add_to(footprint_map)

        if save_figure:
            footprint_map.save(map_save_name)
            logger.info("MAPA SALVO COM SUCESSO")

        validator = True

        return validator, footprint_map, original_data

    return False, None, original_data
