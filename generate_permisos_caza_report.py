import json
import pandas as pd

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def prepare_country_data(df):
    country_counts = df['país'].value_counts().sort_index()
    country_table = "<table><tr><th>País</th><th>Cantidad de Permisos</th></tr>"
    for country, count in country_counts.items():
        country_table += f"<tr><td>{country}</td><td>{count}</td></tr>"
    country_table += "</table>"
    return country_counts.index.tolist(), country_counts.values.tolist(), country_table

def prepare_hunting_type_data(df):
    hunting_type_counts = df['tipo_de_caza'].value_counts().sort_index()
    hunting_type_table = "<table><tr><th>Tipo de Caza</th><th>Cantidad de Permisos</th></tr>"
    for h_type, count in hunting_type_counts.items():
        hunting_type_table += f"<tr><td>{h_type}</td><td>{count}</td></tr>"
    hunting_type_table += "</table>"
    return hunting_type_counts.index.tolist(), hunting_type_counts.values.tolist(), hunting_type_table

def prepare_acm_data(df):
    acm_counts = df['acm_(área_de_caza_mayor)'].value_counts().sort_index()
    acm_table = "<table><tr><th>ACM</th><th>Cantidad de Permisos</th></tr>"
    for acm, count in acm_counts.items():
        acm_table += f"<tr><td>{acm}</td><td>{count}</td></tr>"
    acm_table += "</table>"
    return acm_counts.index.tolist(), acm_counts.values.tolist(), acm_table

def prepare_category_data(df):
    category_counts = df['categoria'].value_counts().sort_index()
    category_table = "<table><tr><th>Categoría</th><th>Cantidad de Permisos</th></tr>"
    for category, count in category_counts.items():
        category_table += f"<tr><td>{category}</td><td>{count}</td></tr>"
    category_table += "</table>"
    return category_counts.index.tolist(), category_counts.values.tolist(), category_table

def prepare_permits_by_month_data(df):
    # Ensure date column is datetime objects, coercing errors
    df['fecha_dt'] = pd.to_datetime(df['fecha_de_inicio_del_uso_de_su_permiso'], errors='coerce')
    
    # Filter out invalid dates and 'No especificado' entries
    valid_dates_df = df.dropna(subset=['fecha_dt']).copy() # Use .copy() to avoid SettingWithCopyWarning

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


def generate_html(data_dict):
    dropdown_options = ""
    for permit_id in data_dict['id_único_list']:
        dropdown_options += f'<option value="{permit_id}">{permit_id}</option>'

    # Prepare JSON strings for JavaScript charts
    country_labels_json = json.dumps(data_dict['country_labels'], ensure_ascii=False)
    country_data_json = json.dumps(data_dict['country_data'], ensure_ascii=False)
    hunting_type_labels_json = json.dumps(data_dict['hunting_type_labels'], ensure_ascii=False)
    hunting_type_data_json = json.dumps(data_dict['hunting_type_data'], ensure_ascii=False)
    acm_labels_json = json.dumps(data_dict['acm_labels'], ensure_ascii=False)
    acm_data_json = json.dumps(data_dict['acm_data'], ensure_ascii=False)
    category_labels_json = json.dumps(data_dict['category_labels'], ensure_ascii=False)
    category_data_json = json.dumps(data_dict['category_data'], ensure_ascii=False)
    permits_by_month_labels_json = json.dumps(data_dict['permits_by_month_labels'], ensure_ascii=False)
    permits_by_month_data_json = json.dumps(data_dict['permits_by_month_data'], ensure_ascii=False)


    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Visor de Permisos de Caza</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <style>
        body {{ font-family: sans-serif; }}
        select {{ width: 100%; padding: 8px; margin-bottom: 20px; }}
        #details-container {{ border: 1px solid #ddd; padding: 10px; display: none; margin-bottom: 20px; }}
        #details-container table th {{ font-size: small; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px;}}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        button {{ padding: 10px; margin: 0 10px 20px 0; }}
        .chart-container {{ display: none; max-width: 500px; margin: auto; }}
        #countryChartContainer {{ max-width: 800px; }}
        #acmChartContainer {{ max-width: 1000px; height: 600px; }} /* Wider and taller for ACM chart */
    </style>
</head>
<body>
    <h2>Visor de Permisos de Caza</h2>
    <select id="permit-select" onchange="showDetails()">
        <option value="">Selecciona un Permiso</option>
        {dropdown_options}
    </select>
    <div id="details-container"></div>
    <button onclick="toggleChart('countryChartContainer')">Permisos por País</button>
    <button onclick="toggleChart('huntingTypeChartContainer')">Tipos de Caza</button>
    <button onclick="toggleChart('acmChartContainer')">Permisos por ACM</button>
    <button onclick="toggleChart('categoryChartContainer')">Permisos por Categoría</button>
    <button onclick="togglePermitsCount()">Cantidad Total de Permisos</button>
    <button onclick="toggleChart('permitsByMonthChartContainer')">Permisos por Mes</button>

    <div id="countryChartContainer" class="chart-container"><canvas id="countryChart"></canvas>{country_table}</div>
    <div id="huntingTypeChartContainer" class="chart-container"><canvas id="huntingTypeChart"></canvas>{hunting_type_table}</div>
    <div id="acmChartContainer" class="chart-container"><canvas id="acmChart"></canvas>{acm_table}</div>
    <div id="categoryChartContainer" class="chart-container"><canvas id="categoryChart"></canvas>{category_table}</div>
    <div id="permitsCountContainer" class="chart-container" style="display:none;"><p>Cantidad total de permisos: <strong>{total_permits}</strong></p></div>
    <div id="permitsByMonthChartContainer" class="chart-container" style="display:none;"><canvas id="permitsByMonthChart"></canvas>{permits_by_month_table}</div>

    <script src="permisos_caza_data.js"></script>
    <script>
        let countryChart, huntingTypeChart, acmChart, categoryChart, permitsByMonthChart;
        Chart.register(ChartDataLabels);
        
        function showDetails() {{
            const select = document.getElementById('permit-select');
            const selectedId = select.value;
            const detailsContainer = document.getElementById('details-container');
            if (!selectedId) {{ detailsContainer.style.display = 'none'; return; }}
            const selectedPermit = permisosCazaData.find(e => e['id_único'] === selectedId);
            if (selectedPermit) {{
                let table = '<table>';
                for (const key in selectedPermit) {{ table += '<tr><th>' + key + '</th><td>' + selectedPermit[key] + '</td></tr>'; }}
                table += '</table>';
                detailsContainer.innerHTML = table;
                detailsContainer.style.display = 'block';
            }}
        }}

        function togglePermitsCount() {{
            const permitsCountContainer = document.getElementById('permitsCountContainer');
            const isHidden = permitsCountContainer.style.display === 'none';
            document.querySelectorAll('.chart-container').forEach(container => {{ if (container.id !== 'permitsCountContainer') {{ container.style.display = 'none'; }} }});
            
            if (isHidden) {{
                permitsCountContainer.style.display = 'block';
            }} else {{
                permitsCountContainer.style.display = 'none';
            }}
        }}

        function toggleChart(chartId) {{
            const chartContainer = document.getElementById(chartId);
            const isHidden = chartContainer.style.display === 'none';
            document.querySelectorAll('.chart-container').forEach(container => {{ if (container.id !== chartId) {{ container.style.display = 'none'; }} }});
            
            if (isHidden) {{
                chartContainer.style.display = 'block';
                const ctx = document.getElementById(chartId.replace('Container', '')).getContext('2d');
                
                if (chartId === 'countryChartContainer' && !countryChart) {{
                    countryChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {country_labels_json}, datasets: [{{ label: 'Cantidad de Permisos', data: {country_data_json}, backgroundColor: 'rgba(54, 162, 235, 0.2)', borderColor: 'rgba(54, 162, 235, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'huntingTypeChartContainer' && !huntingTypeChart) {{
                    huntingTypeChart = new Chart(ctx, {{ type: 'pie', data: {{ labels: {hunting_type_labels_json}, datasets: [{{ data: {hunting_type_data_json}, backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'], borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ formatter: (value, ctx) => {{ let sum = 0; let dataArr = ctx.chart.data.datasets[0].data; dataArr.map(data => {{ sum += data; }}); let percentage = (value*100 / sum).toFixed(2)+"%"; return percentage + ' (' + value + ')'; }}, color: '#000' }} }} }} }});
                }} else if (chartId === 'acmChartContainer' && !acmChart) {{
                    acmChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {acm_labels_json}, datasets: [{{ label: 'Cantidad de Permisos', data: {acm_data_json}, backgroundColor: 'rgba(75, 192, 192, 0.2)', borderColor: 'rgba(75, 192, 192, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'categoryChartContainer' && !categoryChart) {{
                    categoryChart = new Chart(ctx, {{ type: 'pie', data: {{ labels: {category_labels_json}, datasets: [{{ data: {category_data_json}, backgroundColor: ['rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(201, 203, 207, 0.2)'], borderColor: ['rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)', 'rgba(201, 203, 207, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ formatter: (value, ctx) => {{ let sum = 0; let dataArr = ctx.chart.data.datasets[0].data; dataArr.map(data => {{ sum += data; }}); let percentage = (value*100 / sum).toFixed(2)+"%"; return percentage + ' (' + value + ')'; }}, color: '#000' }} }} }} }});
                }} else if (chartId === 'permitsByMonthChartContainer' && !permitsByMonthChart) {{
                    permitsByMonthChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {permits_by_month_labels_json}, datasets: [{{ label: 'Cantidad de Permisos', data: {permits_by_month_data_json}, backgroundColor: 'rgba(255, 205, 86, 0.2)', borderColor: 'rgba(255, 205, 86, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }}
            }} else {{
                chartContainer.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>
""".format(
        dropdown_options=dropdown_options,
        country_table=data_dict['country_table'],
        hunting_type_table=data_dict['hunting_type_table'],
        acm_table=data_dict['acm_table'],
        category_table=data_dict['category_table'],
        total_permits=data_dict['total_permits'],
        permits_by_month_table=data_dict['permits_by_month_table'],
        
        country_labels_json=country_labels_json,
        country_data_json=country_data_json,
        hunting_type_labels_json=hunting_type_labels_json,
        hunting_type_data_json=hunting_type_data_json,
        acm_labels_json=acm_labels_json,
        acm_data_json=acm_data_json,
        category_labels_json=category_labels_json,
        category_data_json=category_data_json,
        permits_by_month_labels_json=permits_by_month_labels_json,
        permits_by_month_data_json=permits_by_month_data_json
    )
    return html_template

if __name__ == '__main__':
    df = load_data('permisos_caza_cleaned.json')
    
    # Prepare data for permisos_caza_data.js
    permisos_caza_data_for_js = df.to_dict(orient='records')
    js_content = f"const permisosCazaData = {json.dumps(permisos_caza_data_for_js, ensure_ascii=False, indent=4)};"
    with open('permisos_caza_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    id_único_list = df['id_único'].tolist()
    total_permits = len(df) # Calculate total permits

    country_labels, country_data, country_table = prepare_country_data(df)
    hunting_type_labels, hunting_type_data, hunting_type_table = prepare_hunting_type_data(df)
    acm_labels, acm_data, acm_table = prepare_acm_data(df)
    category_labels, category_data, category_table = prepare_category_data(df)
    permits_by_month_labels, permits_by_month_data, permits_by_month_table = prepare_permits_by_month_data(df)

    html_data = {
        'id_único_list': id_único_list,
        'total_permits': total_permits, # Add total permits to html_data
        'country_labels': country_labels,
        'country_data': country_data,
        'country_table': country_table,
        'hunting_type_labels': hunting_type_labels,
        'hunting_type_data': hunting_type_data,
        'hunting_type_table': hunting_type_table,
        'acm_labels': acm_labels,
        'acm_data': acm_data,
        'acm_table': acm_table,
        'category_labels': category_labels,
        'category_data': category_data,
        'category_table': category_table,
        'permits_by_month_labels': permits_by_month_labels,
        'permits_by_month_data': permits_by_month_data,
        'permits_by_month_table': permits_by_month_table
    }
    
    html_output = generate_html(html_data)
    
    with open('analisis_permisos_caza.html', 'w', encoding='utf-8') as f:
        f.write(html_output)