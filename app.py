#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ===== 1. Configuración inicial =====
# ===== Estilos CSS personalizados =====
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
server = app.server

# Configuración de estilos
styles = {
    'background': '#F5F5F5',
    'text': '#0A2463',
    'accent': '#0A2463', #COLOR DE TÍTULO GENERAL
    'card': '#FFFFFF',
    'font': 'Roboto, sans-serif',
    'grid': '#E0E0E0'
}

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <title>Dashboard GOEAC</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ===== 2. Conexión a Google Sheets =====
try:
    # Verificación de variables de entorno
    required_vars = [
        'GCP_PROJECT_ID',
        'GCP_PRIVATE_KEY',
        'GCP_CLIENT_EMAIL',
        'GCP_CLIENT_X509_CERT_URL'
    ]
    
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing_vars)}")

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds_dict = {
        "type": "service_account",
        "project_id": os.environ['GCP_PROJECT_ID'],
        "private_key_id": os.environ.get('GCP_PRIVATE_KEY_ID', ''),
        "private_key": os.environ['GCP_PRIVATE_KEY'].replace('\\n', '\n'),
        "client_email": os.environ['GCP_CLIENT_EMAIL'],
        "client_id": os.environ.get('GCP_CLIENT_ID', ''),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ['GCP_CLIENT_X509_CERT_URL']
    }

    credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)

    # Carga de datos
    try:
        spreadsheet = client.open("Raciones_2025")
        cch = pd.DataFrame(spreadsheet.get_worksheet(0).get_all_records())
        ci = pd.DataFrame(spreadsheet.get_worksheet(1).get_all_records())
        cj = pd.DataFrame(spreadsheet.get_worksheet(2).get_all_records())
        cai = pd.DataFrame(spreadsheet.get_worksheet(3).get_all_records())
    except Exception as e:
        print(f"Error al cargar datos: {str(e)}")
        raise

except Exception as e:
    print(f"Error crítico: {str(e)}")
    cch = pd.DataFrame(columns=['Escuela', 'Fecha', 'Inscriptos', 'Presentes', 'Observaciones'])
    ci = pd.DataFrame(columns=['Escuela', 'Fecha', 'Inscriptos', 'Presentes', 'Observaciones'])
    cj = pd.DataFrame(columns=['Escuela', 'Fecha', 'Inscriptos', 'Presentes', 'Observaciones'])
    cai = pd.DataFrame(columns=['Escuela', 'Fecha', 'Inscriptos', 'Presentes', 'Observaciones'])
    print("Modo de fallo seguro activado")

# ===== 3. Layout principal =====
dropdown_style = {
    'backgroundColor': styles['card'],
    'color': styles['text'],
    'border': f'1px solid {styles["accent"]}',
    'fontFamily': styles['font']
}

app.layout = html.Div([
    html.Div([
        html.H1("Dashboard GOEAC", style={
            'color': styles['accent'],
            'backgroundColor': styles['background'],
            'padding': '20px',
            'borderBottom': f'2px solid {styles["accent"]}',
            'marginBottom': '0'
        }),
        html.Button('Actualizar Datos', id='refresh-button', n_clicks=0, style={
            'backgroundColor': styles['card'],
            'color': '#000',
            'border': 'none',
            'padding': '0px 20px',
            'margin': '10px',
            'borderRadius': '5px',
            'fontWeight': 'normal',
            'cursor': 'pointer',
            'justifyContent': 'center',  # Centra horizontalmente
            'alignItems': 'center',      # Centra verticalmente
            'height': '40px',
            'widht': '100%'
        }),
    ], style={'backgroundColor': styles['background']}),
    
    dcc.Tabs(id="tabs", value='tab-ci', children=[
        dcc.Tab(label='Centros Infantiles', value='tab-ci', style={
            'backgroundColor': styles['background'],
            'color': styles['text'],
            'border': f'1px solid {styles["accent"]}',
            'fontWeight': 'bold',
            'padding': '10px'
        }, selected_style={
            'backgroundColor': styles['card'],
            'color': styles['accent'],
            'border': f'2px solid {styles["accent"]}'
        }),
        
        dcc.Tab(label='Club de Chicos', value='tab-cch', style={
            'backgroundColor': styles['background'],
            'color': styles['text'],
            'border': f'1px solid {styles["accent"]}',
            'fontWeight': 'bold',
            'padding': '10px'
        }, selected_style={
            'backgroundColor': styles['card'],
            'color': styles['accent'],
            'border': f'2px solid {styles["accent"]}'
        }),
        
        dcc.Tab(label='Club de Jóvenes', value='tab-cj', style={
            'backgroundColor': styles['background'],
            'color': styles['text'],
            'border': f'1px solid {styles["accent"]}',
            'fontWeight': 'bold',
            'padding': '10px'
        }, selected_style={
            'backgroundColor': styles['card'],
            'color': styles['accent'],
            'border': f'2px solid {styles["accent"]}'
        }),
        dcc.Tab(label='Resumen y Alertas', value='tab-resumen', children=[
            html.Div([
                html.H2("Resumen General", style={'color': styles['accent']}),
                dcc.Graph(id='resumen-graph'),
                html.H2("Alertas", style={'color': styles['accent'], 'marginTop': '30px'}),
                html.Div(id='alertas-container', style={
                    'backgroundColor': styles['card'],
                    'padding': '15px',
                    'borderRadius': '5px',
                    'marginBottom': '20px'
                }),
                html.H2("    Programa", style={'color': styles['accent'], 'marginTop': '30px'}),
                dcc.Dropdown(
                    id='tipo-centro',
                    options=[
                        {'label': 'Centros Infantiles', 'value': 'ci'},
                        {'label': 'Club de Chicos', 'value': 'cch'},
                        {'label': 'Club de Jóvenes', 'value': 'cj'},
                    ],
                    value='ci',
                    style=dropdown_style
                ),
                dcc.Graph(id='tendencias-graph')
            ], style={'padding': '20px'})
        ], style={
            'backgroundColor': styles['background'],
            'color': styles['text'],
            'border': f'1px solid {styles["accent"]}',
            'fontWeight': 'bold',
            'padding': '10px'
        }, selected_style={
            'backgroundColor': styles['card'],
            'color': styles['accent'],
            'border': f'2px solid {styles["accent"]}'
        }),
    ], style={
        'backgroundColor': styles['background'],
        'color': styles['text'],
        'fontFamily': styles['font']
    }),
    
    html.Div(id='tabs-content', style={
        'backgroundColor': styles['background'],
        'padding': '20px'
    })
], style={
    'backgroundColor': styles['background'],
    'minHeight': '100vh',
    'color': styles['text'],
    'fontFamily': styles['font']
})

# ===== 4. Callbacks =====
def create_tab_content(tab):
    if tab == 'tab-ci':
        return html.Div([
            dcc.Dropdown(
                id='ci-escuela',
                options=[{'label': e, 'value': e} for e in ci['Escuela'].unique()],
                value=ci['Escuela'].iloc[0] if not ci.empty else None,
                style=dropdown_style
            ),
            dcc.Graph(id='ci-graph'),
            html.Div(id='ci-table')
        ])
    elif tab == 'tab-cch':
        return html.Div([
            dcc.Dropdown(
                id='cch-escuela',
                options=[{'label': e, 'value': e} for e in cch['Escuela'].unique()],
                value=cch['Escuela'].iloc[0] if not cch.empty else None,
                style=dropdown_style
            ),
            dcc.Graph(id='cch-graph'),
            html.Div(id='cch-table')
        ])
    elif tab == 'tab-cj':
        return html.Div([
            dcc.Dropdown(
                id='cj-escuela',
                options=[{'label': e, 'value': e} for e in cj['Escuela'].unique()],
                value=cj['Escuela'].iloc[0] if not cj.empty else None,
                style=dropdown_style
            ),
            dcc.Graph(id='cj-graph'),
            html.Div(id='cj-table')
        ])
    elif tab == 'tab-cai':
        return html.Div([
            dcc.Dropdown(
                id='cai-escuela',
                options=[{'label': e, 'value': e} for e in cai['Escuela'].unique()],
                value=cai['Escuela'].iloc[0] if not cai.empty else None,
                style=dropdown_style
            ),
            dcc.Graph(id='cai-graph'),
            html.Div(id='cai-table')
        ])
    return html.Div()

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    return create_tab_content(tab)

def create_graph_and_table(worksheet_num, escuela, title):
    try:
        worksheet = client.open("Raciones_2025").get_worksheet(worksheet_num)
        df = pd.DataFrame(worksheet.get_all_records())
        
        filtered = df[df['Escuela'] == escuela]
        
        # Crear gráfico
        fig = px.line(
            filtered,
            x='Fecha',
            y=['Inscriptos', 'Presentes'],
            title=f"{title} - {escuela}",
            color_discrete_sequence=[styles['accent'], '#FF0000']
        )
        
        # Estilo del gráfico
        fig.update_layout(
            plot_bgcolor=styles['card'],
            paper_bgcolor=styles['background'],
            font={'color': styles['text']},
            xaxis={'gridcolor': styles['grid']},
            yaxis={'gridcolor': styles['grid']},
            title={'font': {'size': 20, 'color': styles['accent']}},
            legend_title_text='',
            hovermode='x unified'
        )
        
        # Añadir anotaciones
        for idx, row in filtered.iterrows():
            if row['Presentes'] == 0 and pd.notna(row.get('Observaciones', '')):
                fig.add_annotation(
                    x=row['Fecha'],
                    y=0,
                    text=row['Observaciones'],
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40,
                    bgcolor="rgba(255,165,0,0.3)",
                    bordercolor=styles['accent'],
                    font=dict(size=10, color='blue'),
                    yanchor='top'
                )
        
        # Crear tabla
        table = dash_table.DataTable(
            data=filtered.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in filtered.columns],
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': styles['background'],
                'color': styles['accent'],
                'fontWeight': 'bold',
                'border': f'1px solid {styles["accent"]}'
            },
            style_cell={
                'backgroundColor': styles['card'],
                'color': styles['text'],
                'border': f'1px solid {styles["grid"]}',
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#F5F5F5'
                },
                {
                    'if': {'column_id': 'Observaciones'},
                    'fontStyle': 'italic'
                }
            ],
            page_size=10
        )
        
        return fig, table
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return px.line(), html.Div("Error al cargar datos")

@app.callback(
    [Output('ci-graph', 'figure'),
     Output('ci-table', 'children')],
    [Input('ci-escuela', 'value'),
     Input('refresh-button', 'n_clicks')]    
)
def update_ci(escuela, n_clicks):
    return create_graph_and_table(1, escuela, "Centros Infantiles")

@app.callback(
    [Output('cch-graph', 'figure'),
     Output('cch-table', 'children')],
    [Input('cch-escuela', 'value'),
     Input('refresh-button', 'n_clicks')]
)
def update_cch(escuela, n_clicks):
    return create_graph_and_table(0, escuela, "Club de Chicos")

@app.callback(
    [Output('cj-graph', 'figure'),
     Output('cj-table', 'children')],
    [Input('cj-escuela', 'value'),
     Input('refresh-button', 'n_clicks')]
)
def update_cj(escuela, n_clicks):
    return create_graph_and_table(2, escuela, "Club de Jóvenes")

@app.callback(
    [Output('cai-graph', 'figure'),
     Output('cai-table', 'children')],
    [Input('cai-escuela', 'value'),
     Input('refresh-button', 'n_clicks')]
)
def update_cai(escuela, n_clicks):
    return create_graph_and_table(3, escuela, "CAI")

@app.callback(
    [Output('resumen-graph', 'figure'),
     Output('alertas-container', 'children'),
     Output('tendencias-graph', 'figure')],
    [Input('refresh-button', 'n_clicks'),
     Input('tipo-centro', 'value')]
)

def update_resumen(n_clicks, tipo_centro):
    try:
        # Cargar datos actualizados
        spreadsheet = client.open("Raciones_2025")
        cch = pd.DataFrame(spreadsheet.get_worksheet(0).get_all_records())
        ci = pd.DataFrame(spreadsheet.get_worksheet(1).get_all_records())
        cj = pd.DataFrame(spreadsheet.get_worksheet(2).get_all_records())
        # cai = pd.DataFrame(spreadsheet.get_worksheet(3).get_all_records())  # Descomentar cuando esté disponible
        
        def limpiar_datos(df):
            if df.empty:
                return df
            
            for col in ['Inscriptos', 'Presentes']:
                if col in df.columns:
                    # Convertir a string solo si no es ya string
                    if not pd.api.types.is_string_dtype(df[col]):
                        df[col] = df[col].astype(str)
                    
                    # Extraer números y convertir a numérico
                    df[col] = df[col].str.extract(r'(\d+)', expand=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')  # Mantener como float para detectar NaN
            return df
        
        # Limpiar datos de todos los centros
        ci = limpiar_datos(ci)
        cch = limpiar_datos(cch)
        cj = limpiar_datos(cj)
        # cai = limpiar_datos(cai)  # Descomentar cuando esté disponible
        
        def procesar_datos(df, nombre):
            if df.empty:
                return pd.DataFrame()
            
            # Convertir Fecha a datetime si no lo está
            if not pd.api.types.is_datetime64_any_dtype(df['Fecha']):
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
                df = df.dropna(subset=['Fecha'])
            
            # Ordenar por fecha descendente
            df = df.sort_values('Fecha', ascending=False)
            
            # Filtrar solo registros con Inscriptos válidos (no nulos y no NaN)
            df_validos = df[df['Inscriptos'].notna()]
            
            if df_validos.empty:
                return pd.DataFrame()
            
            # Tomar la última fecha con datos válidos
            ultima_fecha_valida = df_validos['Fecha'].iloc[0]
            df_reciente = df_validos[df_validos['Fecha'] == ultima_fecha_valida]
            
            # Calcular métricas (con protección contra división por cero)
            df_reciente['Presentismo'] = df_reciente.apply(
                lambda x: (x['Presentes'] / x['Inscriptos']) * 100 if x['Inscriptos'] > 0 else 0,
                axis=1
            )
            df_reciente['Tipo'] = nombre
            return df_reciente[['Escuela', 'Inscriptos', 'Presentes', 'Presentismo', 'Tipo', 'Fecha']]
        
        # Procesar cada tipo de centro
        ci_resumen = procesar_datos(ci, 'Centros Infantiles')
        cch_resumen = procesar_datos(cch, 'Club de Chicos')
        cj_resumen = procesar_datos(cj, 'Club de Jóvenes')
        # cai_resumen = procesar_datos(cai, 'CAI')  # Descomentar cuando esté disponible
        
        # Unir todos los datos
        todos_datos = pd.concat([df for df in [ci_resumen, cch_resumen, cj_resumen] if not df.empty])
        
        if todos_datos.empty:
            # Manejo cuando no hay datos válidos
            empty_fig = px.bar()
            empty_fig.update_layout(
                title={'text': "No hay datos válidos disponibles", 'font': {'color': styles['text']}},
                xaxis={'visible': False},
                yaxis={'visible': False},
                plot_bgcolor=styles['card'],
                paper_bgcolor=styles['background']
            )
            
            empty_alert = html.Div([
                html.I(className="fa fa-exclamation-circle", style={'color': 'orange', 'marginRight': '10px'}),
                "No se encontraron datos válidos de inscriptos en ninguna fecha"
            ], style={'color': 'orange'})
            
            empty_line = px.line()
            empty_line.update_layout(
                title={'text': "No hay datos disponibles", 'font': {'color': styles['text']}},
                xaxis={'visible': False},
                yaxis={'visible': False},
                plot_bgcolor=styles['card'],
                paper_bgcolor=styles['background']
            )
            
            return empty_fig, empty_alert, empty_line
        
        # Crear DataFrame resumen con totales por tipo
        resumen_tipos = todos_datos.groupby('Tipo', as_index=False).agg({
            'Inscriptos': 'sum',
            'Presentes': 'sum',
            'Fecha': 'max'  # Última fecha válida (puede ser diferente por tipo)
        })
        
        # Calcular presentismo general por tipo (con protección contra división por cero)
        resumen_tipos['Presentismo'] = resumen_tipos.apply(
            lambda x: (x['Presentes'] / x['Inscriptos']) * 100 if x['Inscriptos'] > 0 else 0,
            axis=1
        )
        
        # Obtener el rango de fechas para el título
        fecha_min = todos_datos['Fecha'].min()
        fecha_max = todos_datos['Fecha'].max()
        
        if fecha_min == fecha_max:
            titulo_fecha = f"Última fecha disponible: {fecha_max.strftime('%d/%m/%Y')}"
        else:
            titulo_fecha = f"Rango de fechas: {fecha_min.strftime('%d/%m/%Y')} a {fecha_max.strftime('%d/%m/%Y')}"
        
        # Gráfico de barras con totales
        fig_resumen = px.bar(
            resumen_tipos,
            x='Tipo',
            y='Inscriptos',
            color='Tipo',
            title=f"Total de Inscriptos por Tipo de Centro ({titulo_fecha})",
            labels={'Inscriptos': 'Total Inscriptos', 'Tipo': 'Tipo de Centro'},
            color_discrete_sequence=[styles['accent'], '#FF7F0E', '#2CA02C', '#D62728'],
            hover_data={
                'Inscriptos': ':,', 
                'Presentes': ':,',
                'Presentismo': ':.1f%',
                'Fecha': False
            }
        )
        
        fig_resumen.update_layout(
            plot_bgcolor=styles['card'],
            paper_bgcolor=styles['background'],
            font={'color': styles['text']},
            xaxis={'gridcolor': styles['grid']},
            yaxis={'gridcolor': styles['grid']},
            title={'font': {'size': 20, 'color': styles['accent']}},
            hovermode='x unified',
            showlegend=False
        )
        
        # Generar alertas (solo para fechas válidas)
        alertas = []
        
        # Alertas para centros con menos del 40% de presentismo
        baja_asistencia = todos_datos[todos_datos['Presentismo'] < 40]
        if not baja_asistencia.empty:
            for _, row in baja_asistencia.iterrows():
                alertas.append(
                    html.Div([
                        html.I(className="fa fa-exclamation-triangle", style={'color': 'red', 'marginRight': '10px'}),
                        html.Span(f"Baja asistencia en {row['Escuela']} ({row['Tipo']}) {row['Fecha'].strftime('%d/%m/%Y')}: {row['Presentismo']:.1f}%"),
                    ], style={'color': 'red', 'marginBottom': '10px'})
                )
        
        # Alertas para centros con menos de 30 inscriptos
        baja_matricula = todos_datos[todos_datos['Inscriptos'] < 30]
        if not baja_matricula.empty:
            for _, row in baja_matricula.iterrows():
                alertas.append(
                    html.Div([
                        html.I(className="fa fa-user-times", style={'color': 'orange', 'marginRight': '10px'}),
                        html.Span(f"Baja matrícula en {row['Escuela']} ({row['Tipo']}) {row['Fecha'].strftime('%d/%m/%Y')}: {row['Inscriptos']} inscriptos"),
                    ], style={'color': 'orange', 'marginBottom': '10px'})
                )
        
        if not alertas:
            alertas = html.Div([
                html.I(className="fa fa-check-circle", style={'color': 'green', 'marginRight': '10px'}),
                f"No hay alertas críticas para las fechas analizadas"
            ], style={'color': 'green'})
        
        # Gráfico de tendencias para el tipo de centro seleccionado
        df_tendencias = None
        title_tendencias = ""
        if tipo_centro == 'ci':
            df_tendencias = ci
            title_tendencias = "Inscriptos en Centros Infantiles"
        elif tipo_centro == 'cch':
            df_tendencias = cch
            title_tendencias = "Inscriptos en Club de Chicos"
        elif tipo_centro == 'cj':
            df_tendencias = cj
            title_tendencias = "Inscriptos en Club de Jóvenes"
        # elif tipo_centro == 'cai':  # Descomentar cuando esté disponible
        #     df_tendencias = cai
        #     title_tendencias = "Tendencias en CAI"
        
        # Filtrar solo datos válidos para el gráfico de tendencias
        if df_tendencias is not None and not df_tendencias.empty:
            df_tendencias = df_tendencias[df_tendencias['Inscriptos'].notna()]
            
            if not df_tendencias.empty:
                # Convertir Fecha a datetime si no lo está
                if not pd.api.types.is_datetime64_any_dtype(df_tendencias['Fecha']):
                    df_tendencias['Fecha'] = pd.to_datetime(df_tendencias['Fecha'], errors='coerce')
                    df_tendencias = df_tendencias.dropna(subset=['Fecha'])
                
                fig_tendencias = px.line(
                    df_tendencias,
                    x='Fecha',
                    y='Inscriptos',
                    color='Escuela',
                    title=title_tendencias,
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    hover_name='Escuela'
                )
                fig_tendencias.update_traces(
                    hovertemplate=(
                        "<b>%{hovertext}</b><br>"
                        "Fecha: %{x|%d/%m/%Y}<br>"
                        "Inscriptos: %{y:,}<br>"
                        "<extra></extra>"
                    ),
                    line=dict(width=2)
                )
                
                fig_tendencias.update_layout(
                    plot_bgcolor=styles['card'],
                    paper_bgcolor=styles['background'],
                    font={'color': styles['text']},
                    xaxis={'gridcolor': styles['grid']},
                    yaxis={'gridcolor': styles['grid']},
                    title={'font': {'size': 20, 'color': styles['accent']}},
                    hovermode='closest',
                    legend_title_text='Centros'
                )
            else:
                # Crear gráfico vacío si no hay datos válidos
                fig_tendencias = px.line(title=title_tendencias)
                fig_tendencias.update_layout(
                    plot_bgcolor=styles['card'],
                    paper_bgcolor=styles['background'],
                    title={'font': {'size': 20, 'color': styles['accent']}},
                    xaxis={'visible': False},
                    yaxis={'visible': False},
                    annotations=[{
                        'text': 'No hay datos válidos de inscriptos',
                        'showarrow': False,
                        'font': {'size': 16, 'color': styles['text']}
                    }]
                )
        else:
            # Crear gráfico vacío si no hay datos
            fig_tendencias = px.line(title=title_tendencias)
            fig_tendencias.update_layout(
                plot_bgcolor=styles['card'],
                paper_bgcolor=styles['background'],
                title={'font': {'size': 20, 'color': styles['accent']}},
                xaxis={'visible': False},
                yaxis={'visible': False},
                annotations=[{
                    'text': 'No hay datos disponibles',
                    'showarrow': False,
                    'font': {'size': 16, 'color': styles['text']}
                }]
            )
        
        return fig_resumen, alertas, fig_tendencias
    
    except Exception as e:
        print(f"Error en resumen: {str(e)}")
        # Retornar gráficos vacíos con mensaje de error
        error_fig = px.bar()
        error_fig.update_layout(
            title={'text': "Error al cargar datos", 'font': {'color': 'red'}},
            xaxis={'visible': False},
            yaxis={'visible': False},
            plot_bgcolor=styles['card'],
            paper_bgcolor=styles['background']
        )
        
        error_alert = html.Div([
            html.I(className="fa fa-exclamation-circle", style={'color': 'red', 'marginRight': '10px'}),
            "Error al generar el resumen. Por favor intente nuevamente."
        ], style={'color': 'red'})
        
        error_line = px.line()
        error_line.update_layout(
            title={'text': "Error al cargar datos", 'font': {'color': 'red'}},
            xaxis={'visible': False},
            yaxis={'visible': False},
            plot_bgcolor=styles['card'],
            paper_bgcolor=styles['background']
        )
        
        return error_fig, error_alert, error_line



# ===== 5. Configuración para Render =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(
        host="0.0.0.0",
        port=port,
        debug=False,
        dev_tools_props_check=False
    )
