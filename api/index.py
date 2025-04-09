from flask import Flask
from dash import Dash
from replica import create_dash_app

# Initialize Flask
server = Flask(__name__)

# Initialize Dash
app = create_dash_app(server)

# Get the Flask application
application = app.server

# Add explicit route handlers
@application.route('/')
def index():
    return app.index()

@application.route('/<path:path>')
def catch_all(path):
    return app.index()

if __name__ == '__main__':
    application.run(debug=True) 