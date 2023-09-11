from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode


def get_numeric_style_with_precision(precision: int) -> dict:
    return {"type": ["numericColumn", "customNumericFormat"], "precision": precision}


PRECISION_ZERO = get_numeric_style_with_precision(0)
PRECISION_ONE = get_numeric_style_with_precision(1)
PRECISION_TWO = get_numeric_style_with_precision(2)
PINLEFT = {"pinned": "left"}
LEN_DEFAULT_PAGINATION = 10
MAX_TABLE_HEIGHT = 500
THEMES = ["streamlit", "light", "blue", "dark", "fresh", "material"]


def draw_grid(
    df,
    formatter: dict = None,
    selection="multiple",
    use_filterable=True,
    use_groupable=True,
    use_checkbox=False,
    use_Pivot=False,
    enableValue=False,
    enableRowGroup=False,
    fit_columns=False,
    validator_all_rows_selected=False,
    validator_enable_enterprise_modules=False,
    theme="streamlit",
    max_height: int = MAX_TABLE_HEIGHT,
    wrap_text: bool = False,
    auto_height: bool = False,
    grid_options: dict = None,
    key=None,
    css: dict = None,
):
    gb = GridOptionsBuilder()
    gb.configure_default_column(
        filterable=use_filterable,
        groupable=use_groupable,
        editable=False,
        wrapText=wrap_text,
        autoHeight=auto_height,
        enablePivot=use_Pivot,
        enableValue=enableValue,
        enableRowGroup=enableRowGroup,
    )

    if len(df) > LEN_DEFAULT_PAGINATION:
        # CONFIGURE PAGINATION
        gb.configure_pagination(
            paginationAutoPageSize=True, paginationPageSize=LEN_DEFAULT_PAGINATION
        )

    # CONFIGURE SIDEBAR OPTIONS
    gb.configure_side_bar(filters_panel=True, columns_panel=True, defaultToolPanel="")

    if grid_options is not None:
        gb.configure_grid_options(**grid_options)

    if formatter is not None and isinstance(formatter, dict):
        if "columnDefs" in formatter.keys():
            for value in formatter.get("columnDefs"):
                field = value["field"]
                header = value["headerName"]
                type = value["type"]

                print(
                    "APLICANDO CONFIGURAÇÃO DE CAMPO PARA - {} - {} - {}".format(
                        field, header, type
                    )
                )

                gb.configure_column(field, header_name=header, type=type)

    # Enable multi-row selection
    print(selection)
    print(use_checkbox)
    gb.configure_selection(selection_mode=selection, use_checkbox=use_checkbox)

    # VALIDANDO SE É DESEJADO QUE TODAS AS LINHAS INICIEM SELECIONADAS
    if validator_all_rows_selected:
        gb.configure_selection("multiple", pre_selected_rows=list(range(len(df))))

    # VALIDANDO O TEMA
    if theme not in THEMES:
        theme = "streamlit"

    return AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=fit_columns,
        height=min(max_height, (1 + len(df.index)) * 29),
        theme=theme,
        enable_enterprise_modules=validator_enable_enterprise_modules,
        key=key,
        custom_css=css,
    )


def highlight(color, condition):
    code = f"""
        function(params) {{
            color = "{color}";
            if ({condition}) {{
                return {{
                    'backgroundColor': color
                }}
            }}
        }};
    """
    return JsCode(code)
