import pandas as pd
import json

def clean_permisos_caza_data(df):
    # Standardize column names (optional, but good practice)
    df.columns = df.columns.str.strip().str.replace(':', '').str.replace('-', '_').str.replace(' ', '_').str.lower()

    # Filter out specified names from 'nombre_y_apellido'
    names_to_remove = ["emanuel tula", "testeo", "karen thuman", "marco lopez", "prueba"]
    df = df[~df['nombre_y_apellido'].str.lower().isin(names_to_remove)]

    # Specific cleaning and unification for 'acm_(área_de_caza_mayor)'
    if 'acm_(área_de_caza_mayor)' in df.columns:
        # Create a temporary lowercase column for processing
        df['acm_temp'] = df['acm_(área_de_caza_mayor)'].astype(str).str.strip().str.lower()

        # Unifications - applied to acm_temp
        replace_map = {
            'algar': 'Algar S.A.',
            'dove outfitter srl': 'Dove Outfitters SRL',
            'dove outfitters srl': 'Dove Outfitters SRL', # Ensure both variations are covered
            'el rincon': 'El Rincón',
            'el rincón': 'El Rincón', # Ensure both variations are covered
            'establecimiento caleufu': 'Estancia Caleufu',
            'establecimiento: caleufu': 'Estancia Caleufu',
            'estancia caleufu': 'Estancia Caleufu',
            'estancia palitue': 'Palitue', # Keep 'Palitue' as target for simplicity
            'palitue': 'Palitue', # Ensure Palitue itself is handled if it appears in other cases
            'santa lucia': 'Santa Lucía',
            'santa lucía': 'Santa Lucía', # Ensure both variations are covered
        }
        df['acm_temp'] = df['acm_temp'].replace(replace_map)

        # Apply standardized names back to original column, capitalizing them for display
        df['acm_(área_de_caza_mayor)'] = df['acm_temp'].apply(lambda x: ' '.join([word.capitalize() for word in x.split(' ')]))
        
        # Removals - applied after unification
        acm_to_remove = ['Agar', 'Bariloche', 'Departamento Zapala', 'Varvarco', 'No especificado']
        # Convert acm_(área_de_caza_mayor) to lower for comparison with acm_to_remove
        df = df[~df['acm_(área_de_caza_mayor)'].str.lower().isin([s.lower() for s in acm_to_remove])]

        # Drop the temporary column
        df.drop(columns=['acm_temp'], inplace=True)
    
    # Fill missing values with 'No especificado'
    df.fillna('No especificado', inplace=True)

    # Clean and standardize text columns - EXCLUDE 'acm_(área_de_caza_mayor)' as it's handled above
    text_cols = [col for col in ['responsable_guía_de_caza', 'nombre_y_apellido', 
                 'ciudad,_estado_o_provincia', 'país', 'categoria'] if col in df.columns and col != 'acm_(área_de_caza_mayor)']
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.capitalize()

    # Process date columns
    date_cols = ['fecha', 'fecha_de_inicio_del_uso_de_su_permiso']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            df[col] = df[col].dt.strftime('%Y-%m-%d').fillna('No especificado')

    # Ensure ID columns are strings
    id_cols = ['id_único', 'ni_número_de_identificación', 'dni_o_pasaporte', 'id_de_envío']
    for col in id_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df

def process_permisos_caza_csv_to_json(csv_file_path, json_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path, encoding='utf-8')

    # Clean the DataFrame
    cleaned_df = clean_permisos_caza_data(df)

    # Convert DataFrame to a list of dictionaries (JSON format)
    data = cleaned_df.to_dict(orient='records')

    # Save the data to a JSON file with UTF-8 encoding
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Successfully processed and cleaned '{csv_file_path}' to '{json_file_path}'")

if __name__ == '__main__':
    csv_path = r'Datos_Crudos\permiso-de-caza-2025-2025-12-16.csv'
    json_path = 'permisos_caza_cleaned.json'
    process_permisos_caza_csv_to_json(csv_path, json_path)