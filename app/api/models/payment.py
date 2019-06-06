from flask_restplus import Namespace, fields

api = Namespace('Payments', 'Payments related APIs', path='/payments')

a_stripe_details = api.model('Charge Details',
                             {'id': fields.Integer(),
                              'paymentReference': fields.String(),
                              'bookingReference': fields.String(),
                              'paymentFor': fields.String()
                             })

a_create_stripe_charges = api.model('Create Charges',
                                    {
                                     'referenceNumber': fields.String(),
                                     'token': fields.String(),
                                     'email': fields.String(),
                                     'amount': fields.Float(),
                                     'description': fields.String(),
                                     'paymentFor': fields.String()
                                     })

a_pay_via_bank = api.model('Pay Via Bank',
                           {
                            'referenceNumber': fields.String(),
                            'email': fields.String(),
                            'paymentFor': fields.String(),
                            'amount': fields.String()
                            })

a_payment_confirmation = api.model('Confirm Pay Via Bank',
                                   {
                                    'isPaid': fields.Boolean()
                                   })