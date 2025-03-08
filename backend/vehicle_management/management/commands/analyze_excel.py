# vehicle_management/management/commands/analyze_excel.py
import pandas as pd
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Analyze Excel file structure'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Path to Excel file')

    def handle(self, *args, **options):
        file_path = options['file']
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Print the first 5 rows as a preview
            self.stdout.write("First 5 rows of data:")
            self.stdout.write(str(df.head()))
            
            # Print column names
            self.stdout.write("\nColumn Names:")
            for i, col in enumerate(df.columns):
                self.stdout.write(f"{i}: {col}")
                
            # Print data types
            self.stdout.write("\nData Types:")
            self.stdout.write(str(df.dtypes))
            
            # Look for specific columns
            self.stdout.write("\nSearching for insurance and expiry columns:")
            key_columns = ['Insurance Company', 'Rego Expiry', 'Insurance Expiry']
            for col in key_columns:
                if col in df.columns:
                    self.stdout.write(f"Found column: '{col}'")
                    # Show a sample of this column's data
                    self.stdout.write(f"Sample data: {df[col].head()}")
                else:
                    self.stdout.write(f"Column not found: '{col}'")
            
            # Try partial matches
            self.stdout.write("\nSearching for partial matches:")
            for search_term in ['Insurance', 'Expiry', 'Rego', 'Company']:
                matches = [col for col in df.columns if search_term in col]
                if matches:
                    self.stdout.write(f"Columns containing '{search_term}': {matches}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error analyzing file: {str(e)}"))