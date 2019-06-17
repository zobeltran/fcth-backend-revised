
"""
Package API version 2
"""
from flask import request
from datetime import datetime
from dateutil.parser import parse
from flask_restplus import Resource
from app.src.models import db, Package, Hotel, Ticket, Itinerary, User, PackageBooking
from app.api.models.v2.package_version2 import API, A_CREATE_PACKAGE_NEW, A_PACKAGE
from app.src.helpers.decorators import token_required, token_details

ERRORS = []
NOW = datetime.now()


def itirate(items):
    view_items = []
    if len(items) == 1:
        None
    for item in items:
        view_items.append(
            {
                'id': item.id,
                'itinerary': item.itinerary
            }
        )
    return view_items


@API.route('')
@API.response(404, 'Not Found')
class PackagedApi(Resource):
    """
        Package version 2 API class
    """
    @API.doc(security='apiKey', responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @API.expect(A_CREATE_PACKAGE_NEW)
    def post(self):
        """POST method for endpoint api/v2/packages

        :returns: a HTTP response

        :rtype: HTTP
        """

        ERRORS.clear()
        data = API.payload
        try:
            name = data['name']
            days = int(data['details']['days'])
            itinerary = data['itinerary']
            notes = data['details']['notes']
            remaining_slots = int(data['remainingSlots'])
            ticket = int(data['ticket'])
            hotel = int(data['hotel'])
            expiration_date = parse(data['expirationDate'])
            if data:
                if (not name or
                        not days or
                        not itinerary or
                        not notes or
                        not remaining_slots or
                        not ticket or
                        not hotel or
                        not expiration_date):
                    if not name:
                        ERRORS.append('Name must not be null')
                    if not days:
                        ERRORS.append('Days must not be null')
                    if not notes:
                        ERRORS.append('Notes must not be null')
                    if not remaining_slots:
                        ERRORS.append('Remaining Slots must not be null')
                    if not ticket:
                        ERRORS.append('Ticket must not be null')
                    if not hotel:
                        ERRORS.append('Hotel must not be null')
                    if not expiration_date:
                        ERRORS.append('Expiration Date must not be null')
                    return {'errors': {'status': 400,
                                       'errorCode': 'E0002',
                                       'message': ERRORS}}, 400
                elif (expiration_date <= NOW or
                      remaining_slots <= 0):
                    if expiration_date <= NOW:
                        ERRORS.append('Expiration date must be not be less is equal '
                                      'to today\'s date')
                    if remaining_slots <= 0:
                        ERRORS.append('Remaining slots must be greater than zero')
                    return {'ERRORS': {'status': 400,
                                       'errorCode': 'E0002',
                                       'message': ERRORS}}, 400
                else:
                    ticket_details = Ticket.query.get(ticket)
                    hotel_details = Hotel.query.get(hotel)
                    basic_price = float(ticket_details.price) + float(hotel_details.price)
                    new_package = Package(destination=name,
                                          price=basic_price,
                                          days=days,
                                          remainingSlots=remaining_slots,
                                          expirationDate=expiration_date,
                                          note=notes,
                                          hotel=hotel,
                                          flight=ticket)
                    db.session.add(new_package)
                    db.session.flush()
                    for itinerary_item in itinerary:
                        new_itinerary = Itinerary(itinerary=itinerary_item['value'],
                                                  package=new_package.id)
                        db.session.add(new_itinerary)
                    db.session.commit()
                    return {'message': 'Successfully added new Packaged'}, 201
        except KeyError:
            ERRORS.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': ERRORS}}, 400

    @API.doc(security="apiKey", responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @API.marshal_list_with(A_PACKAGE, envelope='packages')
    def get(self):
        """GET method for endpoint api/v2/packages

        :returns: a list of dictionaries containing package details

        :rtype: list
        """

        packages = (Package.query.filter(Package.isArchived.is_(False))
                    .filter(Package.isExpired.is_(False))
                    .filter(Package.isApproved.is_(True)).all())
        view_packages = []
        view_itinerary = []
        for package in packages:
            print(package.id)
            ticket = Ticket.query.get(package.flight)
            hotel = Hotel.query.get(package.hotel)
            itineraries = Itinerary.query.filter(Itinerary.package == package.id).all()
            # view_itinerary.clear()
            service_charge = (float(ticket.price) + float(hotel.price))*.02
            vat = float(service_charge) * .12
            for itinerary in itineraries:
                print(itinerary)
                view_itinerary.append(
                    {
                        'id': itinerary.id,
                        'itinerary': itinerary.itinerary
                    }
                )
            view_packages.append(
                {
                    'id': package.id,
                    'name': package.destination,
                    'details': {
                        'days': package.days,
                        'notes': package.note,
                        'date': ticket.departureDate
                    },
                    'departureDate': ticket.departureDate,
                    'itinerary': itirate(itineraries),
                    'price': {
                        'ticket': ticket.price,
                        'hotel': hotel.price,
                        'serviceCharge': service_charge,
                        'vat': vat
                    },
                    'ticket': {
                        'id': ticket.id,
                        'flightNo': ticket.flightNo,
                        'origin': ticket.origin,
                        'destination': ticket.arrival
                    },
                    'hotel': {
                        'id': hotel.id,
                        'name': hotel.name,
                        'roomType': hotel.roomType,
                        'capacity': hotel.capacity
                    },
                    'remainingSlots': package.remainingSlots,
                    'expirationDate': package.expirationDate,
                    'isExpired': package.isExpired
                }
            )
        return view_packages, 200

@API.route('/booking')
@API.response(404, 'Not Found')
class PackageBookingApiId(Resource):
    @API.doc(security="apiKey", responses={200: 'Success', 400: 'Bad Request'})
    @token_required
    @API.marshal_list_with(A_PACKAGE, envelope='packages')
    def get(self):
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId == token['sub']).first()
        bookings = PackageBooking.query.filter(PackageBooking.customer == user.id).all()
        view_packages = []
        view_itinerary = []
        for bookings in bookings:
            package = Package.query.get(bookings.package)
            ticket = Ticket.query.get(package.flight)
            hotel = Hotel.query.get(package.hotel)
            itineraries = Itinerary.query.filter(Itinerary.package == package.id).all()
            view_itinerary.clear()
            service_charge = (float(ticket.price) + float(hotel.price))*.02
            vat = float(service_charge) * .12
            for itinerary in itineraries:
                view_itinerary.append(
                    {
                        'id': itinerary.id,
                        'itinerary': itinerary.itinerary
                    }
                )
            view_packages.append(
                {
                    'id': package.id,
                    'name': package.destination,
                    'details': {
                        'days': package.days,
                        'notes': package.note,
                        'date': ticket.departureDate
                    },
                    'departureDate': ticket.departureDate,
                    'itinerary': itirate(itineraries),
                    'price': {
                        'ticket': ticket.price,
                        'hotel': hotel.price,
                        'serviceCharge': service_charge,
                        'vat': vat
                    },
                    'ticket': {
                        'id': ticket.id,
                        'flightNo': ticket.flightNo,
                        'origin': ticket.origin,
                        'destination': ticket.arrival
                    },
                    'hotel': {
                        'id': hotel.id,
                        'name': hotel.name,
                        'roomType': hotel.roomType,
                        'capacity': hotel.capacity
                    },
                    'remainingSlots': package.remainingSlots,
                    'expirationDate': package.expirationDate,
                    'isExpired': package.isExpired
                }
            )
        return view_packages, 200