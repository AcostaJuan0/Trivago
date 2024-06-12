import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Cargar datos del archivo CSV
data = pd.read_csv("C:/Users/DaliaRachell/PycharmProjects/pythonProject/datasets/hoteles.csv", sep=';')

# Creacion de la aplicación Dash
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True)

# Layout de la pestaña de información
layout_info = html.Div(style={'padding': '20px', 'font-size': '30px'}, children=[
    html.H1([
        html.Span("Mejores Hoteles ", style={'color': 'rgb(18, 145, 210)'}),
        html.Span("para Visitar ", style={'color': 'rgb(252, 158, 22)'}),
        html.Span("en México", style={'color': 'rgb(227, 64, 61)'})
    ], style={'textAlign': 'center'}),
    html.Br(),
    html.H2("UNIVERSIDAD AUTÓNOMA DEL ESTADO DE BAJA CALIFORNIA", style={'textAlign': 'center'}),
    html.H2("Facultad de Contaduría y Administración", style={'textAlign': 'center', 'color': 'rgb(252, 158, 22)'}, ),
    html.H2("Programación para la extracción de datos", style={'textAlign': 'center', 'color': 'rgb(227, 64, 61)'}),
    html.H2("Integrantes:", style={'textAlign': 'center'}),
    html.Ul([
        html.Li("Acosta Cuevas Juan Felipe."),
        html.Li("Escudero Mariscal Dalia Rachell."),
        html.Li("Garcia Silva Luis Daniel."),
        html.Li("Santiago Gonzalez Rodolfo Goku."),
        html.Li("Trejo Silva Jesus Ignacio.")
    ], style={'textAlign': 'center', 'listStylePosition': 'inside'}),
    html.H2("Grupo 951", style={'textAlign': 'center', 'color': 'rgb(252, 158, 22)'}),
    html.H2("Docente:", style={'textAlign': 'center', 'color': 'rgb(227, 64, 61)'}),
    html.Ul([
        html.Li("Josue Miguel Flores Parra.")
    ], style={'textAlign': 'center', 'listStylePosition': 'inside'}),
    html.H2("Objetivos"),
    html.Ul([
        html.Li("Visualizar la relación entre calificación y precio por noche."),
        html.Li("Identificar los hoteles con más opiniones de clientes."),
        html.Li("Analizar la distribución de calificaciones por ciudad."), ]),
    html.Br(),
    html.P([
        "Datos extraidos de ",
        html.A("Trivago", href="https://www.trivago.com", target="_blank"),
        "."
    ]),
])


# Layout del Dashboard 1
layout_dashboard_1 = html.Div(style={'backgroundColor': '#f2f2f2', 'padding': '20px'}, children=[
    html.H1("Dashboard 1: Relación entre Calificación y Precio", style={'color': '#124192'}),
    html.P("Estamos explorando si hay una relación entre la calificación promedio de los hoteles"
           " y sus precios promedio por noche en diversas ciudades de México. ¿Qué significa esto? Básicamente, queremos "
           "averiguar si los hoteles que reciben calificaciones más altas también tienden a tener precios más altos por noche, y viceversa.", style={'font-size': '25px'}),
    html.Div(id='slider-container', children=[
        html.Label('Precio por Noche:'),
        dcc.RangeSlider(
            id='price-slider',
            min=data['Precio por noche'].min(),
            max=data['Precio por noche'].max(),
            step=10,
            marks={i: str(i) for i in range(data['Precio por noche'].min(), data['Precio por noche'].max(), 100)},
            value=[data['Precio por noche'].min(), data['Precio por noche'].max()]
        )
    ]),
    dcc.Dropdown(
        id='dropdown-ciudad',
        options=[{'label': ciudad, 'value': ciudad} for ciudad in data['Ciudad'].unique()],
        value=data['Ciudad'].unique()[0],
        placeholder="Selecciona una ciudad"
    ),
    dcc.Graph(id='scatter-plot'),
    dcc.Graph(id='bar-plot')
])

# Callbacks del Dashboard 1
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('bar-plot', 'figure')],
    [Input('dropdown-ciudad', 'value'),
     Input('price-slider', 'value')]
)
def update_dashboard_1(ciudad, price_range):
    filtered_data = data[(data['Ciudad'] == ciudad) &
                         (data['Precio por noche'] >= price_range[0]) &
                         (data['Precio por noche'] <= price_range[1])]

    # Scatter plot: Calificación vs. Precio por noche
    scatter_fig = px.scatter(filtered_data, x='Calificacion', y='Precio por noche',
                             color='Estrellas', hover_name='Nombre',
                             title=f'Relación entre Calificación y Precio por Noche en {ciudad}',
                             template='plotly_white'
                             )
    scatter_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')

    # Bar plot: Precio promedio por noche por estrellas
    bar_fig = px.bar(filtered_data.groupby('Estrellas')['Precio por noche'].mean().reset_index(),
                     x='Estrellas', y='Precio por noche',
                     title=f'Precio Promedio por Noche por Estrellas en {ciudad}',
                     template='plotly_white'
                     )
    bar_fig.update_traces(marker_color='#e3403d')
    bar_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')

    return scatter_fig, bar_fig


# Layout del Dashboard 2
layout_dashboard_2 = html.Div(style={'backgroundColor': '#f2f2f2', 'padding': '20px'}, children=[
    html.H1("Dashboard 2: Opiniones de los Clientes", style={'color': '#124192'}),
    html.P("Nos estamos centrando en analizar las impresiones de los clientes sobre los hoteles en diversas "
       "localidades. ¿Qué implica esto? Principalmente, buscamos comprender cómo describen los clientes su experiencia "
       "en los hoteles.", style={'font-size': '25px'}),
    dcc.Dropdown(
        id='dropdown-ciudad-2',
        options=[{'label': 'Todas las ciudades', 'value': 'all'}] +
                [{'label': ciudad, 'value': ciudad} for ciudad in data['Ciudad'].unique()],
        value='all',
        placeholder="Selecciona una ciudad"
    ),
    dcc.Dropdown(
        id='stars-dropdown',
        options=[{'label': str(i) + ' estrellas', 'value': i} for i in range(1, 6)],
        value=5,
        placeholder="Selecciona el número de estrellas"
    ),
    dcc.Graph(id='bar-plot-2'),
    dash_table.DataTable(
        id='table-plot',
        data=data.to_dict('records'),
        columns=[
            {'name': 'Nombre', 'id': 'Nombre'},
            {'name': 'Estrellas', 'id': 'Estrellas'},
            {'name': 'Ciudad', 'id': 'Ciudad'},
            {'name': 'Calificacion', 'id': 'Calificacion'},
            {'name': 'Numero de reseñas', 'id': 'Numero de reseñas'},
            {'name': 'Precio por noche', 'id': 'Precio por noche'}
        ],
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#FC9E16', 'color': 'white', 'textAlign': 'left'},
        style_data={'backgroundColor': '#f6b960', 'color': 'black', 'textAlign': 'left'},
    )
])

# Callbacks del Dashboard 2
@app.callback(
    [Output('bar-plot-2', 'figure'),
     Output('table-plot', 'data'),
     Output('table-plot', 'columns')],
    [Input('dropdown-ciudad-2', 'value'),
     Input('stars-dropdown', 'value')]
)
def update_dashboard_2(ciudad, estrellas):
    if ciudad == 'all':
        filtered_data = data[data['Estrellas'] == estrellas]
        title_suffix = f'con {estrellas} Estrellas en Todas las Ciudades'
    else:
        filtered_data = data[(data['Ciudad'] == ciudad) & (data['Estrellas'] == estrellas)]
        title_suffix = f'con {estrellas} Estrellas en {ciudad}'

    # Crear la gráfica de barras
    top_hotels = filtered_data.nlargest(10, 'Numero de reseñas')
    bar_fig = px.bar(top_hotels,
                     x='Nombre', y='Numero de reseñas',
                     title=f'Top 10 Hoteles con Más Opiniones {title_suffix}',
                     labels={'Numero de reseñas': 'Número de Opiniones'},
                     template='plotly_white')

    # Preparar los datos para la tabla
    table_data = top_hotels[['Nombre', 'Estrellas', 'Ciudad', 'Calificacion', 'Numero de reseñas', 'Precio por noche']].to_dict('records')
    table_columns = [{'name': col, 'id': col} for col in ['Nombre', 'Estrellas', 'Ciudad', 'Calificacion', 'Numero de reseñas', 'Precio por noche']]

    bar_fig.update_traces(marker_color='#e3403d')
    bar_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')

    return bar_fig, table_data, table_columns

# Layout del Dashboard 3
layout_dashboard_3 = html.Div(style={'backgroundColor': '#f2f2f2', 'padding': '20px'}, children=[
    html.H1("Dashboard 3: Distribución de Calificaciones por Ciudad", style={'color': '#124192'}),
    html.P("Este dashboard nos ofrece una visión detallada de cómo se distribuyen las calificaciones de los hoteles en "
           "diferentes ciudades. Si seleccionamos una ciudad de la lista, se presenta un histograma que "
           "muestra la frecuencia de las calificaciones de los hoteles en esa ubicación específica.", style={'font-size': '25px'}),
    dcc.Dropdown(
        id='dropdown-ciudad-3',
        options=[{'label': ciudad, 'value': ciudad} for ciudad in data['Ciudad'].unique()],
        value=data['Ciudad'].unique()[0],
        placeholder="Selecciona una ciudad"
    ),
    dcc.Graph(id='histogram-plot')
])


@app.callback(
    Output('histogram-plot', 'figure'),
    [Input('dropdown-ciudad-3', 'value')]
)
def update_dashboard_3(ciudad):
    filtered_data = data[data['Ciudad'] == ciudad]

    # Histogram Plot: Distribución de Calificaciones
    histogram_fig = px.histogram(filtered_data, x='Calificacion',
                                 title=f'Distribución de Calificaciones en {ciudad}',
                                 template='plotly_white'
                                 )
    histogram_fig.update_traces(marker_color='rgb(18, 145, 210)')
    histogram_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    return histogram_fig

# Barra de navegación lateral
navbar = dbc.Nav(
    [
        dbc.NavLink("Información del Proyecto", href="/", id="info-link"),
        dbc.NavLink("Dashboard 1", href="/dashboard-1", id="dashboard-1-link", style={"color": "rgb(18, 145, 210)"}),
        dbc.NavLink("Dashboard 2", href="/dashboard-2", id="dashboard-2-link", style={"color": "rgb(252, 158, 22)"}),
        dbc.NavLink("Dashboard 3", href="/dashboard-3", id="dashboard-3-link", style={"color": "rgb(227, 64, 61)"}),
    ],
    vertical=True,
    pills=True,
    style={"position": "fixed", "top": "0px", "left": "0px", "padding": "20px"}
)

# Contenido de la página
content = html.Div(id="page-content", style={"margin-left": "200px", "padding": "20px"})

# Definimos el layout general de la aplicación
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    content
])

# Callbacks para actualizar el contenido de la página basado en la URL
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/dashboard-1":
        return layout_dashboard_1
    elif pathname == "/dashboard-2":
        return layout_dashboard_2
    elif pathname == "/dashboard-3":
        return layout_dashboard_3
    else:
        return layout_info

# Callbacks para actualizar la barra de navegación basada en la URL
@app.callback(
    [Output(f"{tab}-link", "active") for tab in ["info", "dashboard-1", "dashboard-2", "dashboard-3"]],
    [Input("url", "pathname")]
)
def update_active_links(pathname):
    return [pathname == "/" if tab == "info" else pathname == f"/{tab.replace('_', '-')}" for tab in ["info", "dashboard-1", "dashboard-2", "dashboard-3"]]

if __name__ == '__main__':
    app.run_server(debug=True)