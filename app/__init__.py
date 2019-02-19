from os import getenv
from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from app.src.models import db
from app.api.controller.user import bcrypt
from app.src.routes.api_v1 import api_routes as api_v1_routes

# Flask Activation
app = Flask(__name__)

# Set Configurations
secret_key = getenv('SECRET_KEY')
db_uri = getenv('DATABASE_URI')
sql_track_modification = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
cors_headers = ['content-type', 'x-client-token']

# Activate Configurations
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = sql_track_modification

# Activate Extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt.init_app(app)

# Main Routes
app.register_blueprint(api_v1_routes)

@app.route('/')
def index():
    return redirect(url_for('documentation_version1'))

@app.route('/api/v1/documentation')
def documentation_version1():
    pass

if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run()