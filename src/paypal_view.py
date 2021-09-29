from flask import request
from flask.helpers import make_response
from flask.json import jsonify
from flask_restful import Resource
from flask_security import current_user, auth_required

from server.model import db
from server.utils.response_format import build_data_response, build_error_response, build_message_response

from paypalrestsdk.notifications import WebhookEvent

import logging

logger = logging.getLogger(__name__)


class PaypalView(Resource):
    @auth_required()
    def get(self):
        # to avoid "cannot import name 'app' from partially initialized module 'server.app'"
        # import function from inside method
        from server.lib.paypal.paypal_payments import create_subscription_approve_url
        redirect_url = create_subscription_approve_url(current_user)
        # users paypal_subscription_id is assigned
        db.session.commit()

        if redirect_url:
            return build_data_response(redirect_url, 200)
        else:
            return build_error_response("PAYPAL ERROR", 200)


class PaypalWebhookView(Resource):
    def get(self):
        logger.info(jsonify(request.args))
        print("Webhook GET")

    def post(self):
        from server.app import app
        from server.lib.paypal import paypal_payments as paypal

        logger.info(jsonify(request.args))
        print(request.json)
        print("Webhook POST")

        transmission_id = request.headers.get('Paypal-Transmission-Id')
        timestamp = request.headers.get('Paypal-Transmission-Time')
        webhook_id = app.config["PAYPAL_WEBHOOK_ID"]
        event_body = request.data.decode('utf-8')
        cert_url = request.headers.get('Paypal-Cert-Url')
        auth_algo = request.headers.get('Paypal-Auth-Algo')
        actual_signature = request.headers.get('Paypal-Transmission-Sig')

        response = WebhookEvent.verify(
            transmission_id,
            timestamp,
            webhook_id,
            event_body,
            cert_url,
            actual_signature,
            auth_algo
        )
        if response:
            obj = request.json

            event_type = obj.get('event_type')
            resource = obj.get('resource')

            if event_type == 'PAYMENT.SALE.COMPLETED':
                paypal.set_paid_until(resource, paypal.SUBSCRIPTION)

            if event_type == 'CHECKOUT.ORDER.APPROVED':
                paypal.set_paid_until(resource, paypal.ORDER)

        return make_response({'success': True}, 200, {'ContentType': 'application/json'})
