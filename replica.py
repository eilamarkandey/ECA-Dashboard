import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import os

def load_data():
    # Use relative paths from the current file
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, 'data')
    
    # Define file paths relative to data directory
    input_path = os.path.join(data_path, 'ECA Campaigns_FY25_ALL_v2.xlsx')
    members_path = os.path.join(data_path, 'ECA Campaign Members_FY25_ALL.xlsx')
    
    # Load data
    df = pd.read_excel(input_path)
    members_df = pd.read_excel(members_path)
    
    # Data processing
    df.columns = df.columns.str.lower().str.replace(' ', '')
    
    # Process dates
    df['startdate'] = pd.to_datetime(df['startdateandtime'].str.split(',').str[0], format='%m/%d/%Y', errors='coerce')
    
    # Create binary columns for activity types
    df['meeting'] = (df['ecaactivitytype'] == 'Meeting').astype(int)
    df['event'] = (df['ecaactivitytype'] == 'Event').astype(int)
    
    # Filter for first-time interactions
    first_time_mask = (
        (df['interactiontype'] == "1st Time Inquiry – Requested by Org or Group") | 
        (df['interactiontype'] == "1st Time Outreach – Initiated by ECA Staff")
    )
    df_filtered = df[first_time_mask]
    
    return df, df_filtered

def create_dash_app(server=None):
    # Initialize the Dash app
    if server:
        app = Dash(__name__, 
                   server=server,
                   url_base_pathname='/',
                   external_stylesheets=[dbc.themes.BOOTSTRAP])
    else:
        app = Dash(__name__, 
                  external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Load data
    df, df_filtered = load_data()
    
    # Create the layout
    app.layout = html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("ECA Campaign Dashboard", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='campaign-timeline')
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='interaction-types')
                ])
            ])
        ])
    ])
    
    # Add callbacks
    @app.callback(
        Output('campaign-timeline', 'figure'),
        Input('campaign-timeline', 'relayoutData')
    )
    def update_timeline(relayoutData):
        fig = px.scatter(df_filtered,
                        x='startdate',
                        y='parentcampaignname',
                        color='ecaactivitytype',
                        title='Campaign Timeline')
        return fig
    
    @app.callback(
        Output('interaction-types', 'figure'),
        Input('campaign-timeline', 'selectedData')
    )
    def update_interaction_types(selectedData):
        fig = px.bar(df_filtered,
                    x='interactiontype',
                    title='Interaction Types Distribution')
        return fig
    
    return app

# For local development only
if __name__ == '__main__':
    app = create_dash_app()
    app.run_server(debug=True)





