from behave import given, when, then
import json


@when('we make a POST request at {endpoint} using data from {path}')
def post_two_args(context, endpoint, path):
    with open(path) as f:
        data = json.load(f)
    context.res = context.client.post(endpoint, data=json.dumps(data))
    assert context.res
