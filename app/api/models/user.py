from flask_restplus import Namespace, fields

api = Namespace('Users', 'User Authentication Related APIs', path='/users')

a_user_name = api.model('name',
                        {'first': fields.String(desc="First Name of the User"),
                         'middle': fields.String(desc="Middle Name of the User"),
                         'last': fields.String(desc="Last Name of the User")
                        })

a_auth = api.model('auth', 
                        {'username': fields.String(),
                         'password': fields.String()
                        })

a_auth_hashed = api.model('authDetails',
                         {'username': fields.String(),
                          'passwordHashed': fields.String()
                         })

a_user_details = api.model('details',
                           {'email': fields.String(),
                            'role': fields.String()
                           })

a_user_timestamp = api.model('timestamp',
                             {'dateCreated': fields.DateTime(),
                              'dateUpdated': fields.DateTime()
                             })

a_user = api.model('user',
                   {'name': fields.Nested(a_user_name),
                    'details': fields.Nested(a_user_details),
                    'auth': fields.Nested(a_auth)
                   })

a_user_details = api.model('users',
                           {'id': fields.Integer(),
                            'name': fields.Nested(a_user_name),
                            'auth': fields.Nested(a_auth_hashed),
                            'details': fields.Nested(a_user_details),
                            'timestamp': fields.Nested(a_user_timestamp)
                           })