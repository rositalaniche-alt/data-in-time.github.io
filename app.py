from dash import Dash, html, dcc, callback, Input, Output, ctx, no_update

# --------------------------------------------------------------------------------------------------------------
from table import *
from graph import *
# --------------------------------------------------------------------------------------------------------------

list_buttons = ['graph', 'table',]

buttons = html.Div(
    id='container_buttons',
    children=[
        html.Button(
            children=button.title(),
            id='button_' + button,
            className='button'
        )
        for button in list_buttons
    ]
)

# -----------------------------------------------------------------------------------------------------------------------------------------

app = Dash()
server = app.server

app.layout = html.Div(id='main', children=[
    buttons,
    table,
    graph,
])

# ----------------------------------------------------------------------------------------------------------------------------------
@callback(
    # Cambiar classes de los botones del menu principal
    [
        Output(f'button_{button}', 'className')
        for button in list_buttons
    ],
    # Mostrar contenido con base en el boton seleccionado del menu principal
    [
        Output(f'container_{content}', 'style')
        for content in list_buttons
    ],
    # Obtener el boton seleccionado del menu principal
    [
        Input(f'button_{button}', 'n_clicks')
        for button in list_buttons
    ]
)
def update_button_selected(*inputs):
    triggered_id = ctx.triggered_id
    
    btn_selected = 'button button_selected'
    btn_not_selected = 'button button_not_selected'
    
    style_main_content_not_selected = {'display': 'none'}
    style_main_content_selected = {'display': 'flex'}
    
    # Cuando no sea seleccionado un boton del menu principal
    if not triggered_id:
        # Clases botones del menu principal
        classes_buttons_menu = [
            btn_selected if button == list_buttons[0] 
            else btn_not_selected 
            for button in list_buttons
        ]
        
        # Estilos del cotenido principal
        styles_main_content = [
            style_main_content_selected if button == list_buttons[0] 
            else style_main_content_not_selected
            for button in list_buttons
        ]
        
        result = classes_buttons_menu + styles_main_content
        return result
    
    triggered_id = triggered_id.replace('button_', '')
    
    # Cuando se selecciono un boton del menu principla
    print(f'Be selected: {triggered_id}')
    
    # Clases botones
    classes_buttons_menu = [
        btn_selected if button == triggered_id 
        else btn_not_selected 
        for button in list_buttons
    ]
    
    styles_main_content = [
        style_main_content_selected if triggered_id == button
        else style_main_content_not_selected
        for button in list_buttons
    ]
    
    result = classes_buttons_menu + styles_main_content
    return result

if __name__ == '__main__':
    app.run()