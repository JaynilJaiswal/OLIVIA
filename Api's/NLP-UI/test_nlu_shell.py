import requests

BASE = "http://b04a71104cfb.ngrok.io/"

response = requests.get(BASE, json = {"sentence":"call mom at 10pm and tell her to sleep"}).json()
print("Most related feature : "+response['Most related feature'][0][0])
