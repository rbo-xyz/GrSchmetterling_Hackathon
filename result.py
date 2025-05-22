# result.py
import matplotlib.pyplot as plt

def generate_report(points, lkm, time_hours):
    print(f"Total Leistungskilometer: {lkm}")
    print(f"Estimated march time: {time_hours} hours")

    elevations = [p[2] for p in points]
    distance = list(range(len(points)))

    plt.plot(distance, elevations)
    plt.title("Elevation Profile")
    plt.xlabel("Track Point Index")
    plt.ylabel("Elevation (m)")
    plt.grid(True)
    plt.show()
