import polars as pl
from dash import html, dcc
# --------------------------------------------------------------------------------------------------------------

# Obtenerdatos
data = pl.read_csv('files/data_1.csv')
column_name = {
    "ref_area.label": "country",
    "classif1.label": "currency",
    "time": "year",
    "obs_value": "value",
}

# Renombrar columnas
data = data.rename(
    column_name
).select([
    name for name in column_name.values()
]).filter(
    pl.col('currency') != 'Currency: 2021 PPP $'  
)

# Cambiar valores a mas cortos

data = data.with_columns(
    pl.col("currency").replace({
        "Currency: Local currency": "local",
        "Currency: U.S. dollars": "dollar",
    })
)

column_defs = [
    {"field": "country", "filter": "agSetColumnFilter"},
    {"field": "currency", "filter": "agSetColumnFilter",},
    {"field": "year", "filter": "agSetColumnFilter"},
    {"field": "value", "filter": "agSetColumnFilter"},
]

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
        dag.AgGrid(
            id='table',
            rowData=data.to_dicts(),
            columnDefs=column_defs,
            className='ag-theme-alpine-dark',
            style={'width': '800px',}
        ),
'''