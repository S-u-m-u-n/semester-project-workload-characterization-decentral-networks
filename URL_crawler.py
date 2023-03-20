import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Get website URL from command line argument
url = sys.argv[1]

# Send a request to the website and get the HTML content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all links on the website
links = set()  # use a set to store unique links
for link in soup.find_all('a'):
    href = link.get('href')
    if href is not None and '../A' in href:
        href = href.replace('../A', '/wiki', 1)
        # remove everything after '#' in the link
        if '#' in href:
            href = href[:href.index('#')]
        full_url = urljoin(url, href).replace('https://', '', 1)
        links.add(full_url)  # use the add() method to add unique links to the set

# Extract domain name from URL
domain = urlparse(url).netloc
filename = f"{domain}_links.txt"

# Write links to file
with open(filename, 'w') as file:
    for link in links:
        file.write(link + '\n')

print(f"All unique links on {url} have been saved to {filename}.")