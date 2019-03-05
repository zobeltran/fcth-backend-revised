import uuid
from flask_restplus import Resource
from app.src.models import db, User
from app.api.models.user import api, a_auth, a_user, a_user_details
from app.src.helpers.decorators import token_required
import jwt
from datetime import datetime, timedelta
from os import getenv
from flask_bcrypt import Bcrypt
from flask_mail import Message, Mail

mail = Mail()
secret_key = getenv('SECRET_KEY')
bcrypt = Bcrypt()
errors = []

@api.route('/auth')
class AuthenticationApi(Resource):
    @api.doc(security=None,
             responses={
                200: 'Success',
                400: 'Bad Request'
             })
    @api.expect(a_auth)
    def post(self):
        errors.clear()
        data = api.payload
        try:
            username = data['username']
            password = data['password']
            if data:
                if not username and not password:
                    errors.append('Username must not be null')
                    errors.append('Password must not be null')
                    return {'errors': {'statusCode': 400,
                                       'errorCode': 'A004',
                                       'message': errors}}, 400
                if not username:
                    errors.append('Username must not be null')
                    return {'errors': {'statusCode': 400,
                                       'errorCode': 'A004',
                                       'message': errors}}, 400
                if not password: 
                    errors.append('Password must not be null')
                    return {'errors': {'statusCode': 400,
                                       'errorCode': 'A004',
                                       'message': errors}}, 400
                user = User.query.filter(User.username == username).first()
                if user:
                    db_password = user.password_hashed
                    checked_hash = bcrypt.check_password_hash(db_password, 
                                                              password)
                    role = user.role
                    if checked_hash:
                        time = datetime.utcnow() + timedelta(minutes=60)
                        token = jwt.encode({'sub': user.publicId,
                                            'role': user.role,
                                            'exp': time
                                            }, secret_key)
                        return {'data':
                                    {'token': token.decode('utf-8'),
                                     'role': role
                                    }}, 200
                    else:
                        errors.append('Password invalid')
                        return {'errors': {'statusCode': 400,
                                        'errorCode': 'A005',
                                        'message': errors
                                        }}, 400
                else:
                    errors.append('User not found')
                    return {'errors': {'statusCode': 400,
                                    'errorCode': 'A005',
                                    'message': errors
                                    }}, 400
        except KeyError:
            errors.append('Incomplete json nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

@api.route('')
# @cross_origin(allow_headers=['Content-Type'])
class UserApi(Resource):

    @api.doc(security='apiKey', responses={200: 'Success',
                                           401: 'Unauthorized'
                                           })
    @token_required
    @api.marshal_list_with(a_user_details, envelope='users')
    def get(self):
        users = User.query.all()
        view_users = []
        for user in users:
            view_users.append(
                {
                    'id': user.id,
                    'name': {
                        'first': user.firstName,
                        'middle': user.middleName,
                        'last': user.lastName
                    },
                    'auth': {
                        'username': user.username,
                        'passwordHashed': user.password_hashed
                    },
                    'details': {
                        'email': user.email,
                        'role': user.role
                    },
                    'timestamp': {
                        'dateCreated': user.dateCreated,
                        'dateUpdated': user.dateUpdated
                    }
                }
            )
        return view_users, 200

    @api.doc(security=None, responses={200: 'Success',
                                       401: 'Unauthorized'})
    @api.expect(a_user)
    def post(self):
        try: 
            errors.clear()
            data = api.payload
            first_name = data['name']['first']
            middle_name = data['name']['middle']
            last_name = data['name']['last']
            email = data['details']['email']
            role = data['details']['role']
            username = data['auth']['username']
            password = data['auth']['password']
            public_id = uuid.uuid4()
            if data:
                if (not first_name or
                        not middle_name or
                        not last_name or
                        not username or
                        not password or
                        not email or
                        not role):
                    if not first_name:
                        errors.append('First Name must not be null')
                    if not last_name:
                        errors.append('Last Name must not be null')
                    if not username:
                        errors.append('Username must not be null')
                    if not password:
                        errors.append('Password must not be null')
                    if not email:
                        errors.append('Email must not be null')
                    if not role:
                        errors.append('Role must not be null')
                    return {'errors': {'statusCode': 400,
                                    'errorCode': 'E0002',
                                    'message': errors}}, 400
                else:
                    password_bcryt = (bcrypt.generate_password_hash(password))
                    username_unique = (User.query
                                       .filter(User.username == username).all())
                    password_hashed = (password_bcryt.decode('utf-8'))
                    if username_unique:
                        errors.append('Username is already taken')
                        return {'error': {'statusCode': 400,
                                          'message': errors}}, 400
                    else:
                        new_user = User(firstName=first_name,
                                        middleName=middle_name,
                                        lastName=last_name,
                                        email=email,
                                        role=role,
                                        publicId=public_id,
                                        username=username,
                                        password_hashed=password_hashed)
                        db.session.add(new_user)
                        db.session.commit()
                        msg = Message(subject="First Choice Travel Hub Registration",
                                      body="Informing that you have registered to First Choice Travel Hub.",
                                      recipients=[email])
                        mail.send(msg)
                        return {'data': {'statusCode': 201,
                                         'message': 'User has been registered'}
                                }, 201
            errors.append('Please fill up the form')
            return {'errors': {'statusCode': 400,
                               'errorCode': 'U0001',
                               'message': errors}}
        except KeyError:
            errors.append('Incomplete json nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400
