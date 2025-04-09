from flask import Flask
from dash import Dash
import sys
import os

# Add the parent directory to Python path so we can import replica
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from replica import create_dash_app

# Initialize Flask
server = Flask(__name__)

# Initialize Dash with the server
dash_app = create_dash_app(server)

# Get the Flask application
app = dash_app.server

# For Vercel serverless deployment
@app.route('/')
def home():
    return dash_app.index()

if __name__ == '__main__':
    app.run(debug=True) 