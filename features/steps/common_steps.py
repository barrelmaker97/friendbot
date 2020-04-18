from behave import given, when, then


@given("friendbot is running")
def flask_setup(context):
    assert context.client


@when("we make a GET request at {endpoint}")
def get_endpoint(context, endpoint):
    context.res = context.client.get(endpoint)
    assert context.res


@then("we will get a {status} status code")
def get_code(context, status):
    status = int(status)
    print(f"Expected Status Code: {status}")
    print(f"Received Status Code: {context.res.status_code}")
    assert context.res.status_code == status
