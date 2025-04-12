import csv
import json
import requests
import urllib.parse
import time
from math import sin,cos,acos,radians
import math
import folium
from IPython.display import IFrame, display


CSV_PATH = "DatathonUCI_Addresses.csv"
CSV_WRITE_PATH = "another.csv"

BASE_PERS_URL = "https://personator.melissadata.net/"
BASE_ADD_URL = "https://address.melissa.net/"


address_check = "v3/WEB/ContactVerify/doContactVerify"

def compute_distance(latitude, longitude,latitude_2,longtitude_2):
    A = sin(latitude) * sin(latitude_2) + cos(latitude) * cos(latitude_2) * cos(longtitude_2 - longitude)
    return 3959 * math.atan2(math.sqrt(1 - A * A), A)  # in miles
    

def verify(address, city, state, zip, license_key):
    license = license_key
    address_line = f'{address}'
    address_line = urllib.parse.quote(address_line)
    city = city
    state = state
    postal_code = zip
    country = "US"
    url = f"{BASE_PERS_URL}{address_check}?id={license}&format=json&act=check&a1={address_line}&city={city}&state={state}&postalcode={postal_code}&country={country}&cols=GrpAddressDetails,GrpGeocode"
    # url = urllib.parse.urljoin(BASE_PERS_URL, address_check)
    print(f"URL: {url}")
    time.sleep(1)
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        data = json.dumps(data, indent=4)
        print(data)
        return data
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    
def nearest_neighbor_tsp(distances):
    n = len(distances)
    visited = [False] * n
    route = [0]
    visited[0] = True
    total_distance = 0

    for _ in range(1, n):
        last = route[-1]
        nearest = None
        min_dist = float('inf')
        for i in range(n):
            if not visited[i] and distances[last][i] < min_dist:
                min_dist = distances[last][i]
                nearest = i
        route.append(nearest)
        visited[nearest] = True
        total_distance += min_dist

    total_distance += distances[route[-1]][0]
    route.append(0)
    return route, total_distance


def get_lat_and_log():
    latitude = []
    longitude = []
    with open(CSV_WRITE_PATH, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        try:
            for row in reader:
                if row and len(row) >= 15:
                    latitude.append(row[-15])
                    longitude.append(row[-14])
                else:
                    print("Skipping row with unexpected format:", row)
        except Exception as e:
            pass
    return latitude, longitude

def compute_distance_matrix():
    latitude, longitude = get_lat_and_log()
    distance_matrix = []
    
    for i in range(len(latitude)):
        distances = []
        for j in range(len(latitude)):
            if i== j:
                distances.append(0)
                continue
            try:
                print(latitude[i], longitude[i],latitude[j], longitude[j])
                latitude_1 = radians(float(str(latitude[i]).replace('\u2212', '-')))
                longitude_1 = radians(float(str(longitude[i]).replace('\u2212', '-')))
                latitude_2 = radians(float(str(latitude[j]).replace('\u2212', '-')))
                longitude_2 = radians(float(str(longitude[j]).replace('\u2212', '-')))
            except Exception as e:
                print(f"Error processing row {i} or {j}: {e}")
                continue
            print(latitude_1, longitude_1,latitude_2, longitude_2)  
            print(abs(sin(latitude_1)*sin(latitude_2)-cos(latitude_1)*cos(latitude_2)*cos(longitude_2-longitude_1)))
            distances.append(compute_distance(latitude_1, longitude_1, latitude_2, longitude_2))
        distance_matrix.append(distances)
    return distance_matrix

def main():
    print("Starting geocoder...")
    license_key = "nRz70ptc6Ce3yHYPaA8IaQ**nSAcwXpxhQ0PC2lXxuDAZ-**" 
    with open(CSV_PATH, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        first_row = next(reader)  # Gets the very first row in the CSV file.
        first_row = []
        with open(CSV_WRITE_PATH,mode = 'w', newline='') as csvfile_write:
            writer = csv.writer(csvfile_write)

            # for i in range(1):
            try:
                while second_row := next(reader, None):
                    # second_row = next(reader)
                    
                    address = second_row[1]
                    city = second_row[2]
                    state = second_row[3]
                    zip = second_row[4]
                    jsons = verify(address, city, state, zip, license_key)
                    jsons = json.loads(jsons)
                    print(jsons)
                    if first_row == []:
                        first_row = jsons["Records"][0].keys()                    
                        writer.writerow(first_row)
                    row = [jsons["Records"][0][key] for key in first_row]
                    writer.writerow(row)
                # print(f"Processed {i+1} rows")
            except StopIteration:
                print("End of file reached.")
    #return acos(0.38)

def mains():
    distnacce_matrix = compute_distance_matrix()
    print(nearest_neighbor_tsp(distnacce_matrix))

def plot():
    latitude, longitude = get_lat_and_log()
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    fig,ax = plt.subplots(figsize=(10, 6))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
    plt.scatter(longitude, latitude)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Geographical Points')
    plt.show()

    # fig, ax = plt.subplots(figsize=(10, 6))

# ax.scatter(x, y)

# # Limit the number of ticks on the x-axis to, say, 5
# ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
# # Similarly for y-axis if needed
# ax.yaxis.set_major_locator(ticker.MaxNLocator(5))

# plt.title("Geographical Points")
# plt.xlabel("Longitude")
# plt.ylabel("Latitude")
# plt.show()

def compute_route(latitude, longitude):
    distance_matrix = compute_distance_matrix()
    route,total_distance = nearest_neighbor_tsp(distance_matrix)

    route_latitude = []
    route_longitude = []

    for i in route:
        route_latitude.append(latitude[i])
        route_longitude.append(longitude[i])

    return route_latitude, route_longitude, total_distance


def map_route(latitude, longitude,map_name,m):
    for lat, lon in zip(latitude, longitude):
        folium.Marker(location=[lat, lon]).add_to(m)

    if isinstance(latitude, str):
        latitude = [float(latitude)]
    else:
        latitude = [float(lat) for lat in latitude]

    if isinstance(longitude, str):
        longitude = [float(longitude)]
    else:
        longitude = [float(lon) for lon in longitude]    

    route_points = list(zip(latitude, longitude))
    
    # Draw a PolyLine connecting the route points
    folium.PolyLine(route_points, color="blue", weight=2.5, opacity=1).add_to(m)

    m.save(map_name)
    display(IFrame(src=map_name, width=700, height=500))


def compute_distances(latitude, longitude):
    distance = 0
    for i in range(len(latitude)-1):
        latitude_1 = radians(float(str(latitude[i]).replace('\u2212', '-')))
        longitude_1 = radians(float(str(longitude[i]).replace('\u2212', '-')))
        latitude_2 = radians(float(str(latitude[i+1]).replace('\u2212', '-')))
        longitude_2 = radians(float(str(longitude[i+1]).replace('\u2212', '-')))
        distance+=compute_distance(latitude_1, longitude_1, latitude_2, longitude_2)
    return distance



def map():
    # import folium
    # from IPython.display import IFrame

    # latitude,longitude = get_lat_and_log()
    # # Create a map centered at the average location
    # m = folium.Map(location=[latitude[0], longitude[0]], zoom_start=12)

    # # Add markers for each location
    # for lat, lon in zip(latitude, longitude):
    #     folium.Marker(location=[lat, lon]).add_to(m)

    # # Save the map to an HTML file
    # m.save("map.html")
    # IFrame(src='map.html', width=700, height=500)

    # route_latitude, route_longitude, total_distance = compute_route(latitude, longitude)
    # for i in range(len(route_latitude)):
    #     folium.Marker(location=[route_latitude[i], route_longitude[i]], popup=f"Distance: {total_distance}").add_to(m)
    # m.save("map_with_route.html")



    # Get the base marker coordinates
    latitude, longitude = get_lat_and_log()

    # Create a map centered at the first location
    m = folium.Map(location=[latitude[0], longitude[0]], zoom_start=12)

    # Add markers for each location
    for lat, lon in zip(latitude, longitude):
        folium.Marker(location=[lat, lon]).add_to(m)

    # Save and optionally display the initial map
    m.save("map.html")
    display(IFrame(src='map.html', width=700, height=500))

    # Compute the route (ensure this returns lists or tuples)
    route_latitude, route_longitude, total_distance = compute_route(latitude, longitude)

    # Check if route_latitude and route_longitude are not lists (i.e., if they are strings),
    # then wrap them in a list or split them if they contain multiple comma-separated values.
    # Here is an example if they are single string values:
    if isinstance(route_latitude, str):
        route_latitude = [float(route_latitude)]
    else:
        route_latitude = [float(lat) for lat in route_latitude]

    if isinstance(route_longitude, str):
        route_longitude = [float(route_longitude)]
    else:
        route_longitude = [float(lon) for lon in route_longitude]

    # Add markers for each point on the computed route
    for lat, lon in zip(route_latitude, route_longitude):
        folium.Marker(location=[lat, lon], popup=f"Distance: {total_distance}").add_to(m)

    # Create a list of (lat, lon) tuples in the computed order for drawing the route
    route_points = list(zip(route_latitude, route_longitude))
    
    # Draw a PolyLine connecting the route points
    folium.PolyLine(route_points, color="blue", weight=2.5, opacity=1).add_to(m)

    # Save and display the map with the route drawn
    m.save("map_with_route.html")
    display(IFrame(src='map_with_route.html', width=700, height=500))

    map_route(latitude, longitude,"map_with_route_nothing.html",m)

def mm():
    lat,log = get_lat_and_log()
    print(compute_distances(lat,log))

    

    

if __name__ == "__main__":
    mm()
    # map()
    # mains()
    # plot()


