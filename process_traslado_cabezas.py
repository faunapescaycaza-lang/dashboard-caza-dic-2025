import pandas as pd
import json
import re

def clean_traslado_cabezas_data(csv_file_path):
    """
    Reads and cleans the 'traslado de cabezas' data from a CSV file.

    Args:
        csv_file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A cleaned pandas DataFrame.
    """
    df = pd.read_csv(csv_file_path, encoding='utf-8')

    # 1. Drop rows with too many missing values (e.g., more than 50% missing)
    df.dropna(thresh=df.shape[1] * 0.5, inplace=True)

    # 2. Standardize column names
    df.columns = df.columns.str.strip().str.replace(':', '').str.replace('-', '_').str.replace(' ', '_').str.lower()

    # 3. Filter out test/unwanted names
    if 'nombre_y_apellido' in df.columns:
        names_to_remove = ["testeo", "marco lopez", "prueba", "emanuel tula", "ema", "tester", "1"]
        df = df[~df['nombre_y_apellido'].str.lower().isin(names_to_remove)]

    # 4. Drop rows that appear to be test data based on other columns
    # Example: if 'dni_o_pasaporte' contains 'test' or '123456'
    if 'dni_o_pasaporte' in df.columns:
        test_indicators = ['test', '123456', 'tester', '1']
        df = df[~df['dni_o_pasaporte'].str.lower().isin(test_indicators)]
        
    # 5. Drop fully empty rows if any slipped through
    df.dropna(how='all', inplace=True)

    # 6. Fill remaining NaN with "No especificado" for consistency
    df.fillna('No especificado', inplace=True)

    # 7. Unify species names
    species_col = 'especies_exóticas_posibles_de_ser_cazada_legalmente._(tilde_lo_que_corresponda).'
    if species_col in df.columns:
        df[species_col] = df[species_col].str.replace('Ciervo colarado', 'Ciervo colorado')

    # 8. Unify ACM names
    acm_col = 'acm_(área_de_caza_mayor)'
    if acm_col in df.columns:
        df[acm_col] = df[acm_col].str.replace(r'.*algar.*', 'Algar S.A.', regex=True, flags=re.IGNORECASE)

    # 9. Convert 'fecha' to datetime and create 'month_year' for monthly aggregation
    if 'fecha' in df.columns:
        df['fecha_dt'] = pd.to_datetime(df['fecha'], errors='coerce', dayfirst=True)
        df['month_year'] = df['fecha_dt'].dt.strftime('%Y-%m').fillna('No especificado')
    else:
        df['month_year'] = 'No especificado' # Add column if 'fecha' is missing

    return df

def main():
    """
    Main function to process the data and save it as JSON.
    """
    csv_file = 'Datos_Crudos/parte-1_-guia-de-traslado-de-cabezas-2025-12-17.csv'
    json_output_file = 'traslado_cabezas_cleaned.json'

    print(f"Reading and cleaning {csv_file}...")
    cleaned_df = clean_traslado_cabezas_data(csv_file)
    
    print(f"Saving cleaned data to {json_output_file}...")
    # Convert dataframe to a list of dictionaries for JSON compatibility
    cleaned_df.to_json(json_output_file, orient='records', indent=4, force_ascii=False)
    
    print("Data processing complete.")
    print(f"Original rows: {len(pd.read_csv(csv_file, encoding='utf-8'))}, Cleaned rows: {len(cleaned_df)}")

if __name__ == '__main__':
    main()
