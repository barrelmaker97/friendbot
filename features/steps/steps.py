from behave import given, when, then
import json
import urllib
import os
import time
import hmac
import hashlib


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


@when("we make a POST request for {arg0} and {arg1} at {endpoint} as {user}")
def post_two_args(context, arg0, arg1, endpoint, user):
    text = f"{arg0} {arg1}"
    data_dict = dict(text=text, user_id=user)
    context.res = context.client.post(endpoint, data=data_dict, headers=generate_signed_headers(data_dict))
    assert context.res


@when("we make a POST request for {arg0} at {endpoint} as {user}")
def post_one_arg(context, arg0, endpoint, user):
    text = arg0
    data_dict = dict(text=text, user_id=user)
    context.res = context.client.post(endpoint, data=data_dict, headers=generate_signed_headers(data_dict))
    assert context.res


@when("we make a blank POST request at {endpoint} with no user_id")
def post_endpoint_blank_no_user(context, endpoint):
    data_dict = dict(text="")
    context.res = context.client.post(endpoint, data=data_dict, headers=generate_signed_headers(data_dict))
    assert context.res


@when("we make a blank POST request at {endpoint} as {user}")
def post_endpoint_blank_with_user(context, endpoint, user):
    data_dict = dict(text="", user_id=user)
    context.res = context.client.post(endpoint, data=data_dict, headers=generate_signed_headers(data_dict))
    assert context.res


@when("we make a blank POST request at {endpoint} that isn't signed")
def post_endpoint_blank_unsigned(context, endpoint):
    data_dict = dict(text="", user_id="")
    context.res = context.client.post(endpoint, data=data_dict)
    assert context.res


@when("we make a blank POST request at {endpoint} that is too old")
def post_endpoint_blank_too_old(context, endpoint):
    data_dict = dict(text="", user_id="")
    headers = generate_signed_headers(data_dict, timestamp=(time.time() - 600))
    context.res = context.client.post(endpoint, data=data_dict, headers=headers)
    assert context.res


@then("we will get a {key}: {value} header")
def read_header(context, key, value):
    headers = context.res.headers
    print(f"\nReceived headers: \n{headers}")
    data = headers[key]
    assert value in data


@when("we make a POST request at {endpoint} using {path}")
def post_basic(context, endpoint, path):
    with open(path) as f:
        data = json.load(f)
    data_dict = dict(payload=json.dumps(data))
    context.res = context.client.post(endpoint, data=data_dict, headers=generate_signed_headers(data_dict))
    assert context.res


def generate_signed_headers(data_dict, timestamp=time.time()):
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
    if signing_secret:
        request_body = urllib.parse.urlencode(data_dict)
        str_timestamp = str(int(timestamp))
        slack_basestring = f"v0:{str_timestamp}:{request_body}".encode("utf-8")
        slack_signing_secret = bytes(signing_secret, "utf-8")
        signature = (
            "v0="
            + hmac.new(slack_signing_secret, slack_basestring, hashlib.sha256).hexdigest()
        )
        return {"X-Slack-Request-Timestamp": str_timestamp, "X-Slack-Signature": signature}
