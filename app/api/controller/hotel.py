from flask_restplus import Resource
from app.src.models import db, Hotel
from app.api.models.hotel import api, a_create_hotel, a_hotel_details
from app.src.helpers.decorators import token_required
from datetime import datetime, timedelta
from dateutil.parser import parse

erros = []
now = datetime.now()

@api.route('')
@api.response(404, 'Not Found')
class HotelApi(Resource):
    @api.doc(security="None", responses={200: "Success",
                                         400: "Bad Request"})
    @api.marshal_list_with(a_hotel_details, envelope="hotels")
    def get(self):
        hotels = (Hotel.query.filter(Hotel.isArchived.is_(False))
                  .filter(Hotel.isExpired.is_(False))
                  .filter(Hotel.isPackaged.is_(False))
                  .filter(Hotel.isApproved.is_(False)).all())
        view_hotels = []
        for hotel in hotels:
            view_hotels.append(
                {
                    'id': hotel.id,
                    'name': hotel.name,
                    'room': {
                        'type': hotel.roomType,
                        'capacity': hotel.capacity
                    },
                    'details': hotel.details,
                    'checkDates': {
                        'in': hotel.checkIn,
                        'out': hotel.checkOut
                    },
                    'price': hotel.price,
                    'expirationDate': hotel.expirationDate,
                    'isExpired': hotel.isExpired,
                    'isPackaged': hotel.isPackaged,
                    'remainingRooms': hotel.remainingRooms,
                    'timestamp': {
                        'dateCreated': hotel.dateCreated,
                        'dateUpdated': hotel.dateUpdated
                    }
                }
            )
        return view_hotels, 200
