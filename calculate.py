#import in die Funktion: Geodataframe sowie Marschgeschwindigkeit aus UI

def calculate_lkm(points, marchTime):

    import math

    def flat_distance(lat1, lon1, lat2, lon2):
        dx = (lon2 - lon1) * 111 * math.cos(math.radians((lat1 + lat2) / 2))
        dy = (lat2 - lat1) * 111
        return math.sqrt(dx**2 + dy**2)

    total_distance = 0.0
    total_uphill = 0.0
    steep_downhill = 0.0

    for i in range(1, len(points)):
        lat1, lon1, ele1 = points[i - 1]
        lat2, lon2, ele2 = points[i]
        dist = flat_distance(lat1, lon1, lat2, lon2)
        elev_diff = ele2 - ele1

        total_distance += dist
        if elev_diff > 0:
            total_uphill += elev_diff
        elif dist * 1000 > 0:  # avoid divide-by-zero
            slope = abs(elev_diff) / (dist * 1000)
            if slope >= 0.2:
                steep_downhill += abs(elev_diff)

    lkm = total_distance + (total_uphill / 100) + (steep_downhill / 150)
    march_time = lkm / 4  # assuming 4 Lkm/h

    return round(lkm, 2), round(march_time, 2)
