import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
import requests
from io import BytesIO

def load_data():
    try:
        # Your Google Drive file ID
        file_id = '18Uz_n4Jp1EtXvCnQhqdGDFn1H7clLMyt'
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        response = requests.get(url)
        df = pd.read_excel(BytesIO(response.content))
        df.columns = df.columns.str.lower().str.replace(' ', '')
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
            html.H1("ECA Dashboard", className="text-center my-4"),
            dcc.Loading(
                id="loading",
                children=[dcc.Graph(id='main-graph')]
            )
        ])
    ])
    
    @app.callback(
        Output('main-graph', 'figure'),
        Input('main-graph', 'id')
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