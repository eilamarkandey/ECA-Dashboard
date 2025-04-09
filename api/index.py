from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = Dash(__name__)
server = app.server

# Create sample data
df = pd.DataFrame({
    'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
    'Campaign': ['Campaign A', 'Campaign B', 'Campaign A', 'Campaign B'],
    'Type': ['Email', 'Social', 'Email', 'Social']
})

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
            "Campaign Dashboard",
            style={
                'textAlign': 'center',
                'color': '#2c3e50',
                'marginBottom': '30px'
            }
        ),
        dcc.Graph(
            figure=px.scatter(
                df,
                x='Date',
                y='Campaign',
                color='Type',
                title='Campaign Timeline'
            ).update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
        )
    ]
)

# This is required for Vercel deployment
application = app.server

if __name__ == '__main__':
    app.run_server(debug=True) 