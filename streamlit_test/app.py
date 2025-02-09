import streamlit as st
import requests
from config import GOOGLE_MAPS_API_KEY
from streamlit_searchbox import st_searchbox
from places_utils import (
    get_location_coordinates, find_midpoint,
    search_places, get_gmaps_url, get_walking_time, sort_places
)

def get_place_suggestions(query):
    if len(query.strip()) < 3:
        return []
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={query}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK' and data['predictions']:
            return [(data['predictions'][0]['description'], data['predictions'][0]['place_id'])]
    return []

# Initialize session state for locations
if 'location1' not in st.session_state:
    st.session_state.location1 = {'input': '', 'place_id': None, 'description': ''}
if 'location2' not in st.session_state:
    st.session_state.location2 = {'input': '', 'place_id': None, 'description': ''}

# Add travel_mode to session state initialization
if 'travel_mode' not in st.session_state:
    st.session_state.travel_mode = "Walking"

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
    
    # Update travel_mode in session state when changed
    travel_mode = st.selectbox(
        "Travel mode:",
        options=["Walking", "Driving"],
        key="travel_mode",
        on_change=lambda: st.session_state.update({'show_results': False}),  # Reset results when mode changes
    ).lower()  # Convert to lowercase for API calls

search_clicked = st.button("Search Places")

# Only search on button click and when inputs are valid
if search_clicked and location1 and location2 and len(search_type) >= 3:
    coords1 = get_location_coordinates(location1,GOOGLE_MAPS_API_KEY)
    coords2 = get_location_coordinates(location2,GOOGLE_MAPS_API_KEY)
    
    if coords1 and coords2:
        lat1, lng1 = coords1
        lat2, lng2 = coords2
        mid_lat, mid_lng = find_midpoint(lat1, lng1, lat2, lng2)
        places = search_places(mid_lat, mid_lng, search_type,GOOGLE_MAPS_API_KEY)[:10] + search_places(lat1, lng1, search_type,GOOGLE_MAPS_API_KEY)[:10] + search_places(lat2, lng2, search_type,GOOGLE_MAPS_API_KEY)[:10]
        if places:
            places_sorted = sort_places(location1, location2, places, GOOGLE_MAPS_API_KEY, mode=travel_mode)
            st.session_state.places_data = {
                f"{p[0].get('name', 'Unknown')} - {p[0].get('rating', 'No rating')}/5 (Total {travel_mode} time: {p[1]:.0f} mins)": 
                (p[0], p[1]) for p in places_sorted
            }
            st.session_state.coordinates = (lat1, lng1, lat2, lng2)
            st.session_state.show_results = True
        else:
            st.error(f"No {search_type} places found in this area")
    else:
        st.error("Couldn't find one or both locations")

# Show results section (outside the search condition)
if st.session_state.get('show_results', False):
    st.subheader(f"Nearby Places")
    
    selected_place_name = st.selectbox(
        "Select a place to see the route:",
        options=list(st.session_state.places_data.keys()),
        key="place_selector"
    )

    if selected_place_name and selected_place_name in st.session_state.places_data:
        selected_place, selected_distance = st.session_state.places_data[selected_place_name]
        place_lat = selected_place['geometry']['location']['lat']
        place_lng = selected_place['geometry']['location']['lng']
        lat1, lng1, lat2, lng2 = st.session_state.coordinates
        
        st.info(f"Total {travel_mode} time: {selected_distance:.0f} minutes")
        
        # Create Google Maps links
        route1_url = get_gmaps_url(location1,selected_place['place_id'])
        route2_url = get_gmaps_url(location2,selected_place['place_id'])
        
        # Update the map and links to use selected mode
        map_html = f"""
        <iframe width="100%" height="400" frameborder="0" style="border:0"
        src="https://www.google.com/maps/embed/v1/directions?key={GOOGLE_MAPS_API_KEY}
        &origin={lat1},{lng1}
        &destination={lat2},{lng2}
        &waypoints={place_lat},{place_lng}
        &mode={travel_mode}">
        </iframe>
        """
        st.components.v1.html(map_html, height=400)
        
        # Pass mode to the walking time functions
        time1 = get_walking_time(location1, selected_place['place_id'], GOOGLE_MAPS_API_KEY, mode=travel_mode)
        time2 = get_walking_time(location2, selected_place['place_id'], GOOGLE_MAPS_API_KEY, mode=travel_mode)
        
        # Display travel info with direct links
        st.markdown(f"""
        **Address:** {selected_place.get('vicinity', 'No address')}  
        **Routes:**
        * [Directions from Location 1]({route1_url}) ({time1:.0f} mins)
        * [Directions from Location 2]({route2_url}) ({time2:.0f} mins)
        """)