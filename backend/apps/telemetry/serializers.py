from rest_framework import serializers

from .models import Position, Trip


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ["time", "device_imei", "latitude", "longitude", "speed", "course", "altitude", "attributes"]


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"
