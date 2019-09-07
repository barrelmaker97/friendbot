from behave import when, then


@when("we make a POST request for {arg0} and {arg1} at {endpoint}")
def post_two_args(context, arg0, arg1, endpoint):
    data = "{} {}".format(arg0, arg1)
    context.res = context.client.post(endpoint, data=dict(text=data))
    assert context.res


@when("we make a POST request for {arg0} at {endpoint}")
def post_one_arg(context, arg0, endpoint):
    data = arg0
    context.res = context.client.post(endpoint, data=dict(text=data))
    assert context.res


@when("we make a blank POST request at {endpoint}")
def post_endpoint_blank(context, endpoint):
    context.res = context.client.post(endpoint, data=dict(text=""))
    assert context.res


@then("we will get a {key}: {value} header")
def read_header(context, key, value):
    headers = context.res.headers
    print("\nReceived headers: \n{}".format(headers))
    data = headers[key]
    assert value in data
