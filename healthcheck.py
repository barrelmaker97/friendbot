import requests

requests.get("http://localhost:6000/health").raise_for_status()
