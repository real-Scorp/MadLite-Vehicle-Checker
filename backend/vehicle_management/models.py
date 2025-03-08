from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

class Employee(models.Model):
    """Model representing a company employee who can be assigned to vehicles"""
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    position = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # License Information
    license_number = models.CharField(max_length=50, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    license_class = models.CharField(max_length=20, blank=True)  # e.g., C, LR, MR, HR
    
    # Employment Details
    hire_date = models.DateField(null=True, blank=True)
    fifo = models.BooleanField(default=False, verbose_name="FIFO Worker")
    
    # Job Information
    last_job_completed = models.CharField(max_length=200, blank=True)
    current_job = models.CharField(max_length=200, blank=True)
    next_job = models.CharField(max_length=200, blank=True)
    job_history = models.TextField(blank=True, help_text="History of completed jobs")
    
    # Additional Information
    notes = models.TextField(blank=True)
    
    # User account (if applicable)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        """Return the employee's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def license_valid(self):
        """Check if driver's license is valid and not expired"""
        if not self.license_expiry:
            return False
        return self.license_expiry >= date.today()


class Vehicle(models.Model):
    """Model representing a company vehicle"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('maintenance', 'In Maintenance'),
        ('off_road', 'Off Road'),
        ('decommissioned', 'Decommissioned'),
    )

    assigned_employee = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_vehicles'
    )
    
    # Basic Information
    name = models.CharField(max_length=100, verbose_name="Vehicle ID")  # Vehicle name/ID (e.g., "MAD 2")
    employee_name = models.CharField(max_length=100, blank=True, verbose_name="Employee")  # Name of employee assigned
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    drive_type = models.CharField(max_length=10, choices=[('2x4', '2x4'), ('4x4', '4x4')], blank=True)
    
    # Registration and Identification
    registration = models.CharField(max_length=20, unique=True, verbose_name="Registration")
    registration_expiry = models.DateField(null=True, blank=True, verbose_name="Reg Expiry")
    vin = models.CharField(max_length=50, unique=True, verbose_name="VIN")
    engine_number = models.CharField(max_length=50, blank=True)
    fuel_card_number = models.CharField(max_length=50, blank=True)
    
    # Insurance
    insurance_company = models.CharField(max_length=100, blank=True, verbose_name="Insurance")
    insurance_expiry = models.DateField(null=True, blank=True, verbose_name="Insurance Expiry")
    
    # Operational Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    purchase_date = models.DateField()
    current_mileage = models.IntegerField(default=0)
    tyre_size = models.CharField(max_length=50, blank=True)
    rim_color = models.CharField(max_length=50, blank=True)
    
    # Service Information
    last_service_date = models.DateField(null=True, blank=True)
    last_service_mileage = models.IntegerField(null=True, blank=True)
    service_interval_months = models.IntegerField(default=6)
    service_interval_miles = models.IntegerField(default=10000)
    next_major_service_date = models.DateField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_vehicles')
    
    def __str__(self):
        return f"{self.name} - {self.year} {self.make} {self.model} ({self.registration})"
    
    @property
    def next_service_date(self):
        """Calculate the next service date based on last service and interval"""
        if not self.last_service_date:
            return None
        return self.last_service_date + timedelta(days=self.service_interval_months * 30)
    
    @property
    def next_service_mileage(self):
        """Calculate the next service mileage based on last service and interval"""
        if not self.last_service_mileage:
            return None
        return self.last_service_mileage + self.service_interval_miles
    
    @property
    def service_due(self):
        """Check if service is due based on date or mileage"""
        if not self.last_service_date or not self.last_service_mileage:
            return True
        
        date_due = self.next_service_date <= date.today()
        mileage_due = self.current_mileage >= self.next_service_mileage
        
        return date_due or mileage_due
    
    @property
    def service_due_status(self):
        """
        Return a status indicator for service due:
        ✓ Yes (not due)
        ⚠️ Soon (due within 30 days)
        ✗ No (overdue)
        """
        if not hasattr(self, 'next_service_date') or not self.next_service_date:
            return "✗ No"
            
        days_until_service = (self.next_service_date - date.today()).days
        
        if days_until_service < 0:
            return "✗ No"  # Overdue
        elif days_until_service <= 30:
            return "⚠️ Soon"  # Due soon
        else:
            return "✓ Yes"  # Not due yet
    



    @property
    def service_due_status(self):
        """
        Return a status indicator for service due:
        ✓ Yes (not due)
        ⚠️ Soon (due within 30 days)
        ✗ No (overdue)
        """
        if not self.next_service_date:
            return "✗ No"
            
        days_until_service = (self.next_service_date - date.today()).days
        
        if days_until_service < 0:
            return "✗ No"  # Overdue
        elif days_until_service <= 30:
            return "⚠️ Soon"  # Due soon
        else:
            return "✓ Yes"  # Not due yet



class VehiclePart(models.Model):
    """Model representing parts that can be used in vehicles"""
    part_number = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    supplier = models.CharField(max_length=200)
    current_stock = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=5)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.part_number} - {self.description}"
    
    @property
    def needs_reorder(self):
        """Check if part needs to be reordered"""
        return self.current_stock <= self.minimum_stock


class VehiclePartCompatibility(models.Model):
    """Model linking parts to compatible vehicles"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='compatible_parts')
    part = models.ForeignKey(VehiclePart, on_delete=models.CASCADE, related_name='compatible_vehicles')
    
    class Meta:
        unique_together = ('vehicle', 'part')
        verbose_name_plural = 'Vehicle Part Compatibilities'
    
    def __str__(self):
        return f"{self.part} for {self.vehicle}"


class ServiceRecord(models.Model):
    """Model for tracking service history"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='service_records')
    service_date = models.DateField()
    mileage_at_service = models.IntegerField()
    service_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    performed_by = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.vehicle} - {self.service_date} ({self.service_type})"


class ServicePartUsage(models.Model):
    """Model for tracking parts used during service"""
    service = models.ForeignKey(ServiceRecord, on_delete=models.CASCADE, related_name='parts_used')
    part = models.ForeignKey(VehiclePart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.part} ({self.quantity}) for {self.service}"