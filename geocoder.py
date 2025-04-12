import csv
import json
import requests
import urllib.parse
import time
from math import sin,cos,acos,radians
import math


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


if __name__ == "__main__":
    # mains()
    plot()


