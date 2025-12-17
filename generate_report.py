import json
import pandas as pd

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def prepare_surface_data(df):
    df['Superficie'] = pd.to_numeric(df['Superficie del establecimiento en hectáreas'], errors='coerce').fillna(0)
    return df['Nombre del establecimiento'].tolist(), df['Superficie'].tolist()

def prepare_department_data(df):
    def get_unified_department(department):
        if pd.isna(department):
            return "Desconocido"
        lower_dept = department.strip().lower()
        if "catan" in lower_dept: return "Catan Lil"
        if "collon" in lower_dept: return "Collon Cura"
        if "alumine" in lower_dept: return "Alumine"
        if "lacar" in lower_dept: return "Lacar"
        if "huiliches" in lower_dept: return "Huiliches"
        return department.strip()
    
    df['Departamento Unificado'] = df['Departamento donde se ubica el establecimiento'].apply(get_unified_department)
    department_counts = df['Departamento Unificado'].value_counts().sort_index()
    
    department_table = "<table><tr><th>Departamento</th><th>Cantidad</th><th>Establecimientos</th></tr>"
    for dept, count in department_counts.items():
        establishments = "<br>".join(df[df['Departamento Unificado'] == dept]['Nombre del establecimiento'].tolist())
        department_table += f"<tr><td>{dept}</td><td>{count}</td><td>{establishments}</td></tr>"
    department_table += "</table>"
    
    return department_counts.index.tolist(), department_counts.values.tolist(), department_table

def prepare_breeding_site_data(df):
    df['Inscripto'] = df['Su establecimiento está inscripto y habilitado como criadero de fauna silvestre'].fillna("Desconocido")
    breeding_counts = df['Inscripto'].value_counts().sort_index()

    breeding_table = "<table><tr><th>Inscripto como Criadero</th><th>Cantidad</th><th>Establecimientos</th></tr>"
    for status, count in breeding_counts.items():
        establishments = "<br>".join(df[df['Inscripto'] == status]['Nombre del establecimiento'].tolist())
        breeding_table += f"<tr><td>{status}</td><td>{count}</td><td>{establishments}</td></tr>"
    breeding_table += "</table>"
    
    return breeding_counts.index.tolist(), breeding_counts.values.tolist(), breeding_table

def prepare_species_data(df):
    species_map = { "antílope": "Antílope de la India", "antílope de la india": "Antílope de la India", "jabalí": "Jabalí Europeo", "jabalí europeo": "Jabalí Europeo" }
    def get_unified_species(species):
        if pd.isna(species): return "Desconocido"
        lower_species = species.strip().lower()
        return species_map.get(lower_species, species.strip())

    species_counts = df['Marque el casillero de la especies para las que solicita la práctica de caza. mayor.  Estas especies son exclusivamente para caza en establecimientos debidamente inscriptos como Criaderos de Fauna Silvestre y habilitados como Áreas de Caza Mayor.'].str.split(',').explode().apply(get_unified_species).value_counts().sort_index()
    
    species_table = "<table><tr><th>Especie</th><th>Cantidad de Establecimientos</th></tr>"
    for species, count in species_counts.items():
        species_table += f"<tr><td>{species}</td><td>{count}</td></tr>"
    species_table += "</table>"

    return species_counts.index.tolist(), species_counts.values.tolist(), species_table

def prepare_deer_estimation_data(df):
    df['Estimacion Ciervos'] = df['¿Posee algún tipo de estimación numérica sobre la cantidad de ciervos que alberga su establecimiento?'].fillna("Desconocido")
    estimation_counts = df['Estimacion Ciervos'].value_counts().sort_index()

    estimation_table = "<table><tr><th>Rango de Estimación</th><th>Cantidad de Establecimientos</th></tr>"
    for range_val, count in estimation_counts.items():
        estimation_table += f"<tr><td>{range_val}</td><td>{count}</td></tr>"
    estimation_table += "</table>"

    return estimation_counts.index.tolist(), estimation_counts.values.tolist(), estimation_table

def prepare_deer_trend_data(df):
    df['Tendencia Ciervos'] = df['En los últimos cinco años, el número de ciervos en su campo'].fillna("Desconocido")
    trend_counts = df['Tendencia Ciervos'].value_counts().sort_index()

    trend_table = "<table><tr><th>Tendencia Poblacional</th><th>Cantidad de Establecimientos</th></tr>"
    for trend, count in trend_counts.items():
        trend_table += f"<tr><td>{trend}</td><td>{count}</td></tr>"
    trend_table += "</table>"

    return trend_counts.index.tolist(), trend_counts.values.tolist(), trend_table

def prepare_environment_data(df):
    environment_counts = df['En cuanto a los ambientes que ocupan de manera preferencial los ciervos, seleccione los ambientes donde se encuentran presentes.'].str.split(',').explode().str.strip().value_counts().sort_index()
    
    environment_table = "<table><tr><th>Ambiente</th><th>Cantidad de Establecimientos</th></tr>"
    for env, count in environment_counts.items():
        environment_table += f"<tr><td>{env}</td><td>{count}</td></tr>"
    environment_table += "</table>"
    
    return environment_counts.index.tolist(), environment_counts.values.tolist(), environment_table

def prepare_furtive_extraction_data(df):
    df['Extraccion Furtiva'] = df['Podría estimar el número de ciervos que son extraídos de su establecimiento todos los años, por los cazadores furtivos?'].fillna("No especificado")
    extraction_counts = df['Extraccion Furtiva'].value_counts().sort_index()

    extraction_table = "<table><tr><th>Cantidad Estimada de Ciervos Extraídos</th><th>Establecimientos</th></tr>"
    for extraction, count in extraction_counts.items():
        establishments = "<br>".join(df[df['Extraccion Furtiva'] == extraction]['Nombre del establecimiento'].tolist())
        extraction_table += f"<tr><td>{extraction}</td><td>{count}</td><td>{establishments}</td></tr>"
    extraction_table += "</table>"

    return extraction_counts.index.tolist(), extraction_counts.values.tolist(), extraction_table

def prepare_boar_estimation_data(df):
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
            
    df['Estimacion Jabali'] = df['Indique en forma aproximada, la cantidad de ejemplares de jabalí europeo que alberga su establecimiento.'].apply(group_boars)
    boar_counts = df['Estimacion Jabali'].value_counts().sort_index()
    return boar_counts.index.tolist(), boar_counts.values.tolist()

def prepare_pumas_data(df):
    # Ensure the column is treated as string for processing
    df['Estimacion Pumas Raw'] = df['Si es posible, indique en forma aproximada, la cantidad de pumas que alberga su establecimiento.'].astype(str).str.lower().str.strip()

    def categorize_pumas(value):
        if 'no' in value or 'desconocido' in value or 'no lo se' in value or 'no se' in value or 'muy poco' in value:
            return "No especificado/Desconocido"
        
        try:
            # Handle ranges like "5-10" or "8-10" or "5/6"
            if '-' in value or '/' in value:
                parts = value.replace('aprox', '').replace(' ', '').split('-') if '-' in value else value.replace('aprox', '').replace(' ', '').split('/')
                nums = [int(s) for s in parts if s.strip().isdigit()]
                if nums:
                    num = sum(nums) / len(nums) # Take average for categorization
                else:
                    return "No especificado/Desconocido"
            else:
                # Extract numbers from strings like "20 pumas"
                num_str = ''.join(filter(str.isdigit, value))
                if num_str:
                    num = int(num_str)
                else:
                    return "No especificado/Desconocido"

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

    pumas_table = "<table><tr><th>Rango de Estimación</th><th>Cantidad de Establecimientos</th></tr>"
    for range_val, count in puma_counts.items():
        pumas_table += f"<tr><td>{range_val}</td><td>{count}</td></tr>"
    pumas_table += "</table>"
    
    return puma_counts.index.tolist(), puma_counts.values.tolist(), pumas_table

def prepare_puma_trend_data(df):
    df['Tendencia Pumas'] = df['En los últimos tres años, la población de pumas'].fillna("Desconocido").astype(str).str.strip()
    trend_counts = df['Tendencia Pumas'].value_counts().sort_index()

    trend_table = "<table><tr><th>Tendencia Poblacional</th><th>Cantidad de Establecimientos</th></tr>"
    for trend, count in trend_counts.items():
        trend_table += f"<tr><td>{trend}</td><td>{count}</td></tr>"
    trend_table += "</table>"
    
    return trend_counts.index.tolist(), trend_counts.values.tolist(), trend_table

def prepare_guanacos_data(df):
    df['Poblacion Guanacos'] = df['En su establecimiento viven poblaciones de guanacos?'].fillna("Desconocido").astype(str).str.strip().str.capitalize()
    guanacos_counts = df['Poblacion Guanacos'].value_counts().sort_index()

    guanacos_table = "<table><tr><th>¿Población de Guanacos?</th><th>Cantidad de Establecimientos</th></tr>"
    for status, count in guanacos_counts.items():
        guanacos_table += f"<tr><td>{status}</td><td>{count}</td></tr>"
    guanacos_table += "</table>"
    
    return guanacos_counts.index.tolist(), guanacos_counts.values.tolist(), guanacos_table


def generate_html(data_dict):
    dropdown_options = ""
    for name in data_dict['nombre_establecimiento']:
        words = name.split(' ')
        display_name = ' '.join([word.capitalize() for i, word in enumerate(words) if i < 2] + words[2:])
        dropdown_options += f'<option value="{name}">{display_name}</option>'

    # Prepare JSON strings for JavaScript charts
    surface_labels_json = json.dumps(data_dict['surface_labels'], ensure_ascii=False)
    surface_data_json = json.dumps(data_dict['surface_data'], ensure_ascii=False)
    department_labels_json = json.dumps(data_dict['department_labels'], ensure_ascii=False)
    department_data_json = json.dumps(data_dict['department_data'], ensure_ascii=False)
    breeding_site_labels_json = json.dumps(data_dict['breeding_site_labels'], ensure_ascii=False)
    breeding_site_data_json = json.dumps(data_dict['breeding_site_data'], ensure_ascii=False)
    species_labels_json = json.dumps(data_dict['species_labels'], ensure_ascii=False)
    species_data_json = json.dumps(data_dict['species_data'], ensure_ascii=False)
    deer_estimation_labels_json = json.dumps(data_dict['deer_estimation_labels'], ensure_ascii=False)
    deer_estimation_data_json = json.dumps(data_dict['deer_estimation_data'], ensure_ascii=False)
    deer_trend_labels_json = json.dumps(data_dict['deer_trend_labels'], ensure_ascii=False)
    deer_trend_data_json = json.dumps(data_dict['deer_trend_data'], ensure_ascii=False)
    environment_labels_json = json.dumps(data_dict['environment_labels'], ensure_ascii=False)
    environment_data_json = json.dumps(data_dict['environment_data'], ensure_ascii=False)
    furtive_extraction_labels_json = json.dumps(data_dict['furtive_extraction_labels'], ensure_ascii=False)
    furtive_extraction_data_json = json.dumps(data_dict['furtive_extraction_data'], ensure_ascii=False)
    boar_estimation_labels_json = json.dumps(data_dict['boar_estimation_labels'], ensure_ascii=False)
    boar_estimation_data_json = json.dumps(data_dict['boar_estimation_data'], ensure_ascii=False)
    puma_estimation_labels_json = json.dumps(data_dict['puma_estimation_labels'], ensure_ascii=False)
    puma_estimation_data_json = json.dumps(data_dict['puma_estimation_data'], ensure_ascii=False)
    puma_trend_labels_json = json.dumps(data_dict['puma_trend_labels'], ensure_ascii=False)
    puma_trend_data_json = json.dumps(data_dict['puma_trend_data'], ensure_ascii=False)
    guanacos_labels_json = json.dumps(data_dict['guanacos_labels'], ensure_ascii=False)
    guanacos_data_json = json.dumps(data_dict['guanacos_data'], ensure_ascii=False)

    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Visor de Establecimientos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <style>
        body {{ font-family: sans-serif; }}
        select {{ width: 100%; padding: 8px; margin-bottom: 20px; }}
        #details-container {{ border: 1px solid #ddd; padding: 10px; display: none; margin-bottom: 20px; }}
        #details-container table th {{ font-size: small; }} /* Added: Reduce font size for first column in details table */
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px;}}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        button {{ padding: 10px; margin: 0 10px 20px 0; }}
        .chart-container {{ display: none; max-width: 500px; margin: auto; }}
        #surfaceChartContainer {{ max-width: 800px; }}
    </style>
</head>
<body>
    <h2>Visor de Establecimientos</h2>
    <select id="establishment-select" onchange="showDetails()">
        <option value="">Selecciona un establecimiento</option>
        {dropdown_options}
    </select>
    <div id="details-container"></div>
    <button onclick="toggleChart('surfaceChartContainer')">Superficie por establecimiento de Caza</button>
    <button onclick="toggleChart('departmentChartContainer')">Establecimientos por Departamento</button>
    <button onclick="toggleChart('breedingSiteChartContainer')">Establecimientos por tipo de Criadero</button>
    <button onclick="toggleChart('speciesChartContainer')">Especies para la práctica de caza</button>
    <button onclick="toggleChart('deerEstimationChartContainer')">Estimación de Ciervos</button>
    <button onclick="toggleChart('deerTrendChartContainer')">Tendencia Población de Ciervos</button>
    <button onclick="toggleChart('environmentChartContainer')">Ambientes Preferenciales de Ciervos</button>
    <button onclick="toggleChart('furtiveExtractionChartContainer')">Ciervos Extraídos por Furtivos</button>
    <button onclick="toggleChart('boarEstimationChartContainer')">Estimación de Jabalíes</button>
    <button onclick="toggleChart('pumaEstimationChartContainer')">Estimación de Pumas</button>
    <button onclick="toggleChart('pumaTrendChartContainer')">Tendencia Poblacional de Pumas</button>
    <button onclick="toggleChart('guanacosChartContainer')">Población de Guanacos</button>

    <div id="surfaceChartContainer" class="chart-container"><canvas id="surfaceChart"></canvas></div>
    <div id="departmentChartContainer" class="chart-container"><canvas id="departmentChart"></canvas>{department_table}</div>
    <div id="breedingSiteChartContainer" class="chart-container"><canvas id="breedingSiteChart"></canvas>{breeding_site_table}</div>
    <div id="speciesChartContainer" class="chart-container"><canvas id="speciesChart"></canvas>{species_table}</div>
    <div id="deerEstimationChartContainer" class="chart-container"><canvas id="deerEstimationChart"></canvas>{deer_estimation_table}</div>
    <div id="deerTrendChartContainer" class="chart-container"><canvas id="deerTrendChart"></canvas>{deer_trend_table}</div>
    <div id="environmentChartContainer" class="chart-container"><canvas id="environmentChart"></canvas>{environment_table}</div>
    <div id="furtiveExtractionChartContainer" class="chart-container"><canvas id="furtiveExtractionChart"></canvas>{furtive_extraction_table}</div>
    <div id="boarEstimationChartContainer" class="chart-container"><canvas id="boarEstimationChart"></canvas></div>
    <div id="pumaEstimationChartContainer" class="chart-container"><canvas id="pumaEstimationChart"></canvas>{puma_estimation_table}</div>
    <div id="pumaTrendChartContainer" class="chart-container"><canvas id="pumaTrendChart"></canvas>{puma_trend_table}</div>
    <div id="guanacosChartContainer" class="chart-container"><canvas id="guanacosChart"></canvas>{guanacos_table}</div>

    <script src="data.js"></script>
    <script>
        // Chart.js and other JS logic will be here
        let surfaceChart, departmentChart, breedingSiteChart, speciesChart, deerEstimationChart, deerTrendChart, environmentChart, furtiveExtractionChart, boarEstimationChart, pumaEstimationChart, pumaTrendChart, guanacosChart;
        Chart.register(ChartDataLabels);
        
        function showDetails() {{
            const select = document.getElementById('establishment-select');
            const selectedName = select.value;
            const detailsContainer = document.getElementById('details-container');
            if (!selectedName) {{ detailsContainer.style.display = 'none'; return; }}
            const selectedEstablishment = establishmentData.find(e => e['Nombre del establecimiento'] === selectedName);
            if (selectedEstablishment) {{
                    let table = '<table>';
                for (const key in selectedEstablishment) {{ table += '<tr><th>' + key + '</th><td>' + selectedEstablishment[key] + '</td></tr>'; }}
                table += '</table>';
                detailsContainer.innerHTML = table;
                detailsContainer.style.display = 'block';
            }}
        }}

        function toggleChart(chartId) {{
            const chartContainer = document.getElementById(chartId);
            const isHidden = chartContainer.style.display === 'none';
            document.querySelectorAll('.chart-container').forEach(container => {{ if (container.id !== chartId) {{ container.style.display = 'none'; }} }});
            
            if (isHidden) {{
                chartContainer.style.display = 'block';
                const ctx = document.getElementById(chartId.replace('Container', '')).getContext('2d');
                
                if (chartId === 'surfaceChartContainer' && !surfaceChart) {{
                    surfaceChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {surface_labels_json}, datasets: [{{ label: 'Superficie (hectáreas)', data: {surface_data_json}, backgroundColor: 'rgba(54, 162, 235, 0.2)', borderColor: 'rgba(54, 162, 235, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true }} }} }} }});
                }} else if (chartId === 'departmentChartContainer' && !departmentChart) {{
                    departmentChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {department_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {department_data_json}, backgroundColor: 'rgba(255, 99, 132, 0.2)', borderColor: 'rgba(255, 99, 132, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'breedingSiteChartContainer' && !breedingSiteChart) {{
                    breedingSiteChart = new Chart(ctx, {{ type: 'pie', data: {{ labels: {breeding_site_labels_json}, datasets: [{{ data: {breeding_site_data_json}, backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(255, 206, 86, 0.2)'], borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 206, 86, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ formatter: (value, ctx) => {{ let sum = 0; let dataArr = ctx.chart.data.datasets[0].data; dataArr.map(data => {{ sum += data; }}); let percentage = (value*100 / sum).toFixed(2)+"%"; return percentage + ' (' + value + ')'; }}, color: '#000' }} }} }} }});
                }} else if (chartId === 'speciesChartContainer' && !speciesChart) {{
                    speciesChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {species_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {species_data_json}, backgroundColor: 'rgba(153, 102, 255, 0.2)', borderColor: 'rgba(153, 102, 255, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'deerEstimationChartContainer' && !deerEstimationChart) {{
                    deerEstimationChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {deer_estimation_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {deer_estimation_data_json}, backgroundColor: 'rgba(255, 159, 64, 0.2)', borderColor: 'rgba(255, 159, 64, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'deerTrendChartContainer' && !deerTrendChart) {{
                    deerTrendChart = new Chart(ctx, {{ type: 'pie', data: {{ labels: {deer_trend_labels_json}, datasets: [{{ data: {deer_trend_data_json}, backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'], borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ formatter: (value, ctx) => {{ let sum = 0; let dataArr = ctx.chart.data.datasets[0].data; dataArr.map(data => {{ sum += data; }}); let percentage = (value*100 / sum).toFixed(2)+"%"; return percentage + ' (' + value + ')'; }}, color: '#000' }} }} }} }});
                }} else if (chartId === 'environmentChartContainer' && !environmentChart) {{
                    environmentChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {environment_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {environment_data_json}, backgroundColor: 'rgba(75, 192, 192, 0.2)', borderColor: 'rgba(75, 192, 192, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'furtiveExtractionChartContainer' && !furtiveExtractionChart) {{
                    furtiveExtractionChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {furtive_extraction_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {furtive_extraction_data_json}, backgroundColor: 'rgba(255, 99, 71, 0.2)', borderColor: 'rgba(255, 99, 71, 1)', borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'boarEstimationChartContainer' && !boarEstimationChart) {{
                    boarEstimationChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {boar_estimation_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {boar_estimation_data_json}, backgroundColor: ['rgba(255, 159, 64, 0.2)'], borderColor: ['rgba(255, 159, 64, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'pumaEstimationChartContainer' && !pumaEstimationChart) {{
                    pumaEstimationChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {puma_estimation_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {puma_estimation_data_json}, backgroundColor: ['rgba(102, 102, 153, 0.2)'], borderColor: ['rgba(102, 102, 153, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
                }} else if (chartId === 'pumaTrendChartContainer' && !pumaTrendChart) {{
                    pumaTrendChart = new Chart(ctx, {{ type: 'pie', data: {{ labels: {puma_trend_labels_json}, datasets: [{{ data: {puma_trend_data_json}, backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)'], borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ formatter: (value, ctx) => {{ let sum = 0; let dataArr = ctx.chart.data.datasets[0].data; dataArr.map(data => {{ sum += data; }}); let percentage = (value*100 / sum).toFixed(2)+"%"; return percentage + ' (' + value + ')'; }}, color: '#000' }} }} }} }});
                }} else if (chartId === 'guanacosChartContainer' && !guanacosChart) {{
                    guanacosChart = new Chart(ctx, {{ type: 'bar', data: {{ labels: {guanacos_labels_json}, datasets: [{{ label: 'Nro de Establecimientos', data: {guanacos_data_json}, backgroundColor: ['rgba(255, 159, 64, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(201, 203, 207, 0.2)'], borderColor: ['rgba(255, 159, 64, 1)', 'rgba(75, 192, 192, 1)', 'rgba(201, 203, 207, 1)'], borderWidth: 1 }}] }}, options: {{ plugins: {{ datalabels: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }} }} }});
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
        department_table=data_dict['department_table'],
        breeding_site_table=data_dict['breeding_site_table'],
        species_table=data_dict['species_table'],
        deer_estimation_table=data_dict['deer_estimation_table'],
        deer_trend_table=data_dict['deer_trend_table'],
        environment_table=data_dict['environment_table'],
        furtive_extraction_table=data_dict['furtive_extraction_table'],
        puma_estimation_table=data_dict['puma_estimation_table'],
        puma_trend_table=data_dict['puma_trend_table'],
        guanacos_table=data_dict['guanacos_table'],
        
        surface_labels_json=surface_labels_json,
        surface_data_json=surface_data_json,
        department_labels_json=department_labels_json,
        department_data_json=department_data_json,
        breeding_site_labels_json=breeding_site_labels_json,
        breeding_site_data_json=breeding_site_data_json,
        species_labels_json=species_labels_json,
        species_data_json=species_data_json,
        deer_estimation_labels_json=deer_estimation_labels_json,
        deer_estimation_data_json=deer_estimation_data_json,
        deer_trend_labels_json=deer_trend_labels_json,
        deer_trend_data_json=deer_trend_data_json,
        environment_labels_json=environment_labels_json,
        environment_data_json=environment_data_json,
        furtive_extraction_labels_json=furtive_extraction_labels_json,
        furtive_extraction_data_json=furtive_extraction_data_json,
        boar_estimation_labels_json=boar_estimation_labels_json,
        boar_estimation_data_json=boar_estimation_data_json,
        puma_estimation_labels_json=puma_estimation_labels_json,
        puma_estimation_data_json=puma_estimation_data_json,
        puma_trend_labels_json=puma_trend_labels_json,
        puma_trend_data_json=puma_trend_data_json,
        guanacos_labels_json=guanacos_labels_json,
        guanacos_data_json=guanacos_data_json
    )
    return html_template

if __name__ == '__main__':
    df = load_data('data_cleaned.json')
    
    # Fill NaN values with a friendly string for display
    df.fillna('No especificado', inplace=True)

    # Prepare data for data.js
    establishment_data_for_js = df.to_dict(orient='records')
    js_content = f"const establishmentData = {json.dumps(establishment_data_for_js, ensure_ascii=False, indent=4)};"
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    surface_labels, surface_data = prepare_surface_data(df)
    department_labels, department_data, department_table = prepare_department_data(df)
    breeding_site_labels, breeding_site_data, breeding_site_table = prepare_breeding_site_data(df)
    species_labels, species_data, species_table = prepare_species_data(df)
    deer_estimation_labels, deer_estimation_data, deer_estimation_table = prepare_deer_estimation_data(df)
    deer_trend_labels, deer_trend_data, deer_trend_table = prepare_deer_trend_data(df)
    environment_labels, environment_data, environment_table = prepare_environment_data(df)
    furtive_extraction_labels, furtive_extraction_data, furtive_extraction_table = prepare_furtive_extraction_data(df)
    boar_estimation_labels, boar_estimation_data = prepare_boar_estimation_data(df)
    puma_estimation_labels, puma_estimation_data, puma_estimation_table = prepare_pumas_data(df)
    puma_trend_labels, puma_trend_data, puma_trend_table = prepare_puma_trend_data(df)
    guanacos_labels, guanacos_data, guanacos_table = prepare_guanacos_data(df)

    html_data = {
        'nombre_establecimiento': df['Nombre del establecimiento'].tolist(),
        'surface_labels': surface_labels,
        'surface_data': surface_data,
        'department_labels': department_labels,
        'department_data': department_data,
        'department_table': department_table,
        'breeding_site_labels': breeding_site_labels,
        'breeding_site_data': breeding_site_data,
        'breeding_site_table': breeding_site_table,
        'species_labels': species_labels,
        'species_data': species_data,
        'species_table': species_table,
        'deer_estimation_labels': deer_estimation_labels,
        'deer_estimation_data': deer_estimation_data,
        'deer_estimation_table': deer_estimation_table,
        'deer_trend_labels': deer_trend_labels,
        'deer_trend_data': deer_trend_data,
        'deer_trend_table': deer_trend_table,
        'environment_labels': environment_labels,
        'environment_data': environment_data,
        'environment_table': environment_table,
        'furtive_extraction_labels': furtive_extraction_labels,
        'furtive_extraction_data': furtive_extraction_data,
        'furtive_extraction_table': furtive_extraction_table,
        'boar_estimation_labels': boar_estimation_labels,
        'boar_estimation_data': boar_estimation_data,
        'puma_estimation_labels': puma_estimation_labels,
        'puma_estimation_data': puma_estimation_data,
        'puma_estimation_table': puma_estimation_table,
        'puma_trend_labels': puma_trend_labels,
        'puma_trend_data': puma_trend_data,
        'puma_trend_table': puma_trend_table,
        'guanacos_labels': guanacos_labels,
        'guanacos_data': guanacos_data,
        'guanacos_table': guanacos_table
    }
    
    html_output = generate_html(html_data)
    
    with open('analisis_departamento.html', 'w', encoding='utf-8') as f:
        f.write(html_output)