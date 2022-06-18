import requests
from bs4 import BeautifulSoup
import re
import json

def main():

    base_url = "https://account.venmo.com/u/"

    # Search through collection of valid usernames
    with open("namesTest.txt", 'r') as file:
        names = [line.rstrip() for line in file]

    # Final id_list
    id_list = []

    # Fixed header to ensure spider can crawl (oh how'd that get in there? hehe)
    headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    }

    # Iterate through valid URLs (users)
    for n in names:

        full_url = base_url + n
        r = requests.get(full_url, headers = headers).text
        soup = BeautifulSoup(r, 'html.parser')

        # Parse from HTML 
        venmo_html = str(soup.find('script', id = "__NEXT_DATA__"))
        venmo_html = re.sub('[^A-Za-z0-9]+', ' ',venmo_html)
        venmo_html = venmo_html.split()

        # Add id to list 
        id_aprcn = []
        for i in range(len(venmo_html)):
            if venmo_html[i] == "id":
                id_aprcn.append(i)
        id_term = id_aprcn[-1]
        id = venmo_html[id_term + 1]
        id_list.append(id)

    # Create key-value pairing 
    user_dict = {}
    for i in range(len(names)):
        user_dict[names[i]] = id_list[i]

    # Write dictionary to file
    with open("newDict.txt", "w") as nf:
        nf.write(json.dumps(user_dict))
        nf.close()

if __name__ == "__main__":
    main()