from flask_restplus import Namespace, fields

api = Namespace('Invite', 'Invitation Related APIs', path='/invite')

a_invite = api.model( 'email',
	{ 'email': fields.String() } 
)

a_suggest = api.model( 'suggest',
	{ 
		'email': fields.String(),
		'id': fields.Integer()
	} 
)