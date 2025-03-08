import os
import pandas as pd
import datetime
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vehicle_management.models import Vehicle, VehiclePart, VehiclePartCompatibility


class Command(BaseCommand):
    help = 'Import data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument('--vehicles', type=str, help='Path to vehicles Excel file')
        parser.add_argument('--parts', type=str, help='Path to parts Excel file')

    def handle(self, *args, **options):
        vehicles_file = options.get('vehicles')
        parts_file = options.get('parts')

        if vehicles_file and os.path.exists(vehicles_file):
            self.import_vehicles(vehicles_file)
        else:
            self.stdout.write(self.style.WARNING('Vehicles file not found or not specified'))

        if parts_file and os.path.exists(parts_file):
            self.import_parts(parts_file)
        else:
            self.stdout.write(self.style.WARNING('Parts file not found or not specified'))

    def safe_str(self, value, default=""):
        """Safely convert value to string, handling NaN values"""
        if pd.isna(value):
            return default
        return str(value)

    def import_vehicles(self, file_path):
        """Import vehicles from Excel file."""
        try:
            self.stdout.write(f'Importing vehicles from {file_path}')
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Print column names for debugging
            self.stdout.write(f'Found columns: {df.columns.tolist()}')
            
            vehicles_created = 0
            vehicles_updated = 0
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    # Get vehicle ID
                    vehicle_id = None
                    if 'Motor Vehicle ID' in df.columns and not pd.isna(row['Motor Vehicle ID']):
                        vehicle_id = self.safe_str(row['Motor Vehicle ID'])
                    elif not pd.isna(row.iloc[0]):
                        vehicle_id = self.safe_str(row.iloc[0])
                    
                    # Get registration
                    registration = None
                    if 'Registration' in df.columns and not pd.isna(row['Registration']):
                        registration = self.safe_str(row['Registration'])
                    
                    # Get employee
                    employee_name = None
                    if 'Driver' in df.columns and not pd.isna(row['Driver']):
                        employee_name = self.safe_str(row['Driver'])
                    
                    # Get insurance company - using the exact column name you provided
                    insurance_company = None
                    if 'Insurance Company' in df.columns and not pd.isna(row['Insurance Company']):
                        insurance_company = self.safe_str(row['Insurance Company'])
                    
                    # Get registration expiry - using the exact column name you provided
                    registration_expiry = None
                    if 'Rego Expiry' in df.columns and not pd.isna(row['Rego Expiry']):
                        registration_expiry = row['Rego Expiry']
                        if not isinstance(registration_expiry, datetime.date):
                            try:
                                registration_expiry = pd.to_datetime(registration_expiry).date()
                            except:
                                registration_expiry = None
                    
                    # Get insurance expiry - using the exact column name you provided
                    insurance_expiry = None
                    if 'Insurance Expiry' in df.columns and not pd.isna(row['Insurance Expiry']):
                        insurance_expiry = row['Insurance Expiry']
                        if not isinstance(insurance_expiry, datetime.date):
                            try:
                                insurance_expiry = pd.to_datetime(insurance_expiry).date()
                            except:
                                insurance_expiry = None
                    
                    # Skip rows with missing essential data
                    if not vehicle_id or not registration:
                        self.stdout.write(self.style.WARNING(f'Skipping row {idx+2}: Missing vehicle ID or registration'))
                        continue
                    
                    # Debug output
                    self.stdout.write(f'Vehicle: {vehicle_id}, Registration: {registration}')
                    self.stdout.write(f'  Employee: {employee_name}')
                    self.stdout.write(f'  Insurance: {insurance_company}, Expires: {insurance_expiry}')
                    self.stdout.write(f'  Registration Expires: {registration_expiry}')
                    
                    # Create vehicle record
                    vehicle_data = {
                        'name': vehicle_id,
                        'registration': registration,
                        'employee_name': employee_name,
                        'insurance_company': insurance_company,
                        'registration_expiry': registration_expiry,
                        'insurance_expiry': insurance_expiry,
                        'make': 'Toyota',  # Default - update if needed
                        'model': 'Unknown',  # Default - update if needed
                        'year': 2020,  # Default - update if needed
                        'purchase_date': date.today(),  # Default
                        'status': 'active',  # Default
                    }
                    
                    # Create or update vehicle
                    vehicle, created = Vehicle.objects.update_or_create(
                        registration=registration,
                        defaults=vehicle_data
                    )
                    
                    if created:
                        vehicles_created += 1
                    else:
                        vehicles_updated += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing row {idx+2}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {vehicles_created} vehicles and updated {vehicles_updated} vehicles'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading Excel file: {str(e)}'))
    


        
    def import_parts(self, file_path):
        """Import parts from Excel file's 'Vehicle Stock levels' tab."""
        try:
            self.stdout.write(f'Importing parts from {file_path} (Vehicle Stock levels tab)')
            
            # Read Excel file, specifically the 'Vehicle Stock levels' tab
            df = pd.read_excel(file_path, sheet_name='Vehicle Stock levels')
            
            # Skip the first row which contains headers
            df = df.iloc[1:]
            
            # Print column names for debugging
            self.stdout.write(f'Found columns: {df.columns.tolist()}')
            
            parts_created = 0
            parts_updated = 0
            
            # Process each row (vehicle)
            for idx, row in df.iterrows():
                try:
                    # Skip empty rows
                    if pd.isna(row.iloc[0]):
                        continue
                    
                    # Get vehicle details
                    vehicle_id = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""  # Motor Vehicle ID
                    registration = str(row.iloc[1]) if not pd.isna(row.iloc[1]) else ""  # Rego
                    model = str(row.iloc[2]) if not pd.isna(row.iloc[2]) else ""  # Model
                    year = self.safe_int(row.iloc[3], 0)  # Year
                    tyre_size = str(row.iloc[12]) if not pd.isna(row.iloc[12]) else ""  # Tyre size
                    rim_colour = str(row.iloc[13]) if not pd.isna(row.iloc[13]) else ""  # Rim colour
                    
                    # Process Fuel Filter
                    if not pd.isna(row.iloc[4]):  # Fuel filter part #
                        part_data = {
                            'part_number': str(row.iloc[4]),
                            'description': 'Fuel Filter',
                            'supplier': 'Unknown',
                            'current_stock': self.safe_int(row.iloc[5], 0),  # Fuel filter stock
                            'minimum_stock': 1,
                            'cost': None,
                        }
                        
                        part, created = VehiclePart.objects.update_or_create(
                            part_number=part_data['part_number'],
                            defaults=part_data
                        )
                        
                        if created:
                            parts_created += 1
                        else:
                            parts_updated += 1
                    
                    # Process Oil Filter
                    if not pd.isna(row.iloc[6]):  # Oil filter part #
                        part_data = {
                            'part_number': str(row.iloc[6]),
                            'description': 'Oil Filter',
                            'supplier': 'Unknown',
                            'current_stock': self.safe_int(row.iloc[7], 0),  # Oil filter stock
                            'minimum_stock': 1,
                            'cost': None,
                        }
                        
                        part, created = VehiclePart.objects.update_or_create(
                            part_number=part_data['part_number'],
                            defaults=part_data
                        )
                        
                        if created:
                            parts_created += 1
                        else:
                            parts_updated += 1
                    
                    # Process Air Filter
                    if not pd.isna(row.iloc[8]):  # Air filter part #
                        part_data = {
                            'part_number': str(row.iloc[8]),
                            'description': 'Air Filter',
                            'supplier': 'Unknown',
                            'current_stock': self.safe_int(row.iloc[9], 0),  # Air filter stock
                            'minimum_stock': 1,
                            'cost': None,
                        }
                        
                        part, created = VehiclePart.objects.update_or_create(
                            part_number=part_data['part_number'],
                            defaults=part_data
                        )
                        
                        if created:
                            parts_created += 1
                        else:
                            parts_updated += 1
                    
                    # Process Cabin Filter
                    if not pd.isna(row.iloc[10]):  # Cabin filter part #
                        part_data = {
                            'part_number': str(row.iloc[10]),
                            'description': 'Cabin Filter',
                            'supplier': 'Unknown',
                            'current_stock': self.safe_int(row.iloc[11], 0),  # Cabin filter stock
                            'minimum_stock': 1,
                            'cost': None,
                        }
                        
                        part, created = VehiclePart.objects.update_or_create(
                            part_number=part_data['part_number'],
                            defaults=part_data
                        )
                        
                        if created:
                            parts_created += 1
                        else:
                            parts_updated += 1
                    
                    # Try to find matching vehicle in database for compatibility
                    # First try by vehicle_id (Motor Vehicle ID)
                    matching_vehicles = Vehicle.objects.filter(name__iexact=vehicle_id)
                    
                    # If no match by name, try by registration
                    if not matching_vehicles.exists() and registration:
                        matching_vehicles = Vehicle.objects.filter(registration__iexact=registration)
                    
                    for vehicle in matching_vehicles:
                        # Update vehicle with additional info from parts sheet
                        if tyre_size or rim_colour:
                            # Add these as custom_fields or notes
                            notes = vehicle.notes if hasattr(vehicle, 'notes') else ""
                            if tyre_size:
                                notes += f"Tyre Size: {tyre_size}\n"
                            if rim_colour:
                                notes += f"Rim Colour: {rim_colour}\n"
                            
                            if hasattr(vehicle, 'notes'):
                                vehicle.notes = notes
                                vehicle.save()
                        
                        # Create the compatibility record for each part
                        for part_idx, part_type in [(4, 'Fuel Filter'), (6, 'Oil Filter'), (8, 'Air Filter'), (10, 'Cabin Filter')]:
                            if not pd.isna(row.iloc[part_idx]):
                                try:
                                    part = VehiclePart.objects.get(part_number=str(row.iloc[part_idx]))
                                    compatibility, created = VehiclePartCompatibility.objects.get_or_create(
                                        vehicle=vehicle,
                                        part=part
                                    )
                                    self.stdout.write(self.style.SUCCESS(
                                        f'Linked {part_type} {part.part_number} to vehicle {vehicle.registration}'
                                    ))
                                except VehiclePart.DoesNotExist:
                                    self.stdout.write(self.style.WARNING(
                                        f'Part {str(row.iloc[part_idx])} not found for {part_type}'
                                    ))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing row {idx+2}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported {parts_created} parts and updated {parts_updated} parts'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading Excel file: {str(e)}'))