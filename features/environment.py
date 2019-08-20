from behave import fixture, use_fixture
from friendbot import app

@fixture
def flaskr_client(context, *args, **kwargs):
    app.testing = True
    context.client = app.test_client()
    yield context.client

def before_feature(context, feature):
    use_fixture(flaskr_client, context)
