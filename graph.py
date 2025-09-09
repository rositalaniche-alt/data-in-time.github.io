from table import *
from dash import html, dcc, callback, ctx, no_update, Input, Output
from dash.exceptions import PreventUpdate
from plotly import graph_objects as go
import plotly.express as px
import dash_daq as daq

# -----------------------------------------------------------------------------------------------------------------------------------------
countries_list = sorted([country for country in data['country'].unique().to_list()])
options =[
    {"label": country, "value": country}
    for country in countries_list
]
currencies_list = data['currency'].unique().to_list()

# Years
years_list = sorted(data['year'].unique().to_list())

graph = html.Div(
    id='container_graph',
    children=[
        html.Div(
            id='graph_selection_menu',
            children=[
                html.Div(
                    id='currency_selection_menu',
                    children=[
                        html.P(
                            'Currency: '
                        ),
                        *[
                            html.Button(
                                currency.title(),
                                className='currency_btn',
                                id=f'{currency}_btn'
                            )
                            for currency in currencies_list
                        ],
                        dcc.Store(
                            id='store_currency',
                            data={'currency': 'dollar'},
                            storage_type='session',
                        )
                    ]
                ),
                dcc.Dropdown(
                    id='dropdown_countries',
                    options=options,
                    value=['Colombia'],
                    style={'width': '500px'},
                    multi=True,
                ),
                
            ]
        ),
        dcc.Graph(id='graph'),
        html.Div(
            id='container_range_years',
            children=[
                html.Button(
                    int(min(data['year'])),
                    className='button_range_years'
                ),
                dcc.RangeSlider(
                    min(data['year'].to_list()), 
                    max(data['year'].to_list()), 
                    1,
                    value=[2000, 2020],
                    marks=None,
                    id ='range_years',
                    tooltip={"placement": "top"},
                    updatemode='drag',
                ),
                html.Button(
                    int(max(data['year'])),
                    className='button_range_years'
                ),
                html.Div(
                    id='container_playback_speed',
                    children=[
                        html.Button(
                            id='btn_playback_speed',
                            value='pause',
                        ),
                        dcc.Slider(
                            0.5, 2 , 0.5,
                            value=1,
                            id='slider_playback_speed',
                            marks=None,
                            tooltip={"placement": "top"},
                        ),
                        daq.BooleanSwitch(
                            id='',
                            on=False,
                            label='Loop',
                            labelPosition='left',
                            color='green',
                        )
                    ]
                ),
            ]
        ),

    ]
)

# ----------------------------------------------------------------------------------------------------------------------------------
@callback(
    # Cambiar el estilo del boton seleccionado
    [
        Output(f'{currency}_btn', 'style')
        for currency in currencies_list
    ],
    # Guardar la seleccion entre dollar y loca
    Output('store_currency', 'data'),
    # Obtener el boton seleccionado
    [
        Input(f'{currency}_btn', 'n_clicks')
        for currency in currencies_list
    ],
)
def currencies_style_button(*inputs):
    triggered = ctx.triggered_id
    
    style_not_selected = {'background': 'none'}
    style_selected = {'background': 'black', 'color': 'white'}
    
    # Si no se ha seleccionado ninguna divisa, estableces la divisa de dollar por defecto
    if not triggered:
        currencies_buttons_styles = [style_selected if currency == currencies_list[0] else style_not_selected for currency in currencies_list]
        store_currency =  [no_update]
        result = currencies_buttons_styles + store_currency
        return result
    
    triggered = triggered.replace('_btn', '')
    print('Selected currency:', triggered)
    
    currencies_buttons_styles = [style_selected if currency == triggered else style_not_selected for currency in currencies_list] 
    store_currency = [{'currency': triggered}]
    result = currencies_buttons_styles + store_currency
    
    print(result)
    return result

# -------------------------------------------------------------------------------------------------------------------------------------------
@callback(
    Output('graph', 'figure'),
    Input('dropdown_countries', 'value'),
    Input('range_years', 'value'),
    Input('store_currency', 'data')
)
def update_graph(selected_countries, selected_years, selected_currency):
    
    selected_currency = selected_currency['currency']
    print('Selected currency:', selected_currency)
    print('Selected countries:', selected_countries)
    print('Selected years:', selected_years)
    
    selected_years = [year for year in range(min(selected_years), max(selected_years) + 1, 1)]
    
    if not selected_countries:
        print('No country has been selected.')
        raise PreventUpdate
    
    # Obtener los paises seleccionados
    new_data = data.filter(pl.col('country').is_in(selected_countries))
    
    # Obtener el tipo de divisa
    new_data = new_data.filter(pl.col('currency') == selected_currency)
    
    # Obtener los years
    new_data = new_data.filter(pl.col('year').is_in(selected_years))
    
    fig = px.line(
        new_data,
        x='year',
        y='value',
        color='country',
        markers=True,
        hover_name='country',
        title='Minimum Wages by Country: Global Data'
    )
    
    fig.update_layout(
        template='plotly_dark'
    )
    return fig

# -------------------------------------------------------------------------------------------------------------------------------------------

@callback(
    Output('btn_playback_speed', 'value'),
    Output('btn_playback_speed', 'children'),
    Input('btn_playback_speed', 'n_clicks'),
    Input('btn_playback_speed', 'value')
)
def playback(n_clicks, btn_play_back_speed_value):
    play = 'play'
    pause = 'pause'
    if not n_clicks:
        return '▶️', pause
    
    if btn_play_back_speed_value == pause:
        return play, '▶️'
    elif btn_play_back_speed_value == play:
        return pause, '⏸️'