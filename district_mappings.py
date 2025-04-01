import json
import argparse

def replace_district_names(json_file_path, output_file_path):

    district_mappings = {
        "Anantpur": "Anantapur",
        "Araria": "Araria",
        "Aurangabad": "Aurangabad",
        "Balrampur": "Balrampur",
        "Bastar": "Bastar",
        "Begusarai": "Begusarai",
        "Belgaum": "Belagavi",
        "Bellary": "Ballari",
        "Bhagalpur": "Bhagalpur",
        "Bijapur": "Vijayapura",
        "Bilaspur": "Bilaspur",
        "Budaun": "Budaun",
        "Chamrajnagar": "Chamarajanagara",
        "Chandrapur": "Chandrapur",
        "Chittoor": "Chittoor",
        "Churu": "Churu",
        "DakshinDinajpur": "Dakshin Dinajpur",
        "DakshinKannada": "Dakshina Kannada",
        "Darbhanga": "Darbhanga",
        "Deoria": "Deoria",
        "Dharwad": "Dharwad",
        "Dhule": "Dhule",
        "EastChamparan": "East Champaran",
        "Etah": "Etah",
        "Gaya": "Gaya",
        "Ghazipur": "Ghazipur",
        "Gopalganj": "Gopalganj",
        "Gorakhpur": "Gorakhpur",
        "Gulbarga": "Kalaburagi",
        "Guntur": "Guntur",
        "Hamirpur": "Hamirpur",
        "Jahanabad": "Jehanabad",
        "Jalaun": "Jalaun",
        "Jalpaiguri": "Jalpaiguri",
        "Jamtara": "Jamtara",
        "Jamui": "Jamui",
        "Jashpur": "Jashpur",
        "Jhargram": "Jhargram",
        "JyotibaPhuleNagar": "Amroha",
        "Kabirdham": "Kabeerdham",
        "Karimnagar": "Karimnagar",
        "Kishanganj": "Kishanganj",
        "Kolkata": "Kolkata",
        "Korba": "Korba",
        "Krishna": "Krishna",
        "Lakhisarai": "Lakhisarai",
        "Madhepura": "Madhepura",
        "Malda": "Malda",
        "Muzaffarpur": "Muzaffarpur",
        "Muzzaffarnagar": "Muzaffarnagar",
        "Mysore": "Mysuru",
        "Nagaur": "Nagaur",
        "Nagpur": "Nagpur",
        "Nalgonda": "Nalgonda",
        "North24Parganas": "North 24 Parganas",
        "NorthSouthGoa": "North Goa",
        "PaschimMedinipur": "Paschim Medinipur",
        "Pune": "Pune",
        "Purnia": "Purnia",
        "Purulia": "Purulia",
        "Raichur": "Raichur",
        "Raigarh": "Raigarh",
        "Rajnandgaon": "Rajnandgaon",
        "Saharsa": "Saharsa",
        "Sahebganj": "Sahebganj",
        "Samastipur": "Samastipur",
        "Saran": "Saran",
        "Sarguja": "Surguja",
        "Shimoga": "Shivamogga",
        "Sindhudurga": "Sindhudurg",
        "Sitamarhi": "Sitamarhi",
        "Solapur": "Solapur",
        "Srikakulam": "Srikakulam",
        "Sukma": "Sukma",
        "Supaul": "Supaul",
        "TehriGarhwal": "Tehri Garhwal",
        "Uttarkashi": "Uttarkashi",
        "Vaishali": "Vaishali",
        "Varanasi": "Varanasi",
        "Vishakapattanam": "Visakhapatnam"
    }
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create a new dictionary with updated district names
        updated_data = {}
        
        # For each model in the data
        for model, districts in data.items():
            updated_data[model] = {}
            
            # For each district in the model
            for old_district, district_data in districts.items():
                # Replace district name if it exists in the mappings
                new_district = district_mappings.get(old_district, old_district)
                updated_data[model][new_district] = district_data
        
        # Write updated data to the output file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)
        
        print(f"District names updated successfully. Output written to {output_file_path}")
        return True
        
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found")
        return False
    except json.JSONDecodeError:
        print(f"Error: '{json_file_path}' contains invalid JSON format")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Command line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Replace district names in a JSON file using a mapping')
    parser.add_argument('input_json', help='Path to the input JSON file')
    parser.add_argument('output_json', help='Path to the output JSON file')
    
    args = parser.parse_args()
    
    # Call the function with the provided file paths
    replace_district_names(args.input_json, args.output_json)