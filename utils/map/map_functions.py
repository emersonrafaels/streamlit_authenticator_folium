import branca
import pandas as pd
import folium
import streamlit as st

from utils.generic_functions import calculate_time_usage


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


@calculate_time_usage
def load_map(data=pd.DataFrame(), circle_radius=0, validator_add_layer=False):

    def add_layers_control(mapobj, validator_add_layer=False):
        if validator_add_layer:
            # ADICIONANDO OS LAYERS
            folium.TileLayer("Stamen Terrain").add_to(mapobj)
            folium.TileLayer("Stamen Toner").add_to(mapobj)
            folium.TileLayer("Cartodb dark_matter").add_to(mapobj)

            # ADICIONANDO LAYER CONTROL
            folium.LayerControl().add_to(mapobj)

        return mapobj

    def add_markers(mapobj, data=None, circle_radius=0):
        # VERIFICANDO SE HÁ UM DATAFRAME ENVIADO COMO ARGUMENTO
        if data is not None:
            # PERCORRENDO O DATAFRAME
            for idx, row in data.iterrows():
                # OBTENDO O CÓDIGO DA AGÊNCIA
                cod_ag = row.get("CÓDIGO AG")

                # OBTENDO O STATUS
                status = row.get("STATUS")

                # OBTENDO LATITUDE E LONGITUDE
                lat = row.get("LATITUDE")
                long = row.get("LONGITUDE")

                # OBTENDO O HTML DO ICON
                html = convert_df_html(
                    row_df=row,
                    col_header="ENDEREÇO",
                    left_col_color="#140083",
                    right_col_color="#140083",
                    left_text_color="#FF7200",
                    right_text_color="#FFFFFF",
                )
                iframe = branca.element.IFrame(html=html, width=510, height=280)
                popup = folium.Popup(folium.Html(html, script=True), max_width=500)

                if str(status).upper() == "VERMELHA":
                    current_icon = folium.features.CustomIcon(
                        icon_image="assets/itau_vermelho.png", icon_size=(16, 16)
                    )
                elif str(status).upper() == "AMARELA":
                    current_icon = folium.features.CustomIcon(
                        icon_image="assets/itau_amarelo.png", icon_size=(16, 16)
                    )
                else:
                    current_icon = folium.features.CustomIcon(
                        icon_image="assets/itau_verde.png", icon_size=(16, 16)
                    )

                folium.Marker(
                    location=[lat, long], popup=popup, icon=current_icon, lazy=True
                ).add_to(mapobj)

                if circle_radius > 0:
                    folium.CircleMarker(
                        location=[lat, long],
                        radius=circle_radius,
                    ).add_to(mapobj)

        return mapobj

    if not data.equals(st.session_state.get('current_selected_dataframe')):

        print("ENTROU NO RELOAD DO MAPA")

        # CRIANDO O MAPA
        footprint_map = folium.Map(
            location=[-15.768857589354258, -47.905384728712384],
            zoom_start=4,
            tiles="openstreetmap",
        )

        # ADICIONANDO LAYERS
        footprint_map = add_layers_control(
            mapobj=footprint_map, validator_add_layer=validator_add_layer
        )

        # ADICIONANDO MAKERS
        footprint_map = add_markers(
            mapobj=footprint_map, data=data, circle_radius=circle_radius
        )

        # ARMAZENANDO DATAFRAME ATUAL NO SESSION STATE
        st.session_state['current_selected_dataframe'] = data

        # ARMAZENANDO MAPA ATUAL NO SESSION STATE
        st.session_state['mapa_autosservico'] = footprint_map

        return footprint_map

    else:
        return st.session_state.get('mapa_autosservico')
