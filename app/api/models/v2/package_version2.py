"""
Package Version 2 API Models
"""
from flask_restplus import Namespace, fields

API = Namespace('Packages', 'Package related APIs', path='/packages')


A_TIMESTAMP = API.model('Timestamp',
                        {'dateCreated': fields.DateTime(),
                         'dateUpdated': fields.DateTime()
                         })

A_TICKET_DETAILS = API.model('Ticket Package Details',
                             {'id': fields.Integer(),
                              'flightNo': fields.String(),
                              'origin': fields.String(),
                              'destination': fields.String()
                              })

A_HOTEL_DETAILS = API.model('Hotel Pakage Details',
                            {'id': fields.Integer(),
                             'name': fields.String(),
                             'roomType': fields.String(),
                             'capacity': fields.Integer()
                             })

A_PACKAGE_SPECIFICATION = API.model('Package Specifications',
                                    {'days': fields.String(),
                                     'notes': fields.String(),
                                     'date': fields.Date()
                                     })

A_PACKAGE_PRICES = API.model('Package Prices',
                             {'ticket': fields.Float(),
                              'hotel': fields.Float(),
                              'serviceCharge': fields.Float(),
                              'vat': fields.Float(),
                              'total': fields.Float()})

A_PACKAGE_SPECS = API.model('Package Specifications',
                            {'days': fields.String(),
                             'notes': fields.String(),
                            })

A_ITINERARY = API.model('Itinerary',
                        {'id': fields.Integer(),
                         'itinerary': fields.String()})

A_ITINERARY_INSERT = API.model('Itinerary Insert',
                               {'value': fields.String()})
A_USER_DETAILS = API.model( "User Details", {
  'user': fields.Integer(),
  'email': fields.String()
})
A_PACKAGE = API.model('Package Details',
                      {'booking_id': fields.Integer(),
                       'id': fields.Integer(),
                       'referenceNumber': fields.String(),
                       'name': fields.String(),
                       'price': fields.Nested(A_PACKAGE_PRICES),
                       'departureDate': fields.Date(),
                       'itinerary': fields.List(fields.Nested(A_ITINERARY)),
                       'details': fields.Nested(A_PACKAGE_SPECIFICATION),
                       'ticket': fields.Nested(A_TICKET_DETAILS),
                       'hotel': fields.Nested(A_HOTEL_DETAILS),
                       'user': fields.Nested( A_USER_DETAILS ),
                       'remainingSlots': fields.Integer(),
                       'expirationDate': fields.Date(),
                       'isExpired': fields.Boolean(),
                       'isPaid': fields.Boolean()
                      })

A_CREATE_PACKAGE_NEW = API.model('Create Package',
                                 {'name': fields.String(),
                                  'details': fields.Nested(A_PACKAGE_SPECS),
                                  'itinerary':fields.List(fields.Nested(A_ITINERARY_INSERT), description='itinerary'),
                                  'ticket': fields.Integer(),
                                  'hotel': fields.Integer(),
                                  'remainingSlots': fields.Integer(),
                                  'expirationDate': fields.Date()
                                 })
