from rest_framework import serializers
from .models import Ak



class AkSerializers(serializers.ModelSerializer):
    class Meta:
        model = Ak
        fields = ['view', "name_firma", 'inn', 'kpp', 'Address', 'email', 'director']

