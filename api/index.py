from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import requests
from flask import Flask

# Initialize Flask
server = Flask(__name__)

# Initialize Dash
app = Dash(
    __name__,
    server=server,
    url_base_pathname='/',
    assets_folder='assets'
)

# Enable the app to be imported by Vercel
application = app.server

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
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.replace(' ', '')
        CACHED_DATA = df
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Define the layout
app.layout = html.Div(
    style={
        'margin': '20px',
        'fontFamily': 'Arial',
        'maxWidth': '1200px',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'backgroundColor': '#ffffff',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    },
    children=[
        html.H1(
            "ECA Campaign Dashboard",
            style={
                'textAlign': 'center',
                'color': '#2c3e50',
                'marginBottom': '30px',
                'borderBottom': '2px solid #eee',
                'paddingBottom': '10px'
            }
        ),
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
        legend_title="ECA Activity Type",
        font=dict(family="Arial"),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=False) 