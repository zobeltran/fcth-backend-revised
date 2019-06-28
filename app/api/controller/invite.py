from flask import request
from flask_restplus import Resource
from app.src.models import db, Invitations, User, Package, Hotel, Ticket, Itinerary
from app.api.models.invite import api, a_invite, a_suggest
from flask_mail import Message, Mail
from app.src.helpers.decorators import token_required, token_details

mail = Mail()

@api.route('')
class InviteApi(Resource):
	@api.doc(security=None, responses={200: 'Success',
                                       400: 'Bad Request' 
                                      })
	@api.expect( a_invite )
	@token_required
	def post(self):
		url_redir = request.headers.get( "Referer" ) + "customer/registercustomer"
		data = api.payload
		token = token_details(request.headers['x-client-token'])
		user = User.query.filter(User.publicId==token['sub']).first()

		email = data[ "email" ]
		invited_exists = ( 
			Invitations.query
				.filter( Invitations.email == email )
			.first()
		)
		user_exists = (
			User.query
				.filter( User.email == email )
			.first()
		)

		ret = ({
			'errors': {
				'statusCode': 400,
	            'errorCode': 'A005',
	            'message': 'Sorry but the user you\'re trying to invite is either already invited or already have an account'
        	}
        }, 400)

		print( "REFERER:", url_redir )

		if not invited_exists and not user_exists:
			new_invite = Invitations(
				customer=user.id,
				email=email
			)

			db.session.add( new_invite )
			db.session.commit()
			msg = Message(
				subject="First Choice Travel Hub Registration Invitation",
                body=
                	"This is an email informing that user " + user.lastName + ", " + user.firstName + " " + user.middleName + "( " + user.email + " ) has invited you to register to First Choice Travel Hub.\n" +
                    "The link below will allow you to sign up. Thank you.\n" +
                    "[ " + url_redir + " ]",	
                recipients=[email]
            )
			mail.send(msg)
			ret = ({
				'data': {
					'message': 'Successfuly Invited'	
	            }
	        }, 200)

		return ret

@api.route('/suggest')
class SuggestApi(Resource):
	@api.doc(security=None, responses={200: 'Success',
                                       400: 'Bad Request' 
                                      })
	@api.expect( a_suggest )
	@token_required
	def post(self):		
		data = api.payload
		token = token_details(request.headers['x-client-token'])
		user = User.query.filter(User.publicId==token['sub']).first()

		email = data[ "email" ]
		pid = data[ "id" ]
		url_redir = request.headers.get( "Referer" ) + "suggest?id=" + pid
		
		package = (
			Package.query.filter( Package.id == pid )
				.join( Itinerary, Package.id == Itinerary.package )
				.join( Ticket, Package.flight == Ticket.id )
				.join( Hotel, Package.hotel == Hotel.id )
		).all()

		ret = ({
			'data': {
				'message': 'Package Successfully Suggested'
            }
        }, 200)		

		pkg = package[0]
		ticket_price = float( pkg.Tickets.price )
		hotel_price = float( pkg.Hotel.price )
		service_charge = ( ticket_price + ticket_price )*.02
		vat = float(service_charge) * .12
		total = ticket_price + hotel_price + service_charge + vat
		itineraryList = [ x.itinerary for x in pkg.itineraryList ]
		
		pkg_msg = (
			pkg.destination + "\n"
			"Itineraries:\n" +
			"\t" + "\n\t".join( itineraryList ) + "\n"
			"Days: " + str( pkg.days ) + "\n"
			"Prices:\n" +
			"\tTickets: P" + str( round( pkg.Tickets.price, 2 ) ) + "\n" +
			"\tHotel: P" + str( round( pkg.Hotel.price, 2 ) ) + "\n" +
			"\tService Charge: P" + str( service_charge ) + "\n" +
			"\tVAT: P" + str( vat ) + "\n" +
			"\tTotal: P" + str( total ) + "\n" +
			"Flight Ticket: " + pkg.Tickets.flightNo + " (" + pkg.Tickets.origin + "-" + pkg.Tickets.arrival + ")\n" +
			"Hotel: " + pkg.Hotel.name + "\n" +
			"Slots Available: " + str( pkg.remainingSlots ) + "\n" +
			"Departure Date: " + str( pkg.Tickets.departureDate ) + "\n" +
			"Expiration Date: " + str( pkg.expirationDate ) + "\n" +
			"Note: " + pkg.note
		)

		print( pkg_msg )
		msg = Message(
			subject="First Choice Travel Hub Package Suggestion",
            body=
            	"This is an email informing that user " + user.lastName + ", " + user.firstName + " " + user.middleName + "( " + user.email + " ) has suggested a package for you at First Choice Travel Hub.\n\n" +
            	pkg_msg + "\n\n" +
                "The link below will allow you to book this. Thank you.\n" +
                "[ " + url_redir + " ]",	
            recipients=[email]
        )
		mail.send(msg)

		return ret