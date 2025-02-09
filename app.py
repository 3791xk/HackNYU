import streamlit as st
import requests
from config import GOOGLE_MAPS_API_KEY
from streamlit_searchbox import st_searchbox
from places_utils import (
    get_location_coordinates, find_midpoint,
    search_places, get_gmaps_url, get_walking_time, sort_places, get_place_address
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

logo = 'assets/LogoDesign.png'

# Set page config
st.set_page_config(page_title='MapTogether', page_icon = logo, layout = 'wide')

# Add logo and title in a horizontal layout
col1, col2 = st.columns([1, 9])
with col1:
    st.image(logo, width=150)
with col2:
    st.title("MapTogether")
    st.markdown("Search for spots a convenient distance from both you and your friends")

# Input for locations
col1, col2 = st.columns([1, 1])

with col1:
    selected_value = st_searchbox(
        get_place_suggestions,
        placeholder="Enter first location:",
        key="loc1_input"
    )
    location1 = selected_value

with col2:
    selected_value = st_searchbox(
        get_place_suggestions,
        placeholder="Enter second location:",
        key="loc2_input"
    )
    location2 = selected_value

# Search options row
search_col1, search_col2 = st.columns([1, 1])

with search_col1:
    search_type = st.text_input(
        label='What are you looking for?',
        placeholder="Food, park, gym, etc.",
        label_visibility="visible",
        key='search_type'
    )

with search_col2:
    travel_mode = st.selectbox(
        "Travel mode?",
        options=["Walking", "Driving"],
        key="travel_mode",
        on_change=lambda: st.session_state.update({'show_results': False}),  # Reset results when mode changes
    ).lower()  # Convert to lowercase for API calls

# Search button in full-width row
search_clicked = st.button(label="Search Places", use_container_width=True)

# Only search on button click and when inputs are valid
if search_clicked and location1 and location2 and len(search_type) >= 3:
    coords1 = get_location_coordinates(location1,GOOGLE_MAPS_API_KEY)
    coords2 = get_location_coordinates(location2,GOOGLE_MAPS_API_KEY)
    
    if coords1 and coords2:
        lat1, lng1 = coords1
        lat2, lng2 = coords2
        mid_lat, mid_lng = find_midpoint(lat1, lng1, lat2, lng2)
        places = search_places(mid_lat, mid_lng, search_type,GOOGLE_MAPS_API_KEY)[:15] + search_places(lat1, lng1, search_type,GOOGLE_MAPS_API_KEY)[:7] + search_places(lat2, lng2, search_type,GOOGLE_MAPS_API_KEY)[:7]
        if places:
            places_sorted = sort_places(location1, location2, places, GOOGLE_MAPS_API_KEY, mode=travel_mode)
            places_dict = {place[0]['place_id']: place[0] for place in places_sorted}
            more_places = [search_places(place[0]['geometry']['location']['lat'], place[0]['geometry']['location']['lng'], search_type, GOOGLE_MAPS_API_KEY)[0:5] for place in places_sorted]
            og_places = list(places_dict.values())
            for place in og_places:
                for p in search_places(place['geometry']['location']['lat'], place['geometry']['location']['lng'], search_type, GOOGLE_MAPS_API_KEY)[0:5]:
                    if p['place_id'] not in places_dict:
                        places_dict[p['place_id']] = p
            more_places = list(places_dict.values())
            more_places_sorted = sort_places(location1, location2, more_places, GOOGLE_MAPS_API_KEY, mode=travel_mode)
            st.session_state.places_data = {
                f"{p[0].get('name', 'Unknown')} - {p[0].get('rating', 'No rating')}/5 (Total {travel_mode} time: {p[1]:.0f} mins)": 
                (p[0], p[1]) for p in more_places_sorted
            }
            st.session_state.coordinates = (lat1, lng1, lat2, lng2)
            st.session_state.show_results = True
        else:
            st.error(f"No {search_type} places found in this area")
    else:
        st.error("Couldn't find one or both locations")

# Show results section (outside the search condition)
if st.session_state.get('show_results', False):
    st.subheader(f"Recommended Spots")
    
    # Create two columns for results layout
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        selected_place_name = st.selectbox(
            "Options:",
            options=list(st.session_state.places_data.keys()),
            key="place_selector"
        )

        if selected_place_name and selected_place_name in st.session_state.places_data:
            selected_place, selected_distance = st.session_state.places_data[selected_place_name]
            place_lat = selected_place['geometry']['location']['lat']
            place_lng = selected_place['geometry']['location']['lng']
            lat1, lng1, lat2, lng2 = st.session_state.coordinates
            
            # Pass mode to the walking time functions
            time1 = get_walking_time(location1, selected_place['place_id'], GOOGLE_MAPS_API_KEY, mode=travel_mode)
            time2 = get_walking_time(location2, selected_place['place_id'], GOOGLE_MAPS_API_KEY, mode=travel_mode)
            route1_url = get_gmaps_url(lat1,lng1,place_lat,place_lng)
            route2_url = get_gmaps_url(lat2,lng2,place_lat,place_lng)
            # Get formatted addresses
            address1 = get_place_address(location1, GOOGLE_MAPS_API_KEY)
            address2 = get_place_address(location2, GOOGLE_MAPS_API_KEY)
            
            # Display travel info with direct links
            st.markdown(f"**Address:** {selected_place.get('vicinity', 'No address')}")
            #st.markdown("**Routes:**")
            
            st.link_button(
                f"Route from {address1} ({time1:.0f} mins)",
                route1_url,
                use_container_width=True
            )
            st.link_button(
                f"Route from {address2} ({time2:.0f} mins)",
                route2_url,
                use_container_width=True
            )
    
    with right_col:
        if selected_place_name and selected_place_name in st.session_state.places_data:
            # Create Google Maps links
            
            
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