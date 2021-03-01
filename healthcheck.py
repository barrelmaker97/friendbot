import requests

requests.get("http://localhost:8000/health").raise_for_status()
