from django.db import models

# Create your models here.


class Sweets(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10 , decimal_places=2)
    quantity = models.IntegerField() # Assume number of sweets and not weight in kg

    def __str__(self):
        return self.name




