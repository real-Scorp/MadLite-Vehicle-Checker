from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_reporting

# Create a router for API views
router = DefaultRouter()
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'parts', views.VehiclePartViewSet)
router.register(r'services', views.ServiceRecordViewSet)
router.register(r'compatibility', views.VehiclePartCompatibilityViewSet)

urlpatterns = [
    path('', views.vehicle_list, name='home'),
    path('api/', include(router.urls)),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('parts/', views.part_list, name='part_list'),
    
    # Add reporting endpoints
    path('api/reports/service-forecast/', views_reporting.service_forecast, name='service_forecast'),
    path('api/reports/vehicle-utilization/', views_reporting.vehicle_utilization, name='vehicle_utilization'),
    path('api/reports/maintenance-costs/', views_reporting.maintenance_costs, name='maintenance_costs'),
    path('api/reports/parts-usage/', views_reporting.parts_usage_report, name='parts_usage_report'),
]