from table import *
from dash import html, dcc, callback, ctx, no_update, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px

# -----------------------------------------------------------------------------------------------------------------------------------------
countries_list = sorted([country for country in data['country'].unique().to_list()])
options =[
    {"label": country, "value": country}
    for country in countries_list
]
currencies_list = data['currency'].unique().to_list()

# Years
years_list = sorted(data['year'].unique().to_list())

chart = html.Div(
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
                    style={'width': '100%', 'color': 'black'},
                    multi=True,
                ),
                
            ]
        ),
        dcc.Graph(id='graph',),
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
                        dcc.Interval(
                            id='interval_playback_speed', 
                            interval=1000,
                            disabled=True,
                        ),
                        html.Button(
                            '▶️',
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
                        html.Div(
                            dcc.Checklist(
                                id='loop_playback_speed',
                                options=[{'label': 'Loop', "value": 'loop'}],
                                value=['loop'],
                                inline=True,
                                style={'display': 'flex'}
                            )
                        ),
                    ]
                ),
            ]
        ),
    ]
)


texto = '''
This project compiles the historical values of the minimum wage for the period from 1980 to 2025, expressed in both U.S. dollars and the local currency.

The minimum wage is defined as the legally mandated minimum compensation that employers are required to pay workers, intended to ensure the fulfillment of their basic needs and guarantee a decent standard of living.
'''
description = html.Div(
    style={'width': '100%'},
    children=[
        html.P(
            texto,
            className='description',
        )
    ]

)

graph = html.Div(
    style={'color': 'white', 'background': 'rgb(34, 34, 53)', 'display': 'flex', 'flex-direction': 'column', },
    children=[
        description,
        chart,
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
#Actualizar el icono del btn de reproduccion y el estado del dcc.Interval()
max_range_years = max(data['year'])
min_range_years = min(data['year'])

@callback(
    Output('btn_playback_speed', 'children'),
    Output('interval_playback_speed', 'disabled'),
    Output('range_years', 'value'),
    Output('interval_playback_speed', 'interval'),
    Input('btn_playback_speed', 'n_clicks'),
    Input('interval_playback_speed', 'n_intervals'),
    State('btn_playback_speed', 'children'),
    State('range_years', 'value'),
    State('loop_playback_speed', 'value'),
    State('slider_playback_speed', 'value'),
    prevent_initial_call=True,
)
def update_states_playback(n_clicks, n_intervals, value_playback_speed, range_years, loop, speed_slider):
    
    btn_playback = disabled = updated_range_years = interval = no_update
    
    play, pause = '▶️', '⏸️'
    
    triggered = ctx.triggered_id
    
    # Cuando se presione el boton de play
    if triggered == 'btn_playback_speed':
        if value_playback_speed == play:
            
            # El rango de los years se encuentra a el maximo, retablecer a sus valores minimos
            if range_years[1] == max_range_years:
                updated_range_years = [min_range_years, min_range_years]
            else:
                updated_range_years = no_update
            
            btn_playback = pause; disabled = False
        
        elif value_playback_speed == pause:
            btn_playback = play; disabled = True; updated_range_years = no_update
    
    # Cuando el bucle este activado
    elif triggered == 'interval_playback_speed':
        
        # Cuando el bucle llegue al valor maximo del range_years
        if range_years[1] == max_range_years:
            # Si el bucle esta activo
            if loop:
                btn_playback = no_update
                disabled = no_update
                updated_range_years = [min_range_years, min_range_years]
            else: 
                btn_playback = play
                disabled = True
                updated_range_years = no_update
        
        # bucle funcionando normalmente
        else:
            btn_playback = pause
            disabled = no_update
            updated_range_years = [range_years[0], range_years[1] + 1]
            interval = 1000/speed_slider
    
    return btn_playback, disabled, updated_range_years, interval



'''
                            daq.ToggleSwitch(
                                id='loop_playback_speed',
                                value=False,
                                color="#4F57C2",
                            ),
'''