import json
import requests
from .models import Location

from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY


def get_photo(city, state):
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search?query="
    params = {
        "per_page": 1,
        "query": str(city) + "," + str(state),
    }

    r = requests.get(url=url, headers=headers, params=params)
    content = json.loads(r.content)
    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except (KeyError, IndexError):
        return {"picture_url": None}


def get_weather(city, state):
    params = {
        "q": f"{city}, {state}, US",
        "limit": 1,
        "appid": OPEN_WEATHER_API_KEY,
    }
    url = "http://api.openweathermap.org/geo/1.0/direct"
    r = requests.get(url=url, params=params)
    content = json.loads(r.content)
    try:
        latitude = content[0]["lat"]
        longitude = content[0]["lon"]

    except (KeyError, IndexError):
        return {"coordinates": None}

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "imperial",
    }
    url = "https://api.openweathermap.org/data/2.5/weather"

    r = requests.get(url, params=params)
    content = json.loads(r.content)

    try:
        return {
            "description": content["weather"][0]["description"],
            "temperature": content["main"]["temp"],
            # "wind_speed": content["main"]["temp"],
        }
    except (KeyError, IndexError):
        return {"Weather data": None}


# def get_weather_data(city, state):
# # Create the URL for the geocoding API with the city and state
# url = "http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}"
# # Make the request
# r = requests.get(url)
# # Parse the JSON response
# local = json.loads(r.content)
# # Get the latitude and longitude from the response
# location = {"lat": local["lat"],"lon": local["lon"]}
# # Create the URL for the current weather API with the latitude
# url = https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}
# #   and longitude
# # Make the request
# r = request.get(url)
# # Parse the JSON response
# weather = json.loads(r.content)
# # Get the main temperature and the weather's description and put
# #   them in a dictionary
# weather_data = {}
# # Return the dictionary
