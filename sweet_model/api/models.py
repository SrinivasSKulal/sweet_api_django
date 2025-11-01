from django.db import models

# Create your models here.


class Sweets(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.IntegerField() # Assume number of sweets and not weight in kg

    def __str__(self):
        return self.name




