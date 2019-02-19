from flask import Blueprint
from flask_restplus import Api
from app.src.helpers.decorators import authentication
from app.api.controller.user import api as user_api
from app.api.controller.ticket import api as ticket_api
from app.api.controller.hotel import api as hotel_api

api_routes = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_routes, title='First Choice Travel Hub API', 
          version='1', doc='/documentation', authorizations=authentication)

api.add_namespace(user_api)
api.add_namespace(ticket_api)
api.add_namespace(hotel_api)
