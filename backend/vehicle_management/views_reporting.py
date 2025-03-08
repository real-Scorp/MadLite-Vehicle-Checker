# vehicle_management/views_reporting.py
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from calendar import monthrange

from .models import Vehicle, ServiceRecord, VehiclePart, VehiclePartCompatibility, ServicePartUsage

@api_view(['GET'])
def service_forecast(request):
    """
    Generate a forecast of upcoming services over the next 6 months
    """
    try:
        # Get current date
        today = timezone.now().date()
        
        # Initialize forecast data structure
        forecast_data = []
        
        # Calculate scheduled and predicted services for the next 6 months
        for i in range(6):
            month_start = (today.replace(day=1) + timedelta(days=32 * i)).replace(day=1)
            month_end = (month_start.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Format month name (e.g., "Jan 2023")
            month_name = month_start.strftime("%b %Y")
            
            # Get scheduled services (already in the system)
            scheduled_services = ServiceRecord.objects.filter(
                service_date__gte=month_start,
                service_date__lte=month_end
            ).count()
            
            # Calculate predicted services based on service intervals
            # This is a simplified calculation - in real implementation you might need more complex logic
            predicted_services = Vehicle.objects.filter(
                status='active'
            ).filter(
                # Vehicles with last_service_date in appropriate range
                Q(last_service_date__isnull=False) &
                (
                    # Calculate next service date using service_interval_months
                    Q(last_service_date__lt=month_end - timedelta(days=30 * F('service_interval_months'))) |
                    
                    # Or using mileage if available
                    Q(current_mileage__gte=F('last_service_mileage') + F('service_interval_miles'))
                )
            ).exclude(
                # Exclude vehicles already accounted for in scheduled services
                service_records__service_date__gte=month_start,
                service_records__service_date__lte=month_end
            ).count()
            
            # Add to forecast data
            forecast_data.append({
                'name': month_name,
                'scheduled': scheduled_services,
                'predicted': predicted_services,
            })
        
        return Response(forecast_data)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def vehicle_utilization(request):
    """
    Calculate vehicle utilization metrics based on service records
    """
    try:
        # Get query parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Default to last 12 months if no dates provided
        today = timezone.now().date()
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=365)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = today
        
        # Get all vehicles
        vehicles = Vehicle.objects.all()
        
        # Initialize results
        results = []
        
        for vehicle in vehicles:
            # Get service records for this vehicle in the date range
            services = ServiceRecord.objects.filter(
                vehicle=vehicle,
                service_date__gte=start_date,
                service_date__lte=end_date
            )
            
            # Calculate metrics
            total_services = services.count()
            total_cost = services.aggregate(Sum('cost'))['cost__sum'] or 0
            downtime_days = 0
            
            # Simple estimate of downtime (assuming 1 day per service)
            # In a real app, you would track actual downtime
            downtime_days = total_services
            
            # Calculate utilization percentage (days not in maintenance / total days)
            total_days = (end_date - start_date).days + 1
            utilization_percentage = ((total_days - downtime_days) / total_days) * 100 if total_days > 0 else 0
            
            # Get latest mileage
            latest_service = services.order_by('-service_date').first()
            latest_mileage = latest_service.mileage_at_service if latest_service else vehicle.current_mileage
            
            # Calculate mileage change if we have data points
            first_service = services.order_by('service_date').first()
            mileage_change = 0
            if first_service and latest_service and first_service != latest_service:
                mileage_change = latest_service.mileage_at_service - first_service.mileage_at_service
            
            # Add to results
            results.append({
                'id': vehicle.id,
                'name': vehicle.name,
                'registration': vehicle.registration,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'total_services': total_services,
                'total_cost': float(total_cost),
                'downtime_days': downtime_days,
                'utilization_percentage': round(utilization_percentage, 2),
                'latest_mileage': latest_mileage,
                'mileage_change': mileage_change,
            })
        
        return Response(results)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def maintenance_costs(request):
    """
    Generate maintenance cost reports
    """
    try:
        # Get query parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'month')  # month, vehicle, service_type
        
        # Default to last 12 months if no dates provided
        today = timezone.now().date()
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=365)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = today
        
        # Base query for all service records in the date range
        services = ServiceRecord.objects.filter(
            service_date__gte=start_date,
            service_date__lte=end_date
        )
        
        # Different aggregations based on grouping
        if group_by == 'month':
            # Group by month
            monthly_costs = []
            current_date = start_date.replace(day=1)
            
            while current_date <= end_date:
                next_month = current_date.replace(day=28) + timedelta(days=4)
                next_month = next_month.replace(day=1)
                
                # Get services for this month
                month_services = services.filter(
                    service_date__gte=current_date,
                    service_date__lt=next_month
                )
                
                # Calculate total cost
                month_total = month_services.aggregate(Sum('cost'))['cost__sum'] or 0
                
                # Add to results
                monthly_costs.append({
                    'period': current_date.strftime('%b %Y'),
                    'total_cost': float(month_total),
                    'service_count': month_services.count(),
                })
                
                current_date = next_month
            
            return Response(monthly_costs)
            
        elif group_by == 'vehicle':
            # Group by vehicle
            vehicle_costs = []
            
            # Get all vehicles that had services
            vehicle_ids = services.values_list('vehicle', flat=True).distinct()
            vehicles = Vehicle.objects.filter(id__in=vehicle_ids)
            
            for vehicle in vehicles:
                # Get services for this vehicle
                vehicle_services = services.filter(vehicle=vehicle)
                
                # Calculate total cost
                vehicle_total = vehicle_services.aggregate(Sum('cost'))['cost__sum'] or 0
                
                # Add to results
                vehicle_costs.append({
                    'vehicle_id': vehicle.id,
                    'vehicle_name': vehicle.name,
                    'registration': vehicle.registration,
                    'make_model': f"{vehicle.make} {vehicle.model}",
                    'total_cost': float(vehicle_total),
                    'service_count': vehicle_services.count(),
                    'avg_cost_per_service': float(vehicle_total) / vehicle_services.count() if vehicle_services.count() > 0 else 0,
                })
            
            # Sort by total cost (highest first)
            vehicle_costs.sort(key=lambda x: x['total_cost'], reverse=True)
            
            return Response(vehicle_costs)
            
        elif group_by == 'service_type':
            # Group by service type
            service_type_costs = []
            
            # Get all service types
            service_types = services.values_list('service_type', flat=True).distinct()
            
            for service_type in service_types:
                # Get services of this type
                type_services = services.filter(service_type=service_type)
                
                # Calculate total cost
                type_total = type_services.aggregate(Sum('cost'))['cost__sum'] or 0
                
                # Add to results
                service_type_costs.append({
                    'service_type': service_type,
                    'total_cost': float(type_total),
                    'service_count': type_services.count(),
                    'avg_cost_per_service': float(type_total) / type_services.count() if type_services.count() > 0 else 0,
                })
            
            # Sort by total cost (highest first)
            service_type_costs.sort(key=lambda x: x['total_cost'], reverse=True)
            
            return Response(service_type_costs)
            
        else:
            return Response(
                {'error': f"Invalid group_by parameter: {group_by}. Valid options: month, vehicle, service_type"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def parts_usage_report(request):
    """
    Generate a report of parts usage over time
    """
    try:
        # Get query parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Default to last 12 months if no dates provided
        today = timezone.now().date()
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=365)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = today
        
        # Find all service records in the date range
        services = ServiceRecord.objects.filter(
            service_date__gte=start_date,
            service_date__lte=end_date
        )
        
        # Get all part usages for these services
        part_usages = ServicePartUsage.objects.filter(
            service__in=services
        ).select_related('part', 'service')
        
        # Aggregate by part
        part_usage_data = {}
        
        for usage in part_usages:
            part_id = usage.part.id
            
            if part_id not in part_usage_data:
                part_usage_data[part_id] = {
                    'part_id': part_id,
                    'part_number': usage.part.part_number,
                    'description': usage.part.description,
                    'total_quantity': 0,
                    'current_stock': usage.part.current_stock,
                    'minimum_stock': usage.part.minimum_stock,
                    'usage_by_month': {},
                }
            
            # Update total quantity
            part_usage_data[part_id]['total_quantity'] += usage.quantity
            
            # Update monthly usage
            month_key = usage.service.service_date.strftime('%Y-%m')
            month_name = usage.service.service_date.strftime('%b %Y')
            
            if month_key not in part_usage_data[part_id]['usage_by_month']:
                part_usage_data[part_id]['usage_by_month'][month_key] = {
                    'month': month_name,
                    'quantity': 0,
                }
            
            part_usage_data[part_id]['usage_by_month'][month_key]['quantity'] += usage.quantity
        
        # Convert to list and sort usage_by_month
        result = []
        for part_id, data in part_usage_data.items():
            monthly_usage = list(data['usage_by_month'].values())
            monthly_usage.sort(key=lambda x: datetime.strptime(x['month'], '%b %Y'))
            
            data['usage_by_month'] = monthly_usage
            result.append(data)
        
        # Sort by total quantity used (highest first)
        result.sort(key=lambda x: x['total_quantity'], reverse=True)
        
        return Response(result)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )