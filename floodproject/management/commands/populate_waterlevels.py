from django.core.management.base import BaseCommand
from ...models import WaterLevel
import requests





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




class Command(BaseCommand):
    help = 'populates the database with Water levels information'

    def handle(self, *args, **options):
        point_list = []
        for dct in response_dict["features"]:

            coordinates = dct['geometry']['coordinates']
            longitude, latitude = coordinates
            messstelle = dct['properties']['messstelle']
            wert = dct['properties']['wert']
            einheit = dct['properties']['einheit']
            land = dct['properties']['land']

            if wert and not land:
                point_list.append(WaterLevel(measuring_point=messstelle, latitude=latitude, longitude=longitude, value=wert, unit=einheit))




        WaterLevel.objects.bulk_create(point_list)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully inserted {len(point_list)} data points')
            )