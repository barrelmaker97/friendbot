from behave import when, then


@when("we make a POST request for {arg0} and {arg1} at {endpoint} as {user}")
def post_two_args(context, arg0, arg1, endpoint, user):
    text = f"{arg0} {arg1}"
    context.res = context.client.post(
        endpoint, data=dict(text=text, user_id=user)
    )
    assert context.res


@when("we make a POST request for {arg0} at {endpoint} as {user}")
def post_one_arg(context, arg0, endpoint, user):
    text = arg0
    context.res = context.client.post(
        endpoint, data=dict(text=text, user_id=user)
    )
    assert context.res


@when("we make a blank POST request at {endpoint} with no user_id")
def post_endpoint_blank(context, endpoint):
    context.res = context.client.post(endpoint, data=dict(text=""))
    assert context.res


@when("we make a blank POST request at {endpoint} as {user}")
def post_endpoint_blank(context, endpoint, user):
    context.res = context.client.post(endpoint, data=dict(text="", user_id=user))
    assert context.res


@then("we will get a {key}: {value} header")
def read_header(context, key, value):
    headers = context.res.headers
    print(f"\nReceived headers: \n{headers}")
    data = headers[key]
    assert value in data
