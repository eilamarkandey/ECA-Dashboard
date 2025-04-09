from flask import Flask
from dash import Dash
from replica import create_dash_app

server = Flask(__name__)
app = create_dash_app(server)

# This is needed for Vercel serverless deployment
application = app.server

# Add a root route handler
@server.route('/')
def index():
    return app.index()

if __name__ == '__main__':
    application.run(debug=True) 