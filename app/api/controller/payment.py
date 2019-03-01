from flask_restplus import Resource
from app.src.models import db, Payments, Hotel, Ticket, Package
from app.src.models import FlightBooking, HotelBooking, PackageBooking
from app.src.models import StripeCustomer
from app.api.models.payment import api, a_create_stripe_charges, a_stripe_details
from app.src.helpers.decorators import referenceNumber
import stripe
from flask import request

errors = []

pubkey = 'pk_test_GjK3GmJJ1exs60wIcgTpfggq'
secretkey = 'sk_test_RXyvP1FBgkRyCwyEBGyZeymo'

stripe.api_key = secretkey

@api.route('')
@api.response(404, 'Not Found')
class PaymentsApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'
                                          })
    @token_required
    @api.expect(a_create_stripe_charges)
    def post(self):
        error.clear()
        data = api.payload
        booking = data['referenceNumber']
        email = data['email']
        token = data['token']
        amount = data['amount']
        description = data['description']
        paymentFor = data['paymentFor']
        try:
            customer = (StripeCustomer.query
                    .filter(StripeCustomer.email == email).first())
            if customer is None:
                customer_stripe = (stripe.Customer.create(email=email,
                                                        source=token))
                new_customer = StripeCustomer(email=email,
                                            stripeCustomerId=customer_stripe.id)
                db.session.add(new_customer)
                db.session.flush()
                db.session.commit()
                customer = (StripeCustomer.query
                            .filter(StripeCustomer.email == email).first())
            charge = stripe.Charge.create(customer=customer.stripeCustomerId,
                                        amount=price * 100,
                                        currency='php',
                                        description=description)
            new_payment = Payments(paymentReference='PC' + referenceNumber,
                                bookingReference=booking,
                                paymentFor=paymentFor,
                                StripeCustomer=customer.id,
                                stripeChargeId=charge.id)
            db.session.add(new_payment)
            db.session.commit()
            if paymentFor == 'Packages':
                package = PackageBooking.query.filter(PackageBooking.referenceNumber == booking)
                package.update({PackageBooking.isPaid: True})
                db.session.commit()
                return {'message': 'Booking has been successfully charged'}, 200
            elif paymentFor == 'Hotels':
                hotel = HotelBooking.query.filter(HotelBooking.referenceNumber == booking)
                hotel.update({HotelBooking.isPaid: True})
                db.session.commit()
                return {'message': 'Booking has been successfully charged'}, 200
            elif paymentFor == 'Tickets':
                ticket = FlightBooking.query.filter(FlightBooking.referenceNumber == booking)
                ticket.update({FlightBooking.isPaid: True})
                db.session.commit()
                return {'message': 'Booking has been successfully charged'}, 200
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400