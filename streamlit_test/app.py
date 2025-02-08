import streamlit as st
import requests
from config import GOOGLE_MAPS_API_KEY

# Set page config
st.set_page_config(
    page_title="Google Maps Explorer",
    layout="wide"
)

# Title and description
st.title("Location Explorer")
st.markdown("Explore locations and get information using Google Maps integration")

def get_location_coordinates(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None

# Default location (New York City)
default_lat, default_lng = 40.7128, -74.0060
lat, lng = default_lat, default_lng

# Search box
search_query = st.text_input("Enter location to search:", "")
if st.button("Search"):
    if search_query:
        result = get_location_coordinates(search_query)
        if result:
            lat, lng = result
            st.success(f"Found location: {search_query}")
        else:
            st.error("Location not found")

# Embed Google Maps
map_html = f"""
<iframe width="100%" height="600" frameborder="0" style="border:0"
src="https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAPS_API_KEY}&q={lat},{lng}&zoom=13">
</iframe>
"""
st.components.v1.html(map_html, height=600)

# Add some example interactions
st.subheader("Map Controls")
if st.button("Center on New York"):
    st.info("Map centered on New York City")

if st.button("Show Satellite View"):
    st.info("Switching to satellite view") 