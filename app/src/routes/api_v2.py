"""
API Routes Blueprint for Version 2
"""
from flask import Blueprint
from flask_restplus import Api
from app.src.helpers.decorators import authentication
from app.api.controller.v2.package_version2 import API as package_api

API_ROUTES_V2 = Blueprint('apiV2', __name__, url_prefix='/api/v2')
API = Api(API_ROUTES_V2, title='First Choice Travel Hub API',
          version='2', doc='/documentation', authorizations=authentication)

API.add_namespace(package_api)
