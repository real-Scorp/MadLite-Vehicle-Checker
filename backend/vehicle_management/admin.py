from django.contrib import admin
from .models import Vehicle, VehiclePart, VehiclePartCompatibility, ServiceRecord, ServicePartUsage

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_name', 'registration', 'insurance_company', 
                   'registration_expiry', 'insurance_expiry', 'service_due_status', 'status')
    list_filter = ('status', 'insurance_company')
    search_fields = ('name', 'registration', 'employee_name')
    
    def get_urls(self):
        from django.urls import path
        from . import views
        
        urls = super().get_urls()
        custom_urls = [
            path('overview/', views.vehicle_list, name='vehicle_overview'),
        ]
        return custom_urls + urls

# Register with custom admin class
admin.site.register(Vehicle, VehicleAdmin)

# Register other models
admin.site.register(VehiclePart)
admin.site.register(VehiclePartCompatibility)
admin.site.register(ServiceRecord)
admin.site.register(ServicePartUsage)