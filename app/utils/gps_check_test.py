from gps_check import is_within_location

# Office/lecture hall location
OFFICE_LAT, OFFICE_LON = 6.5244, 3.3792  # Example: Lagos coordinates

if is_within_location(6.5244, 3.3791, OFFICE_LAT, OFFICE_LON):
    print("User is within the location.")
else:
    print("User is outside allowed location.")
