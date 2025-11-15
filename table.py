import polars as pl
from dash import html, dcc
# --------------------------------------------------------------------------------------------------------------

# Obtenerdatos
data = pl.read_excel('files/data_1.xlsx')
data = data.with_columns(
    pl.col("value").cast(pl.Float64)
)


table = html.Div(
    id='container_table',
    children=[
        html.P(
            children='Minimum Wages by Country: Global Data',
            className='titule_table',
        ),
    ]
)

'''
column_defs = [
    {"field": "country", "filter": "agSetColumnFilter"},
    {"field": "currency", "filter": "agSetColumnFilter",},
    {"field": "year", "filter": "agSetColumnFilter"},
    {"field": "value", "filter": "agSetColumnFilter"},
]

        dag.AgGrid(
            id='table',
            rowData=data.to_dicts(),
            columnDefs=column_defs,
            className='ag-theme-alpine-dark',
            style={'width': '800px',}
        ),
'''