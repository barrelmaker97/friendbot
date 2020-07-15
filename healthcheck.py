import requests as r

payload = {"text": "", "user_id": "healthcheck"}
endpoint = "http://localhost:6000/sentence"
resp = r.post(endpoint, payload)
resp.raise_for_status()
assert resp.headers["Friendbot-Error"] == "False"
