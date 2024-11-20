import requests

url = "https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&REQUEST=GetCapabilities&VERSION=2.0.0&SERVICE=WFS"
response = requests.get(url)

if response.status_code == 200:
    print(response.text)
else:
    print(f"Failed to fetch feature description. Status code: {response.status_code}")