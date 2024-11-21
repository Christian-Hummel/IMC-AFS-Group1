import requests

# get the features and their attributes in json format
get_json_url = "https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&request=GetFeature&service=WFS&version=2.0.0&outputFormat=json&typeNames=inspire:pegelaktuell"
response = requests.get(get_json_url)

response_dict = response.json()


resp_dict = response_dict['features'][0]
features = []
for key, value in resp_dict.items():
    if type(value) == dict:
        for key1 in value.keys():
            features.append(key1)
    features.append(key)

# keys of the one dictionary in response_dict['features']
# these keys are supposedly the same for all of the other dictionaries as well

# print(features)

# most important features for our purposes will probably be

## coordinates - or lon and lat
## wert
## einheit


# print(response_dict)

# print(response_dict["features"])

for dct in response_dict["features"]:


    coordinates = dct['geometry']['coordinates']
    longitude, latitude = coordinates
    messstelle = dct['properties']['messstelle']
    wert = dct['properties']['wert']
    einheit = dct['properties']['einheit']
    land = dct['properties']['land']

    if wert and not land:
        print(f"Messstelle {messstelle}, coordinates {coordinates}, wert {wert}, einheit {einheit}")





# if response.status_code == 200:
#     print(response.text)  # This will describe the feature types and their attributes
# else:
#     print(f"Failed to fetch feature description. Status code: {response.status_code}")