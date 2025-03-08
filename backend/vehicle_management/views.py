from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Vehicle, VehiclePart, VehiclePartCompatibility, ServiceRecord, ServicePartUsage
from .serializers import (
    VehicleSerializer, 
    VehiclePartSerializer, 
    VehiclePartCompatibilitySerializer,
    ServiceRecordSerializer, 
    ServicePartUsageSerializer
)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for vehicles
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    
    @action(detail=True, methods=['get'])
    def service_history(self, request, pk=None):
        """Get service history for a specific vehicle"""
        vehicle = self.get_object()
        services = vehicle.service_records.all().order_by('-service_date')
        serializer = ServiceRecordSerializer(services, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_for_service(self, request):
        """Get all vehicles due for service"""
        # In a real application, we would calculate this on the fly
        # For simplicity, we'll just return vehicles with service_due property = True
        vehicles = [v for v in Vehicle.objects.all() if v.service_due]
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)


class VehiclePartViewSet(viewsets.ModelViewSet):
    """
    API endpoint for vehicle parts
    """
    queryset = VehiclePart.objects.all()
    serializer_class = VehiclePartSerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get parts with low stock that need reordering"""
        parts = [p for p in VehiclePart.objects.all() if p.needs_reorder]
        serializer = VehiclePartSerializer(parts, many=True)
        return Response(serializer.data)


class ServiceRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for service records
    """
    queryset = ServiceRecord.objects.all().order_by('-service_date')
    serializer_class = ServiceRecordSerializer


class VehiclePartCompatibilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for vehicle-part compatibility
    """
    queryset = VehiclePartCompatibility.objects.all()
    serializer_class = VehiclePartCompatibilitySerializer
    
    @action(detail=False, methods=['get'])
    def compatible_parts(self, request):
        """Get compatible parts for a specific vehicle"""
        vehicle_id = request.query_params.get('vehicle_id')
        if not vehicle_id:
            return Response({"error": "vehicle_id query parameter is required"}, status=400)
        
        compatibilities = VehiclePartCompatibility.objects.filter(vehicle_id=vehicle_id)
        serializer = VehiclePartCompatibilitySerializer(compatibilities, many=True)
        return Response(serializer.data)
    


    
# HTML view of vehicle list table
def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by('registration')
    return render(request, 'vehicle_management/vehicle_list.html', {'vehicles': vehicles})
# HTML view of part list table
def part_list(request):
    parts = VehiclePart.objects.all().order_by('part_number')
    return render(request, 'vehicle_management/part_list.html', {'parts': parts})

def vehicle_service_parts(request, vehicle_id):
    try:
        vehicle = Vehicle.objects.get(pk=vehicle_id)
        compatible_parts = VehiclePart.objects.filter(compatible_vehicles__vehicle=vehicle)
        
        return render(request, 'vehicle_management/vehicle_service_parts.html', {
            'vehicle': vehicle,
            'compatible_parts': compatible_parts
        })
    except Vehicle.DoesNotExist:
        from django.http import Http404
        raise Http404("Vehicle not found")
    
        