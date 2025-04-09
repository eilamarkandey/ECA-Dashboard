from flask import Flask
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import requests
from io import BytesIO

server = Flask(__name__)
app = Dash(__name__, server=server)

# Cache the data
CACHED_DATA = None

def load_data():
    global CACHED_DATA
    if CACHED_DATA is not None:
        return CACHED_DATA
        
    try:
        file_id = '18Uz_n4Jp1EtXvCnQhqdGDFn1H7clLMyt'
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url)
        df = pd.read_excel(BytesIO(response.content))
        df.columns = df.columns.str.lower().str.replace(' ', '')
        CACHED_DATA = df
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame()

app.layout = html.Div(
    style={
        'margin': '20px',
        'fontFamily': 'Arial',
        'maxWidth': '1200px',
        'marginLeft': 'auto',
        'marginRight': 'auto'
    },
    children=[
        html.H1("ECA Campaign Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        html.Div([
            dcc.Loading(
                id="loading-graph",
                type="circle",
                children=[dcc.Graph(id='main-graph')]
            )
        ])
    ]
)

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
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Start Date",
        yaxis_title="Parent Campaign Name",
        legend_title="ECA Activity Type"
    )
    
    return fig

# For Vercel
application = app.server

if __name__ == '__main__':
    app.run_server(debug=True) 