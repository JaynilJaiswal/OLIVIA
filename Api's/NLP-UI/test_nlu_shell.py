import requests

BASE = "http://127.0.0.1:5000/"

response = requests.get(BASE, json = {"sentence":"call mom at 10pm and tell her to sleep"})
print(response.json())
