from rest_framework import serializers
from .models import Sweets


class SweetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sweets
        fields = '__all__'
        