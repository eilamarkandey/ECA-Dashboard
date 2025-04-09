import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import requests
from io import BytesIO

# Main file ID (using just one file for now to get it working)
FILE_ID = '18Uz_n4Jp1EtXvCnQhqdGDFn1H7clLMyt'

def load_data():
    try:
        url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
        response = requests.get(url)
        df = pd.read_excel(BytesIO(response.content))
        
        # Basic processing
        df.columns = df.columns.str.lower().str.replace(' ', '')
        df['startdate'] = pd.to_datetime(df['startdateandtime'].str.split(',').str[0], 
                                       format='%m/%d/%Y', 
                                       errors='coerce')
        return df
    except Exception as e:
        print(f"Error: {str(e)}")
        return pd.DataFrame()

def create_dash_app(server=None):
    app = Dash(__name__, 
               server=server,
               url_base_pathname='/',
               external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    app.layout = html.Div([
        dbc.Container([
            html.H1("ECA Campaign Dashboard", className="text-center mb-4"),
            dcc.Loading(
                id="loading",
                children=[dcc.Graph(id='timeline-graph')]
            )
        ])
    ])
    
    @app.callback(
        Output('timeline-graph', 'figure'),
        Input('timeline-graph', 'id')
    )
    def update_graph(_):
        df = load_data()
        if df.empty:
            return {}
            
        fig = px.scatter(df,
                        x='startdate',
                        y='parentcampaignname',
                        color='ecaactivitytype',
                        title='Campaign Timeline')
        return fig
    
    return app

if __name__ == '__main__':
    app = create_dash_app()
    app.run_server(debug=True) 