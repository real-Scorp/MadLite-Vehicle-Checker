from rest_framework import serializers
from .models import Vehicle, VehiclePart, VehiclePartCompatibility, ServiceRecord, ServicePartUsage
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class VehiclePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePart
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    service_due = serializers.BooleanField(read_only=True)
    next_service_date = serializers.DateField(read_only=True)
    next_service_mileage = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Vehicle
        fields = '__all__'


class VehiclePartCompatibilitySerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    part = VehiclePartSerializer(read_only=True)
    
    class Meta:
        model = VehiclePartCompatibility
        fields = '__all__'


class ServicePartUsageSerializer(serializers.ModelSerializer):
    part = VehiclePartSerializer(read_only=True)
    
    class Meta:
        model = ServicePartUsage
        fields = '__all__'


class ServiceRecordSerializer(serializers.ModelSerializer):
    parts_used = ServicePartUsageSerializer(many=True, read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    
    class Meta:
        model = ServiceRecord
        fields = '__all__'