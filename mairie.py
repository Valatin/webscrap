import re
import sys
import csv
import time
import requests
from bs4 import BeautifulSoup as bs


start_time = time.time()
def main():
    #Ensure correct usage...............
    if not len(sys.argv) == 2:
        sys.exit("Usage: mairie.py datafile.csv")

    # Initialize variables and tmp we need later   
    dicterror = {
        "mairie": "Not Found",
        "telephone": "Not Found",
        "horaires": "Not Found"
    }

    # Open CSV file and creates an array of dict "mairies" in witch the infos will go
    mairies = []
    with open(sys.argv[1], "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        for row in reader:
            # Create the URL to visit and adds it to the row
            row["url"] = get_url(row["insee"], row["commune"])
            # Append the dict row to the mairies array
            mairies.append(row)

    for city in mairies:
        print(city["url"])
        try:
            page = requests.get(city["url"], timeout=10)
            if not page.status_code == requests.codes.ok:
                city.update(dicterror)
                print("Error")
            else:
                print(page.status_code)
        except requests.exceptions.ReadTimeout:
            print("TimeOut")

    print(mairies)
    
    print("--- {} seconds ---".format(time.time() - start_time))


def get_url(insee, cityname):
    characters = [" ", "_"]
    cityname_url = cityname.lower()
    for character in characters:
        cityname_url =  cityname_url.replace(character,"-")
    url = "http://www.linternaute.com/ville/{}/ville-{}/mairie/".format(cityname_url, insee)
    return url


if __name__ == "__main__":
    main()