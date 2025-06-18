#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 30 11:41:52 2025

@author: gonzalo
"""

import gspread
from google.oauth2.service_account import Credentials


# Configura los alcances (scopes)
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

import os

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

credentials = Credentials.from_service_account_info(creds_dict)  # ✅

# Autoriza el cliente
client = gspread.authorize(credentials)

# Abre la hoja de cálculo (por nombre o URL)
spreadsheet = client.open("Raciones_2025")  # o usa .open_by_url("URL")

# Selecciona una hoja específica
worksheet1 = spreadsheet.get_worksheet(0)  # 0 para la primera hoja
worksheet2 = spreadsheet.get_worksheet(1)  # 1 para la segunda hoja
worksheet3 = spreadsheet.get_worksheet(2)  # 2 para la tercera hoja

import pandas as pd
cch = pd.DataFrame(worksheet1.get_all_records())
ci = pd.DataFrame(worksheet2.get_all_records())
cj = pd.DataFrame(worksheet3.get_all_records())

# %% SEGUIMIENTO CLUB DE CHICOS
'''
SEGUIMIENTO CLUB DE CHICOS
'''
    
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import locale
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  
# import pandas as pd

# Cargar tus datos (ejemplo con tu estructura)
# cch = pd.read_csv("tu_cchset.csv", encoding='latin1')  # Ajusta el encoding si es necesario
# cch["Fecha"] = pd.to_datetime(cch["Fecha"], format="%d-%b")  # Convertir a datetime

# Iniciar la app Dash
app = dash.Dash(__name__)

# Layout del dashboard
app.layout = html.Div([
    html.H1("Dashboard de Seguimiento de Club de Chicos"),
    
    # Dropdown para seleccionar escuela
    dcc.Dropdown(
        id="escuela-dropdown",
        options=[{"label": escuela, "value": escuela} for escuela in cch["Escuela"].unique()],
        value=cch["Escuela"].iloc[0],
        multi=False
    ),
    
    # Gráficos
    dcc.Graph(id="inscriptos-presentes"),
    dcc.Graph(id="raciones"),
    
    # Tabla resumen
    html.Div(id="tabla-resumen")
])

# Callbacks para interactividad
@app.callback(
    [Output("inscriptos-presentes", "figure"),
     Output("raciones", "figure"),
     Output("tabla-resumen", "children")],
    [Input("escuela-dropdown", "value")]
)
def update_dashboard(escuela_seleccionada):
    filtered_cch = cch[cch["Escuela"] == escuela_seleccionada]
  
    # Gráfico de inscriptos vs. presentes
    fig1 = px.line(
        filtered_cch, x="Fecha", y=["Inscriptos", "Presentes"],
        labels={
            'value' : 'Cantidad',
            'variable' : 'Tipo'
            },
        title=f"Evolución de Inscriptos vs. Presentes - {escuela_seleccionada}"
    )
    # Personalización adicional
    fig1.update_traces(
        line=dict(width=3),
        selector=dict(name='Presentes')
    )
    for idx, row in filtered_cch.iterrows():
       if row['Presentes'] == 0 and pd.notna(row['Observaciones']):
           fig1.add_annotation(
               x=row['Fecha'],
               y=0,
               text=row['Observaciones'],
               showarrow=True,
               arrowhead=1,
               ax=0,
               ay=-40,
               bgcolor="rgba(255,0,0,0.2)",
               bordercolor="#FF0000",
               font=dict(size=10)
           )

    # Gráfico de raciones
    fig2 = px.bar(
        filtered_cch, x="Fecha", y="Raciones",
        title=f"Raciones entregadas - {escuela_seleccionada}"
    )
    
    # Tabla resumen
    tabla = html.Div([
        html.H3("Resumen por Fecha"),
        dash.dash_table.DataTable(
            data=filtered_cch.to_dict("records"),
            columns=[{"name": col, "id": col} for col in filtered_cch.columns]
        )
    ])
    
    return fig1, fig2, tabla

if __name__ == "__main__":
    app.run(debug=True)
    
# %% SEGUIMIENTO CENTROS INFANTILES
'''
SEGUIMIENTO CENTROS INFANTILES
'''
    
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import locale
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  
# import pandas as pd

# Cargar tus datos (ejemplo con tu estructura)
# ci = pd.read_csv("tu_ciset.csv", encoding='latin1')  # Ajusta el encoding si es necesario
# ci["Fecha"] = pd.to_datetime(ci["Fecha"], format="%d-%b")  # Convertir a datetime

# Iniciar la app Dash
app = dash.Dash(__name__)

# Layout del dashboard
app.layout = html.Div([
    html.H1("Dashboard de Seguimiento de Centros Infantiles"),
    
    # Dropdown para seleccionar escuela
    dcc.Dropdown(
        id="escuela-dropdown",
        options=[{"label": escuela, "value": escuela} for escuela in ci["Escuela"].unique()],
        value=ci["Escuela"].iloc[0],
        multi=False
    ),
    
    # Gráficos
    dcc.Graph(id="inscriptos-presentes"),
    dcc.Graph(id="raciones"),
    
    # Tabla resumen
    html.Div(id="tabla-resumen")
])

# Callbacks para interactividad
@app.callback(
    [Output("inscriptos-presentes", "figure"),
     Output("raciones", "figure"),
     Output("tabla-resumen", "children")],
    [Input("escuela-dropdown", "value")]
)
def update_dashboard(escuela_seleccionada):
    filtered_ci = ci[ci["Escuela"] == escuela_seleccionada]
  
    # Gráfico de inscriptos vs. presentes
    fig1 = px.line(
        filtered_ci, x="Fecha", y=["Inscriptos", "Presentes"],
        labels={
            'value' : 'Cantidad',
            'variable' : 'Tipo'
            },
        title=f"Evolución de Inscriptos vs. Presentes - {escuela_seleccionada}"
    )
    # Personalización adicional
    fig1.update_traces(
        line=dict(width=3),
        selector=dict(name='Presentes')
    )
    for idx, row in filtered_ci.iterrows():
       if row['Presentes'] == 0 and pd.notna(row['Observaciones']):
           fig1.add_annotation(
               x=row['Fecha'],
               y=0,
               text=row['Observaciones'],
               showarrow=True,
               arrowhead=1,
               ax=0,
               ay=-40,
               bgcolor="rgba(255,0,0,0.2)",
               bordercolor="#FF0000",
               font=dict(size=10)
           )

    # Gráfico de raciones
    fig2 = px.bar(
        filtered_ci, x="Fecha", y="Raciones",
        title=f"Raciones entregadas - {escuela_seleccionada}"
    )
    
    # Tabla resumen
    tabla = html.Div([
        html.H3("Resumen por Fecha"),
        dash.dash_table.DataTable(
            data=filtered_ci.to_dict("records"),
            columns=[{"name": col, "id": col} for col in filtered_ci.columns]
        )
    ])
    
    return fig1, fig2, tabla

if __name__ == "__main__":
    app.run(debug=True)
# %% SEGUIMIENTO CLUB DE JÓVENES
'''
SEGUIMIENTO CLUB DE JÓVENES
'''
    
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import locale
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  
# import pandas as pd

# Cargar tus datos (ejemplo con tu estructura)
# ci = pd.read_csv("tu_ciset.csv", encoding='latin1')  # Ajusta el encoding si es necesario
# ci["Fecha"] = pd.to_datetime(ci["Fecha"], format="%d-%b")  # Convertir a datetime

# Iniciar la app Dash
app = dash.Dash(__name__)

# Layout del dashboard
app.layout = html.Div([
    html.H1("Dashboard de Seguimiento de Club de Jóvenes"),
    
    # Dropdown para seleccionar escuela
    dcc.Dropdown(
        id="escuela-dropdown",
        options=[{"label": escuela, "value": escuela} for escuela in cj["Escuela"].unique()],
        value=cj["Escuela"].iloc[0],
        multi=False
    ),
    
    # Gráficos
    dcc.Graph(id="inscriptos-presentes"),
    dcc.Graph(id="raciones"),
    
    # Tabla resumen
    html.Div(id="tabla-resumen")
])

# Callbacks para interactividad
@app.callback(
    [Output("inscriptos-presentes", "figure"),
     Output("raciones", "figure"),
     Output("tabla-resumen", "children")],
    [Input("escuela-dropdown", "value")]
)
def update_dashboard(escuela_seleccionada):
    filtered_cj = cj[cj["Escuela"] == escuela_seleccionada]
  
    # Gráfico de inscriptos vs. presentes
    fig1 = px.line(
        filtered_cj, x="Fecha", y=["Inscriptos", "Presentes"],
        labels={
            'value' : 'Cantidad',
            'variable' : 'Tipo'
            },
        title=f"Evolución de Inscriptos vs. Presentes - {escuela_seleccionada}"
    )
    # Personalización adicional
    fig1.update_traces(
        line=dict(width=3),
        selector=dict(name='Presentes')
    )
    for idx, row in filtered_cj.iterrows():
       if row['Presentes'] == 0 and pd.notna(row['Observaciones']):
           fig1.add_annotation(
               x=row['Fecha'],
               y=0,
               text=row['Observaciones'],
               showarrow=True,
               arrowhead=1,
               ax=0,
               ay=-40,
               bgcolor="rgba(255,0,0,0.2)",
               bordercolor="#FF0000",
               font=dict(size=10)
           )

    # Gráfico de raciones
    fig2 = px.bar(
        filtered_cj, x="Fecha", y="Raciones",
        title=f"Raciones entregadas - {escuela_seleccionada}"
    )
    
    # Tabla resumen
    tabla = html.Div([
        html.H3("Resumen por Fecha"),
        dash.dash_table.DataTable(
            data=filtered_cj.to_dict("records"),
            columns=[{"name": col, "id": col} for col in filtered_cj.columns]
        )
    ])
    
    return fig1, fig2, tabla

if __name__ == "__main__":
    app.run(debug=True)
