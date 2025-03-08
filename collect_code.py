import os
import glob

def collect_code(directory_path):
    """Collect all important code files in the project"""
    code_contents = {}
    
    # Define file patterns to collect
    patterns = [
        '*/models.py',
        '*/views.py',
        '*/urls.py',
        '*/admin.py',
        '*/serializers.py',
        '*/management/commands/*.py'
    ]
    
    # Collect the files
    for pattern in patterns:
        full_pattern = os.path.join(directory_path, pattern)
        for file_path in glob.glob(full_pattern):
            try:
                with open(file_path, 'r') as file:
                    relative_path = os.path.relpath(file_path, directory_path)
                    code_contents[relative_path] = file.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return code_contents

def print_formatted_code(code_dict):
    """Print the code in a formatted way"""
    for file_path, content in code_dict.items():
        print(f"\n{'='*80}\n{file_path}\n{'='*80}\n")
        print(content)
        print("\n\n")

if __name__ == "__main__":
    # Replace with your project directory
    project_dir = "/Users/sebastianprendergast/Documents/mining-inventory-system/backend"
    
    code = collect_code(project_dir)
    print_formatted_code(code)