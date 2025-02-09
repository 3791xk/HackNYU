import streamlit as st
import requests
from config import GOOGLE_MAPS_API_KEY
import json
import urllib.parse

from streamlit_searchbox import st_searchbox



# Initialize session state for locations
if 'location1' not in st.session_state:
    st.session_state.location1 = {'input': '', 'place_id': None, 'description': ''}
if 'location2' not in st.session_state:
    st.session_state.location2 = {'input': '', 'place_id': None, 'description': ''}

def update_location(number, value):
    suggestions = get_place_suggestions(value)
    if suggestions:
        description, place_id = suggestions[0]  # Auto-select first suggestion
        st.session_state[f'location{number}'] = {
            'input': value,
            'place_id': place_id,
            'description': description
        }

# Set page config
st.set_page_config(
    page_title="MeetTogether",
    layout="wide"
)

# Add logo and title in a horizontal layout
col1, col2 = st.columns([1, 4])
with col1:
    st.image("assets/MapTogetherLogoDesign.svg", width=100)
with col2:
    st.title("Find Places Between Locations")
    st.markdown("Explore places and get directions from both starting points")

def get_place_suggestions(query):
    if len(query.strip()) < 3:
        return []
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={urllib.parse.quote(query)}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK' and data['predictions']:
            # Return first suggestion only
            return [(data['predictions'][0]['description'], data['predictions'][0]['place_id'])]
    return []

def get_location_coordinates(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=geometry&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['result']['geometry']['location']
            return location['lat'], location['lng']
    return None

def find_midpoint(lat1, lng1, lat2, lng2):
    return (lat1 + lat2) / 2, (lng1 + lng2) / 2

def search_places(lat, lng, query):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=2000&keyword={urllib.parse.quote(query)}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_gmaps_url(origin_lat, origin_lng, dest_lat, dest_lng):
    return f"https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lng}&destination={dest_lat},{dest_lng}"

# pass search function and other options as needed

#st.write(f"Selected value: {selected_value}")


# Input for locations and search type
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    selected_value = st_searchbox(
    get_place_suggestions,
    placeholder="Enter first location:",
    key="loc1_input")
    location1 = selected_value

with col2:
    selected_value = st_searchbox(
    get_place_suggestions,
    placeholder="Enter second location:",
    key="loc2_input")
    location2 = selected_value

with col3:
    search_type = st.text_input(
        label='doom',
        placeholder="What are you looking for?",
        label_visibility="hidden",
        key='search_type'
    )

# Check for Enter press or button click and valid inputs
if (st.button("Search Places") or search_type) and location1 and location2 and len(search_type) >= 3:
    coords1 = get_location_coordinates(location1)
    coords2 = get_location_coordinates(location2)
    
    if coords1 and coords2:
        lat1, lng1 = coords1
        lat2, lng2 = coords2
        mid_lat, mid_lng = find_midpoint(lat1, lng1, lat2, lng2)
        places = search_places(mid_lat, mid_lng, search_type)
        
        st.subheader(f"Nearby {search_type.title()} Places")
        for place in places[:10]:
            name = place.get('name', 'Unknown')
            rating = place.get('rating', 'No rating')
            address = place.get('vicinity', 'No address')
            place_lat = place['geometry']['location']['lat']
            place_lng = place['geometry']['location']['lng']
            
            # Create Google Maps links
            route1_url = get_gmaps_url(lat1, lng1, place_lat, place_lng)
            route2_url = get_gmaps_url(lat2, lng2, place_lat, place_lng)
            
            st.markdown(f"**{name}** (Rating: {rating}/5)")
            
            # Display map with routes
            map_html = f"""
            <iframe width="100%" height="400" frameborder="0" style="border:0"
            src="https://www.google.com/maps/embed/v1/directions?key={GOOGLE_MAPS_API_KEY}
            &origin={lat1},{lng1}
            &destination={place_lat},{place_lng}
            &waypoints={lat2},{lng2}
            &mode=walking">
            </iframe>
            """
            st.components.v1.html(map_html, height=400)
            
            # Display travel info with direct links
            st.markdown(f"""
            **Address:** {address}  
            **Routes:**
            * [Directions from Location 1]({route1_url})
            * [Directions from Location 2]({route2_url})
            """)
            st.divider()
    else:
        st.error("Couldn't find one or both locations")
