from flask import Flask
from dash import Dash
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_dash_app

server = Flask(__name__)
dash_app = create_dash_app(server)
app = dash_app.server

# The application
app = server

# For Vercel serverless deployment
@app.route('/')
def home():
    return dash_app.index()

# Handle all Dash routes
@app.route('/<path:path>')
def catch_all(path):
    return dash_app.index()

# Required for Vercel
app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True) 