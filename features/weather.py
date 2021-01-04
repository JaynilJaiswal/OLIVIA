import requests
import json
def getWeather(city):
    base = "http://api.openweathermap.org/data/2.5/weather"
    r= requests.get(base,params={'q':city, 'appid':'9bddc47d0c9f0c233a0e912fb471fa97'})
    data = json.loads(r.text)
    weather  = data['weather'][0]['main']
    temp = (data['main']['temp'])-273.15
    wind_speed  = data['wind']['speed']
    humi = data['main']['humidity']
    return "Sir, it's "+str(round(temp,2))+" degree celsius and "+weather+" in "+city+". The forecast wind speed today in "+city+" is "+str(wind_speed)+" kilometer per hour. The forecast humidity in "+city+" today is "+str(humi)+" %."