import requests as r
import time
import hmac
import hashlib
import ujson
import os

payload = {"text": "", "user_id": "healthcheck"}
signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
if signing_secret is not None:
    request_body = "text=&user_id=healthcheck"
    timestamp = str(int(time.time()))
    slack_basestring = f"v0:{timestamp}:{request_body}".encode("utf-8")
    slack_signing_secret = bytes(signing_secret, "utf-8")
    signature = (
        "v0="
        + hmac.new(slack_signing_secret, slack_basestring, hashlib.sha256).hexdigest()
    )
    headers = {"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": signature}
else:
    headers = {"X-Friendbot-Healthcheck": "true"}
endpoint = "http://localhost:6000/sentence"
resp = r.post(endpoint, payload, headers=headers)
resp.raise_for_status()
assert resp.headers["Friendbot-Error"] == "False"
