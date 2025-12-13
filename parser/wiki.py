import requests

url = "https://en.wikipedia.org/wiki/Deaths_in_August_2023"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
}

req = requests.get(url, headers=headers)

src = req.text
print(src)

with open("Deaths_in_August_2023.html", "w") as file:
    file.write(src)
