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

# ===== 2. Conexión a Google Sheets =====
creds_dict = {
    "type": "service_account",
    "project_id": os.environ['GCP_PROJECT_ID'],
    "private_key_id": os.environ['GCP_PRIVATE_KEY_ID'],
    "private_key": os.environ['GCP_PRIVATE_KEY'].replace('\\n', '\n'),
    "client_email": os.environ['GCP_CLIENT_EMAIL'],
    "client_id": os.environ['GCP_CLIENT_ID'],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ['GCP_CLIENT_X509_CERT_URL']
}

credentials = Credentials.from_service_account_info(creds_dict)
client = gspread.authorize(credentials)

# Carga de datos
spreadsheet = client.open("Raciones_2025")
cch = pd.DataFrame(spreadsheet.get_worksheet(0).get_all_records())
ci = pd.DataFrame(spreadsheet.get_worksheet(1).get_all_records())
cj = pd.DataFrame(spreadsheet.get_worksheet(2).get_all_records())

# ===== 3. Layout principal con pestañas =====
app.layout = html.Div([
    html.H1("Dashboard Educativo GOEAC"),
    dcc.Tabs([
        dcc.Tab(label='Club de Chicos', children=[
            dcc.Dropdown(id='cch-escuela', options=[{'label': e, 'value': e} for e in cch['Escuela'].unique()], value=cch['Escuela'].iloc[0]),
            dcc.Graph(id='cch-graph'),
            html.Div(id='cch-table')
        ]),
        dcc.Tab(label='Centros Infantiles', children=[
            dcc.Dropdown(id='ci-escuela', options=[{'label': e, 'value': e} for e in ci['Escuela'].unique()], value=ci['Escuela'].iloc[0]),
            dcc.Graph(id='ci-graph'),
            html.Div(id='ci-table')
        ]),
        dcc.Tab(label='Club de Jóvenes', children=[
            dcc.Dropdown(id='cj-escuela', options=[{'label': e, 'value': e} for e in cj['Escuela'].unique()], value=cj['Escuela'].iloc[0]),
            dcc.Graph(id='cj-graph'),
            html.Div(id='cj-table')
        ])
    ])
])

# ===== 4. Callbacks para cada pestaña =====
# Callback Club de Chicos
@app.callback(
    [Output('cch-graph', 'figure'),
     Output('cch-table', 'children')],
    [Input('cch-escuela', 'value')]
)
def update_cch(escuela):
    filtered = cch[cch['Escuela'] == escuela]
    fig = px.line(filtered, x='Fecha', y=['Inscriptos', 'Presentes'], title=f"Club de Chicos - {escuela}")
    table = dash_table.DataTable(data=filtered.to_dict('records'))
    return fig, table

# Callback Centros Infantiles
@app.callback(
    [Output('ci-graph', 'figure'),
     Output('ci-table', 'children')],
    [Input('ci-escuela', 'value')]
)
def update_ci(escuela):
    filtered = ci[ci['Escuela'] == escuela]
    fig = px.line(filtered, x='Fecha', y=['Inscriptos', 'Presentes'], title=f"Centros Infantiles - {escuela}")
    table = dash_table.DataTable(data=filtered.to_dict('records'))
    return fig, table

# Callback Club de Jóvenes
@app.callback(
    [Output('cj-graph', 'figure'),
     Output('cj-table', 'children')],
    [Input('cj-escuela', 'value')]
)
def update_cj(escuela):
    filtered = cj[cj['Escuela'] == escuela]
    fig = px.line(filtered, x='Fecha', y=['Inscriptos', 'Presentes'], title=f"Club de Jóvenes - {escuela}")
    table = dash_table.DataTable(data=filtered.to_dict('records'))
    return fig, table

# ===== 5. Configuración para Render =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Usa el puerto de Render o 8050 por defecto
    app.run_server(host="0.0.0.0", port=port, debug=False)
