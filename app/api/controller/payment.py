import stripe
import os
from flask import request, Flask
from flask_restplus import Resource, reqparse
from flask_mail import Message
import app
from app.src.models import db, Payments, Hotel, Ticket, Package, User, Itinerary
from app.src.models import FlightBooking, HotelBooking, PackageBooking
from app.src.models import StripeCustomer
from app.api.models.payment import api, a_create_stripe_charges, a_stripe_details
from app.api.models.payment import a_pay_via_bank, a_payment_confirmation
from app.src.helpers.decorators import referenceNumber, token_required, token_details
from app.api.controller.user import mail
from xhtml2pdf import pisa

app = Flask( __name__ )
errors = []

pubkey = 'pk_test_GjK3GmJJ1exs60wIcgTpfggq'
secretkey = 'sk_test_RXyvP1FBgkRyCwyEBGyZeymo'

stripe.api_key = secretkey
@api.route('')
@api.response(404, 'Not Found')
class PaymentApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'
                                          })
    @token_required
    @api.expect(a_create_stripe_charges)
    def post(self):
        errors.clear()
        data = api.payload
        try:
            booking = data['referenceNumber']
            email = data['email']
            token = data['token']
            amount = data['amount']
            description = data['description']
            payment_for = data['paymentFor']
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
                                          amount=int(amount/100),
                                          currency='php',
                                          description=description)
            payment_reference = 'PC' + referenceNumber
            new_payment = Payments(paymentReference=payment_reference,
                                   bookingReference=booking,
                                   paymentFor=payment_for,
                                   stripeCustomer=customer.id,
                                   stripeChargeId=charge.id,
                                   paymentMethod="CARD")
            db.session.add(new_payment)
            db.session.commit()
            if payment_for == 'Packages':
                package = PackageBooking.query.filter(PackageBooking.referenceNumber == booking)
                package.update({PackageBooking.isPaid: True})
                package.update({PackageBooking.paymentMethod: "CARD"})
                db.session.commit()
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment_for, payment_reference, int(amount/100), description))
                mail.send(msg)
                return {'message': 'Booking has been successfully charged'}, 200
            if payment_for == 'Hotels':
                hotel = HotelBooking.query.filter(HotelBooking.referenceNumber == booking)
                hotel.update({HotelBooking.isPaid: True})
                hotel.update({HotelBooking.paymentMethod: "CARD"})
                db.session.commit()
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment_for, payment_reference, int(amount/100), description))
                mail.send(msg)
                return {'message': 'Booking has been successfully charged'}, 200
            if payment_for == 'Tickets':
                ticket = FlightBooking.query.filter(FlightBooking.referenceNumber == booking)
                ticket.update({FlightBooking.isPaid: True})
                ticket.update({FlightBooking.paymentMethod: "CARD"})
                db.session.commit()
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment_for, payment_reference, int(amount/100), description))
                mail.send(msg)
                return {'message': 'Booking has been successfully charged'}, 200
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

@api.route('/bank')
@api.response(404, 'Not Found')
class PaymentViaBankApi(Resource):
    @api.doc(security='apiKey', responses={200: 'Success',
                                           400: 'Bad Request'
                                          })
    @token_required
    @api.expect(a_pay_via_bank)
    def post(self):
        errors.clear()
        data = api.payload
        token = token_details(request.headers['x-client-token'])
        user = User.query.filter(User.publicId==token['sub']).first()
        try:
            id = data[ 'id' ]
            print( "ID SUBMITTED:", id )
            pkg = (
                PackageBooking.query.filter( PackageBooking.id == id )
                    .join( Package, PackageBooking.package == Package.id )
                    .join( Ticket, Package.flight == Ticket.id )
                    .join( Hotel, Package.hotel == Hotel.id )
            ).first()

            print( "DIR:", dir( pkg.Package ) )
            ticket_price = float( pkg.Package.Tickets.price )
            hotel_price = float( pkg.Package.Hotel.price )
            service_charge = ( ticket_price + ticket_price )*.02
            vat = float(service_charge) * .12
            total = ticket_price + hotel_price + service_charge + vat

            booking = pkg.referenceNumber
            email = user.email
            payment_for = data['paymentFor']
            amount = total
            payment_reference = 'PB' + referenceNumber
            print( "No ERROR" )
            new_payment = Payments(paymentReference=payment_reference,
                                   bookingsReference=booking,
                                   paymentFor=payment_for,
                                   stripeCustomer=None,
                                   stripeChargeId=None,
                                   paymentMethod="Bank")
            db.session.add(new_payment)
            db.session.commit()
            if payment_for == 'Packages':
                package = PackageBooking.query.filter(PackageBooking.referenceNumber == booking)
                package.update({PackageBooking.paymentMethod: "BANK"})
                db.session.commit()
                msg = Message(subject='Pay Via Bank Details', recipients=[email])
                template = (
                    "<br><br>PAYMENT REFERENCE NUMBER: " + payment_reference + "<br>AMOUNT: " + str( int( amount ) ) +
                    "<br><br>Deposit in Saving Account (BDO)" +
                    "<br>Account Number: 123-123123-123" +
                    "<br>Account Name: First Choice Travel Hub" +
                    "<br>Email: renzo.beltran@via-appia.ph"
                )
                filedest = "app/api/controller/pdfs/invoice.pdf"
                resultFile = open( filedest, "w+b" )
                status = pisa.CreatePDF( template, dest=resultFile )
                resultFile.close()
                fp = app.open_resource( "pdfs/invoice.pdf" )
                msg.attach( "invoice.pdf", "application/pdf", fp.read() )
                msg.html = ("Good Day, attached file will serve as your Payment Via Bank Invoice."
                            )
                mail.send(msg)
                return {'message': 'Booking has been set to pending'}, 200
            if payment_for == 'Hotels':
                hotel = HotelBooking.query.filter(HotelBooking.referenceNumber == booking)
                hotel.update({HotelBooking.paymentMethod: "BANK"})
                db.session.commit()
                msg = Message(subject='Pay Via Bank Details', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your Payment Via Bank Details."
                            "<br><br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}"
                            "<br><br>Deposit in Saving Account (BDO)"
                            "<br>Account Number: 123-123123-123"
                            "<br>Account Name: First Choice Travel Hub"
                            .format(payment_reference, int(amount/100)))
                mail.send(msg)
                return {'message': 'Booking has been set to pending'}, 200
            if payment_for == 'Tickets':
                ticket = FlightBooking.query.filter(FlightBooking.referenceNumber == booking)
                ticket.update({FlightBooking.paymentMethod: "BANK"})
                db.session.commit()
                msg = Message(subject='Pay Via Bank Details', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your Payment Via Bank Details."
                            "<br><br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}"
                            "<br><br>Deposit in Saving Account (BDO)"
                            "<br>Account Number: 123-123123-123"
                            "<br>Account Name: First Choice Travel Hub"
                            .format(payment_reference, int(amount/100)))
                mail.send(msg)
                return {'message': 'Booking has been set to pending'}, 200
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400

    @api.doc(security='apiKey', response={200: 'Success', 400: 'Bad Request'})
    @token_required
    @api.param('referenceNumber', 'Reference Number', 'query')
    @api.expect(a_payment_confirmation)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('referenceNumber', location='args')
        args = parser.parse_args()
        errors.clear()
        data = api.payload
        try:
            reference_number = args['referenceNumber']
            is_paid = data['isPaid']
            payment = Payments.query.filter(Payments.paymentReference == reference_number)
            if payment.paymentFor == "Packages":
                package = PackageBooking.query.filter(PackageBooking.referenceNumber == payment.bookingReference)
                package.update({PackageBooking.isPaid: True})
                db.session.commit()
                package_details = Package.query.filter(Package.id == package.package)
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment.payment_for, reference_number, int(package_details.price), package_details.destination))
                mail.send(msg)
                return {'message': 'Booking has been successfully updated'}, 200
            if payment.paymentFor == "Hotels":
                hotel = HotelBooking.query.filter(HotelBooking.referenceNumber == payment.bookingReference)
                hotel.update({HotelBooking.isPaid: True})
                db.session.commit()
                hotel_details = Hotel.query.filter(Hotel.id == hotel.hotel)
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment.payment_for, reference_number, int(hotel_details.price/100), hotel_details.name))
                mail.send(msg)
                return {'message': 'Booking has been successfully updated'}, 200
            if payment.paymentFor == "Tickets":
                ticket = FlightBooking.query.filter(FlightBooking.referenceNumber == payment.bookingReference)
                ticket.update({FlightBooking.isPaid: True})
                db.session.commit()
                ticket_details = Ticket.query.filter(Ticket.id == ticket.ticket)
                msg = Message(subject='Invoice', recipients=[email])
                msg.html = ("Good Day, the message below will serve as your invoice."
                            "<br><br>PAYMENT: {} "
                            "<br>PAYMENT REFERENCE NUMBER: {}<br>AMOUNT: {}<br>DESCRIPTION: {}"
                            .format(payment_for, payment_reference, int(ticket_details.price/100), ticket_details.flightNo))
                mail.send(msg)
                return {'message': 'Booking has been successfully updated'}, 200
        except KeyError:
            errors.append('Incomplete JSON nodes')
            return {'errors': {'status': 400,
                               'errorCode': 'E0001',
                               'message': errors}}, 400