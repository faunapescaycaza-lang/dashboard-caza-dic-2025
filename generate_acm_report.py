
import json
import pandas as pd

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

# Helper functions for per-ACM aggregation (will be called for each ACM)
def get_country_data_for_acm(df_acm):
    country_counts = df_acm['país'].value_counts().sort_index()
    country_table = "<table><tr><th>País</th><th>Cantidad de Permisos</th></tr>"
    for country, count in country_counts.items():
        country_table += f"<tr><td>{country}</td><td>{count}</td></tr>"
    country_table += "</table>"
    return country_counts.index.tolist(), country_counts.values.tolist(), country_table

def get_hunting_type_data_for_acm(df_acm):
    hunting_type_counts = df_acm['tipo_de_caza'].value_counts().sort_index()
    hunting_type_table = "<table><tr><th>Tipo de Caza</th><th>Cantidad de Permisos</th></tr>"
    for h_type, count in hunting_type_counts.items():
        hunting_type_table += f"<tr><td>{h_type}</td><td>{count}</td></tr>"
    hunting_type_table += "</table>"
    return hunting_type_counts.index.tolist(), hunting_type_counts.values.tolist(), hunting_type_table

def get_category_data_for_acm(df_acm):
    category_counts = df_acm['categoria'].value_counts().sort_index()
    category_table = "<table><tr><th>Categoría</th><th>Cantidad de Permisos</th></tr>"
    for category, count in category_counts.items():
        category_table += f"<tr><td>{category}</td><td>{count}</td></tr>"
    category_table += "</table>"
    return category_counts.index.tolist(), category_counts.values.tolist(), category_table

def get_permits_by_month_data_for_acm(df_acm):
    # Ensure date column is datetime objects, coercing errors
    df_acm['fecha_dt'] = pd.to_datetime(df_acm['fecha_de_inicio_del_uso_de_su_permiso'], errors='coerce')
    
    # Filter out invalid dates and 'No especificado' entries
    valid_dates_df = df_acm.dropna(subset=['fecha_dt']).copy() # Use .copy() to avoid SettingWithCopyWarning

    if valid_dates_df.empty:
        return [], [], "<table><tr><th>Mes</th><th>Cantidad</th></tr><tr><td colspan='2'>No hay datos de permisos por mes.</td></tr></table>"

    # Extract month and year, create a 'YYYY-MM' string for grouping
    valid_dates_df['month_year'] = valid_dates_df['fecha_dt'].dt.to_period('M')

    # Group by month_year and count permits
    monthly_counts = valid_dates_df['month_year'].value_counts().sort_index()

    # Convert Period objects to display format (e.g., 'Jan-2025')
    labels = [m.strftime('%b-%Y') for m in monthly_counts.index]
    data = monthly_counts.values.tolist()

    # Create HTML table
    monthly_table = "<table><tr><th>Mes</th><th>Cantidad de Permisos</th></tr>"
    for i, month_year in enumerate(labels):
        monthly_table += f"<tr><td>{month_year}</td><td>{data[i]}</td></tr>"
    monthly_table += "</table>"
    
    return labels, data, monthly_table

def get_responsable_guia_list_for_acm(df_acm):
    responsables = df_acm['responsable_guía_de_caza'].unique().tolist()
    responsables_html = "<ul>" + "".join([f"<li>{r}</li>" for r in responsables]) + "</ul>"
    return responsables_html

def get_hunter_names_list_for_acm(df_acm):
    hunters = df_acm['nombre_y_apellido'].unique().tolist()
    hunters_html = "<ul>" + "".join([f"<li>{h}</li>" for h in hunters]) + "</ul>"
    return hunters_html

def get_emails_list_for_acm(df_acm):
    emails = df_acm['email_address'].unique().tolist()
    emails_html = "<ul>" + "".join([f"<li>{e}</li>" for e in emails]) + "</ul>"
    return emails_html


def generate_html(unique_acms): # Only need unique_acms to build dropdown
    dropdown_options = ""
    for acm_name in unique_acms:
        dropdown_options += f'<option value="{acm_name}">{acm_name}</option>'

    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Visor de ACM</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <style>
        body {{ font-family: sans-serif; }}
        select {{ width: 100%; padding: 8px; margin-bottom: 20px; }}
        #acm-details-output {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; min-height: 200px; display: none; }}
        #acm-details-output h3 {{ margin-top: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px;}}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        button {{ padding: 10px; margin: 0 10px 20px 0; }}
        .chart-container {{ max-width: 600px; margin: 20px auto; }} /* Centralize and size charts */
        .chart-container canvas {{ width: 100% !important; height: auto !important; }} /* Make canvas responsive within container */
        #permitsByCountryChartContainer, #permitsByMonthChartContainer {{ max-width: 700px; height: 400px; }} /* Specific sizing for larger charts */
    </style>
</head>
<body>
    <h2>Visor de ACM</h2>
    <select id="acm-select" onchange="showAcmDetails()">
        <option value="">Selecciona un ACM</option>
        {dropdown_options}
    </select>

    <div id="acm-details-output">
        <h3 id="selectedAcmTitle"></h3>
        <p>Cantidad total de permisos: <strong id="totalPermitsValue"></strong></p>

        <h3>Permisos por País</h3>
        <div id="permitsByCountryChartContainer" class="chart-container"><canvas id="permitsByCountryChart"></canvas></div>
        <div id="permitsByCountryTableContainer"></div>

        <h3>Tipos de Caza</h3>
        <div id="huntingTypesChartContainer" class="chart-container"><canvas id="huntingTypesChart"></canvas></div>
        <div id="huntingTypesTableContainer"></div>

        <h3>Permisos por Categoría</h3>
        <div id="categoriesChartContainer" class="chart-container"><canvas id="categoriesChart"></canvas></div>
        <div id="categoriesTableContainer"></div>

        <h3>Permisos por Mes</h3>
        <div id="permitsByMonthChartContainer" class="chart-container"><canvas id="permitsByMonthChart"></canvas></div>
        <div id="permitsByMonthTableContainer"></div>

        <h3>Responsables Guía de Caza</h3>
        <div id="responsableGuiaListContainer"></div>

        <h3>Nombres de Cazadores</h3>
        <div id="hunterNamesListContainer"></div>

        <h3>Correos Electrónicos</h3>
        <div id="emailsListContainer"></div>
    </div>

    <script src="acm_aggregated_data.js"></script>
    <script>
        let permitsByCountryChart, huntingTypesChart, categoriesChart, permitsByMonthChart;
        Chart.register(ChartDataLabels);

        function resetCharts() {{
            if (permitsByCountryChart) permitsByCountryChart.destroy();
            if (huntingTypesChart) huntingTypesChart.destroy();
            if (categoriesChart) categoriesChart.destroy();
            if (permitsByMonthChart) permitsByMonthChart.destroy();
        }}

        function showAcmDetails() {{
            resetCharts();
            const select = document.getElementById('acm-select');
            const selectedAcmName = select.value;
            const acmDetailsOutput = document.getElementById('acm-details-output');
            
            if (!selectedAcmName) {{
                acmDetailsOutput.style.display = 'none';
                return;
            }}

            const acmAggregatedData = window.acmAggregatedData[selectedAcmName];

            if (acmAggregatedData) {{
                document.getElementById('selectedAcmTitle').textContent = 'Análisis para: ' + selectedAcmName;
                document.getElementById('totalPermitsValue').textContent = acmAggregatedData.total_permits;

                // Permits by Country
                document.getElementById('permitsByCountryTableContainer').innerHTML = acmAggregatedData.country_table;
                const ctxCountry = document.getElementById('permitsByCountryChart').getContext('2d');
                permitsByCountryChart = new Chart(ctxCountry, {{ type: 'bar', data: {{ labels: acmAggregatedData.country_labels, datasets: [{{ label: 'Cantidad de Permisos', data: acmAggregatedData.country_data, backgroundColor: 'rgba(54, 162, 235, 0.2)', borderColor: ['rgba(54, 162, 235, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});

                // Hunting Types
                document.getElementById('huntingTypesTableContainer').innerHTML = acmAggregatedData.hunting_type_table;
                const ctxHuntingType = document.getElementById('huntingTypesChart').getContext('2d');
                huntingTypesChart = new Chart(ctxHuntingType, {{ type: 'pie', data: {{ labels: acmAggregatedData.hunting_type_labels, datasets: [{{ data: acmAggregatedData.hunting_type_data, backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'], borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ formatter: (value, ctx) => {{ let sum = 0; let dataArr = ctx.chart.data.datasets[0].data; dataArr.map(data => {{ sum += data; }}); let percentage = (value*100 / sum).toFixed(2)+"%"; return percentage + ' (' + value + ')'; }}, color: '#000' }} }} }} }});

                // Categories
                document.getElementById('categoriesTableContainer').innerHTML = acmAggregatedData.category_table;
                const ctxCategories = document.getElementById('categoriesChart').getContext('2d');
                categoriesChart = new Chart(ctxCategories, {{ type: 'pie', data: {{ labels: acmAggregatedData.category_labels, datasets: [{{ data: acmAggregatedData.category_data, backgroundColor: ['rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(201, 203, 207, 0.2)'], borderColor: ['rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)', 'rgba(201, 203, 207, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ formatter: (value, ctx) => {{ let sum = 0; let dataArr = ctx.chart.data.datasets[0].data; dataArr.map(data => {{ sum += data; }}); let percentage = (value*100 / sum).toFixed(2)+"%"; return percentage + ' (' + value + ')'; }}, color: '#000' }} }} }} }});

                // Permits by Month
                document.getElementById('permitsByMonthTableContainer').innerHTML = acmAggregatedData.permits_by_month_table;
                const ctxPermitsByMonth = document.getElementById('permitsByMonthChart').getContext('2d');
                permitsByMonthChart = new Chart(ctxPermitsByMonth, {{ type: 'bar', data: {{ labels: acmAggregatedData.permits_by_month_labels, datasets: [{{ label: 'Cantidad de Permisos', data: acmAggregatedData.permits_by_month_data, backgroundColor: 'rgba(255, 205, 86, 0.2)', borderColor: ['rgba(255, 205, 86, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});

                // Lists of Responsables and Hunters
                document.getElementById('responsableGuiaListContainer').innerHTML = acmAggregatedData.responsable_guia_list;
                document.getElementById('hunterNamesListContainer').innerHTML = acmAggregatedData.hunter_names_list;
                document.getElementById('emailsListContainer').innerHTML = acmAggregatedData.emails_list;


                acmDetailsOutput.style.display = 'block';
            }} else {{
                acmDetailsOutput.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>
""".format(
        dropdown_options=dropdown_options
    )
    return html_template

if __name__ == '__main__':
    df_permits = load_data('permisos_caza_cleaned.json')
    
    # Get unique ACMs
    unique_acms = df_permits['acm_(área_de_caza_mayor)'].unique().tolist()
    
    # Prepare aggregated data for each ACM
    acm_aggregated_data = {}
    for acm_name in unique_acms:
        df_acm = df_permits[df_permits['acm_(área_de_caza_mayor)'] == acm_name].copy() # Use .copy() to avoid SettingWithCopyWarning
        
        country_labels, country_data, country_table = get_country_data_for_acm(df_acm)
        hunting_type_labels, hunting_type_data, hunting_type_table = get_hunting_type_data_for_acm(df_acm)
        category_labels, category_data, category_table = get_category_data_for_acm(df_acm)
        permits_by_month_labels, permits_by_month_data, permits_by_month_table = get_permits_by_month_data_for_acm(df_acm)
        responsable_guia_list = get_responsable_guia_list_for_acm(df_acm)
        hunter_names_list = get_hunter_names_list_for_acm(df_acm)
        emails_list = get_emails_list_for_acm(df_acm)

        acm_aggregated_data[acm_name] = {
            'total_permits': len(df_acm),
            'country_labels': country_labels,
            'country_data': country_data,
            'country_table': country_table,
            'hunting_type_labels': hunting_type_labels,
            'hunting_type_data': hunting_type_data,
            'hunting_type_table': hunting_type_table,
            'category_labels': category_labels,
            'category_data': category_data,
            'category_table': category_table,
            'permits_by_month_labels': permits_by_month_labels,
            'permits_by_month_data': permits_by_month_data,
            'permits_by_month_table': permits_by_month_table,
            'responsable_guia_list': responsable_guia_list,
            'hunter_names_list': hunter_names_list,
            'emails_list': emails_list
        }
    
    # Dump aggregated data to a JS file
    js_content = f"window.acmAggregatedData = {json.dumps(acm_aggregated_data, ensure_ascii=False, indent=4)};"
    with open('acm_aggregated_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    html_output = generate_html(unique_acms) # Pass unique_acms to generate dropdown
    
    with open('analisis_acm.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
