from flask import request
from flask_restplus import Resource
from app.src.models import User, HotelInquiry, FlightInquiry, User
from app.src.helpers.decorators import token_required, token_details
from app.api.models.inquiry import api, a_inquiries_flight_details
from app.api.models.inquiry import a_inquiries_hotel_create, a_inquiries_flight_create
from datetime import datetime
from dateutil.parser import parse

errors = []
now = datetime.now()

@api.route('/tickets')
@api.response(404, 'Not Found')
class TicketInquiry(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'})
    @token_required
    @api.marshal_list_with(a_inquiries_flight_details, envelope='flight')
    def get(self):
        ticket_inquiry = FlightInquiry.query.all()
        view_ticket_inquiry = []
        for ticket in ticket_inquiry:
            user = User.query.get(ticket.customer)
            view_ticket_inquiry.append(
                {
                    'id': ticket.id,
                    'customer': {
                        'id': user.id,
                        'name': {
                            'first': user.firstName,
                            'middle': user.middleName,
                            'last': user.lastName
                        },
                        'email': user.email
                    },
                    'flight': {
                        'origin': {
                            'location': ticket.origin,
                            'date': ticket.departureDate
                        },
                        'departure': {
                            'location': ticket.arrival,
                            'date': ticket.arrivalDate
                        }
                    },
                    'passenger': {
                        'adult': ticket.adult,
                        'child': ticket.child,
                        'infant': ticket.infant
                    },
                    'note': ticket.note
                }
            )
        return view_ticket_inquiry, 200

        # @api.doc(security='apiKey', responses={200: 'Success',
        #                                        400: 'Bad Request'})
        # @token_required
        # @api.expect(a_inquiries_flight_create)
        # def post(self):
        #     errors.clear()
        #     data = api.payload
        #     token = token_details(request.headers['x-client-token'])
        #     user = User.query.filter(User.publicId==token['sub']).first()
        #     try:
        #         flight_details = data['flight']
        #         origin = flight_details['origin']['location']
        #         departure = flight_details['departure']['location']
        #         origin_date = flight_details['origin']['date']
        #         departure_date = flight_details['departure']['date']
        #         passenger = data['passenger']
        #         adults = passenger['adult']
        #         child = passenger['child']
        #         infant = passenger['infant']
        #         note = data['note']
        #         if (not origin or
        #                 not departure or
        #                 not origin_date or
        #                 not departure_date or
        #                 not adults or
        #                 not child or
        #                 not infant or
        #                 not note):
        #             if not origin:
        #                 errors.append('Origin must not be null')
        #             elif not departure:
        #                 errors.append('Departure must not be null')
        #             elif not origin_date:
        #                 errors.append('Origin Date must not be null')
        #             elif not departure_date:
        #                 errors.append('Departure Date must not be null')
        #             elif not adults:
        #                 errors.append('Adult count must not be null')
        #             elif not infant:
        #                 errors.append('Infant count must not be null')
        #             elif not child:
        #                 errors.append('Children count must not be null')
        #             elif not note:
        #                 errors.append('Note must not be null')
        #             return {'errors': {'status': 400,
        #                                'errorsCodes': 'E00I2',
        #                                'message': errors}}, 400
        #         if (parse(origin_date) < now or
        #                 parse(departure_date) < now or
        #                 parse(departure_date) < parse(origin_date) or
        #                 int(adults) < 0 or
        #                 int(child) < 0 or
        #                 int(infant) < 0):
        #             return {'errors': {'status': 400,
        #                                'errorsCodes': 'E00I2',
        #                                'message': errors}}, 400
        #         else:
        #             new_inquiry = FlightInquiry(customer=user.id,
        #                                         origin=origin,
        #                                         arrival=departure,
        #                                         departureDate=parse(origin_date),
        #                                         arrivalDate=parse(departure_date),
        #                                         adult=int(adults),
        #                                         child=int(child),
        #                                         infant=int(infant),
        #                                         note=note)