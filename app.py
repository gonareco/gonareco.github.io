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
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # ¡Crítico para Render!

# ===== 2. Conexión a Google Sheets (Versión Mejorada) =====
try:
    # Verificación de variables de entorno críticas
    required_vars = [
        'GCP_PROJECT_ID',
        'GCP_PRIVATE_KEY',
        'GCP_CLIENT_EMAIL',
        'GCP_CLIENT_X509_CERT_URL'
    ]
    
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing_vars)}")

    # Configuración de scopes necesarios
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

    # Carga de datos con manejo de errores
    try:
        spreadsheet = client.open("Raciones_2025")
        cch = pd.DataFrame(spreadsheet.get_worksheet(0).get_all_records())
        ci = pd.DataFrame(spreadsheet.get_worksheet(1).get_all_records())
        cj = pd.DataFrame(spreadsheet.get_worksheet(2).get_all_records())
    except Exception as e:
        print(f"Error al cargar datos de Google Sheets: {str(e)}")
        raise

except Exception as e:
    print(f"Error crítico en inicialización: {str(e)}")
    # Crear datos vacíos para que la app pueda iniciar (modo de fallo seguro)
    cch = pd.DataFrame(columns=['Escuela', 'Fecha', 'Inscriptos', 'Presentes'])
    ci = pd.DataFrame(columns=['Escuela', 'Fecha', 'Inscriptos', 'Presentes'])
    cj = pd.DataFrame(columns=['Escuela', 'Fecha', 'Inscriptos', 'Presentes'])
    print("Modo de fallo seguro activado - usando datos vacíos")

# ===== 3. Layout principal con pestañas =====
app.layout = html.Div([
    html.H1("Dashboard Educativo GOEAC"),
    dcc.Tabs([
        dcc.Tab(label='Centros Infantiles', children=[
            dcc.Dropdown(
                id='ci-escuela', 
                options=[{'label': e, 'value': e} for e in ci['Escuela'].unique()], 
                value=ci['Escuela'].iloc[0] if not ci.empty else None
            ),
            dcc.Graph(id='ci-graph'),
            html.Div(id='ci-table')
        ]),
        dcc.Tab(label='Club de Chicos', children=[
            dcc.Dropdown(
                id='cch-escuela', 
                options=[{'label': e, 'value': e} for e in cch['Escuela'].unique()], 
                value=cch['Escuela'].iloc[0] if not cch.empty else None
            ),
            dcc.Graph(id='cch-graph'),
            html.Div(id='cch-table')
        ]),
        dcc.Tab(label='Club de Jóvenes', children=[
            dcc.Dropdown(
                id='cj-escuela', 
                options=[{'label': e, 'value': e} for e in cj['Escuela'].unique()], 
                value=cj['Escuela'].iloc[0] if not cj.empty else None
            ),
            dcc.Graph(id='cj-graph'),
            html.Div(id='cj-table')
        ])
    ])
])

# ===== 4. Callbacks para cada pestaña (con manejo de errores) =====
@app.callback(
    [Output('cch-graph', 'figure'),
     Output('cch-table', 'children')],
    [Input('cch-escuela', 'value')]
)
def update_cch(escuela):
    try:
        filtered = cch[cch['Escuela'] == escuela]
        fig = px.line(filtered, x='Fecha', y=['Inscriptos', 'Presentes'], title=f"Club de Chicos - {escuela}")
        table = dash_table.DataTable(
            data=filtered.to_dict('records'),
            style_table={'overflowX': 'auto'}
        )
        return fig, table
    except Exception as e:
        print(f"Error en callback cch: {str(e)}")
        return px.line(), html.Div("Error al cargar datos")

# Callbacks para ci y cj (patrón similar)
@app.callback(
    [Output('ci-graph', 'figure'),
     Output('ci-table', 'children')],
    [Input('ci-escuela', 'value')]
)
def update_ci(escuela):
    try:
        filtered = ci[ci['Escuela'] == escuela]
        fig = px.line(filtered, x='Fecha', y=['Inscriptos', 'Presentes'], title=f"Centros Infantiles - {escuela}")
        table = dash_table.DataTable(
            data=filtered.to_dict('records'),
            style_table={'overflowX': 'auto'}
        )
        return fig, table
    except:
        return px.line(), html.Div("Error al cargar datos")

@app.callback(
    [Output('cj-graph', 'figure'),
     Output('cj-table', 'children')],
    [Input('cj-escuela', 'value')]
)
def update_cj(escuela):
    try:
        filtered = cj[cj['Escuela'] == escuela]
        fig = px.line(filtered, x='Fecha', y=['Inscriptos', 'Presentes'], title=f"Club de Jóvenes - {escuela}")
        table = dash_table.DataTable(
            data=filtered.to_dict('records'),
            style_table={'overflowX': 'auto'}
        )
        return fig, table
    except:
        return px.line(), html.Div("Error al cargar datos")

# ===== 5. Configuración para Render =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(
        host="0.0.0.0",
        port=port,
        debug=False,
        dev_tools_props_check=False  # Para evitar warnings en producción
    )
