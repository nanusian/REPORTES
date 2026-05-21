#!/usr/bin/env python3
"""
Generador de reporte HTML con gráficos de evolución temporal
Incluye visualizaciones de progresión usando Chart.js
"""

import json
import sys
import os
import base64
from pathlib import Path
from datetime import datetime

def format_currency(value):
    if value is None:
        return "$0"
    return f"${value:,.0f}".replace(",", ".")

def format_number(value):
    if value is None:
        return "0"
    return f"{int(value):,}".replace(",", ".")

def image_to_base64(image_path):
    """Convierte una imagen a base64"""
    try:
        if not os.path.exists(image_path):
            return None
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            ext = Path(image_path).suffix.lower()
            mime_type = 'image/jpeg'
            if ext == '.png':
                mime_type = 'image/png'
            elif ext == '.gif':
                mime_type = 'image/gif'
            return f"data:{mime_type};base64,{base64_data}"
    except:
        return None

def generate_html_with_charts(json_path):
    """Genera HTML con gráficos de evolución"""

    # Leer datos
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    resumen = data.get('resumen', {})
    conjuntos = data.get('conjuntos_de_anuncios', [])
    anuncios = data.get('anuncios', [])
    datos_diarios = data.get('datos_diarios', [])

    cliente = metadata.get('cliente', 'Cliente')
    periodo = metadata.get('periodo', '')

    # Preparar datos para gráficos
    fechas = [d['date'] for d in datos_diarios]
    inversiones = [d['spend'] for d in datos_diarios]
    alcances = [d['reach'] for d in datos_diarios]
    impresiones = [d['impressions'] for d in datos_diarios]
    conversaciones = [d['conversaciones'] for d in datos_diarios]

    # Calcular totales acumulados
    inversion_acumulada = []
    alcance_acumulado = []
    total = 0
    total_alcance = 0
    for inv, alc in zip(inversiones, alcances):
        total += inv
        total_alcance += alc
        inversion_acumulada.append(total)
        alcance_acumulado.append(total_alcance)

    # Directorio de imágenes
    json_dir = os.path.dirname(json_path)
    images_dir = os.path.join(json_dir, 'images')

    # Generar HTML
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte META Ads - {cliente}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            color: #2d3748;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 50px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        /* HEADER */
        .header {{
            text-align: center;
            padding: 50px 0;
            border-bottom: 4px solid #00D9C1;
            margin-bottom: 50px;
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            color: white;
            border-radius: 12px;
        }}

        .header h1 {{
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 15px;
        }}

        .header .subtitle {{
            font-size: 26px;
            font-weight: 300;
            margin-bottom: 10px;
            opacity: 0.9;
        }}

        .header .period {{
            font-size: 20px;
            margin-top: 15px;
            font-weight: 500;
            color: #00D9C1;
        }}

        /* RESUMEN */
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 60px;
        }}

        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .summary-card.turquoise {{
            background: linear-gradient(135deg, #00D9C1 0%, #00b8a0 100%);
        }}

        .summary-card.orange {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}

        .summary-card.blue {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}

        .summary-card.green {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }}

        .summary-card h3 {{
            font-size: 16px;
            font-weight: 400;
            margin-bottom: 10px;
            opacity: 0.95;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .summary-card .value {{
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        /* CHARTS */
        .charts-section {{
            margin-bottom: 60px;
        }}

        .section-title {{
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 30px;
            padding-bottom: 12px;
            border-bottom: 3px solid #00D9C1;
        }}

        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 40px;
        }}

        .chart-title {{
            font-size: 20px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 20px;
            text-align: center;
        }}

        canvas {{
            max-height: 400px;
        }}

        /* CONJUNTOS */
        .adset-card {{
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        .adset-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 2px solid #00D9C1;
        }}

        .adset-name {{
            font-size: 26px;
            font-weight: 700;
            color: #1a202c;
        }}

        .adset-spend {{
            font-size: 28px;
            font-weight: 700;
            color: #00D9C1;
        }}

        .adset-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric {{
            text-align: center;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
        }}

        .metric-label {{
            font-size: 13px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: #2d3748;
        }}

        /* ANUNCIOS */
        .ads-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}

        .ad-card {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .ad-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }}

        .ad-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f7fafc;
        }}

        .ad-content {{
            padding: 20px;
        }}

        .ad-name {{
            font-size: 16px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 15px;
            min-height: 40px;
        }}

        .ad-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 13px;
        }}

        .ad-metric {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .ad-metric-label {{
            color: #718096;
            font-weight: 500;
        }}

        .ad-metric-value {{
            color: #2d3748;
            font-weight: 600;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
            .ad-card {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>{cliente}</h1>
            <div class="subtitle">Reporte META Ads con Evolución Temporal</div>
            <div class="period">{periodo.replace('_', ' al ')}</div>
        </div>

        <!-- RESUMEN EJECUTIVO -->
        <div class="summary-grid">
            <div class="summary-card turquoise">
                <h3>Inversión Total</h3>
                <div class="value">{format_currency(resumen.get('inversion_total', 0))}</div>
            </div>
            <div class="summary-card orange">
                <h3>Alcance Total</h3>
                <div class="value">{format_number(resumen.get('alcance_total', 0))}</div>
            </div>
            <div class="summary-card blue">
                <h3>Impresiones</h3>
                <div class="value">{format_number(resumen.get('impresiones_totales', 0))}</div>
            </div>
            <div class="summary-card green">
                <h3>Anuncios Activos</h3>
                <div class="value">{resumen.get('total_anuncios', 0)}</div>
            </div>
        </div>

        <!-- GRÁFICOS DE EVOLUCIÓN -->
        <div class="charts-section">
            <h2 class="section-title">📈 Evolución Temporal (Sep - Dic 2025)</h2>

            <!-- Gráfico de Inversión Diaria -->
            <div class="chart-container">
                <div class="chart-title">Inversión Diaria (ARS)</div>
                <canvas id="inversionChart"></canvas>
            </div>

            <!-- Gráfico de Alcance Diario -->
            <div class="chart-container">
                <div class="chart-title">Alcance Diario (Personas)</div>
                <canvas id="alcanceChart"></canvas>
            </div>

            <!-- Gráfico de Inversión Acumulada -->
            <div class="chart-container">
                <div class="chart-title">Inversión Acumulada</div>
                <canvas id="acumuladoChart"></canvas>
            </div>

            <!-- Gráfico de Conversaciones -->
            <div class="chart-container">
                <div class="chart-title">Conversaciones Generadas por Día</div>
                <canvas id="conversacionesChart"></canvas>
            </div>
        </div>

        <!-- CONJUNTOS DE ANUNCIOS -->
        <div class="adsets-section">
            <h2 class="section-title">🎯 Detalle por Conjunto de Anuncios</h2>
"""

    # Agregar conjuntos
    for conjunto in conjuntos:
        adset_name = conjunto.get('adset_name', 'Sin nombre')
        spend = conjunto.get('spend', 0)
        reach = conjunto.get('reach', 0)
        impressions = conjunto.get('impressions', 0)
        frequency = conjunto.get('frequency', 0)

        # Conversaciones
        conversations = conjunto.get('actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
        cost_per_conv = conjunto.get('cost_per_actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)

        html += f"""
            <div class="adset-card">
                <div class="adset-header">
                    <div class="adset-name">{adset_name}</div>
                    <div class="adset-spend">{format_currency(spend)}</div>
                </div>
                <div class="adset-metrics">
                    <div class="metric">
                        <div class="metric-label">Alcance</div>
                        <div class="metric-value">{format_number(reach)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Impresiones</div>
                        <div class="metric-value">{format_number(impressions)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Frecuencia</div>
                        <div class="metric-value">{frequency:.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Conversaciones</div>
                        <div class="metric-value">{conversations}</div>
                    </div>
                </div>

                <!-- Anuncios de este conjunto -->
                <div class="ads-grid">
"""

        # Filtrar anuncios de este conjunto
        anuncios_conjunto = [a for a in anuncios if a.get('adset_name') == adset_name]

        for ad in anuncios_conjunto:
            ad_name = ad.get('ad_name', 'Sin nombre')
            ad_reach = ad.get('reach', 0)
            ad_spend = ad.get('spend', 0)
            ad_ctr = ad.get('ctr', 0)
            ad_cpc = ad.get('cpc', 0)
            ad_freq = ad.get('frequency', 0)

            # Buscar imagen
            ad_image_hash = ad.get('image_hash', '')
            image_base64 = None

            if ad_image_hash and os.path.exists(images_dir):
                for img_file in os.listdir(images_dir):
                    if img_file.startswith(ad_image_hash):
                        img_path = os.path.join(images_dir, img_file)
                        image_base64 = image_to_base64(img_path)
                        break

            img_html = f'<img src="{image_base64}" class="ad-image" alt="{ad_name}">' if image_base64 else '<div class="ad-image"></div>'

            html += f"""
                    <div class="ad-card">
                        {img_html}
                        <div class="ad-content">
                            <div class="ad-name">{ad_name}</div>
                            <div class="ad-metrics">
                                <div class="ad-metric">
                                    <span class="ad-metric-label">Alcance:</span>
                                    <span class="ad-metric-value">{format_number(ad_reach)}</span>
                                </div>
                                <div class="ad-metric">
                                    <span class="ad-metric-label">Inversión:</span>
                                    <span class="ad-metric-value">{format_currency(ad_spend)}</span>
                                </div>
                                <div class="ad-metric">
                                    <span class="ad-metric-label">CTR:</span>
                                    <span class="ad-metric-value">{ad_ctr:.2f}%</span>
                                </div>
                                <div class="ad-metric">
                                    <span class="ad-metric-label">CPC:</span>
                                    <span class="ad-metric-value">{format_currency(ad_cpc)}</span>
                                </div>
                                <div class="ad-metric">
                                    <span class="ad-metric-label">Frecuencia:</span>
                                    <span class="ad-metric-value">{ad_freq:.1f}</span>
                                </div>
                            </div>
                        </div>
                    </div>
"""

        html += """
                </div>
            </div>
"""

    # Scripts de Chart.js
    html += f"""
        </div>
    </div>

    <script>
        // Datos para los gráficos
        const fechas = {json.dumps(fechas)};
        const inversiones = {json.dumps(inversiones)};
        const alcances = {json.dumps(alcances)};
        const impresiones = {json.dumps(impresiones)};
        const conversaciones = {json.dumps(conversaciones)};
        const inversionAcumulada = {json.dumps(inversion_acumulada)};

        // Configuración común
        const commonOptions = {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    display: false
                }}
            }},
            scales: {{
                x: {{
                    ticks: {{
                        maxTicksLimit: 20
                    }}
                }}
            }}
        }};

        // Gráfico de Inversión Diaria
        new Chart(document.getElementById('inversionChart'), {{
            type: 'line',
            data: {{
                labels: fechas,
                datasets: [{{
                    label: 'Inversión (ARS)',
                    data: inversiones,
                    borderColor: '#00D9C1',
                    backgroundColor: 'rgba(0, 217, 193, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: commonOptions
        }});

        // Gráfico de Alcance Diario
        new Chart(document.getElementById('alcanceChart'), {{
            type: 'bar',
            data: {{
                labels: fechas,
                datasets: [{{
                    label: 'Alcance (Personas)',
                    data: alcances,
                    backgroundColor: '#667eea',
                }}]
            }},
            options: commonOptions
        }});

        // Gráfico de Inversión Acumulada
        new Chart(document.getElementById('acumuladoChart'), {{
            type: 'line',
            data: {{
                labels: fechas,
                datasets: [{{
                    label: 'Inversión Acumulada (ARS)',
                    data: inversionAcumulada,
                    borderColor: '#f5576c',
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: commonOptions
        }});

        // Gráfico de Conversaciones
        new Chart(document.getElementById('conversacionesChart'), {{
            type: 'bar',
            data: {{
                labels: fechas,
                datasets: [{{
                    label: 'Conversaciones',
                    data: conversaciones,
                    backgroundColor: '#43e97b',
                }}]
            }},
            options: commonOptions
        }});
    </script>
</body>
</html>
"""

    # Guardar HTML
    output_path = json_path.replace('.json', '_CON_GRAFICOS.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML con gráficos generado: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso: python3 generate_html_with_charts.py <ruta_al_json>")
        sys.exit(1)

    json_path = sys.argv[1]

    if not os.path.exists(json_path):
        print(f"❌ Error: No se encuentra el archivo {json_path}")
        sys.exit(1)

    generate_html_with_charts(json_path)
