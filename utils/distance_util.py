import requests
from config import GOOGLE_MAPS_API_KEY

def get_distance(origin, destination):
    try:
        if not GOOGLE_MAPS_API_KEY:
            return "⚠️ Please set OPENROUTE_API_KEY."
        
        headers = {
            'Authorization': GOOGLE_MAPS_API_KEY,
            'Content-Type': 'application/json',
        }

        def geocode(place_name):
            url = f"https://api.openrouteservice.org/geocode/search?text={place_name}&api_key={GOOGLE_MAPS_API_KEY}"
            response = requests.get(url, headers=headers)
            data = response.json()
            if not data["features"]:
                raise ValueError(f"Location '{place_name}' not found.")
            return {
                "lat": data["features"][0]["geometry"]["coordinates"][1],
                "lng": data["features"][0]["geometry"]["coordinates"][0]
            }

        origin_coords = geocode(origin)
        destination_coords = geocode(destination)

        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        response = requests.post(
            url,
            headers=headers,
            json={
                "coordinates": [
                    [origin_coords["lng"], origin_coords["lat"]],
                    [destination_coords["lng"], destination_coords["lat"]],
                ],
                "units": "km"
            }
        )
        data = response.json()

        if "routes" not in data:
            return f"⚠️ No route found. Error: {data.get('error')['message']}"

        distance_km = data["routes"][0]["summary"]["distance"]
        duration_min = data["routes"][0]["summary"]["duration"] / 60

        return (
            f"📍 Distance from {origin} to {destination}:\n\n"
            f"\t\t🚙 Driving distance: {distance_km:.1f} km\n\n"
            f"\t⌚ Estimated duration: {duration_min:.1f} minutes\n"
        )

    except Exception as e:
        return f"⚠️ Error calculating distance: {str(e)}"