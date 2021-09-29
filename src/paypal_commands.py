import yaml
import paypalrestsdk
import os
import click

from server.app import app
from .paypal_payments import mode, PRODUCT_CONF_PATH, PLAN_CONF_PATH, PRODUCT, PLAN


myapi = paypalrestsdk.Api({
    "mode": mode(),  # noqa
    "client_id": app.config["PAYPAL_CLIENT_ID"],
    "client_secret": app.config["PAYPAL_CLIENT_SECRET"],
})


def test(app):
  print(f'"client_id": {app.config["PAYPAL_CLIENT_ID"]}')
  print(f'DEBUG: {app.config["DEBUG"]}')
  print(f'ENV: {app.config["ENV"]}')
  print(f'SECRET_KEY: {app.config["SECRET_KEY"]}')
  print(f'PAYPAL_PLAN_MONTHLY_ID: {app.config["PAYPAL_PLAN_MONTHLY_ID"]}')
  print(f'debug: {app.debug}')
  print(f"mode: {mode()}")
  app.logger.info(f'"client_secret": {app.config["PAYPAL_CLIENT_SECRET"]}')


def add_arguments(parser):
    parser.add_argument(
        "--create",
        "-c",
        choices=[PRODUCT, PLAN],
        help="Creates Paypal product or plan"
    )
    parser.add_argument(
        "--list",
        "-l",
        choices=[PRODUCT, PLAN],
        help="List Paypal products or plans"
    )


def create_product():
    with open(PRODUCT_CONF_PATH, "r") as f:
        data = yaml.safe_load(f)
        app.logger.info(data)
        ret = myapi.post("v1/catalogs/products", data)
        app.logger.info(ret)


def create_plan():
    with open(PLAN_CONF_PATH, "r") as f:
        data = yaml.safe_load(f)
        app.logger.info(data)
        ret = myapi.post("v1/billing/plans", data)
        app.logger.info(ret)


def list_product():
    ret = myapi.get("v1/catalogs/products")
    app.logger.info(ret)


def list_plan():
    ret = myapi.get("v1/billing/plans")
    app.logger.info(ret)


def create(what):
    if what == PRODUCT:
        create_product()
    else:
        create_plan()


def list(self, what):
    if what == PRODUCT:
        self.list_product()
    else:
        self.list_plan()


def handle(self, *args, **options):
    create_what = options.get("create")
    list_what = options.get("list")

    if create_what:
        app.logger.info(f"Create a {create_what}")
        self.create(create_what)
    elif list_what:
        app.logger.info(f"List {list_what}")
        self.list(list_what)
