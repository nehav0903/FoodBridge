import googlemaps

gmaps = googlemaps.Client(key='AIzaSyAsFO1AlGYVnhjAFo7OHwFPftLwbUyERGY')

def find_ngos_nearby(lat, lng):
    places_result = gmaps.places_nearby(
        location=(lat, lng),
        radius=5000,
        keyword='NGO'
    )
    return places_result['results']

# Example:
# ngos = find_ngos_nearby(12.9716, 77.5946)
