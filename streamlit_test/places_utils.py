import requests
from math import sqrt, pow



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

def get_walking_times(place1, place2, dest, api_key):
    total = 0
    for place in [place1, place2]:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:{place}&destinations=place_id:{dest}&mode=walking&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                times = [element['duration']['value'] / 60 for element in data['rows'][0]['elements']]
                total += sum(times)
    return total if total > 0 else float('inf')

def get_walking_time(place, dest, api_key):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:{place}&destinations=place_id:{dest}&mode=walking&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            times = [element['duration']['value'] / 60 for element in data['rows'][0]['elements']]
            return sum(times)
    return float('inf')

def calculate_total_distance(place1, place2, dest, api_key):
    return get_walking_times(place1, place2, dest, api_key) 

def sort_places(location1, location2, places, api_key):
    # Sort places by total distance and calculate distances
    places_with_distance = [(
        place,
        calculate_total_distance(
        location1, location2,
        place['place_id'], api_key)
    ) for place in places]
    sorted_places_with_distance = sorted(places_with_distance, key=lambda x: x[1])[:10]
    return sorted_places_with_distance