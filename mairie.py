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
    dict_error = {
        "maire": "Not Found",
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

    # Iterate through all cities
    for city in mairies:
        # Try to connect to webpage
        try:
            page = requests.get(city["url"], timeout=5)
        
        # Skip if request give error code
        except requests.exceptions.RequestException:
            city.update(dict_error)
            print("TimeOut or page not found")

        # Skip if cannot connect to url
        if not page.status_code == requests.codes.ok:
            city.update(dict_error)
            print("Error: URL Not Found")

        # Proceed to look for info
        else:
            soup=bs(page.content, 'html.parser')
            
            # Checks if good url
            if soup.title.text == "Erreur!":
                city.update(dict_error)
                print("Error: Wrong URL")
            
            # Else proceeds with scraping
            else :
                infosoup = soup.find("div", {"id": "mairie"})

                # Search for mayor: (Monsieur ou madame) (a word) (- or " ") (a word with an Uppercase) (1 or 0 word with uppercase)
                maire = re.search('(Monsieur |Madame )\w+[-\ ]([A-Z][a-z]+ )*[A-Z]+( [A-Z]+)*', str(infosoup))
                city["maire"] = "Mayor Not Found" if maire == None else maire.group()

                # Search for phone nbr
                telephone = re.search('((\d{2}) ){4}(\d{2})', str(infosoup))
                city["telephone"] = "Phone Not Found" if telephone == None else telephone.group()

                # Search for opening hours
                horairessoup = soup.find('h2', text = re.compile('Horaires')).next_sibling
                horaires = " ".join(horairessoup.text.split())
                city["horaires"] = horaires.split('ouverte : ')[1]

        print("Status: {}, {}, Mayor:{}, Tel: {}, Horaires: {}".format(page.status_code, city["commune"], city["maire"], city["telephone"], city["horaires"]))


    
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