# gps_check.py
import math

# Haversine formula to calculate distance between two GPS points in meters
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # distance in meters


def check_gps_location(user_lat, user_lon, office_lat, office_lon, radius_meters=50):
    """
    Check if user is within the allowed location radius.
    """
    distance = haversine_distance(user_lat, user_lon, office_lat, office_lon)
    return distance <= radius_meters
