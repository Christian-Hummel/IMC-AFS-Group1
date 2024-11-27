import requests

# describe the feature types and their attributes
describe_url = "https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&REQUEST=DescribeFeatureType&VERSION=2.0.0&SERVICE=WFS"
response = requests.get(describe_url)

if response.status_code == 200:
    print(response.text)  # This will describe the feature types and their attributes
else:
    print(f"Failed to fetch feature description. Status code: {response.status_code}")