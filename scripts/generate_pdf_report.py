#!/usr/bin/env python3
"""
Generador de reportes PDF desde datos de Meta Ads
Estilo: SOMA PIXEL - Fondo rojo minimalista
"""

import json
import sys
import os
import subprocess
from datetime import datetime

def format_currency(value):
    """Formatea números como moneda ARS"""
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(value):
    """Formatea números con separador de miles"""
    return f"{int(value):,}".replace(",", ".")

def generate_html_report(json_path, usar_soma=False):
    """Genera HTML desde JSON de análisis"""

    # Leer JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data['metadata']
    resumen = data['resumen']
    conjuntos = data['conjuntos_de_anuncios']
    anuncios = data['anuncios']
    analisis = data['analisis']
    daily_data = data.get('datos_diarios', [])
    insights = analisis.get('insights', [])

    # Colores según estética
    if usar_soma:
        color_fondo = '#E74C3C'
        color_acento = 'white'
        logo_text = 'SOMA'
        logo_subtitle = 'PIXEL'
    else:
        color_fondo = '#2d3748'
        color_acento = '#00D9C1'
        logo_text = 'LINE'
        logo_subtitle = 'AD STUDIO'

    cliente = metadata['cliente'].upper()
    periodo_raw = metadata['periodo']

    # Formatear período
    fecha_inicio, fecha_fin = periodo_raw.split('_')
    mes_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%B %Y')
    mes_inicio_esp = {
        'January': 'ENERO', 'February': 'FEBRERO', 'March': 'MARZO',
        'April': 'ABRIL', 'May': 'MAYO', 'June': 'JUNIO',
        'July': 'JULIO', 'August': 'AGOSTO', 'September': 'SEPTIEMBRE',
        'October': 'OCTUBRE', 'November': 'NOVIEMBRE', 'December': 'DICIEMBRE'
    }
    for eng, esp in mes_inicio_esp.items():
        mes_inicio = mes_inicio.replace(eng, esp)

    # Agrupar anuncios por conjunto
    anuncios_por_conjunto = {}
    for anuncio in anuncios:
        adset = anuncio['adset_name']
        if adset not in anuncios_por_conjunto:
            anuncios_por_conjunto[adset] = []
        anuncios_por_conjunto[adset].append(anuncio)

    # HTML Template
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Campaña - {cliente}</title>
    <style>
        @page {{
            margin: 0;
            size: A4 landscape;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
            color: white;
            background: {color_fondo};
        }}

        /* Portada */
        .cover-page {{
            width: 297mm;
            height: 210mm;
            background: {color_fondo};
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            page-break-after: always;
        }}

        .logo {{
            position: absolute;
            top: 40px;
            right: 40px;
        }}

        .logo-text {{
            font-size: 36px;
            font-weight: 900;
            color: white;
            letter-spacing: 2px;
        }}

        .logo-subtitle {{
            font-size: 14px;
            font-weight: 400;
            color: {color_acento};
            letter-spacing: 3px;
        }}

        .cover-title {{
            font-size: 72px;
            font-weight: 300;
            letter-spacing: 8px;
            margin-bottom: 40px;
        }}

        .cover-client {{
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 20px;
        }}

        .cover-period {{
            font-size: 28px;
            font-weight: 300;
            opacity: 0.9;
        }}

        /* Páginas internas */
        .content-page {{
            width: 297mm;
            height: 210mm;
            background: {color_fondo};
            padding: 50px 60px;
            position: relative;
            page-break-after: always;
        }}

        .page-title {{
            font-size: 48px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 40px;
        }}

        /* Glosario */
        .glossary-box {{
            border: 2px solid white;
            padding: 40px;
            margin-top: 60px;
        }}

        .glossary-item {{
            margin-bottom: 25px;
            font-size: 18px;
            line-height: 1.6;
        }}

        .glossary-term {{
            font-weight: 700;
            font-size: 20px;
        }}

        /* Tablas */
        table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(255,255,255,0.1);
            font-size: 16px;
        }}

        th {{
            background: rgba(0,0,0,0.3);
            padding: 15px;
            text-align: left;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}

        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}

        /* Métricas destacadas */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            margin: 40px 0;
        }}

        .metric-card {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-left: 5px solid {color_acento};
        }}

        .metric-label {{
            font-size: 16px;
            opacity: 0.8;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .metric-value {{
            font-size: 36px;
            font-weight: 900;
            margin-bottom: 5px;
        }}

        .metric-change {{
            font-size: 14px;
            opacity: 0.7;
        }}

        /* Anuncios grid */
        .ads-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 30px;
        }}

        .ad-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-left: 4px solid {color_acento};
        }}

        .ad-name {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 15px;
        }}

        .ad-metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            font-size: 14px;
        }}

        .ad-metric {{
            margin: 5px 0;
        }}

        .ad-metric-label {{
            opacity: 0.7;
            font-size: 12px;
        }}

        .ad-metric-value {{
            font-weight: 700;
            font-size: 16px;
        }}

        /* Insights */
        .insight-box {{
            background: rgba(0,0,0,0.2);
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid {color_acento};
        }}

        .insight-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .insight-text {{
            font-size: 16px;
            line-height: 1.6;
        }}

        /* Insights cards */
        .insights-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
            margin-top: 30px;
        }}

        .insight-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-left: 5px solid {color_acento};
        }}

        .insight-card.alerta {{
            border-left-color: #fc8181;
        }}

        .insight-card.oportunidad {{
            border-left-color: #f6ad55;
        }}

        .insight-card.exito {{
            border-left-color: #68d391;
        }}

        .insight-card-title {{
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .insight-card-desc {{
            font-size: 14px;
            line-height: 1.5;
            opacity: 0.9;
            margin-bottom: 10px;
        }}

        .insight-card-action {{
            font-size: 13px;
            opacity: 0.8;
            font-style: italic;
        }}

        /* Gráficos */
        .chart-container {{
            width: 100%;
            height: 300px;
            background: rgba(255,255,255,0.05);
            padding: 20px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>

    <!-- PORTADA -->
    <div class="cover-page">
        <div class="logo">
            <div class="logo-text">{logo_text}</div>
            <div class="logo-subtitle">{logo_subtitle}</div>
        </div>

        <div class="cover-title">REPORTE DE CAMPAÑA</div>
        <div class="cover-client">CLIENTE: {cliente}</div>
        <div class="cover-period">{mes_inicio}</div>
    </div>

    <!-- GLOSARIO -->
    <div class="content-page">
        <div class="logo">
            <div class="logo-text">{logo_text}</div>
            <div class="logo-subtitle">{logo_subtitle}</div>
        </div>

        <h1 class="page-title">GLOSARIO DE MÉTRICAS</h1>

        <div class="glossary-box">
            <div class="glossary-item">
                <span class="glossary-term">■ Impresiones:</span> cantidad de veces que se mostraron los avisos.
            </div>
            <div class="glossary-item">
                <span class="glossary-term">■ Alcance:</span> cantidad de personas a las que se mostró el anuncio.
            </div>
            <div class="glossary-item">
                <span class="glossary-term">■ Frecuencia:</span> cantidad de veces que se mostraron los anuncios a cada persona en promedio (impresiones/alcance)
            </div>
            <div class="glossary-item">
                <span class="glossary-term">■ Clicks:</span> sobre algún elemento del anuncio.
            </div>
            <div class="glossary-item">
                <span class="glossary-term">■ CTR:</span> porcentaje de clicks sobre impresiones (Click-Through Rate).
            </div>
            <div class="glossary-item">
                <span class="glossary-term">■ CPM:</span> costo por cada mil impresiones.
            </div>
            <div class="glossary-item">
                <span class="glossary-term">■ CPC:</span> costo promedio por cada click.
            </div>
        </div>
    </div>

    <!-- RESUMEN EJECUTIVO -->
    <div class="content-page">
        <div class="logo">
            <div class="logo-text">{logo_text}</div>
            <div class="logo-subtitle">{logo_subtitle}</div>
        </div>

        <h1 class="page-title">RESUMEN DEL PERÍODO</h1>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Inversión Total</div>
                <div class="metric-value">{format_currency(resumen['inversion_total'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Alcance Total</div>
                <div class="metric-value">{format_number(resumen['alcance_total'])}</div>
                <div class="metric-change">personas alcanzadas</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Impresiones</div>
                <div class="metric-value">{format_number(resumen['impresiones_totales'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Anuncios Corridos</div>
                <div class="metric-value">{resumen['total_anuncios']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Conjuntos</div>
                <div class="metric-value">{resumen['total_conjuntos']}</div>
                <div class="metric-change">conjuntos de anuncios</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Frecuencia Promedio</div>
                <div class="metric-value">{(resumen['impresiones_totales'] / resumen['alcance_total']):.2f}</div>
                <div class="metric-change">veces por persona</div>
            </div>
        </div>

        <div class="insight-box">
            <div class="insight-title">🎯 Insight Clave</div>
            <div class="insight-text">
                El anuncio con mejor performance fue "{analisis['best_ad']['ad_name']}"
                alcanzando {format_number(analisis['best_ad']['reach'])} personas con una inversión
                de {format_currency(analisis['best_ad']['spend'])}.
            </div>
        </div>
    </div>
"""

    # Página de insights automáticos
    if insights:
        # Ordenar por prioridad
        insights_sorted = sorted(insights, key=lambda x: {'alta': 0, 'media': 1, 'baja': 2}.get(x['prioridad'], 3))

        html += f"""
    <!-- INSIGHTS AUTOMÁTICOS -->
    <div class="content-page">
        <div class="logo">
            <div class="logo-text">{logo_text}</div>
            <div class="logo-subtitle">{logo_subtitle}</div>
        </div>

        <h1 class="page-title">INSIGHTS AUTOMÁTICOS</h1>

        <p style="font-size: 16px; opacity: 0.8; margin-bottom: 30px;">
            Análisis automático de {len(insights)} oportunidades de optimización detectadas en tus campañas.
        </p>

        <div class="insights-grid">"""

        for insight in insights_sorted[:6]:  # Top 6 insights
            tipo_clase = insight['tipo'].lower()
            emoji = {'alerta': '🔴', 'oportunidad': '🟡', 'éxito': '🟢'}.get(tipo_clase, '📊')

            html += f"""
            <div class="insight-card {tipo_clase}">
                <div class="insight-card-title">{emoji} {insight['titulo']}</div>
                <div class="insight-card-desc">{insight['descripcion']}</div>
                <div class="insight-card-action">→ {insight['accion']}</div>
            </div>"""

        html += """
        </div>
    </div>
"""

    # Página de gráficos de evolución
    if daily_data and len(daily_data) > 1:
        # Preparar datos para gráfico
        dates = [d['date'] for d in daily_data]
        spend_data = [d['spend'] for d in daily_data]
        reach_data = [d['reach'] for d in daily_data]
        conv_data = [d.get('conversaciones', 0) for d in daily_data]

        html += f"""
    <!-- EVOLUCIÓN TEMPORAL -->
    <div class="content-page">
        <div class="logo">
            <div class="logo-text">{logo_text}</div>
            <div class="logo-subtitle">{logo_subtitle}</div>
        </div>

        <h1 class="page-title">EVOLUCIÓN DEL PERÍODO</h1>

        <div style="margin-top: 40px;">
            <h3 style="font-size: 20px; margin-bottom: 20px;">Inversión Diaria</h3>
            <div class="chart-container">
                <canvas id="spendChart"></canvas>
            </div>

            <h3 style="font-size: 20px; margin-bottom: 20px; margin-top: 40px;">Alcance Diario</h3>
            <div class="chart-container">
                <canvas id="reachChart"></canvas>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
        // Gráfico de inversión
        new Chart(document.getElementById('spendChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Inversión (ARS)',
                    data: {json.dumps(spend_data)},
                    borderColor: '{color_acento}',
                    backgroundColor: 'rgba(0, 217, 193, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ color: 'white' }}
                    }},
                    x: {{
                        ticks: {{ color: 'white' }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{ color: 'white' }}
                    }}
                }}
            }}
        }});

        // Gráfico de alcance
        new Chart(document.getElementById('reachChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Alcance (personas)',
                    data: {json.dumps(reach_data)},
                    backgroundColor: '{color_acento}',
                    borderColor: '{color_acento}',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ color: 'white' }}
                    }},
                    x: {{
                        ticks: {{ color: 'white' }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{ color: 'white' }}
                    }}
                }}
            }}
        }});
    </script>
"""

    html += """
    <!-- CONJUNTOS DE ANUNCIOS -->
    <div class="content-page">
        <div class="logo">
            <div class="logo-text">{logo_text}</div>
            <div class="logo-subtitle">{logo_subtitle}</div>
        </div>

        <h1 class="page-title">CONJUNTOS DE ANUNCIOS QUE CORRIERON</h1>

        <table style="margin-top: 40px;">
            <thead>
                <tr>
                    <th>Conjunto de anuncios</th>
                    <th>Resultados</th>
                    <th>Alcance</th>
                    <th>Frecuencia</th>
                    <th>Costo por resultado</th>
                    <th>Importe gastado</th>
                </tr>
            </thead>
            <tbody>"""

    # Agregar filas de conjuntos
    for conjunto in conjuntos:
        conversaciones = conjunto['actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)
        cost_per_conv = conjunto['cost_per_actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)

        html += f"""
                <tr>
                    <td><strong>{conjunto['adset_name']}</strong></td>
                    <td>{conversaciones}<br><small style="opacity: 0.7;">Conversaciones con...</small></td>
                    <td>{format_number(conjunto['reach'])}</td>
                    <td>{conjunto['frequency']:.2f}</td>
                    <td>{format_currency(cost_per_conv) if cost_per_conv > 0 else '—'}<br><small style="opacity: 0.7;">Por conversación con...</small></td>
                    <td><strong>{format_currency(conjunto['spend'])}</strong></td>
                </tr>"""

    html += """
            </tbody>
        </table>
    </div>
"""

    # Generar páginas por cada conjunto de anuncios
    for adset_name, ads_list in anuncios_por_conjunto.items():
        # Buscar datos del conjunto
        conjunto_data = next((c for c in conjuntos if c['adset_name'] == adset_name), None)
        conversaciones = 0
        cost_per_conv = 0
        if conjunto_data:
            conversaciones = conjunto_data['actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)
            cost_per_conv = conjunto_data['cost_per_actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)

        html += f"""
    <!-- ANUNCIOS: {adset_name} -->
    <div class="content-page">
        <div class="logo">
            <div class="logo-text">{logo_text}</div>
            <div class="logo-subtitle">{logo_subtitle}</div>
        </div>

        <h1 class="page-title">ANUNCIOS<br>{adset_name.upper()}</h1>

        <div class="metrics-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 30px;">
            <div class="metric-card">
                <div class="metric-label">Conversaciones</div>
                <div class="metric-value">{conversaciones}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Costo / Conv.</div>
                <div class="metric-value" style="font-size: 24px;">{format_currency(cost_per_conv) if cost_per_conv > 0 else '—'}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Inversión</div>
                <div class="metric-value" style="font-size: 24px;">{format_currency(sum(ad['spend'] for ad in ads_list))}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Alcance</div>
                <div class="metric-value" style="font-size: 24px;">{format_number(sum(ad['reach'] for ad in ads_list))}</div>
            </div>
        </div>

        <div class="ads-grid">"""

        for ad in ads_list:
            ad_convs = ad['actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)
            ad_cost_conv = ad['cost_per_actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)

            html += f"""
            <div class="ad-card">
                <div class="ad-name">{ad['ad_name']}</div>
                <div class="ad-metrics">
                    <div class="ad-metric">
                        <div class="ad-metric-label">Alcance</div>
                        <div class="ad-metric-value">{format_number(ad['reach'])}</div>
                    </div>
                    <div class="ad-metric">
                        <div class="ad-metric-label">Frecuencia</div>
                        <div class="ad-metric-value">{ad['frequency']:.2f}</div>
                    </div>
                    <div class="ad-metric">
                        <div class="ad-metric-label">CTR</div>
                        <div class="ad-metric-value">{ad['ctr']:.2f}%</div>
                    </div>
                    <div class="ad-metric">
                        <div class="ad-metric-label">CPC</div>
                        <div class="ad-metric-value">${ad['cpc']:.0f}</div>
                    </div>"""

            if ad_convs > 0:
                html += f"""
                    <div class="ad-metric">
                        <div class="ad-metric-label">Conversaciones</div>
                        <div class="ad-metric-value">{ad_convs}</div>
                    </div>
                    <div class="ad-metric">
                        <div class="ad-metric-label">Costo/Conv</div>
                        <div class="ad-metric-value">${ad_cost_conv:,.0f}</div>
                    </div>"""

            html += f"""
                    <div class="ad-metric" style="grid-column: 1 / -1;">
                        <div class="ad-metric-label">Inversión</div>
                        <div class="ad-metric-value">{format_currency(ad['spend'])}</div>
                    </div>
                </div>
            </div>"""

        html += """
        </div>
    </div>
"""

    html += """
</body>
</html>"""

    return html


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 generate_pdf_report.py <json_file> [usar_soma]")
        print("  usar_soma: opcional, usar 'soma' para estética SOMA")
        sys.exit(1)

    json_path = sys.argv[1]
    usar_soma = len(sys.argv) > 2 and sys.argv[2].lower() == 'soma'

    if not os.path.exists(json_path):
        print(f"❌ No se encuentra el archivo: {json_path}")
        sys.exit(1)

    estetica = "SOMA" if usar_soma else "LINE"
    print(f"📄 Generando reporte PDF desde: {json_path} (Estética: {estetica})")

    # Generar HTML
    html_content = generate_html_report(json_path, usar_soma)

    # Guardar HTML temporal
    html_path = json_path.replace('.json', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML generado: {html_path}")

    # Generar PDF usando Chrome
    pdf_path = html_path.replace('.html', '.pdf').replace('output/', 'output/ENTREGABLES/Reporte_Pauta_')

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        "--no-margins",
        f"file://{os.path.abspath(html_path)}"
    ]

    subprocess.run(cmd, capture_output=True)

    print(f"✅ PDF generado: {pdf_path}")
    print(f"\n🎉 Reporte completado!\n")


if __name__ == "__main__":
    main()
