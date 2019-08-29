from behave import given, when, then


@given('friendbot is running')
def flask_setup(context):
    assert context.client


@when('we make a GET request at {endpoint}')
def get_endpoint(context, endpoint):
    context.res = context.client.get(endpoint)
    assert context.res


@when('we make a POST request for channel {channel} user {user} at {endpoint}')
def post_endpoint(context, channel, user, endpoint):
    data = "{} {}".format(channel, user)
    context.res = context.client.post(endpoint, data=dict(text=data))
    assert context.res


@when('we make a blank POST request at {endpoint}')
def post_endpoint_blank(context, endpoint):
    context.res = context.client.post(endpoint, data=dict(text=""))
    assert context.res


@then('we will get a {status} status code')
def get_code(context, status):
    status = int(status)
    print("Expected Status Code: {}".format(status))
    print("Received Status Code: {}".format(context.res.status_code))
    assert context.res.status_code == status


@then('we will get a {key}: {value} header')
def read_header(context, key, value):
    headers = context.res.headers
    print("\nReceived headers: \n{}".format(headers))
    data = headers[key]
    assert value in data
