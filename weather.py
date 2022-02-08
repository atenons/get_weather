import httpx
import click
import sys

from configparser import ConfigParser


BASE_URL = f"http://api.openweathermap.org/data/2.5/weather?"
GEO_URL = f"http://api.openweathermap.org/geo/1.0/direct?"


def _get_api_key():
    """Fetch api-key from api.ini file"""
    config = ConfigParser()
    config.read("api.ini")
    return config["openweather"]["api_key"]


API_KEY = _get_api_key()


def get_json(url, params):
    try:
        resp = httpx.get(url, params=params)
    except httpx.HTTPError as exc:
        sys.exit(f"Error while requesting {exc.request.url!r}")
    return resp.json()


def get_weather(location, limit, lang, api_key=API_KEY, units="metric"):
    params = {"q": location, "limit": limit, "appid": api_key}
    cities = get_json(GEO_URL, params=params)
    weather_in_cities = []
    for city in cities:
        params = {
            "lat": city["lat"],
            "lon": city["lon"],
            "units": units,
            "lang": lang,
            "appid": API_KEY,
        }
        weather_in_cities.append(get_json(BASE_URL, params=params))
    return weather_in_cities


@click.command()
@click.argument("location")
@click.option(
    "--amount-of-locations",
    "-n",
    help="max number of locations of the same name",
)
@click.option("--lang", "-l", default="RU", help="use your preffered language")
def main(location, amount_of_locations, lang):
    """Weather tool that shows you the current weather in locations of your choice.
    API-key for connect to OpenWeatherAPI required"""
    weather = get_weather(location, amount_of_locations, lang)
    for loc in weather:
        print(
            f'{loc["name"]},{loc["sys"]["country"]}: {loc["weather"][0]["description"]}, t {loc["main"]["temp"]}°C'
        )


if __name__ == "__main__":
    main()
