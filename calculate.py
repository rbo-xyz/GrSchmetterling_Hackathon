# calculate.py
def calculate_lkm(points):
    import math

    def haversine(lat1, lon1, lat2, lon2):
        # simplified, rough distance in km
        from math import radians, cos, sin, asin, sqrt
        R = 6371.0
        dlon = radians(lon2 - lon1)
        dlat = radians(lat2 - lat1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    total_distance = 0.0
    total_uphill = 0.0
    total_downhill = 0.0
    steep_downhill = 0.0

    for i in range(1, len(points)):
        lat1, lon1, ele1 = points[i - 1]
        lat2, lon2, ele2 = points[i]
        dist = haversine(lat1, lon1, lat2, lon2)
        elev_diff = ele2 - ele1

        total_distance += dist
        if elev_diff > 0:
            total_uphill += elev_diff
        else:
            if abs(elev_diff) / (dist * 1000) > 0.2:
                steep_downhill += abs(elev_diff)
            total_downhill += abs(elev_diff)

    lkm = total_distance + (total_uphill / 100) + (steep_downhill / 150)
    march_time = lkm / 4  # assuming 4 Lkm/h
    return round(lkm, 2), round(march_time, 2)
