from behave import given, when, then


@given('friendbot is running')
def flask_setup(context):
    assert context.client


@then('we will get a {status} status code')
def get_code(context, status):
    status = int(status)
    print("Expected Status Code: {}".format(status))
    print("Received Status Code: {}".format(context.res.status_code))
    assert context.res.status_code == status
