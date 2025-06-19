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

# ===== 5. Configuración para Render =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(
        host="0.0.0.0",
        port=port,
        debug=False,
        dev_tools_props_check=False
    )
