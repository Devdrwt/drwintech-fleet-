from rest_framework import serializers

from .models import GpsUnit, SimCard, SimRecharge, Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"


class GpsUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = GpsUnit
        fields = "__all__"
        read_only_fields = ["traccar_device_id", "last_synced_at"]


class SimCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimCard
        fields = "__all__"


class SimRechargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimRecharge
        fields = "__all__"
        read_only_fields = ["recharged_at", "created_by"]
