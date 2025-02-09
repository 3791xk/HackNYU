import math
import requests

def get_location_coordinates(place_id, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=geometry&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['result']['geometry']['location']
            return location['lat'], location['lng']
    return None

def find_midpoint(lat1, lng1, lat2, lng2):
    return (lat1 + lat2) / 2, (lng1 + lng2) / 2

def search_places(lat, lng, query, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=2000&keyword={query}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_gmaps_url(place, dest):
    return f"https://www.google.com/maps/dir/?api=1&origin=place_id:{place}&destination=place_id{dest}"

def get_walking_time(place, dest, api_key, mode="walking"):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:{place}&destinations=place_id:{dest}&mode={mode}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            times = [element['duration']['value'] / 60 for element in data['rows'][0]['elements']]
            return sum(times)
    return float('inf')

def get_walking_times(place1, place2, dest, api_key, mode="walking"):
    walking_times = []
    for place in [place1, place2]:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:{place}&destinations=place_id:{dest}&mode={mode}&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                times = [element['duration']['value'] / 60 for element in data['rows'][0]['elements']]
                walking_times.append(sum(times))
    return walking_times if len(walking_times) == 2 else [float('inf'), float('inf')]

def calculate_total_distance(place1, place2, dest, api_key, mode="walking"):
    times = get_walking_times(place1, place2, dest, api_key, mode=mode)
    return sum(times)

def sort_places(location1, location2, places, api_key, mode="walking"):
    # Sort places by total distance and calculate distances
    places_with_distance = [(
        place,
        calculate_total_distance(
            location1, location2,
            place['place_id'], 
            api_key,
            mode=mode
        ),
        get_walking_times(location1, location2, 
            place['place_id'], 
            api_key, 
            mode=mode)
    ) for place in places]
    places_with_distance = filter_places(places_with_distance)
    sorted_places_with_distance = sorted(places_with_distance, key=lambda x: x[1])[:10]
    return sorted_places_with_distance

def filter_places(places_with_distance):
    disparity = lambda x: abs(x[2][0] - x[2][1])
    percent_of_total = lambda x: x[2][0] / sum(x[2])
    return [place for place in places_with_distance if disparity(place) > 20 and percent_of_total(place) > 0.3 and percent_of_total(place) < 0.7]
