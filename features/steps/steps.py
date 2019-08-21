from behave import *

@given('friendbot is running')
def flask_setup(context):
    assert context.client

@when('we make a GET request at the {endpoint} endpoint')
def step_impl(context, endpoint):
    context.res = context.client.get(endpoint)
    assert context.res

@when('we make a POST request for channel {channel} user {user} at the {endpoint} endpoint')
def step_impl(context, channel, user, endpoint):
    data = "{} {}".format(channel, user)
    context.res = context.client.post(endpoint, data=dict(text=data))
    assert context.res

@then('we will get a {status} status code')
def step_impl(context, status):
    status = int(status)
    print("Expected: {}".format(status))
    print("Actual: {}".format(context.res.status_code))
    assert context.res.status_code == status