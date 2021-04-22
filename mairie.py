import re
import sys
import csv
import time
import requests
from bs4 import BeautifulSoup as bs
from unidecode import unidecode


start_time = time.time()
def main():
    #Ensure correct usage...............
    if not len(sys.argv) == 2:
        sys.exit("Usage: mairie.py datafile.csv")

    # Initialize variable in case of error  
    dict_error = {
        "maire": "Not Found",
        "telephone": "Not Found",
        "horaires": "Not Found"
    }
    errors = 0

    # Open CSV file and creates an array of dict "mairies" in witch the infos will go
    mairies = []
    with open(sys.argv[1], "r", encoding='utf-8') as csv_file:
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
            errors += 1
            print("→ Error 1: " + str(errors), end="--")

        # Skip if cannot connect to url
        if not page.status_code == requests.codes.ok:
            city.update(dict_error)
            errors += 1
            print("→ Error 2: " + str(errors), end="--")

        # Proceed to look for info
        else:
            soup=bs(page.content, 'html.parser')
            
            # Checks if good url
            if soup.title.text == "Erreur!":
                city.update(dict_error)
                errors += 1
                print("→ Error 3: " + str(errors), end="--")
            
            # Else proceeds with scraping
            else :
                # Get the right div in the page
                infosoup = soup.find("div", {"id": "mairie"})
                # Search for mayor
                city["maire"] = find_mayor(infosoup)
                # Search for phone nbr
                city["telephone"] = find_phone(infosoup)
                # Search for opening hours
                city["horaires"] = find_openhours(infosoup)
        
        print("-{}: maire: {}; url: {}".format(city["commune"], city["maire"], city["url"]))

    print("Analysis : --- {} seconds --- {} Error(s)".format((time.time() - start_time), errors))

    # Create the output csv file
    create_csv(mairies)

    print("Complete : --- {} seconds --- {} Error(s)".format((time.time() - start_time), errors))


def get_url(insee, cityname):
    characters = [" ", "_", "'"]
    cityname_url = unidecode(cityname.lower())
    for character in characters:
        cityname_url =  cityname_url.replace(character,"-")
    url = "http://www.linternaute.com/ville/{}/ville-{}/mairie".format(cityname_url, insee)
    return url


def find_mayor(soup):
    # Search for mayor: (Monsieur ou madame) (a word) (- or " ") (a word with an Uppercase) (1 or 0 word with uppercase)
    maire = re.search('(Monsieur |Madame )\w+[-\ ]([A-Z][a-z]+ )*[A-Z]+( [A-Z]+)*', str(soup))
    return "Mayor Not Found" if maire == None else maire.group()


def find_phone(soup):
    telephone = re.search('((\d{2}) ){4}(\d{2})', str(soup))
    return "Phone Not Found" if telephone == None else telephone.group()


def find_openhours(soup):  
    try:
        horairessoup = soup.find('h2', text = re.compile('Horaires')).next_sibling
    except AttributeError:
        return "Opening hours Not Found"

    horaires = " ".join(horairessoup.text.split())
    try:
        return horaires.split('ouverte : ')[1]
    except IndexError:
        return "Opening hours Not Found"

# Write CSV file from a "list_of_dict", each dict will be a line in output.csv
def create_csv(list_of_dict):
    with open('output.csv', 'w', encoding='utf-8') as file:
        w = csv.DictWriter(file, list_of_dict[0].keys(), dialect='excel', delimiter=';', lineterminator = '\n')
        w.writeheader()
        for line in list_of_dict:
            w.writerow(line)

if __name__ == "__main__":
    main()