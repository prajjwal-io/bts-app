import json
import argparse

def extract_district_names_by_model(json_file_path):
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Dictionary to store models and their districts
        model_districts = {}
        
        # Extract model names (top-level keys in the JSON)
        models = data.keys()
        
        # For each model, extract the district names
        for model in models:
            district_names = list(data.get(model, {}).keys())
            # Sort districts alphabetically
            district_names.sort()
            model_districts[model] = district_names
        
        # Print the models and their district names
        for model, districts in model_districts.items():
            print(f"\nModel: {model}")
            print("District Names:")
            for district in districts:
                print(f"{district}")
        
        return model_districts
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error: '{json_file_path}' contains invalid JSON format")
        return {}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}

# Command line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract district names by model from a JSON file')
    parser.add_argument('json_file', help='Path to the JSON file')
    
    args = parser.parse_args()
    
    # Call the function with the provided file path
    extract_district_names_by_model(args.json_file)