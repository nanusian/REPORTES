#!/usr/bin/env python3
"""
Genera reporte consolidado de Google Ads para ASPA
Combina datos de Sep-Dic 2025
"""

import json
import os
from datetime import datetime
from collections import defaultdict

# Rutas a los reportes mensuales
REPORTES_DIR = "/Users/laureanomedeot/Documents/REPORTES/reportes"
MESES = [
    ("2025-09-SEP", "ASPA_2025-09-01_2025-09-30_google_ads.json", "Septiembre"),
    ("2025-10-OCT", "ASPA_2025-10-01_2025-10-31_google_ads.json", "Octubre"),
    ("2025-11-NOV", "ASPA_2025-11-01_2025-11-30_google_ads.json", "Noviembre"),
    ("2025-12-DIC", "ASPA_2025-12-01_2025-12-28_google_ads.json", "Diciembre")
]

def load_monthly_data():
    """Carga datos de los 4 meses"""
    monthly_reports = []

    for mes_dir, filename, mes_nombre in MESES:
        filepath = f"{REPORTES_DIR}/{mes_dir}/ASPA/google/{filename}"

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['mes_nombre'] = mes_nombre
                monthly_reports.append(data)
                print(f"✅ Cargado: {mes_nombre}")
        else:
            print(f"⚠️  No encontrado: {filepath}")

    return monthly_reports

def extract_ad_group_metrics(ad_group):
    """Extrae métricas de un grupo de anuncios"""
    return {
        'campaign_name': ad_group.get('campaign_name', ''),
        'ad_group_name': ad_group.get('ad_group_name', ''),
        'estado': ad_group.get('estado', ''),
        'clicks': ad_group.get('clicks', 0),
        'impressions': ad_group.get('impressions', 0),
        'cost': ad_group.get('cost', 0),
        'conversions': ad_group.get('conversions', 0),
        'ctr': ad_group.get('ctr', 0),
        'avg_cpc': ad_group.get('avg_cpc', 0),
        'cost_per_conversion': ad_group.get('cost_per_conversion', 0)
    }

def generate_html_report(monthly_reports):
    """Genera reporte HTML consolidado"""

    # Calcular totales generales
    total_cost = sum(r['resumen']['inversion_total'] for r in monthly_reports)
    total_clicks = sum(r['resumen']['clics_totales'] for r in monthly_reports)
    total_impressions = sum(r['resumen']['impresiones_totales'] for r in monthly_reports)
    total_conversions = sum(r['resumen']['conversiones_totales'] for r in monthly_reports)

    # Evolución por grupo de anuncios
    ad_group_evolution = defaultdict(lambda: {'sep': {}, 'oct': {}, 'nov': {}, 'dic': {}})

    for report in monthly_reports:
        mes_key = report['mes_nombre'].lower()[:3]

        for ag in report.get('grupos_de_anuncios', []):
            key = f"{ag['campaign_name']}|{ag['ad_group_name']}"
            ad_group_evolution[key][mes_key] = extract_ad_group_metrics(ag)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASPA - Reporte Google Ads Sep-Dic 2025</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        header {{
            text-align: center;
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 3px solid #667eea;
        }}

        h1 {{
            font-size: 2.5em;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .subtitle {{
            font-size: 1.2em;
            color: #666;
        }}

        .period {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            display: inline-block;
            margin: 20px 0;
            font-weight: bold;
        }}

        .monthly-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 50px;
        }}

        .month-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}

        .month-card h3 {{
            font-size: 1.5em;
            margin-bottom: 15px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            font-size: 0.95em;
        }}

        .metric-value {{
            font-weight: bold;
            font-size: 1.1em;
        }}

        h2 {{
            color: #667eea;
            font-size: 2em;
            margin: 40px 0 20px 0;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}

        .comparison-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .comparison-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .comparison-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}

        .comparison-table tbody tr:hover {{
            background: #f8f9fa;
        }}

        .comparison-table tbody tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        .empty-cell {{
            color: #999;
            font-style: italic;
        }}

        .recommendations {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            margin: 40px 0;
        }}

        .recommendations h2 {{
            color: white;
            border-bottom-color: rgba(255,255,255,0.3);
        }}

        .recommendation-item {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            border-left: 5px solid white;
        }}

        .recommendation-item h3 {{
            margin-bottom: 10px;
            font-size: 1.2em;
        }}

        .highlight {{
            background: #fff3cd;
            padding: 2px 8px;
            border-radius: 4px;
            color: #856404;
            font-weight: bold;
        }}

        .positive {{
            color: #28a745;
            font-weight: bold;
        }}

        .negative {{
            color: #dc3545;
            font-weight: bold;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #eee;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ASPA</h1>
            <div class="subtitle">Reporte de Rendimiento Google Ads</div>
            <div class="period">Septiembre - Diciembre 2025</div>
        </header>

        <h2>📊 Resumen por Mes</h2>
        <div class="monthly-summary">
"""

    # Cards mensuales
    for report in monthly_reports:
        html += f"""
            <div class="month-card">
                <h3>{report['mes_nombre']}</h3>
                <div class="metric">
                    <span>Inversión</span>
                    <span class="metric-value">${report['resumen']['inversion_total']:,.2f}</span>
                </div>
                <div class="metric">
                    <span>Clics</span>
                    <span class="metric-value">{report['resumen']['clics_totales']:,}</span>
                </div>
                <div class="metric">
                    <span>Impresiones</span>
                    <span class="metric-value">{report['resumen']['impresiones_totales']:,}</span>
                </div>
                <div class="metric">
                    <span>Conversiones</span>
                    <span class="metric-value">{report['resumen']['conversiones_totales']:.1f}</span>
                </div>
                <div class="metric">
                    <span>CPC Prom</span>
                    <span class="metric-value">${report['resumen']['inversion_total']/report['resumen']['clics_totales']:.2f}</span>
                </div>
                <div class="metric">
                    <span>Costo/Conv</span>
                    <span class="metric-value">${report['resumen']['inversion_total']/report['resumen']['conversiones_totales'] if report['resumen']['conversiones_totales'] > 0 else 0:.2f}</span>
                </div>
            </div>
"""

    html += """
        </div>

        <h2>📈 Evolución por Grupo de Anuncios</h2>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Campaña</th>
                    <th>Grupo de Anuncios</th>
                    <th>Métrica</th>
                    <th>Sep</th>
                    <th>Oct</th>
                    <th>Nov</th>
                    <th>Dic</th>
                </tr>
            </thead>
            <tbody>
"""

    # Tabla de evolución por grupo
    for key, evolution in ad_group_evolution.items():
        campaign, ad_group = key.split('|')

        # Fila de clics
        html += f"""
                <tr>
                    <td rowspan="4"><strong>{campaign}</strong></td>
                    <td rowspan="4">{ad_group}</td>
                    <td><strong>Clics</strong></td>
"""
        for mes_key in ['sep', 'oct', 'nov', 'dic']:
            data = evolution[mes_key]
            if data:
                html += f'<td>{data["clicks"]:,}</td>'
            else:
                html += '<td class="empty-cell">-</td>'
        html += "</tr>"

        # Fila de inversión
        html += "<tr><td><strong>Inversión</strong></td>"
        for mes_key in ['sep', 'oct', 'nov', 'dic']:
            data = evolution[mes_key]
            if data:
                html += f'<td>${data["cost"]:,.0f}</td>'
            else:
                html += '<td class="empty-cell">-</td>'
        html += "</tr>"

        # Fila de conversiones
        html += "<tr><td><strong>Conversiones</strong></td>"
        for mes_key in ['sep', 'oct', 'nov', 'dic']:
            data = evolution[mes_key]
            if data:
                html += f'<td>{data["conversions"]:.1f}</td>'
            else:
                html += '<td class="empty-cell">-</td>'
        html += "</tr>"

        # Fila de costo por conversión
        html += "<tr><td><strong>Costo/Conv</strong></td>"
        for mes_key in ['sep', 'oct', 'nov', 'dic']:
            data = evolution[mes_key]
            if data and data["conversions"] > 0:
                costo_conv = data["cost"] / data["conversions"]
                html += f'<td><span class="highlight">${costo_conv:,.2f}</span></td>'
            else:
                html += '<td class="empty-cell">-</td>'
        html += "</tr>"

    html += """
            </tbody>
        </table>
"""

    # Recomendaciones estratégicas
    html += f"""
        <div class="recommendations">
            <h2>💡 Recomendaciones Estratégicas</h2>

            <div class="recommendation-item">
                <h3>1. Consolidar Presupuesto en Buscadores 2025</h3>
                <p>El grupo "Buscadores 2025" muestra el mejor rendimiento consistente con un costo por conversión competitivo (~$2,226 en Sep). Recomendamos incrementar el presupuesto de esta campaña en un 30-40% redistribuyendo fondos de campañas menos eficientes.</p>
            </div>

            <div class="recommendation-item">
                <h3>2. Optimizar La Alborada 2025</h3>
                <p>Esta campaña mostró crecimiento en Oct-Dic con inversiones significativas. Analizar qué creatividades y palabras clave están generando las conversiones para replicar el éxito.</p>
            </div>

            <div class="recommendation-item">
                <h3>3. Revisar Torre Aura - Tráfico</h3>
                <p>Múltiples grupos de anuncios de Torre Aura muestran actividad esporádica. Consolidar en un único grupo optimizado podría mejorar el rendimiento y simplificar la gestión.</p>
            </div>

            <div class="recommendation-item">
                <h3>4. Pausar Grupos de Bajo Rendimiento</h3>
                <p>Los grupos marcados como "Detenido" con inversión residual deberían ser completamente pausados o reactivados con estrategia clara. La inversión fragmentada reduce la eficiencia del presupuesto.</p>
            </div>

            <div class="recommendation-item">
                <h3>5. Implementar Extensiones de Anuncio</h3>
                <p>Para campañas de búsqueda como "Buscadores 2025", agregar extensiones de llamada, ubicación y enlaces adicionales puede incrementar el CTR entre 10-25% sin costo adicional.</p>
            </div>

            <div class="recommendation-item">
                <h3>6. Optimizar Landing Pages</h3>
                <p>Con un costo por conversión promedio de ${total_cost/total_conversions:.2f}, mejorar la tasa de conversión de las landing pages en 15-20% podría reducir significativamente el CPL sin aumentar la inversión.</p>
            </div>

            <div class="recommendation-item">
                <h3>7. Pruebas A/B de Creatividades</h3>
                <p>Implementar sistema de rotación de anuncios para identificar mensajes de mayor rendimiento. Crear al menos 3 variantes por grupo de anuncios y evaluar rendimiento mensual.</p>
            </div>
        </div>

        <div class="footer">
            <p><strong>Período del Reporte:</strong> 1 de Septiembre - 28 de Diciembre 2025</p>
            <p><strong>Inversión Total:</strong> ${total_cost:,.2f} ARS</p>
            <p><strong>Clics Totales:</strong> {total_clicks:,}</p>
            <p><strong>Conversiones Totales:</strong> {total_conversions:.1f}</p>
            <p style="margin-top: 20px; font-size: 0.9em; color: #999;">
                Generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}
            </p>
        </div>
    </div>
</body>
</html>
"""

    return html

def main():
    print("\n" + "="*70)
    print("📊 GENERADOR DE REPORTE CONSOLIDADO GOOGLE ADS - ASPA")
    print("="*70 + "\n")

    # Cargar datos mensuales
    monthly_reports = load_monthly_data()

    if len(monthly_reports) < 4:
        print(f"⚠️  Solo se encontraron {len(monthly_reports)} meses de 4 esperados")

    # Generar HTML
    print("\n📝 Generando reporte HTML...")
    html = generate_html_report(monthly_reports)

    # Guardar
    output_dir = f"{REPORTES_DIR}/2025-12-DIC/ASPA/google"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/ASPA_REPORTE_COMPLETO_GOOGLE_ADS.html"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ Reporte generado: {output_path}")
    print("\n" + "="*70)
    print("✅ Proceso completado!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
