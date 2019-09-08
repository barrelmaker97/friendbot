from behave import when
import json


@when("we make a POST request at {endpoint} using {path}")
def post_two_args(context, endpoint, path):
    with open(path) as f:
        data = json.load(f)
    data_dict = dict(payload=json.dumps(data))
    context.res = context.client.post(endpoint, data=data_dict)
    assert context.res
