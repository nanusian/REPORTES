#!/usr/bin/env python3
"""
Generador de reporte COMPLETO con comparación mensual integrada
Incluye: Comparación + Detalle completo con imágenes
"""

import json
import sys
import os
import base64
from datetime import datetime
from pathlib import Path

def format_currency(value):
    if value is None:
        return "$0"
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(value):
    if value is None:
        return "0"
    return f"{int(value):,}".replace(",", ".")

def calculate_change(old, new):
    """Calcula cambio porcentual"""
    if old == 0:
        return "+100%" if new > 0 else "0%"
    change = ((new - old) / old) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"

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

def get_campaign_key_result(conjunto):
    """Identifica el resultado clave basado en el nombre de la campaña"""
    name = conjunto['adset_name'].lower()

    # Reproducciones de video (debe ir primero)
    if 'reprod' in name or 'video' in name or 'visualiz' in name or 'fiestas' in name:
        video_views = conjunto.get('actions', {}).get('video_view', 0)
        cost = conjunto.get('cost_per_actions', {}).get('video_view', 0)
        return {
            'type': 'Visualizaciones',
            'value': video_views,
            'cost': cost,
            'label': 'visualizaciones'
        }

    # Tráfico = Clicks (debe ir ANTES que hormigón para "Tráfico - hormigón")
    elif 'tráfico' in name or 'trafico' in name:
        clicks = conjunto.get('actions', {}).get('link_click', 0)
        cost = conjunto.get('cost_per_actions', {}).get('link_click', 0)
        if clicks == 0:
            return {
                'type': 'Alcance',
                'value': conjunto.get('reach', 0),
                'cost': conjunto.get('spend', 0) / conjunto.get('reach', 1) if conjunto.get('reach', 0) > 0 else 0,
                'label': 'personas alcanzadas'
            }
        return {
            'type': 'Clicks',
            'value': clicks,
            'cost': cost,
            'label': 'clicks'
        }

    # VÉNETO y AÑELO = Conversaciones (forzado)
    elif 'véneto' in name or 'veneto' in name or 'hormigón' in name or 'hormigon' in name or 'mensaje' in name or 'añelo' in name or 'anelo' in name:
        conversations = conjunto.get('actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
        cost = conjunto.get('cost_per_actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
        return {
            'type': 'Conversaciones',
            'value': conversations,
            'cost': cost,
            'label': 'conversaciones'
        }

    # Interacción
    elif 'interacción' in name or 'interaccion' in name:
        engagement = conjunto.get('actions', {}).get('post_engagement', 0)
        cost = conjunto.get('cost_per_actions', {}).get('post_engagement', 0)
        return {
            'type': 'Interacciones',
            'value': engagement,
            'cost': cost,
            'label': 'interacciones'
        }

    # Default: Alcance
    else:
        return {
            'type': 'Alcance',
            'value': conjunto.get('reach', 0),
            'cost': conjunto.get('spend', 0) / conjunto.get('reach', 1) if conjunto.get('reach', 0) > 0 else 0,
            'label': 'personas alcanzadas'
        }

def generate_full_report(json_old_path, json_new_path):
    """Genera reporte completo: Comparación + Detalle con imágenes"""

    def aggregate_by_campaign(conjuntos_list, adset_campaign_map):
        """Agrega conjuntos de anuncios a nivel de campaña, sumando métricas."""
        campaigns = {}
        for c in conjuntos_list:
            camp = c['adset_name']  # usar adset_name directo para evitar colisiones de mapeo
            if camp not in campaigns:
                campaigns[camp] = {
                    'adset_name': camp,
                    'spend': 0, 'reach': 0, 'impressions': 0,
                    'actions': {}, 'cost_per_actions': {}
                }
            agg = campaigns[camp]
            agg['spend'] += c.get('spend', 0)
            agg['reach'] += c.get('reach', 0)
            agg['impressions'] += c.get('impressions', 0)
            for k, v in c.get('actions', {}).items():
                agg['actions'][k] = agg['actions'].get(k, 0) + v
        # Recalcular cost_per_actions desde spend agregado
        for agg in campaigns.values():
            for action_type, count in agg['actions'].items():
                if count > 0:
                    agg['cost_per_actions'][action_type] = agg['spend'] / count
        return campaigns

    # Leer JSONs
    with open(json_old_path, 'r', encoding='utf-8') as f:
        data_old = json.load(f)

    with open(json_new_path, 'r', encoding='utf-8') as f:
        data_new = json.load(f)

    cliente = data_new['metadata']['cliente'].upper()
    metadata = data_new['metadata']
    resumen = data_new['resumen']
    conjuntos = data_new['conjuntos_de_anuncios']
    anuncios = data_new['anuncios']
    analisis = data_new['analisis']
    insights = analisis.get('insights', [])

    # Formatear períodos
    periodo_raw = metadata['periodo']
    fecha_inicio, fecha_fin = periodo_raw.split('_')
    mes_actual = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%B %Y')
    mes_anterior = datetime.strptime(data_old['metadata']['periodo'].split('_')[0], '%Y-%m-%d').strftime('%B %Y')

    mes_esp = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    for eng, esp in mes_esp.items():
        mes_actual = mes_actual.replace(eng, esp)
        mes_anterior = mes_anterior.replace(eng, esp)

    # Agrupar anuncios por conjunto
    anuncios_por_conjunto = {}
    for anuncio in anuncios:
        adset = anuncio['adset_name']
        if adset not in anuncios_por_conjunto:
            anuncios_por_conjunto[adset] = []
        anuncios_por_conjunto[adset].append(anuncio)

    # Crear mapeo de adset_name a campaign_name
    adset_to_campaign = {}
    for anuncio in data_new['anuncios']:
        adset_to_campaign[anuncio['adset_name']] = anuncio['campaign_name']
    for anuncio in data_old['anuncios']:
        if anuncio['adset_name'] not in adset_to_campaign:
            adset_to_campaign[anuncio['adset_name']] = anuncio['campaign_name']

    # Obtener conjuntos agregados por campaña
    conjuntos_old = aggregate_by_campaign(data_old['conjuntos_de_anuncios'], adset_to_campaign)
    conjuntos_new = aggregate_by_campaign(
        [c for c in data_new['conjuntos_de_anuncios'] if c.get('spend', 0) > 0],
        adset_to_campaign
    )
    all_campaigns = set(conjuntos_new.keys())

    # === GENERAR HTML ===
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Completo - {cliente}</title>
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
            border-bottom: 4px solid #4A5568;
            margin-bottom: 50px;
        }}

        .header h1 {{
            font-size: 48px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 15px;
        }}

        .header .subtitle {{
            font-size: 26px;
            color: #718096;
            font-weight: 300;
            margin-bottom: 10px;
        }}

        .header .period {{
            font-size: 20px;
            color: #4A5568;
            margin-top: 15px;
            font-weight: 500;
        }}

        /* SECTION */
        .section {{
            margin-bottom: 60px;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 25px;
            padding-bottom: 12px;
            border-bottom: 3px solid #4A5568;
        }}

        .section-subtitle {{
            font-size: 20px;
            color: #4A5568;
            margin-bottom: 20px;
        }}

        /* COMPARISON TABLE */
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }}

        .comparison-table th {{
            background: #4A5568;
            color: white;
            padding: 16px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
        }}

        .comparison-table td {{
            padding: 16px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 15px;
        }}

        .comparison-table tbody tr:hover {{
            background: #f7fafc;
        }}

        .campaign-name {{
            font-weight: 600;
            color: #1a202c;
            font-size: 16px;
        }}

        .result-type {{
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
            margin-top: 3px;
        }}

        .metric-cell {{
            text-align: center;
        }}

        .metric-value {{
            font-size: 22px;
            font-weight: 700;
            color: #1a202c;
        }}

        .metric-label {{
            font-size: 11px;
            color: #718096;
            text-transform: uppercase;
            margin-top: 3px;
        }}

        .change {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 14px;
            margin-top: 5px;
        }}

        .change-positive {{
            background: #C6F6D5;
            color: #22543D;
        }}

        .change-negative {{
            background: #FED7D7;
            color: #742A2A;
        }}

        .change-neutral {{
            background: #E2E8F0;
            color: #2D3748;
        }}

        .cost-improved {{
            color: #22543D;
            font-weight: 700;
        }}

        .cost-worse {{
            color: #742A2A;
            font-weight: 700;
        }}

        .new-badge {{
            display: inline-block;
            background: #90CDF4;
            color: #1A365D;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 8px;
        }}

        .removed-badge {{
            display: inline-block;
            background: #FEB2B2;
            color: #742A2A;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 8px;
        }}

        /* SUMMARY CARDS */
        .summary {{
            display: flex;
            gap: 25px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}

        .summary-card {{
            flex: 1;
            min-width: 220px;
            background: #f7fafc;
            padding: 25px;
            border-left: 4px solid #4A5568;
            border-radius: 4px;
        }}

        .summary-title {{
            font-size: 13px;
            color: #718096;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}

        .summary-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 8px;
        }}

        .summary-change {{
            font-size: 15px;
            font-weight: 600;
        }}

        /* METRICS GRID */
        .metrics-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            flex: 1;
            min-width: 200px;
            background: #f7fafc;
            padding: 25px;
            border-left: 4px solid #4A5568;
            border-radius: 4px;
        }}

        .metric-card .metric-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 8px;
        }}

        .metric-card .metric-label {{
            font-size: 13px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* TABLE */
        table.detail-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
        }}

        table.detail-table thead {{
            background: #4A5568;
            color: white;
        }}

        table.detail-table th {{
            padding: 14px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
        }}

        table.detail-table td {{
            padding: 14px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}

        table.detail-table tbody tr:hover {{
            background: #f7fafc;
        }}

        /* INSIGHTS */
        .insights {{
            margin: 30px 0;
        }}

        .insight {{
            background: #f7fafc;
            padding: 22px;
            margin-bottom: 18px;
            border-left: 4px solid #4A5568;
            border-radius: 4px;
        }}

        .insight-alerta {{
            border-left-color: #E53E3E;
            background: #FFF5F5;
        }}

        .insight-oportunidad {{
            border-left-color: #D69E2E;
            background: #FFFAF0;
        }}

        .insight-exito {{
            border-left-color: #38A169;
            background: #F0FFF4;
        }}

        .insight-title {{
            font-size: 17px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 10px;
        }}

        .insight-description {{
            font-size: 15px;
            color: #4A5568;
            margin-bottom: 10px;
            line-height: 1.6;
        }}

        .insight-action {{
            font-size: 14px;
            color: #2D3748;
            font-weight: 500;
        }}

        /* ADSET DETAIL */
        .adset-detail {{
            margin: 50px 0;
            padding: 35px;
            background: #f7fafc;
            border-radius: 8px;
            page-break-inside: avoid;
        }}

        .adset-header {{
            background: #4A5568;
            color: white;
            padding: 25px;
            margin: -35px -35px 25px -35px;
            border-radius: 8px 8px 0 0;
        }}

        .adset-title {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 18px;
        }}

        .adset-metrics {{
            display: flex;
            gap: 35px;
            flex-wrap: wrap;
        }}

        .adset-metric {{
            flex: 1;
            min-width: 160px;
        }}

        .adset-metric-value {{
            font-size: 26px;
            font-weight: 700;
        }}

        .adset-metric-label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            margin-top: 5px;
        }}

        /* AD ITEM */
        .ad-item {{
            background: white;
            padding: 30px;
            margin-bottom: 25px;
            border-left: 4px solid #718096;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            page-break-inside: avoid;
        }}

        .ad-header {{
            display: flex;
            flex-direction: column;
            gap: 25px;
            margin-bottom: 25px;
        }}

        .ad-image-container {{
            flex-shrink: 0;
            width: 100%;
            max-width: 350px;
            height: 250px;
            border-radius: 8px;
            overflow: hidden;
            background: #f7fafc;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #e2e8f0;
        }}

        .ad-image {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}

        .ad-info {{
            flex: 1;
        }}

        .ad-name {{
            font-size: 22px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 15px;
        }}

        .ad-copy {{
            font-size: 15px;
            color: #4A5568;
            line-height: 1.7;
            font-style: italic;
            padding: 18px;
            background: #f7fafc;
            border-radius: 4px;
            margin-bottom: 18px;
        }}

        .ad-metrics {{
            display: flex;
            gap: 25px;
            flex-wrap: wrap;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
        }}

        .ad-metric {{
            flex: 1;
            min-width: 110px;
            text-align: center;
        }}

        .ad-metric-value {{
            font-size: 22px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 6px;
        }}

        .ad-metric-label {{
            font-size: 11px;
            color: #718096;
            text-transform: uppercase;
        }}

        /* GLOSSARY */
        .glossary {{
            background: #f7fafc;
            padding: 35px;
            border-radius: 8px;
            margin-bottom: 50px;
        }}

        .glossary-item {{
            margin-bottom: 22px;
        }}

        .glossary-term {{
            font-size: 17px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 6px;
        }}

        .glossary-definition {{
            font-size: 15px;
            color: #4A5568;
            line-height: 1.6;
        }}

        /* DIVIDER */
        .divider {{
            height: 3px;
            background: linear-gradient(to right, #4A5568, transparent);
            margin: 60px 0;
        }}

        /* FOOTER */
        .footer {{
            margin-top: 80px;
            padding-top: 30px;
            border-top: 2px solid #e2e8f0;
            text-align: center;
            color: #718096;
            font-size: 14px;
        }}

        @media print {{
            body {{ background: white; padding: 0; font-size: 13px; }}
            .container {{ box-shadow: none; padding: 25px; max-width: 100%; }}
            .section {{ page-break-inside: avoid; margin-bottom: 30px; }}
            .section-title {{ font-size: 20px; margin-bottom: 15px; }}
            .header {{ padding: 25px 0; margin-bottom: 30px; }}
            .header h1 {{ font-size: 32px; }}
            .header .subtitle {{ font-size: 18px; }}

            /* Imágenes pequeñas en print */
            .ad-item {{ padding: 15px; margin-bottom: 12px; }}
            .ad-header {{ gap: 15px; }}
            .ad-image-container {{
                width: 120px !important;
                max-width: 120px !important;
                height: 120px !important;
                flex-shrink: 0;
            }}
            .ad-image {{ object-fit: cover; }}
            .ad-name {{ font-size: 15px; margin-bottom: 8px; }}
            .ad-copy {{ font-size: 12px; padding: 10px; margin-bottom: 10px; }}
            .ad-metric-value {{ font-size: 16px; }}
            .ad-metric-label {{ font-size: 10px; }}
            .ad-metrics {{ gap: 12px; padding-top: 10px; }}

            /* Resumen más compacto */
            .summary-card {{ padding: 15px; }}
            .summary-value {{ font-size: 22px; }}

            /* Tabla más compacta */
            .comparison-table th, .comparison-table td {{ padding: 10px 12px; font-size: 12px; }}
            .metric-value {{ font-size: 16px; }}

            /* Adset header compacto */
            .adset-section {{ padding: 20px; margin-bottom: 20px; }}
            .adset-title {{ font-size: 18px; }}
        }}

        /* RESPONSIVE MOBILE */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .container {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 32px;
            }}

            .header .subtitle {{
                font-size: 18px;
            }}

            .header .period {{
                font-size: 16px;
            }}

            .section-title {{
                font-size: 24px;
            }}

            .section-subtitle {{
                font-size: 16px;
            }}

            /* Tablas responsive */
            table {{
                font-size: 11px;
            }}

            table th, table td {{
                padding: 8px 4px;
            }}

            .comparison-table th,
            .comparison-table td {{
                padding: 10px 6px;
            }}

            /* Hacer tablas scrolleables horizontalmente */
            .table-container {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}

            /* Tarjetas de resumen en columna */
            .summary {{
                flex-direction: column;
            }}

            .summary-card {{
                min-width: 100%;
            }}

            /* Métricas en columna */
            .metrics-grid {{
                flex-direction: column;
            }}

            .metric-card {{
                min-width: 100%;
            }}

            /* Anuncios en columna */
            .ad-header {{
                flex-direction: column;
            }}

            .ad-image-container {{
                width: 100%;
                max-width: 100%;
                height: auto;
            }}

            .ad-image {{
                width: 100%;
                height: auto;
                max-height: none;
            }}

            .ad-metrics {{
                flex-wrap: wrap;
                gap: 10px;
            }}

            .ad-metric {{
                min-width: calc(50% - 5px);
            }}

            /* Adset metrics */
            .adset-metrics {{
                flex-direction: column;
                gap: 15px;
            }}

            .adset-metric {{
                min-width: 100%;
            }}

            /* Insights */
            .insight {{
                padding: 15px;
            }}

            /* Glossary */
            .glossary {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">

        <!-- HEADER -->
        <div class="header">
            <h1>{cliente}</h1>
            <div class="subtitle">Reporte Completo de Campaña Publicitaria</div>
            <div class="period">{mes_actual}</div>
        </div>

        <!-- SECCIÓN 1: COMPARACIÓN MENSUAL -->
        <div class="section">
            <h2 class="section-title">📊 Comparación Mensual</h2>
            <p class="section-subtitle">{mes_anterior} vs {mes_actual}</p>

            <table class="comparison-table">
                <thead>
                    <tr>
                        <th style="width: 25%;">Campaña</th>
                        <th style="width: 12%;">Resultado Clave</th>
                        <th style="width: 12%;">{mes_anterior}</th>
                        <th style="width: 12%;">{mes_actual}</th>
                        <th style="width: 13%;">Eficiencia vs. mes anterior</th>
                        <th style="width: 13%;">Costo/Resultado</th>
                        <th style="width: 13%;">Variación respecto a mes anterior</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Generar filas de comparación
    for campaign in sorted(all_campaigns):
        old_data = conjuntos_old.get(campaign)
        new_data = conjuntos_new.get(campaign)

        if old_data and new_data:
            # Campaña existe en ambos meses
            old_result = get_campaign_key_result(old_data)
            new_result = get_campaign_key_result(new_data)

            change_pct = calculate_change(old_result['value'], new_result['value'])

            # Clase de cambio para resultados
            if new_result['value'] > old_result['value']:
                change_class = 'change-positive'
            elif new_result['value'] < old_result['value']:
                change_class = 'change-negative'
            else:
                change_class = 'change-neutral'

            # NUEVO: Eficiencia de costo - INVERTIDO:
            # Cuando el costo BAJA (variación negativa) = VERDE (mejoró)
            # Cuando el costo SUBE (variación positiva) = ROJO (empeoró)
            cost_change_pct = calculate_change(old_result['cost'], new_result['cost'])

            if new_result['cost'] < old_result['cost'] and old_result['cost'] > 0:
                cost_change_class = 'change-positive'  # Verde
                cost_display = cost_change_pct
            elif new_result['cost'] > old_result['cost']:
                cost_change_class = 'change-negative'  # Rojo
                cost_display = cost_change_pct
            else:
                cost_change_class = 'change-neutral'
                cost_display = '0%'

            html += f"""
                <tr>
                    <td>
                        <div class="campaign-name">{campaign}</div>
                    </td>
                    <td>
                        <div class="result-type">{new_result['type']}</div>
                    </td>
                    <td class="metric-cell">
                        <div class="metric-value">{format_number(old_result['value'])}</div>
                        <div class="metric-label">{old_result['label']}</div>
                    </td>
                    <td class="metric-cell">
                        <div class="metric-value">{format_number(new_result['value'])}</div>
                        <div class="metric-label">{new_result['label']}</div>
                    </td>
                    <td class="metric-cell">
                        <span class="change {change_class}">{change_pct}</span>
                    </td>
                    <td class="metric-cell">
                        <div style="font-weight: 600; color: #1a202c;">{format_currency(new_result['cost'])}</div>
                        <div style="font-size: 11px; color: #718096; margin-top: 3px;">
                            Ant: {format_currency(old_result['cost'])}
                        </div>
                    </td>
                    <td class="metric-cell">
                        <span class="change {cost_change_class}">{cost_display}</span>
                    </td>
                </tr>
"""

        elif new_data:
            # Campaña nueva
            new_result = get_campaign_key_result(new_data)
            html += f"""
                <tr style="background: #F0F9FF;">
                    <td>
                        <div class="campaign-name">{campaign}<span class="new-badge">Nueva</span></div>
                    </td>
                    <td>
                        <div class="result-type">{new_result['type']}</div>
                    </td>
                    <td class="metric-cell" style="color: #CBD5E0;">-</td>
                    <td class="metric-cell">
                        <div class="metric-value">{format_number(new_result['value'])}</div>
                        <div class="metric-label">{new_result['label']}</div>
                    </td>
                    <td class="metric-cell">
                        <span class="change change-neutral">NUEVA</span>
                    </td>
                    <td class="metric-cell">
                        <div style="font-weight: 600; color: #1a202c;">{format_currency(new_result['cost'])}</div>
                    </td>
                    <td class="metric-cell" style="color: #718096;">-</td>
                </tr>
"""

        elif old_data:
            # Campaña pausada
            old_result = get_campaign_key_result(old_data)
            html += f"""
                <tr style="background: #FFF5F5;">
                    <td>
                        <div class="campaign-name">{campaign}<span class="removed-badge">Pausada</span></div>
                    </td>
                    <td>
                        <div class="result-type">{old_result['type']}</div>
                    </td>
                    <td class="metric-cell">
                        <div class="metric-value">{format_number(old_result['value'])}</div>
                        <div class="metric-label">{old_result['label']}</div>
                    </td>
                    <td class="metric-cell" style="color: #CBD5E0;">-</td>
                    <td class="metric-cell">
                        <span class="change change-neutral">PAUSADA</span>
                    </td>
                    <td class="metric-cell" style="color: #CBD5E0;">-</td>
                    <td class="metric-cell" style="color: #CBD5E0;">-</td>
                </tr>
"""

    html += """
                </tbody>
            </table>
        </div>

        <div class="divider"></div>
"""

    # SECCIÓN 2: RESUMEN EJECUTIVO MES ACTUAL
    html += f"""
        <div class="section">
            <h2 class="section-title">📈 Resumen Ejecutivo - {mes_actual}</h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{format_currency(resumen['inversion_total'])}</div>
                    <div class="metric-label">Inversión Total (ARS)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_number(resumen['alcance_total'])}</div>
                    <div class="metric-label">Alcance Total</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{format_number(resumen['impresiones_totales'])}</div>
                    <div class="metric-label">Impresiones</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{resumen['total_anuncios']}</div>
                    <div class="metric-label">Anuncios Corridos</div>
                </div>
            </div>
        </div>
"""

    # SECCIÓN 3: GLOSARIO
    html += """
        <div class="section">
            <h2 class="section-title">📚 Glosario de Métricas</h2>
            <div class="glossary">
                <div class="glossary-item">
                    <div class="glossary-term">Impresiones</div>
                    <div class="glossary-definition">Cantidad de veces que tu anuncio fue mostrado en pantalla, sin importar si fue clickeado o no.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">Alcance</div>
                    <div class="glossary-definition">Número de personas únicas que vieron tu anuncio al menos una vez.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">Frecuencia</div>
                    <div class="glossary-definition">Promedio de veces que cada persona vio tu anuncio (Impresiones ÷ Alcance). Idealmente debe estar entre 2-4.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">CTR (Click-Through Rate)</div>
                    <div class="glossary-definition">Porcentaje de personas que hicieron click después de ver el anuncio. Mide qué tan atractivo es el contenido.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">CPC (Costo Por Click)</div>
                    <div class="glossary-definition">Cuánto pagaste en promedio por cada click en tu anuncio.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">CPM (Costo Por Mil impresiones)</div>
                    <div class="glossary-definition">Cuánto pagaste por cada 1,000 veces que tu anuncio fue mostrado.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">Conversaciones iniciadas</div>
                    <div class="glossary-definition">Personas que iniciaron una conversación en Messenger o Instagram después de ver el anuncio.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">Costo por conversación</div>
                    <div class="glossary-definition">Cuánto pagaste en promedio por cada conversación iniciada.</div>
                </div>
            </div>
        </div>

        <div class="divider"></div>
"""

    # SECCIÓN 5: DETALLE POR CONJUNTO CON IMÁGENES
    html += f"""
        <div class="section">
            <h2 class="section-title">🎯 Detalle Completo por Campaña</h2>
            <p class="section-subtitle">Análisis detallado de cada anuncio con creatividades</p>
        </div>
"""

    for conjunto in conjuntos:
        if conjunto.get('spend', 0) == 0:
            continue

        adset_name = conjunto['adset_name']

        # Identificar la métrica clave del conjunto
        key_result = get_campaign_key_result(conjunto)
        result_value = key_result['value']
        result_cost = key_result['cost']
        result_type = key_result['type']

        html += f"""
        <div class="adset-detail">
            <div class="adset-header">
                <div class="adset-title">{adset_name}</div>
                <div class="adset-metrics">
                    <div class="adset-metric">
                        <div class="adset-metric-value">{format_number(result_value)}</div>
                        <div class="adset-metric-label">{result_type}</div>
                    </div>
                    <div class="adset-metric">
                        <div class="adset-metric-value">{format_currency(result_cost) if result_cost else '-'}</div>
                        <div class="adset-metric-label">Costo por {result_type}</div>
                    </div>
                    <div class="adset-metric">
                        <div class="adset-metric-value">{format_currency(conjunto['spend'])}</div>
                        <div class="adset-metric-label">Inversión Total</div>
                    </div>
                </div>
            </div>

            <h3 style="font-size: 20px; margin-bottom: 25px; color: #1a202c;">Anuncios en este conjunto:</h3>
"""

        # Si hay más de 1 anuncio, agregar tabla comparativa
        anuncios_conjunto = anuncios_por_conjunto.get(adset_name, [])
        if len(anuncios_conjunto) > 1:
            # Identificar el resultado clave del conjunto
            key_result = get_campaign_key_result(conjunto)
            key_metric_type = key_result['type']

            # Determinar etiqueta y campo de métrica según el tipo
            if key_metric_type == 'Conversaciones':
                result_label = 'Conversaciones'
                result_field = 'onsite_conversion.messaging_conversation_started_7d'
                cost_field = 'onsite_conversion.messaging_conversation_started_7d'
            elif key_metric_type == 'Interacciones':
                result_label = 'Interacciones'
                result_field = 'post_engagement'
                cost_field = 'post_engagement'
            elif key_metric_type == 'Clicks':
                result_label = 'Clicks'
                result_field = 'link_click'
                cost_field = 'link_click'
            elif key_metric_type == 'Visualizaciones':
                result_label = 'Visualizaciones'
                result_field = 'video_view'
                cost_field = 'video_view'
            else:  # Alcance
                result_label = 'Alcance'
                result_field = 'reach'
                cost_field = None

            html += f"""
            <div style="margin-bottom: 40px;">
                <h4 style="font-size: 16px; margin-bottom: 15px; color: #4A5568; text-transform: uppercase; letter-spacing: 0.5px;">Comparación de Anuncios - Resultado Clave: {key_metric_type}</h4>
                <table class="detail-table">
                    <thead>
                        <tr>
                            <th>Anuncio</th>
                            <th style="background: #38A169; color: white;">{result_label}</th>
                            <th style="background: #38A169; color: white;">Costo/{result_label}</th>
                            <th>Alcance</th>
                            <th>Impresiones</th>
                            <th>Frecuencia</th>
                            <th>CTR</th>
                            <th>CPC</th>
                            <th>CPM</th>
                            <th>Inversión</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for anuncio in anuncios_conjunto:
                # Extraer el resultado clave del anuncio
                if result_field == 'reach':
                    result_value = anuncio.get('reach', 0)
                    cost_per_result = anuncio.get('spend', 0) / result_value if result_value > 0 else 0
                else:
                    result_value = anuncio.get('actions', {}).get(result_field, 0)
                    cost_per_result = anuncio.get('cost_per_actions', {}).get(cost_field, 0)

                html += f"""
                        <tr>
                            <td><strong>{anuncio['ad_name']}</strong></td>
                            <td style="background: #F0FFF4; font-weight: 700; color: #22543D; font-size: 16px;">{format_number(result_value)}</td>
                            <td style="background: #F0FFF4; font-weight: 700; color: #22543D; font-size: 16px;">{format_currency(cost_per_result)}</td>
                            <td>{format_number(anuncio['reach'])}</td>
                            <td>{format_number(anuncio['impressions'])}</td>
                            <td>{anuncio['frequency']:.2f}</td>
                            <td>{anuncio['ctr']:.2f}%</td>
                            <td>{format_currency(anuncio['cpc'])}</td>
                            <td>{format_currency(anuncio['cpm'])}</td>
                            <td>{format_currency(anuncio['spend'])}</td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
            </div>
"""

        # Anuncios con imágenes
        for anuncio in anuncios_conjunto:
            # Buscar imagen path - puede estar en image_path o en creative.local_image_path
            image_path = anuncio.get('image_path', '')
            if not image_path:
                creative = anuncio.get('creative', {})
                image_path = creative.get('local_image_path', '')
                ad_copy = creative.get('body', '')
                ad_title = creative.get('title', '')
            else:
                creative = anuncio.get('creative', {})
                ad_copy = creative.get('body', '')
                ad_title = creative.get('title', '')

            # Imagen
            image_html = ''
            if image_path and os.path.exists(image_path):
                image_base64 = image_to_base64(image_path)
                if image_base64:
                    image_html = f'<img src="{image_base64}" class="ad-image" alt="Creatividad"/>'
                else:
                    image_html = '<div style="text-align: center; color: #CBD5E0; padding: 60px; font-size: 16px;">Sin imagen disponible</div>'
            else:
                image_html = '<div style="text-align: center; color: #CBD5E0; padding: 60px; font-size: 16px;">Sin imagen disponible</div>'

            # Texto
            copy_text = ''
            if ad_title:
                copy_text = f"<strong>{ad_title}</strong><br>"
            if ad_copy:
                if len(ad_copy) > 250:
                    ad_copy = ad_copy[:250] + '...'
                copy_text += ad_copy

            html += f"""
                <div class="ad-item">
                    <div class="ad-header">
                        <div class="ad-image-container">
                            {image_html}
                        </div>
                        <div class="ad-info">
                            <div class="ad-name">{anuncio['ad_name']}</div>
                            {f'<div class="ad-copy">"{copy_text}"</div>' if copy_text else ''}
                        </div>
                    </div>
                    <div class="ad-metrics">
                        <div class="ad-metric">
                            <div class="ad-metric-value">{format_number(anuncio['reach'])}</div>
                            <div class="ad-metric-label">Alcance</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{anuncio['frequency']:.2f}</div>
                            <div class="ad-metric-label">Frecuencia</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{anuncio['ctr']:.2f}%</div>
                            <div class="ad-metric-label">CTR</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{format_currency(anuncio['cpc'])}</div>
                            <div class="ad-metric-label">CPC</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{format_currency(anuncio['cpm'])}</div>
                            <div class="ad-metric-label">CPM</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{format_currency(anuncio['spend'])}</div>
                            <div class="ad-metric-label">Inversión</div>
                        </div>
                    </div>
                </div>
"""

        html += """
        </div>
"""

    # INSIGHTS AL FINAL
    if insights:
        html += """
        <div class="divider"></div>
        <div class="section">
            <h2 class="section-title">💡 Insights y Recomendaciones</h2>
            <div class="insights">
"""

        for insight in insights[:12]:
            tipo_clase = insight['tipo'].lower()
            emoji = {'alerta': '⚠️', 'oportunidad': '💡', 'exito': '✅'}.get(tipo_clase, '📊')

            html += f"""
                <div class="insight insight-{tipo_clase}">
                    <div class="insight-title">{emoji} {insight['titulo']}</div>
                    <div class="insight-description">{insight['descripcion']}</div>
                    <div class="insight-action">→ Acción sugerida: {insight['accion']}</div>
                </div>
"""

        html += """
            </div>
        </div>
"""

    # FOOTER
    html += f"""
        <div class="footer">
            <p>Reporte generado automáticamente el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}</p>
            <p style="margin-top: 10px; font-weight: 600;">{cliente} • {mes_actual}</p>
        </div>

    </div>
</body>
</html>
"""

    return html


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 generate_full_report.py <json_octubre> <json_noviembre>")
        sys.exit(1)

    json_old = sys.argv[1]
    json_new = sys.argv[2]

    print(f"\n📊 Generando reporte completo...")
    print(f"   Mes anterior: {json_old}")
    print(f"   Mes actual: {json_new}")

    # Leer JSON para obtener cliente y período
    with open(json_new, 'r', encoding='utf-8') as f:
        data_new = json.load(f)

    cliente = data_new['metadata']['cliente'].upper()
    periodo = data_new['metadata']['periodo'].split('_')[0]
    date_obj = datetime.strptime(periodo, '%Y-%m-%d')
    mes_folder = date_obj.strftime('%b-%y').upper()  # NOV-25

    # Crear carpeta de salida organizada: output/ENTREGABLES/MES/CLIENTE/
    output_dir = Path(f"output/ENTREGABLES/{mes_folder}/{cliente}")
    output_dir.mkdir(parents=True, exist_ok=True)

    html = generate_full_report(json_old, json_new)

    # Guardar en carpeta organizada
    output_path = output_dir / f"{cliente}_REPORTE_COMPLETO.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Reporte completo generado: {output_path}\n")
    return output_path


if __name__ == "__main__":
    main()
