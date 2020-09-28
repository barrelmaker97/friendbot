from behave import fixture, use_fixture
from friendbot import app
import os


@fixture
def flaskr_client(context, *args, **kwargs):
    app.testing = True
    context.client = app.test_client()
    yield context.client


def before_tag(context, tag):
    if tag == "PostStart":
        use_fixture(flaskr_client, context)
    if tag == "PostStartNoRedis":
        os.environ["FRIENDBOT_REDIS_HOST"] = "notredis"
        use_fixture(flaskr_client, context)
