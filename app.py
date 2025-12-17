from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import json
import os

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Data Cleaning and Processing Functions ---

def clean_permisos_caza_data(df):
    # Standardize column names
    df.columns = df.columns.str.strip().str.replace(':', '').str.replace('-', '_').str.replace(' ', '_').str.lower()
    # Filter out test names
    names_to_remove = ["emanuel tula", "testeo", "karen thuman", "marco lopez", "prueba"]
    if 'nombre_y_apellido' in df.columns:
        df = df[~df['nombre_y_apellido'].str.lower().isin(names_to_remove)]
    # Clean and unify 'acm_(área_de_caza_mayor)'
    if 'acm_(área_de_caza_mayor)' in df.columns:
        df['acm_temp'] = df['acm_(área_de_caza_mayor)'].astype(str).str.strip().str.lower()
        replace_map = {
            'algar': 'Algar S.A.', 'dove outfitter srl': 'Dove Outfitters SRL', 'dove outfitters srl': 'Dove Outfitters SRL',
            'el rincon': 'El Rincón', 'el rincón': 'El Rincón', 'establecimiento caleufu': 'Estancia Caleufu',
            'establecimiento: caleufu': 'Estancia Caleufu', 'estancia caleufu': 'Estancia Caleufu',
            'estancia palitue': 'Palitue', 'palitue': 'Palitue', 'santa lucia': 'Santa Lucía', 'santa lucía': 'Santa Lucía',
        }
        df['acm_temp'] = df['acm_temp'].replace(replace_map)
        df['acm_(área_de_caza_mayor)'] = df['acm_temp'].apply(lambda x: ' '.join([word.capitalize() for word in x.split(' ')]))
        acm_to_remove = ['Agar', 'Bariloche', 'Departamento Zapala', 'Varvarco', 'No especificado']
        df = df[~df['acm_(área_de_caza_mayor)'].str.lower().isin([s.lower() for s in acm_to_remove])]
        df.drop(columns=['acm_temp'], inplace=True)
    df.fillna('No especificado', inplace=True)
    text_cols = [col for col in ['responsable_guía_de_caza', 'nombre_y_apellido', 'ciudad,_estado_o_provincia', 'país', 'categoria'] if col in df.columns and col != 'acm_(área_de_caza_mayor)']
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.capitalize()
    date_cols = ['fecha', 'fecha_de_inicio_del_uso_de_su_permiso']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            df[col] = df[col].dt.strftime('%Y-%m-%d').fillna('No especificado')
    id_cols = ['id_único', 'ni_número_de_identificación', 'dni_o_pasaporte', 'id_de_envío']
    for col in id_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df

def get_cleaned_permisos_caza_data(csv_file_path):
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    return clean_permisos_caza_data(df)

def get_acm_data(csv_file_path):
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    return df.to_dict(orient='records')

# --- Report Aggregation Functions (from generate_permisos_caza_report.py) ---
# Modified to return data dictionaries, not HTML.

def prepare_country_data(df, top_n=15):
    
    def unify_country(country_name):
        if pd.isna(country_name):
            return 'No especificado'
        
        # Lowercase and strip for consistent matching
        c = country_name.lower().strip()

        # Mapping variations to a standard name
        # USA variations
        if c in ['eeuu', 'estados unidos', 'estados unidos de america', 'u.s.a', 'usa', 'alaska', 
                 'atlanta', 'bend', 'california', 'colorado', 'fort lauderdale', 'gardenville', 
                 'georgia', 'houston', 'kansas', 'leesville', 'los gatos', 'milpitas', 
                 'montana', 'nevada', 'pensilvania', 'portland', 'sacramento', 
                 'south carolina', 'tecas', 'texas', 'willis', 'wisconsin']:
            return 'Eeuu'
        
        # Argentina variations
        if c in ['argentin', 'argentina', 'alicura', 'alumine', 'buenos aires', 'capital federal', 
                 'cinco saltos, rio negro', 'collon curá', 'general roca, rio negro', 'gral villegas', 
                 'j de los andes', 'junin de los andes', 'la plata buenos aires', 'neuquen', 
                 'neuquen, san martin de los andes', 'rio negro', 'rosario', 'san carlos de bariloche', 
                 'san isidro', 'san martin de los andes', 'san martín de los andes', 'santa fe', 'sma', 'toay',
                 'villa ballester buenos aires', 'villa maza', 'gral. villegas']:
            return 'Argentina'
            
        # Canada variations
        if c in ['canada', 'canadá']:
            return 'Canadá'

        # Mexico variations
        if c in ['mexico', 'ciudad de mexico', 'nuevo leon', 'nuevo león']:
            return 'México'

        # Brazil variations
        if c in ['brasil', 'sao paulo']:
            return 'Brasil'

        # Germany variations
        if c in ['alemania', 'bonn', 'hagen', 'siegen']:
            return 'Alemania'

        # Czech Republic variations
        if c in ['republic checa', 'republica checa']:
            return 'República Checa'

        if c == 'uk':
            return 'Reino Unido'

        # Return the original name, capitalized, if no mapping is found
        return country_name.capitalize()

    df['país_unificado'] = df['país'].apply(unify_country)
    country_counts = df['país_unificado'].value_counts()
    
    others_breakdown = {}
    if len(country_counts) > top_n:
        top_counts = country_counts.nlargest(top_n - 1).copy()
        others_series = country_counts.iloc[top_n - 1:]
        other_sum = others_series.sum()
        top_counts.loc['Otros'] = other_sum
        final_counts = top_counts
        others_breakdown = others_series.to_dict()
    else:
        final_counts = country_counts.copy()
    
    final_counts = final_counts.sort_values(ascending=False) 
    return {
        "labels": final_counts.index.tolist(), 
        "data": final_counts.values.tolist(),
        "others_breakdown": others_breakdown
    }

def prepare_hunting_type_data(df):
    # Ensure the column exists before processing
    if 'tipo_de_caza' not in df.columns:
        return {"labels": [], "data": []}
    hunting_type_counts = df['tipo_de_caza'].value_counts().sort_index()
    return {"labels": hunting_type_counts.index.tolist(), "data": hunting_type_counts.values.tolist()}

def prepare_acm_data(df):
    acm_counts = df['acm_(área_de_caza_mayor)'].value_counts().sort_index()
    return {"labels": acm_counts.index.tolist(), "data": acm_counts.values.tolist()}

def prepare_category_data(df):
    category_counts = df['categoria'].value_counts().sort_index()
    return {"labels": category_counts.index.tolist(), "data": category_counts.values.tolist()}

def prepare_permits_by_month_data(df):
    df['fecha_dt'] = pd.to_datetime(df['fecha_de_inicio_del_uso_de_su_permiso'], errors='coerce')
    valid_dates_df = df.dropna(subset=['fecha_dt']).copy()
    if valid_dates_df.empty:
        return {"labels": [], "data": []}
    valid_dates_df['month_year'] = valid_dates_df['fecha_dt'].dt.to_period('M')
    monthly_counts = valid_dates_df['month_year'].value_counts().sort_index()
    labels = [m.strftime('%b-%Y') for m in monthly_counts.index]
    data = monthly_counts.values.tolist()
    return {"labels": labels, "data": data}

# --- API Endpoints ---

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/Datos_Crudos/<path:filename>')
def serve_datos_crudos(filename):
    return send_from_directory('Datos_Crudos', filename)

@app.route('/api/reporte/permisos')
def permisos_report():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_name = 'permiso-de-caza-2025-2025-12-16.csv'
    csv_path = os.path.join(base_dir, 'Datos_Crudos', csv_file_name)

    try:
        # 1. Get cleaned data
        df = get_cleaned_permisos_caza_data(csv_path)
        
        # 2. Perform all aggregations
        country_chart_data = prepare_country_data(df)
        hunting_type_chart_data = prepare_hunting_type_data(df)
        acm_chart_data = prepare_acm_data(df)
        category_chart_data = prepare_category_data(df)
        permits_by_month_chart_data = prepare_permits_by_month_data(df)

        # 3. Assemble the final JSON response
        report_data = {
            "permits_data": df.to_dict(orient='records'), # Raw data for details table
            "total_permits": len(df),
            "charts": {
                "country": country_chart_data,
                "hunting_type": hunting_type_chart_data,
                "acm": acm_chart_data,
                "category": category_chart_data,
                "permits_by_month": permits_by_month_chart_data
            }
        }
        return jsonify(report_data)

    except FileNotFoundError:
        return jsonify({"error": f"CSV file not found at {csv_path}"}), 404
    except Exception as e:
        # It's good practice to log the error on the server
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred processing the data."}), 500

@app.route('/api/acm_data')

def acm_data():

    base_dir = os.path.dirname(os.path.abspath(__file__))

    csv_file_name = 'planilla-de-inscripción-de-establecimiento-particulares-2025-12-15.csv'

    csv_path = os.path.join(base_dir, 'Datos_Crudos', csv_file_name)

    try:

        data = get_acm_data(csv_path)

        return jsonify(data)

    except FileNotFoundError:

        return jsonify({"error": f"CSV file not found at {csv_path}"}), 404

    except Exception as e:

        return jsonify({"error": str(e)}), 500



# --- New endpoint for ACM report ---



def get_country_data_for_acm(df_acm):

    country_counts = df_acm['país'].value_counts().sort_index()

    return {"labels": country_counts.index.tolist(), "data": country_counts.values.tolist()}



def get_hunting_type_data_for_acm(df_acm):

    if 'tipo_de_caza' not in df_acm.columns: return {"labels": [], "data": []}

    hunting_type_counts = df_acm['tipo_de_caza'].value_counts().sort_index()

    return {"labels": hunting_type_counts.index.tolist(), "data": hunting_type_counts.values.tolist()}



def get_category_data_for_acm(df_acm):

    category_counts = df_acm['categoria'].value_counts().sort_index()

    return {"labels": category_counts.index.tolist(), "data": category_counts.values.tolist()}



def get_permits_by_month_data_for_acm(df_acm):

    df_acm['fecha_dt'] = pd.to_datetime(df_acm['fecha_de_inicio_del_uso_de_su_permiso'], errors='coerce')

    valid_dates_df = df_acm.dropna(subset=['fecha_dt']).copy()

    if valid_dates_df.empty: return {"labels": [], "data": []}

    valid_dates_df['month_year'] = valid_dates_df['fecha_dt'].dt.to_period('M')

    monthly_counts = valid_dates_df['month_year'].value_counts().sort_index()

    return {"labels": [m.strftime('%b-%Y') for m in monthly_counts.index], "data": monthly_counts.values.tolist()}



def get_responsable_guia_list_for_acm(df_acm):

    if 'responsable_guía_de_caza' not in df_acm.columns: return []

    return df_acm['responsable_guía_de_caza'].unique().tolist()



def get_hunter_names_list_for_acm(df_acm):

    if 'nombre_y_apellido' not in df_acm.columns: return []

    return df_acm['nombre_y_apellido'].unique().tolist()



def get_emails_list_for_acm(df_acm):

    # Assuming the column is 'email_address' as in the script, adjust if needed

    if 'email_address' not in df_acm.columns: return []

    return df_acm['email_address'].unique().tolist()



@app.route('/api/reporte/acm')



def acm_report():



    base_dir = os.path.dirname(os.path.abspath(__file__))



    csv_file_name = 'permiso-de-caza-2025-2025-12-16.csv'



    csv_path = os.path.join(base_dir, 'Datos_Crudos', csv_file_name)



    



    try:



        df_permits = get_cleaned_permisos_caza_data(csv_path)



        unique_acms = df_permits['acm_(área_de_caza_mayor)'].unique().tolist()



        



        acm_aggregated_data = {}



        for acm_name in unique_acms:



            df_acm = df_permits[df_permits['acm_(área_de_caza_mayor)'] == acm_name].copy()



            



            acm_aggregated_data[acm_name] = {



                'total_permits': len(df_acm),



                'charts': {



                    'country': get_country_data_for_acm(df_acm),



                    'hunting_type': get_hunting_type_data_for_acm(df_acm),



                    'category': get_category_data_for_acm(df_acm),



                    'permits_by_month': get_permits_by_month_data_for_acm(df_acm),



                },



                'lists': {



                    'responsable_guia': get_responsable_guia_list_for_acm(df_acm),



                    'hunter_names': get_hunter_names_list_for_acm(df_acm),



                    'emails': get_emails_list_for_acm(df_acm)



                }



            }



        



        final_report = {



            "unique_acms": unique_acms,



            "aggregated_data": acm_aggregated_data



        }



        



        return jsonify(final_report)







    except FileNotFoundError:



        return jsonify({"error": f"CSV file not found at {csv_path}"}), 404



    except Exception as e:



        print(f"An error occurred in /api/reporte/acm: {e}")



        return jsonify({"error": "An internal error occurred processing the ACM report."}), 500







# --- New functions and endpoint for Establecimientos report ---



def prepare_surface_data(df):



    df['Superficie'] = pd.to_numeric(df['Superficie del establecimiento en hectáreas'], errors='coerce').fillna(0)



    return {"labels": df['Nombre del establecimiento'].tolist(), "data": df['Superficie'].tolist()}







def prepare_department_data(df):



    def get_unified_department(department):



        if pd.isna(department): return "Desconocido"



        lower_dept = department.strip().lower()



        if "catan" in lower_dept: return "Catan Lil"



        if "collon" in lower_dept: return "Collon Cura"



        if "alumine" in lower_dept: return "Alumine"



        if "lacar" in lower_dept: return "Lacar"



        if "huiliches" in lower_dept: return "Huiliches"



        return department.strip()



    



    df['Departamento Unificado'] = df['Departamento donde se ubica el establecimiento'].apply(get_unified_department)



    department_counts = df['Departamento Unificado'].value_counts().sort_index()



    return {"labels": department_counts.index.tolist(), "data": department_counts.values.tolist()}







def prepare_breeding_site_data(df):



    df['Inscripto'] = df['Su establecimiento está inscripto y habilitado como criadero de fauna silvestre'].fillna("Desconocido")



    breeding_counts = df['Inscripto'].value_counts().sort_index()



    return {"labels": breeding_counts.index.tolist(), "data": breeding_counts.values.tolist()}







def prepare_species_data(df):



    col_name = 'Marque el casillero de la especies para las que solicita la práctica de caza. mayor.  Estas especies son exclusivamente para caza en establecimientos debidamente inscriptos como Criaderos de Fauna Silvestre y habilitados como Áreas de Caza Mayor.'



    if col_name not in df.columns: return {"labels": [], "data": []}



    species_counts = df[col_name].str.split(',').explode().str.strip().value_counts().sort_index()



    return {"labels": species_counts.index.tolist(), "data": species_counts.values.tolist()}







def prepare_deer_estimation_data(df):



    col_name = '¿Posee algún tipo de estimación numérica sobre la cantidad de ciervos que alberga su establecimiento?'



    if col_name not in df.columns: return {"labels": [], "data": []}



    df['Estimacion Ciervos'] = df[col_name].fillna("Desconocido")



    estimation_counts = df['Estimacion Ciervos'].value_counts().sort_index()



    return {"labels": estimation_counts.index.tolist(), "data": estimation_counts.values.tolist()}







def prepare_deer_trend_data(df):







    col_name = 'En los últimos cinco años, el número de ciervos en su campo'







    if col_name not in df.columns: return {"labels": [], "data": []}







    df['Tendencia Ciervos'] = df[col_name].fillna("Desconocido")







    trend_counts = df['Tendencia Ciervos'].value_counts().sort_index()







    return {"labels": trend_counts.index.tolist(), "data": trend_counts.values.tolist()}















def prepare_environment_data(df):







    col_name = 'En cuanto a los ambientes que ocupan de manera preferencial los ciervos, seleccione los ambientes donde se encuentran presentes.'







    if col_name not in df.columns: return {"labels": [], "data": []}







    environment_counts = df[col_name].str.split(',').explode().str.strip().value_counts().sort_index()







    return {"labels": environment_counts.index.tolist(), "data": environment_counts.values.tolist()}















def prepare_furtive_extraction_data(df):















    col_name = 'Podría estimar el número de ciervos que son extraídos de su establecimiento todos los años, por los cazadores furtivos?'















    if col_name not in df.columns:















        return {"chart_data": {"labels": [], "data": []}, "table_data": []}















    















    df['Extraccion Furtiva'] = df[col_name].fillna("No especificado")















    















    # For the chart















    extraction_counts = df['Extraccion Furtiva'].value_counts().sort_index()















    chart_data = {"labels": extraction_counts.index.tolist(), "data": extraction_counts.values.tolist()}















    















    # For the table















    # Group by the extraction count and aggregate establishment names into a list















    table_df = df.groupby('Extraccion Furtiva')['Nombre del establecimiento'].apply(list).reset_index()















    # Sort by the extraction count for a more logical table layout















    table_df = table_df.sort_values(by='Extraccion Furtiva')















    table_data = table_df.to_dict(orient='records')































    return {"chart_data": chart_data, "table_data": table_data}















def prepare_boar_estimation_data(df):







    col_name = 'Indique en forma aproximada, la cantidad de ejemplares de jabalí europeo que alberga su establecimiento.'







    if col_name not in df.columns: return {"labels": [], "data": []}







    







    def group_boars(value):







        if pd.isna(value): return "No especificado"







        try:







            num = int(str(value).split('-')[0].split('+')[0].replace('aprox','').replace(' ',''))







            if num <= 50: return "0-50"







            if num <= 100: return "51-100"







            if num <= 200: return "101-200"







            if num <= 500: return "201-500"







            return "501+"







        except (ValueError, IndexError):







            return "No especificado"







            







    df['Estimacion Jabali'] = df[col_name].apply(group_boars)







    boar_counts = df['Estimacion Jabali'].value_counts().sort_index()







    return {"labels": boar_counts.index.tolist(), "data": boar_counts.values.tolist()}















def prepare_pumas_data(df): # This is puma estimation







    col_name = 'Si es posible, indique en forma aproximada, la cantidad de pumas que alberga su establecimiento.'







    if col_name not in df.columns: return {"labels": [], "data": []}















    df['Estimacion Pumas Raw'] = df[col_name].astype(str).str.lower().str.strip()















    def categorize_pumas(value):







        if 'no' in value or 'desconocido' in value or 'no lo se' in value or 'no se' in value or 'muy poco' in value:







            return "No especificado/Desconocido"







        try:







            if '-' in value or '/' in value:







                parts = value.replace('aprox', '').replace(' ', '').split('-') if '-' in value else value.replace('aprox', '').replace(' ', '').split('/')







                nums = [int(s) for s in parts if s.strip().isdigit()]







                num = sum(nums) / len(nums) if nums else 0







            else:







                num_str = ''.join(filter(str.isdigit, value))







                num = int(num_str) if num_str else 0















            if num == 0: return "0"







            if 1 <= num <= 5: return "1-5"







            if 6 <= num <= 10: return "6-10"







            if 11 <= num <= 20: return "11-20"







            if num > 20: return "21+"







        except ValueError:







            return "No especificado/Desconocido"







        return "No especificado/Desconocido"







            







    df['Pumas Categorized'] = df['Estimacion Pumas Raw'].apply(categorize_pumas)







    puma_counts = df['Pumas Categorized'].value_counts().sort_index()







    return {"labels": puma_counts.index.tolist(), "data": puma_counts.values.tolist()}















def prepare_puma_trend_data(df):







    col_name = 'En los últimos tres años, la población de pumas'







    if col_name not in df.columns: return {"labels": [], "data": []}







    df['Tendencia Pumas'] = df[col_name].fillna("Desconocido").astype(str).str.strip()







    trend_counts = df['Tendencia Pumas'].value_counts().sort_index()







    return {"labels": trend_counts.index.tolist(), "data": trend_counts.values.tolist()}















def prepare_guanacos_data(df):







    col_name = 'En su establecimiento viven poblaciones de guanacos?'







    if col_name not in df.columns: return {"labels": [], "data": []}







    df['Poblacion Guanacos'] = df[col_name].fillna("Desconocido").astype(str).str.strip().str.capitalize()







    guanacos_counts = df['Poblacion Guanacos'].value_counts().sort_index()







    return {"labels": guanacos_counts.index.tolist(), "data": guanacos_counts.values.tolist()}















@app.route('/api/reporte/establecimientos')















def establecimientos_report():















    base_dir = os.path.dirname(os.path.abspath(__file__))















    csv_file_name = 'planilla-de-inscripción-de-establecimiento-particulares-2025-12-15.csv'















    csv_path = os.path.join(base_dir, 'Datos_Crudos', csv_file_name)















    try:















        df = pd.read_csv(csv_path, encoding='utf-8')















        df.fillna('No especificado', inplace=True)































        report_data = {















            "establecimientos_data": df.to_dict(orient='records'),















            "charts": {















                "surface": prepare_surface_data(df),















                "department": prepare_department_data(df),















                "breeding_site": prepare_breeding_site_data(df),















                "species": prepare_species_data(df),















                "deer_estimation": prepare_deer_estimation_data(df),















                "deer_trend": prepare_deer_trend_data(df),















                "environment": prepare_environment_data(df),















                "furtive_extraction": prepare_furtive_extraction_data(df),















                "boar_estimation": prepare_boar_estimation_data(df),















                "puma_estimation": prepare_pumas_data(df),















                "puma_trend": prepare_puma_trend_data(df),















                "guanacos": prepare_guanacos_data(df)















            }















        }















        return jsonify(report_data)















    except FileNotFoundError:















        return jsonify({"error": f"CSV file not found at {csv_path}"}), 404















    except Exception as e:















        print(f"An error occurred in /api/reporte/establecimientos: {e}")















        return jsonify({"error": "An internal error occurred processing the establecimientos report."}), 500































@app.route('/api/reporte/traslado-cabezas')















def traslado_cabezas_report():















    try:















        with open('traslado_cabezas_cleaned.json', 'r', encoding='utf-8') as f:















            data = json.load(f)















        return jsonify(data)















    except FileNotFoundError:















        return jsonify({"error": "Cleaned data for 'traslado de cabezas' not found."}), 404















    except Exception as e:















        print(f"An error occurred in /api/reporte/traslado-cabezas: {e}")















        return jsonify({"error": "An internal error occurred processing the data."}), 500







































if __name__ == '__main__':







    app.run(debug=True), 500











if __name__ == '__main__':



    app.run(debug=True)






