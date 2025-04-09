from flask import Flask
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_dash_app

server = Flask(__name__)
app = create_dash_app(server).server

if __name__ == '__main__':
    app.run(debug=True) 