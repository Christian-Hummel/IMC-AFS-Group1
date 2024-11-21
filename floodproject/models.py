from django.db import models


class WaterLevel(models.Model):
    measuring_point =  models.CharField(max_length=256)
    latitude = models.FloatField()
    longitude = models.FloatField()
    value = models.FloatField()
    unit = models.CharField(max_length=256)

    def __str__self(self):
        return self.measuring_point