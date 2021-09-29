import os
from werkzeug.utils import redirect
import yaml
import paypalrestsdk
import logging
from datetime import datetime, timedelta
from server.app import app
from server.model import db, User


logger = logging.getLogger(__name__)

BASE_DIR = os.path.join(
    "..",  # paypal
    "..",  # lib
    os.path.dirname(__file__)  # commands
)

PRODUCT_CONF_PATH = os.path.join(BASE_DIR, "product.yml")
PLAN_CONF_PATH = os.path.join(BASE_DIR, "plan.yml")
ORDER_CONF_PATH = os.path.join(BASE_DIR, "order.yml")

app.logger.info("PRODUCT_CONF_PATH %s", PRODUCT_CONF_PATH)

PRODUCT = "product"
PLAN = "plan"

SUBSCRIPTION = 'subscription'
ORDER = 'order'


def plus_days(count):
    _date = datetime.now()
    return _date + timedelta(days=count)


def mode():
    if app.config["ENV"] == "development":
        return "sandbox"

    return "live"


myapi = paypalrestsdk.Api({
    "mode": mode(),  # noqa
    "client_id": app.config["PAYPAL_CLIENT_ID"],
    "client_secret": app.config["PAYPAL_CLIENT_SECRET"],
})


def get_plan():
    data = None

    with open(PLAN_CONF_PATH, "r") as f:
        data = yaml.safe_load(f)
        app.logger.debug(data)

    return data


def get_product():
    data = None

    with open(PRODUCT_CONF_PATH, "r") as f:
        data = yaml.safe_load(f)
        app.logger.debug(data)

    return data


def get_order():
    data = None

    with open(ORDER_CONF_PATH, "r") as f:
        data = yaml.safe_load(f)
        app.logger.debug(data)

    return data


def create_order():
    order = get_order()
    return myapi.post("v2/checkout/orders", order)


def create_subscription():
    data = {
        'plan_id': app.config["PAYPAL_PLAN_MONTHLY_ID"],
    }
    resp = myapi.post("v1/billing/subscriptions", data)
    app.logger.info(resp)
    return resp

def create_subscription_approve_url(user: User):
    resp = create_subscription()
    if resp["status"] == "APPROVAL_PENDING":
      user.paypal_subscription_id = resp['id']
      # return approve url from resp
      return get_url_from(resp['links'], 'approve')
    else:
      return None



def list_subscription():
    resp = myapi.post("v1/billing/subscriptions")
    app.logger.info(resp)
    return resp


def get_url_from(iterator, what):
    for link in iterator:
        if link['rel'] == what:
            return link['href']


def set_paid_until(obj, from_what):

    if from_what == SUBSCRIPTION:
        billing_agreement_id = obj['billing_agreement_id']
        ret = myapi.get(f"v1/billing/subscriptions/{billing_agreement_id}")

        user = User.by_paypal_subscription_id(ret['id'])
        if not user:
            app.logger.error(f"User with order id={ret['id']} not found.")
            return False

        app.logger.debug(f"SUBSCRIPTION {obj} for user {user.email}")
        if obj['amount']['total'] == '19.99':
            user.set_paid_until(plus_days(count=31))
            db.session.commit()

    if from_what == ORDER:
        url = get_url_from(obj['links'], 'self')
        ret = myapi.get(url)

        user = User.by_paypal_subscription_id(ret['id'])
        if not user:
            app.logger.error(f"User with order id={ret['id']} not found.")
            return False

        app.logger.debug(f"ORDER {obj} for user {user.email}")

    return True
