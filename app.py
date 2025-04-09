import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import os
import requests
from io import BytesIO

# Google Drive file IDs
FILE_IDS = {
    'file1': '18Uz_n4Jp1EtXvCnQhqdGDFn1H7clLMyt',
    'file2': '1Htdb4O5oSVL2taiRzWZP4W0zZKRZAFf0',
    'file3': '1kPvkmNKkdfqa0RrM6-goqHOJvXJPxYTh'
}

def get_drive_file_content(file_id):
    """Get file content from Google Drive"""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        response = requests.get(url)
        return BytesIO(response.content)
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None

def load_data():
    try:
        # Get the main campaigns file (assuming it's the first file)
        file_content = get_drive_file_content(FILE_IDS['file1'])
        if file_content is None:
            raise Exception("Could not download file from Google Drive")
            
        # Read Excel content
        df = pd.read_excel(file_content)
        
        # Process data
        df.columns = df.columns.str.lower().str.replace(' ', '')
        
        # Process dates
        df['startdate'] = pd.to_datetime(df['startdateandtime'].str.split(',').str[0], 
                                       format='%m/%d/%Y', 
                                       errors='coerce')
        
        print("Data loaded successfully!")
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_dash_app(server=None):
    if server:
        app = Dash(__name__, 
                   server=server,
                   url_base_pathname='/',
                   external_stylesheets=[dbc.themes.BOOTSTRAP])
    else:
        app = Dash(__name__, 
                  external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Create layout
    app.layout = html.Div([
        dbc.Container([
            html.H1("ECA Campaign Dashboard", className="text-center mb-4"),
            html.Div(id="data-status", className="text-center mb-3"),
            dcc.Loading(
                id="loading",
                type="default",
                children=[dcc.Graph(id='timeline-graph')]
            ),
            dcc.Interval(
                id='interval-component',
                interval=300000,  # refresh every 5 minutes
                n_intervals=0
            )
        ])
    ])
    
    @app.callback(
        [Output('timeline-graph', 'figure'),
         Output('data-status', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_graph(n):
        try:
            df = load_data()  # Reload data
            if df.empty:
                return {}, "Error: No data available"
                
            fig = px.scatter(df,
                           x='startdate',
                           y='parentcampaignname',
                           color='ecaactivitytype',
                           title='Campaign Timeline')
            
            return fig, f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as e:
            return {}, f"Error loading data: {str(e)}"
    
    return app

if __name__ == '__main__':
    app = create_dash_app()
    app.run_server(debug=True) 