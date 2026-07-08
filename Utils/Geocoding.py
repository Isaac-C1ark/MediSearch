import requests
from Utils.config import ORS_API_KEY


def geocode_address(address_string):
    if not address_string or not address_string.strip():
        return None, None

    url = "https://api.openrouteservice.org/geocode/search"
    headers = {
        "Authorization": ORS_API_KEY
    }
    params = {
        "text": address_string.strip(),
        "size": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])

            if features:
                lon, lat = features[0]["geometry"]["coordinates"]
                return float(lat), float(lon)

        print(f"Geocoding failed for text address. Status: {response.status_code}")
    except Exception as e:
        print("Geocoding API network connection failure error:", e)

    return None, None