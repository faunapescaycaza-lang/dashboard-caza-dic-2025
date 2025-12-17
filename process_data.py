
import pandas as pd
import json

def process_csv_to_json(csv_file_path, json_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path, encoding='utf-8') # Assuming UTF-8 encoding for CSV

    # Convert DataFrame to a list of dictionaries (JSON format)
    # This will create a list where each element is a dictionary representing a row
    data = df.to_dict(orient='records')

    # Save the data to a JSON file with UTF-8 encoding
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    csv_path = 'Datos_Crudos/planilla-de-inscripción-de-establecimiento-particulares-2025-12-15.csv'
    json_path = 'data_cleaned.json'
    process_csv_to_json(csv_path, json_path)
    print(f"Successfully processed '{csv_path}' to '{json_path}'")
