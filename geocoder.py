import csv
import json
import requests
import urllib.parse


CSV_PATH = "DatathonUCI_Addresses.csv"

BASE_PERS_URL = "https://personator.melissadata.net/"
BASE_ADD_URL = "https://address.melissa.net/"


address_check = "v3/WEB/ContactVerify/doContactVerify"

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

    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        data = json.dumps(data, indent=4)
        print(data)
        return data
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    

def main():
    print("Starting geocoder...")
    license_key = "nRz70ptc6Ce3yHYPaA8IaQ**nSAcwXpxhQ0PC2lXxuDAZ-**" 
    with open(CSV_PATH, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        first_row = next(reader)  # Gets the very first row in the CSV file.
        second_row = next(reader)
        address = second_row[1]
        city = second_row[2]
        state = second_row[3]
        zip = second_row[4]
        verify(address, city, state, zip, license_key)



if __name__ == "__main__":
    main()


