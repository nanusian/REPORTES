#!/usr/bin/env python3
"""
Generador de reporte completo ASPA con comparaciones mensuales
Foco en visitas al sitio web (Landing Page Views)
Formato basado en MEDICAL HAIR
"""

import json
import os
import base64
from pathlib import Path
from collections import defaultdict

def format_currency(value):
    if value is None or value == 0:
        return "$0"
    return f"${value:,.0f}".replace(",", ".")

def format_number(value):
    if value is None:
        return "0"
    return f"{int(value):,}".replace(",", ".")

def calculate_change(old, new):
    """Calcula cambio porcentual"""
    if old == 0:
        if new > 0:
            return "+∞", "positive"
        return "0%", "neutral"
    change = ((new - old) / old) * 100
    sign = "+" if change > 0 else ""
    direction = "positive" if change > 0 else ("negative" if change < 0 else "neutral")
    return f"{sign}{change:.1f}%", direction

def calculate_change_cost(old_cost, new_cost):
    """Calcula cambio de costo (inversión: bajada es buena)"""
    if old_cost == 0:
        return "Nuevo", "neutral"
    change = ((new_cost - old_cost) / old_cost) * 100
    if abs(change) < 2:
        return "Sin cambio", "neutral"
    sign = "+" if change > 0 else ""
    # Para costos: negativo es bueno (bajó el costo)
    direction = "improved" if change < 0 else "worse"
    return f"{sign}{change:.1f}%", direction

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

def load_monthly_data():
    """Carga datos mensuales de ASPA"""
    base_path = "/Users/laureanomedeot/Documents/REPORTES/reportes"

    # IMPORTANTE: Usar archivos regenerados con la cuenta correcta (act_280276187315030)
    # que incluyen TODAS las campañas: La Alborada, Torre Aura, Gran Alameda, etc
    months = {
        'Sep': f"{base_path}/2025-09-SEP/ASPA/meta/ASPA_2025-09-01_2025-09-30_analisis_pauta.json",
        'Oct': f"{base_path}/2025-10-OCT/ASPA/meta/ASPA_2025-10-01_2025-10-31_analisis_pauta.json",
        'Nov': f"{base_path}/2025-11-NOV/ASPA/meta/ASPA_2025-11-01_2025-11-30_analisis_pauta.json",
        'Dic': f"{base_path}/2025-12-DIC/ASPA/meta/ASPA_2025-12-01_2025-12-28_analisis_pauta.json",
    }

    monthly_data = {}
    for month, path in months.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                monthly_data[month] = json.load(f)
        else:
            print(f"⚠️  No se encontró: {path}")

    return monthly_data

def extract_adset_metrics(adset_data):
    """Extrae métricas clave de un conjunto de anuncios"""
    # Usar landing_page_view si existe, sino link_click
    lpv = adset_data.get('actions', {}).get('landing_page_view', 0)
    link_clicks = adset_data.get('actions', {}).get('link_click', 0)

    # Usar la que tenga valor
    visits = lpv if lpv > 0 else link_clicks

    # Costo por visita
    cost_lpv = adset_data.get('cost_per_actions', {}).get('landing_page_view', 0)
    cost_click = adset_data.get('cost_per_actions', {}).get('link_click', 0)

    cost_per_visit = cost_lpv if cost_lpv > 0 else cost_click

    return {
        'name': adset_data.get('adset_name', 'Sin nombre'),
        'spend': adset_data.get('spend', 0),
        'reach': adset_data.get('reach', 0),
        'impressions': adset_data.get('impressions', 0),
        'frequency': adset_data.get('frequency', 0),
        'landing_page_views': visits,  # Ahora puede ser lpv o link_click
        'cost_per_lpv': cost_per_visit,
        'link_clicks': link_clicks,
    }

def generate_comparison_table(monthly_data):
    """Genera tabla de comparación mensual por conjunto de anuncios"""

    # Agrupar por conjunto de anuncios
    adsets = defaultdict(dict)

    for month, data in monthly_data.items():
        for adset in data.get('conjuntos_de_anuncios', []):
            adset_name = adset.get('adset_name', 'Sin nombre')
            adsets[adset_name][month] = extract_adset_metrics(adset)

    return adsets

def generate_html_report(monthly_data):
    """Genera el reporte HTML completo"""

    # Generar tabla de comparación
    adsets_comparison = generate_comparison_table(monthly_data)

    # Calcular totales por mes
    totals_by_month = {}
    for month, data in monthly_data.items():
        total_spend = data.get('resumen', {}).get('inversion_total', 0)
        total_reach = data.get('resumen', {}).get('alcance_total', 0)

        # Sumar landing page views o link clicks
        total_visits = 0
        for adset in data.get('conjuntos_de_anuncios', []):
            lpv = adset.get('actions', {}).get('landing_page_view', 0)
            clicks = adset.get('actions', {}).get('link_click', 0)
            total_visits += lpv if lpv > 0 else clicks

        cost_per_visit = total_spend / total_visits if total_visits > 0 else 0

        totals_by_month[month] = {
            'spend': total_spend,
            'reach': total_reach,
            'lpv': total_visits,
            'cost_per_lpv': cost_per_visit,
        }

    # HTML
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Completo - ASPA (Sep-Dic 2025)</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            color: #2d3748;
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            padding: 50px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header {
            text-align: center;
            padding: 50px 0;
            border-bottom: 4px solid #4A5568;
            margin-bottom: 50px;
        }

        .header h1 {
            font-size: 48px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 15px;
        }

        .header .subtitle {
            font-size: 26px;
            color: #718096;
            font-weight: 300;
            margin-bottom: 10px;
        }

        .header .period {
            font-size: 20px;
            color: #4A5568;
            margin-top: 15px;
            font-weight: 500;
        }

        .section {
            margin-bottom: 60px;
            page-break-inside: avoid;
        }

        .section-title {
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 25px;
            padding-bottom: 12px;
            border-bottom: 3px solid #4A5568;
        }

        .section-subtitle {
            font-size: 20px;
            color: #4A5568;
            margin-bottom: 20px;
        }

        /* SUMMARY CARDS */
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }

        .summary-card h3 {
            font-size: 13px;
            font-weight: 400;
            margin-bottom: 10px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .summary-card .value {
            font-size: 32px;
            font-weight: 700;
        }

        .summary-card .subvalue {
            font-size: 14px;
            opacity: 0.85;
            margin-top: 5px;
        }

        /* COMPARISON TABLE */
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
            font-size: 14px;
        }

        .comparison-table th {
            background: #4A5568;
            color: white;
            padding: 16px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            position: sticky;
            top: 0;
        }

        .comparison-table td {
            padding: 16px 12px;
            border-bottom: 1px solid #e2e8f0;
        }

        .comparison-table tbody tr:hover {
            background: #f7fafc;
        }

        .campaign-name {
            font-weight: 600;
            color: #1a202c;
            font-size: 15px;
        }

        .metric-cell {
            text-align: center;
        }

        .metric-value {
            font-size: 18px;
            font-weight: 700;
            color: #1a202c;
            display: block;
        }

        .metric-label {
            font-size: 10px;
            color: #718096;
            text-transform: uppercase;
            margin-top: 2px;
            display: block;
        }

        .change {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
            margin-top: 5px;
        }

        .change-positive {
            background: #C6F6D5;
            color: #22543D;
        }

        .change-negative {
            background: #FED7D7;
            color: #742A2A;
        }

        .change-neutral {
            background: #E2E8F0;
            color: #2D3748;
        }

        .cost-improved {
            color: #22543D;
            font-weight: 700;
        }

        .cost-worse {
            color: #742A2A;
            font-weight: 700;
        }

        .new-badge {
            display: inline-block;
            background: #90CDF4;
            color: #1A365D;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }

        /* RECOMMENDATIONS */
        .recommendations {
            background: #f7fafc;
            padding: 30px;
            border-radius: 10px;
            border-left: 5px solid #4A5568;
        }

        .recommendation-item {
            margin-bottom: 25px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        .recommendation-title {
            font-size: 18px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 10px;
        }

        .recommendation-type {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .type-optimization {
            background: #FED7AA;
            color: #7C2D12;
        }

        .type-expansion {
            background: #C6F6D5;
            color: #22543D;
        }

        .type-testing {
            background: #BFDBFE;
            color: #1E3A8A;
        }

        .recommendation-desc {
            color: #4A5568;
            line-height: 1.7;
            margin-bottom: 10px;
        }

        .recommendation-impact {
            font-size: 13px;
            color: #718096;
            font-weight: 600;
        }

        /* AD CARDS */
        .ads-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .ad-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .ad-image {
            width: 100%;
            height: 180px;
            object-fit: cover;
            background: #f7fafc;
        }

        .ad-content {
            padding: 15px;
        }

        .ad-name {
            font-size: 14px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 12px;
            min-height: 35px;
        }

        .ad-metrics {
            font-size: 12px;
        }

        .ad-metric {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .ad-metric-label {
            color: #718096;
        }

        .ad-metric-value {
            color: #2d3748;
            font-weight: 600;
        }

        @media print {
            body {
                background: white;
                padding: 0;
            }
            .container {
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>ASPA</h1>
            <div class="subtitle">Reporte Completo de Campañas META Ads</div>
            <div class="period">Septiembre - Diciembre 2025</div>
        </div>

        <!-- RESUMEN MENSUAL -->
        <div class="section">
            <h2 class="section-title">📊 Resumen por Mes</h2>
            <div class="summary">
"""

    # Tarjetas de resumen por mes
    months_order = ['Sep', 'Oct', 'Nov', 'Dic']
    for month in months_order:
        if month in totals_by_month:
            data = totals_by_month[month]
            html += f"""
                <div class="summary-card">
                    <h3>{month} 2025</h3>
                    <div class="value">{format_currency(data['spend'])}</div>
                    <div class="subvalue">{format_number(data['lpv'])} visitas</div>
                    <div class="subvalue">{format_currency(data['cost_per_lpv'])}/visita</div>
                </div>
"""

    html += """
            </div>
        </div>

        <!-- COMPARACIÓN MENSUAL POR CONJUNTO -->
        <div class="section">
            <h2 class="section-title">📈 Evolución Mensual por Proyecto</h2>
            <p class="section-subtitle">Comparación de visitas al sitio web y costo por visita</p>

            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Proyecto</th>
                        <th>Sep 2025</th>
                        <th>Oct 2025</th>
                        <th>Nov 2025</th>
                        <th>Dic 2025</th>
                        <th>Total Período</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Generar filas de comparación
    for adset_name, months_data in sorted(adsets_comparison.items()):
        html += f"""
                    <tr>
                        <td>
                            <div class="campaign-name">{adset_name}</div>
                        </td>
"""

        total_spend = 0
        total_lpv = 0

        prev_lpv = None
        prev_cost = None

        for month in months_order:
            if month in months_data:
                data = months_data[month]
                lpv = data['landing_page_views']
                cost_lpv = data['cost_per_lpv']
                spend = data['spend']

                total_spend += spend
                total_lpv += lpv

                # Calcular cambios
                lpv_change = ""
                cost_change_html = ""

                if prev_lpv is not None:
                    change_text, direction = calculate_change(prev_lpv, lpv)
                    lpv_change = f'<div class="change change-{direction}">{change_text}</div>'

                if prev_cost is not None and cost_lpv > 0:
                    change_text, direction = calculate_change_cost(prev_cost, cost_lpv)
                    cost_class = "cost-improved" if direction == "improved" else ("cost-worse" if direction == "worse" else "")
                    cost_change_html = f'<div class="{cost_class}" style="font-size: 11px; margin-top: 3px;">{change_text}</div>'

                prev_lpv = lpv
                prev_cost = cost_lpv if cost_lpv > 0 else prev_cost

                html += f"""
                        <td class="metric-cell">
                            <span class="metric-value">{format_number(lpv)}</span>
                            <span class="metric-label">visitas</span>
                            {lpv_change}
                            <div style="margin-top: 8px; font-size: 13px; color: #4A5568;">
                                {format_currency(cost_lpv)}/visita
                                {cost_change_html}
                            </div>
                        </td>
"""
            else:
                html += """
                        <td class="metric-cell">
                            <span style="color: #CBD5E0;">Sin datos</span>
                        </td>
"""

        # Total del período
        avg_cost = total_spend / total_lpv if total_lpv > 0 else 0
        html += f"""
                        <td class="metric-cell" style="background: #F7FAFC; font-weight: 700;">
                            <span class="metric-value">{format_number(total_lpv)}</span>
                            <span class="metric-label">visitas</span>
                            <div style="margin-top: 8px; font-size: 13px; color: #4A5568;">
                                {format_currency(avg_cost)}/visita
                            </div>
                        </td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>

        <!-- COMPARACIÓN DE ANUNCIOS INDIVIDUALES -->
        <div class="section">
            <h2 class="section-title">🎯 Comparación de Anuncios Individuales por Proyecto</h2>
            <p class="section-subtitle">Evolución mensual de cada anuncio dentro de su grupo</p>
"""

    # Agrupar anuncios por conjunto y mes
    ads_by_adset = defaultdict(lambda: defaultdict(list))

    for month, data in monthly_data.items():
        for anuncio in data.get('anuncios', []):
            adset_name = anuncio.get('adset_name', 'Sin conjunto')
            ad_name = anuncio.get('ad_name', 'Sin nombre')

            ad_lpv = anuncio.get('actions', {}).get('landing_page_view', 0)
            ad_clicks = anuncio.get('actions', {}).get('link_click', 0)
            ad_visits = ad_lpv if ad_lpv > 0 else ad_clicks
            ad_spend = anuncio.get('spend', 0)
            cost_per_visit = ad_spend / ad_visits if ad_visits > 0 else 0

            ads_by_adset[adset_name][ad_name].append({
                'month': month,
                'visits': ad_visits,
                'spend': ad_spend,
                'cost_per_visit': cost_per_visit,
                'ctr': anuncio.get('ctr', 0),
                'reach': anuncio.get('reach', 0)
            })

    # Renderizar tablas por conjunto
    for adset_name in sorted(ads_by_adset.keys()):
        html += f"""
            <h3 class="section-subtitle">{adset_name}</h3>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Anuncio</th>
                        <th>Sep 2025</th>
                        <th>Oct 2025</th>
                        <th>Nov 2025</th>
                        <th>Dic 2025</th>
                        <th>Total / Promedio</th>
                    </tr>
                </thead>
                <tbody>
"""

        ads_in_adset = ads_by_adset[adset_name]

        for ad_name in sorted(ads_in_adset.keys()):
            html += f"""
                    <tr>
                        <td>
                            <div class="campaign-name">{ad_name}</div>
                        </td>
"""

            monthly_data_by_ad = {item['month']: item for item in ads_in_adset[ad_name]}

            total_visits = 0
            total_spend = 0
            prev_visits = None
            prev_cost = None

            for month in months_order:
                if month in monthly_data_by_ad:
                    ad_data = monthly_data_by_ad[month]
                    visits = ad_data['visits']
                    cost = ad_data['cost_per_visit']
                    spend = ad_data['spend']

                    total_visits += visits
                    total_spend += spend

                    # Calcular cambios
                    visit_change = ""
                    cost_change_html = ""

                    if prev_visits is not None:
                        change_text, direction = calculate_change(prev_visits, visits)
                        visit_change = f'<div class="change change-{direction}">{change_text}</div>'

                    if prev_cost is not None and cost > 0:
                        change_text, direction = calculate_change_cost(prev_cost, cost)
                        cost_class = "cost-improved" if direction == "improved" else ("cost-worse" if direction == "worse" else "")
                        cost_change_html = f'<div class="{cost_class}" style="font-size: 11px; margin-top: 3px;">{change_text}</div>'

                    prev_visits = visits
                    prev_cost = cost if cost > 0 else prev_cost

                    html += f"""
                        <td class="metric-cell">
                            <span class="metric-value">{format_number(visits)}</span>
                            <span class="metric-label">visitas</span>
                            {visit_change}
                            <div style="margin-top: 8px; font-size: 13px; color: #4A5568;">
                                {format_currency(cost)}/visita
                                {cost_change_html}
                            </div>
                        </td>
"""
                else:
                    html += """
                        <td class="metric-cell">
                            <span style="color: #CBD5E0;">-</span>
                        </td>
"""

            # Total del período
            avg_cost = total_spend / total_visits if total_visits > 0 else 0
            html += f"""
                        <td class="metric-cell" style="background: #F7FAFC; font-weight: 700;">
                            <span class="metric-value">{format_number(total_visits)}</span>
                            <span class="metric-label">visitas</span>
                            <div style="margin-top: 8px; font-size: 13px; color: #4A5568;">
                                {format_currency(avg_cost)}/visita
                            </div>
                        </td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
"""

    html += """
        </div>

        <!-- RECOMENDACIONES ESTRATÉGICAS -->
        <div class="section">
            <h2 class="section-title">💡 Recomendaciones Estratégicas</h2>
            <div class="recommendations">
"""

    # Generar recomendaciones basadas en datos
    recommendations = []

    # Analizar rendimiento por proyecto
    best_cost_per_lpv = None
    best_project = None
    worst_cost_per_lpv = 0
    worst_project = None

    for adset_name, months_data in adsets_comparison.items():
        total_spend = sum(m['spend'] for m in months_data.values())
        total_lpv = sum(m['landing_page_views'] for m in months_data.values())
        avg_cost = total_spend / total_lpv if total_lpv > 0 else 0

        if avg_cost > 0:
            if best_cost_per_lpv is None or avg_cost < best_cost_per_lpv:
                best_cost_per_lpv = avg_cost
                best_project = adset_name
            if avg_cost > worst_cost_per_lpv:
                worst_cost_per_lpv = avg_cost
                worst_project = adset_name

    # Recomendación 1: Optimizar mejor proyecto
    if best_project:
        recommendations.append({
            'type': 'expansion',
            'title': f'Escalar presupuesto en {best_project}',
            'desc': f'Este proyecto tiene el mejor costo por visita del período ({format_currency(best_cost_per_lpv)}). Aumentar la inversión aquí probablemente genere el mejor ROI.',
            'impact': 'Alto impacto - Mejora inmediata en eficiencia'
        })

    # Recomendación 2: Optimizar peor proyecto
    if worst_project and worst_cost_per_lpv > best_cost_per_lpv * 1.5:
        recommendations.append({
            'type': 'optimization',
            'title': f'Optimizar o pausar {worst_project}',
            'desc': f'El costo por visita ({format_currency(worst_cost_per_lpv)}) es significativamente más alto que el promedio. Considerar: (1) Refinar audiencia, (2) Mejorar creatividades, (3) Ajustar ubicaciones.',
            'impact': 'Medio impacto - Reducción de costos'
        })

    # Recomendación 3: Diversificar objetivos
    recommendations.append({
        'type': 'testing',
        'title': 'Implementar campaña de conversiones (leads)',
        'desc': 'Actualmente todas las campañas están optimizadas para tráfico. Crear una campaña paralela optimizada para "leads" o "mensajes" podría capturar usuarios con mayor intención de compra desde el inicio.',
        'impact': 'Alto impacto - Nueva fuente de leads calificados'
    })

    # Recomendación 4: Retargeting
    recommendations.append({
        'type': 'expansion',
        'title': 'Crear campaña de retargeting para visitantes',
        'desc': f'Con {format_number(sum(totals_by_month[m]["lpv"] for m in months_order if m in totals_by_month))} visitas al sitio en 4 meses, hay una audiencia considerable para retargeting. Crear anuncios específicos para quienes visitaron pero no convirtieron.',
        'impact': 'Alto impacto - Mayor tasa de conversión'
    })

    # Recomendación 5: Video vs Estático
    recommendations.append({
        'type': 'testing',
        'title': 'A/B testing: Video vs Imagen estática',
        'desc': 'Analizar rendimiento de videos vs imágenes estáticas por proyecto. Los insights pueden ayudar a optimizar el tipo de creatividad según el proyecto.',
        'impact': 'Medio impacto - Optimización de creatividades'
    })

    # Recomendación 6: Lookalike audiences
    recommendations.append({
        'type': 'expansion',
        'title': 'Crear audiencias similares (Lookalike) de visitantes',
        'desc': 'Usar la base de visitantes web para crear audiencias lookalike. Esto permite alcanzar personas similares a quienes ya mostraron interés en los proyectos.',
        'impact': 'Alto impacto - Expansión de audiencia calificada'
    })

    # Recomendación 7: Estacionalidad
    recommendations.append({
        'type': 'optimization',
        'title': 'Ajustar presupuesto según estacionalidad',
        'desc': 'Analizar qué meses tuvieron mejor rendimiento y ajustar presupuestos futuros según estos patrones estacionales en el mercado inmobiliario.',
        'impact': 'Medio impacto - Eficiencia presupuestaria'
    })

    # Renderizar recomendaciones
    for rec in recommendations:
        type_class = f"type-{rec['type']}"
        html += f"""
                <div class="recommendation-item">
                    <span class="recommendation-type {type_class}">{rec['type'].upper()}</span>
                    <div class="recommendation-title">{rec['title']}</div>
                    <div class="recommendation-desc">{rec['desc']}</div>
                    <div class="recommendation-impact">💥 {rec['impact']}</div>
                </div>
"""

    html += """
            </div>
        </div>
"""

    # Agregar detalle de anuncios por proyecto
    html += """
        <div class="section">
            <h2 class="section-title">🎯 Detalle de Anuncios por Proyecto</h2>
"""

    # Cargar datos de diciembre (más recientes) para mostrar anuncios
    if 'Dic' in monthly_data:
        dic_data = monthly_data['Dic']
        images_dir = "/Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC/ASPA/meta/images"

        # Agrupar anuncios por conjunto
        anuncios_por_conjunto = defaultdict(list)
        for anuncio in dic_data.get('anuncios', []):
            conjunto = anuncio.get('adset_name', 'Sin conjunto')
            anuncios_por_conjunto[conjunto].append(anuncio)

        for conjunto_name in sorted(anuncios_por_conjunto.keys()):
            html += f"""
            <h3 class="section-subtitle">{conjunto_name}</h3>
            <div class="ads-grid">
"""

            for anuncio in anuncios_por_conjunto[conjunto_name]:
                ad_name = anuncio.get('ad_name', 'Sin nombre')
                ad_reach = anuncio.get('reach', 0)
                ad_spend = anuncio.get('spend', 0)
                ad_ctr = anuncio.get('ctr', 0)
                ad_lpv = anuncio.get('actions', {}).get('landing_page_view', 0)
                ad_clicks = anuncio.get('actions', {}).get('link_click', 0)
                ad_visits = ad_lpv if ad_lpv > 0 else ad_clicks
                cost_lpv = ad_spend / ad_visits if ad_visits > 0 else 0

                # Buscar imagen - usar ad_id
                ad_id = anuncio.get('ad_id', '')
                image_base64 = None

                if ad_id and os.path.exists(images_dir):
                    for img_file in os.listdir(images_dir):
                        if img_file.startswith(ad_id):
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
                                <span class="ad-metric-label">Visitas web:</span>
                                <span class="ad-metric-value">{format_number(ad_visits)}</span>
                            </div>
                            <div class="ad-metric">
                                <span class="ad-metric-label">Costo/visita:</span>
                                <span class="ad-metric-value">{format_currency(cost_lpv)}</span>
                            </div>
                            <div class="ad-metric">
                                <span class="ad-metric-label">CTR:</span>
                                <span class="ad-metric-value">{ad_ctr:.2f}%</span>
                            </div>
                            <div class="ad-metric">
                                <span class="ad-metric-label">Alcance:</span>
                                <span class="ad-metric-value">{format_number(ad_reach)}</span>
                            </div>
                            <div class="ad-metric">
                                <span class="ad-metric-label">Inversión:</span>
                                <span class="ad-metric-value">{format_currency(ad_spend)}</span>
                            </div>
                        </div>
                    </div>
                </div>
"""

            html += """
            </div>
"""

    html += """
        </div>
    </div>
</body>
</html>
"""

    return html

def main():
    print("📊 Generando reporte completo de ASPA...")

    # Cargar datos mensuales
    monthly_data = load_monthly_data()

    if not monthly_data:
        print("❌ No se encontraron datos mensuales")
        return

    print(f"✅ Datos cargados: {', '.join(monthly_data.keys())}")

    # Generar HTML
    html = generate_html_report(monthly_data)

    # Guardar
    output_path = "/Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC/ASPA/meta/ASPA_REPORTE_COMPLETO.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Reporte generado: {output_path}")

if __name__ == "__main__":
    main()
