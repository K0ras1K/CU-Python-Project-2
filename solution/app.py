from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("ACCUWEATHER_TOKEN") 

def get_weather(city):
    try:
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}&language=ru-ru"
        location_data = requests.get(location_url).json()

        if location_data:
            location_key = location_data[0]['Key']
            weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_KEY}&language=ru-ru&details=true"
            weather_data = requests.get(weather_url).json()

            if weather_data:
                return {
                    "city": city,
                    "temperature": weather_data[0]['Temperature']['Metric']['Value'],
                    "humidity": weather_data[0]['RelativeHumidity'],
                    "wind_speed": weather_data[0]['Wind']['Speed']['Metric']['Value'],
                    "precipitation": weather_data[0]['HasPrecipitation'],
                    "weather_text": weather_data[0]['WeatherText']
                }
    except:
        return render_template('error.html')
    return None

def check_bad_weather(weather, preference):
    conditions = []
    if preference == 'southern':
        if weather['temperature'] < 15 or weather['temperature'] > 30:
            conditions.append('температура')
        if weather['humidity'] > 80:
            conditions.append('влажность')
    elif preference == 'northern':
        if weather['temperature'] < -10 or weather['temperature'] > 20:
            conditions.append('температура')
        if weather['humidity'] > 60:
            conditions.append('влажность')

    return conditions if conditions else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_weather', methods=['POST'])
def check_weather():
    start_city = request.form['start_city']
    end_city = request.form['end_city']
    preference = request.form['preference']

    start_weather = get_weather(start_city)
    end_weather = get_weather(end_city)

    if not start_weather or not end_weather:
        return redirect(url_for('index'))

    start_conditions = check_bad_weather(start_weather, preference)
    end_conditions = check_bad_weather(end_weather, preference)

    return render_template('result.html', start_weather=start_weather, end_weather=end_weather,
                           start_conditions=start_conditions, end_conditions=end_conditions)

if __name__ == '__main__':
    app.run(debug=True)
