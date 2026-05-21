#!/usr/bin/env python3
"""
Generador de reportes HTML desde datos de Meta Ads
Versión optimizada - HTML limpio y responsivo
"""

import json
import sys
import os
import base64
from datetime import datetime
from pathlib import Path

def format_currency(value):
    """Formatea números como moneda ARS"""
    if value is None:
        return "$0"
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(value):
    """Formatea números con separador de miles"""
    if value is None:
        return "0"
    return f"{int(value):,}".replace(",", ".")

def image_to_base64(image_path):
    """Convierte una imagen a base64 para embeber en HTML"""
    try:
        if not os.path.exists(image_path):
            return None

        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')

            # Detectar tipo de imagen
            ext = Path(image_path).suffix.lower()
            mime_type = 'image/jpeg'
            if ext == '.png':
                mime_type = 'image/png'
            elif ext == '.gif':
                mime_type = 'image/gif'

            return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        print(f"⚠️  Error convirtiendo imagen: {e}")
        return None

def generate_html_report(json_path):
    """Genera HTML desde JSON de análisis"""

    # Leer JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data['metadata']
    resumen = data['resumen']
    conjuntos = data['conjuntos_de_anuncios']
    anuncios = data['anuncios']
    analisis = data['analisis']
    insights = analisis.get('insights', [])

    cliente = metadata['cliente'].upper()
    periodo_raw = metadata['periodo']

    # Formatear período
    fecha_inicio, fecha_fin = periodo_raw.split('_')
    mes_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%B %Y')
    mes_inicio_esp = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
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

    # Obtener análisis de conjuntos (con objetivos detectados)
    adsets_analysis = analisis.get('adsets_analysis', [])

    # HTML Template
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Campaña - {cliente}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            color: #2d3748;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        /* Header */
        .header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 3px solid #4A5568;
            margin-bottom: 40px;
        }}

        .header h1 {{
            font-size: 42px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 24px;
            color: #718096;
            font-weight: 300;
        }}

        .header .period {{
            font-size: 18px;
            color: #4A5568;
            margin-top: 15px;
            font-weight: 500;
        }}

        /* Section */
        .section {{
            margin-bottom: 50px;
        }}

        .section-title {{
            font-size: 28px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #4A5568;
        }}

        /* Metrics Grid */
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

        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 8px;
        }}

        .metric-label {{
            font-size: 13px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Table */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}

        thead {{
            background: #4A5568;
            color: white;
        }}

        th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}

        tbody tr:hover {{
            background: #f7fafc;
        }}

        /* Insights */
        .insights {{
            margin: 30px 0;
        }}

        .insight {{
            background: #f7fafc;
            padding: 20px;
            margin-bottom: 15px;
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
            font-size: 16px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 8px;
        }}

        .insight-description {{
            font-size: 14px;
            color: #4A5568;
            margin-bottom: 8px;
        }}

        .insight-action {{
            font-size: 13px;
            color: #2D3748;
            font-weight: 500;
        }}

        /* AdSet Detail */
        .adset-detail {{
            margin: 40px 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .adset-header {{
            background: #4A5568;
            color: white;
            padding: 20px 25px;
        }}

        .adset-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 12px;
        }}

        .adset-metrics {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}

        .adset-metric {{
            flex: 1;
            min-width: 150px;
        }}

        .adset-metric-value {{
            font-size: 22px;
            font-weight: 700;
        }}

        .adset-metric-label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
        }}

        /* Tabla comparativa de anuncios */
        .comparison-table-wrap {{
            overflow-x: auto;
            background: white;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        .comparison-table thead tr {{
            background: #edf2f7;
        }}

        .comparison-table th {{
            padding: 11px 14px;
            text-align: center;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            color: #4A5568;
            border-bottom: 2px solid #cbd5e0;
            white-space: nowrap;
        }}

        .comparison-table th.col-ad {{
            text-align: left;
            min-width: 200px;
        }}

        .comparison-table td {{
            padding: 14px;
            border-bottom: 1px solid #e2e8f0;
            text-align: center;
            vertical-align: middle;
            color: #2d3748;
        }}

        .comparison-table td.col-ad {{
            text-align: left;
        }}

        .comparison-table tbody tr:hover {{
            background: #f7fafc;
        }}

        .comparison-table tbody tr:last-child td {{
            border-bottom: none;
        }}

        .ad-cell {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .ad-thumb {{
            flex-shrink: 0;
            width: 60px;
            height: 60px;
            border-radius: 6px;
            overflow: hidden;
            background: #edf2f7;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #e2e8f0;
        }}

        .ad-thumb img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .ad-cell-name {{
            font-weight: 600;
            color: #1a202c;
            font-size: 14px;
        }}

        .metric-highlight {{
            font-weight: 700;
            color: #1a202c;
        }}

        .tag-best {{
            display: inline-block;
            background: #c6f6d5;
            color: #22543d;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: 4px;
            vertical-align: middle;
        }}

        .tag-low {{
            display: inline-block;
            background: #fed7d7;
            color: #742a2a;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: 4px;
            vertical-align: middle;
        }}

        /* Glossary */
        .glossary {{
            background: #f7fafc;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 40px;
        }}

        .glossary-item {{
            margin-bottom: 20px;
        }}

        .glossary-term {{
            font-size: 16px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 5px;
        }}

        .glossary-definition {{
            font-size: 14px;
            color: #4A5568;
        }}

        /* Footer */
        .footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #718096;
            font-size: 13px;
        }}

        @media print {{
            @page {{ size: A4 landscape; margin: 12mm 15mm; }}
            body {{ background: white; padding: 0; font-size: 11px; }}
            .container {{ box-shadow: none; padding: 0; max-width: 100%; }}

            /* Header compacto */
            .header {{ padding: 16px 20px; margin-bottom: 14px; }}
            .header h1 {{ font-size: 22px; }}
            .header .subtitle {{ font-size: 14px; }}

            /* Métricas resumen más pequeñas */
            .metrics-grid {{ gap: 8px; margin-bottom: 14px; }}
            .metric-card {{ padding: 10px 12px; }}
            .metric-value {{ font-size: 20px; }}
            .metric-label {{ font-size: 10px; }}

            /* Secciones sin sombra */
            .adset-detail {{ box-shadow: none; border: 1px solid #e2e8f0; margin-bottom: 14px; page-break-inside: avoid; }}
            .adset-header {{ padding: 10px 14px; }}
            .adset-title {{ font-size: 13px; }}

            /* Tablas compactas */
            .comparison-table-wrap {{ overflow: visible; }}
            .comparison-table {{ font-size: 10px; width: 100%; }}
            .comparison-table th {{ padding: 6px 8px; font-size: 9px; }}
            .comparison-table td {{ padding: 6px 8px; }}
            .comparison-table th.col-ad {{ min-width: 140px; }}

            /* Miniaturas más pequeñas */
            .ad-thumb {{ width: 36px; height: 36px; flex-shrink: 0; }}
            .ad-cell {{ gap: 7px; }}
            .ad-cell-name {{ font-size: 11px; }}
            .tag-best, .tag-low {{ font-size: 9px; padding: 1px 4px; }}

            /* Insights compactos */
            .insights {{ margin-top: 12px; }}
            .insight {{ padding: 8px 12px; margin-bottom: 6px; }}
            .insight-title {{ font-size: 11px; }}
            .insight-description, .insight-action {{ font-size: 10px; }}

            /* No cortar filas entre páginas */
            .comparison-table tbody tr {{ page-break-inside: avoid; }}
            .adset-metrics {{ gap: 6px; }}
            .adset-metric {{ padding: 6px 10px; }}
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
                font-size: 28px;
            }}

            .header .subtitle {{
                font-size: 18px;
            }}

            .section-title {{
                font-size: 24px;
            }}

            /* Tablas responsive */
            table {{
                font-size: 12px;
            }}

            table th, table td {{
                padding: 8px 4px;
            }}

            /* Hacer tablas scrolleables horizontalmente */
            .table-container {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
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
            }}

            .ad-metrics {{
                flex-wrap: wrap;
                gap: 10px;
            }}

            .ad-metric {{
                min-width: calc(50% - 5px);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">

        <!-- HEADER -->
        <div class="header">
            <h1>{cliente}</h1>
            <div class="subtitle">Reporte de Campaña Publicitaria</div>
            <div class="period">{mes_inicio}</div>
        </div>

        <!-- RESUMEN EJECUTIVO -->
        <div class="section">
            <h2 class="section-title">Resumen Ejecutivo</h2>

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

            <h3 style="font-size: 20px; margin: 30px 0 15px 0; color: #1a202c;">Rendimiento por Campaña</h3>

            <table>
                <thead>
                    <tr>
                        <th>Campaña</th>
                        <th>Alcance</th>
                        <th>Frecuencia</th>
                        <th>Inversión</th>
                        <th>Resultado Principal</th>
                        <th>Costo por Resultado</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Tabla de conjuntos - usar análisis de conjuntos si está disponible
    if adsets_analysis:
        # Crear un mapa de nombre de conjunto a su análisis
        adset_analysis_map = {a['name']: a for a in adsets_analysis}

        for conjunto in conjuntos:
            adset_name = conjunto['adset_name']
            analysis = adset_analysis_map.get(adset_name, {})

            # Usar análisis si está disponible, si no, fallback a conversaciones
            if analysis and 'main_result' in analysis:
                result_label = analysis.get('objective_short_label', 'resultados')
                main_result = analysis.get('main_result', 0)
                cost_per_result = analysis.get('cost_per_result', 0)
            else:
                result_label = 'conversaciones'
                main_result = conjunto.get('actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
                cost_per_result = conjunto.get('cost_per_actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)

            html += f"""
                    <tr>
                        <td><strong>{adset_name}</strong></td>
                        <td>{format_number(conjunto['reach'])}</td>
                        <td>{conjunto['frequency']:.2f}</td>
                        <td>{format_currency(conjunto['spend'])}</td>
                        <td>{format_number(main_result)} {result_label}</td>
                        <td>{format_currency(cost_per_result) if cost_per_result else '-'}</td>
                    </tr>
"""
    else:
        # Fallback para compatibilidad con JSONs antiguos
        for conjunto in conjuntos:
            conversations = conjunto.get('actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
            cost_per_conv = conjunto.get('cost_per_actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)

            html += f"""
                    <tr>
                        <td><strong>{conjunto['adset_name']}</strong></td>
                        <td>{format_number(conjunto['reach'])}</td>
                        <td>{conjunto['frequency']:.2f}</td>
                        <td>{format_currency(conjunto['spend'])}</td>
                        <td>{conversations} conversaciones</td>
                        <td>{format_currency(cost_per_conv) if cost_per_conv else '-'}</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
"""

    # INSIGHTS
    if insights:
        html += """
        <div class="section">
            <h2 class="section-title">Insights y Recomendaciones</h2>
            <div class="insights">
"""

        for insight in insights[:10]:
            tipo_clase = insight['tipo'].lower()
            emoji = {'alerta': '⚠️', 'oportunidad': '💡', 'exito': '✅'}.get(tipo_clase, '📊')

            html += f"""
                <div class="insight insight-{tipo_clase}">
                    <div class="insight-title">{emoji} {insight['titulo']}</div>
                    <div class="insight-description">{insight['descripcion']}</div>
                    <div class="insight-action">→ {insight['accion']}</div>
                </div>
"""

        html += """
            </div>
        </div>
"""

    # GLOSARIO
    html += """
        <div class="section">
            <h2 class="section-title">Glosario de Métricas</h2>
            <div class="glossary">
                <div class="glossary-item">
                    <div class="glossary-term">Impresiones</div>
                    <div class="glossary-definition">Cantidad de veces que tu anuncio fue mostrado en pantalla.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">Alcance</div>
                    <div class="glossary-definition">Número de personas únicas que vieron tu anuncio al menos una vez.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">Frecuencia</div>
                    <div class="glossary-definition">Promedio de veces que cada persona vio tu anuncio. Idealmente entre 2-4.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">CTR (Click-Through Rate)</div>
                    <div class="glossary-definition">Porcentaje de personas que hicieron click después de ver el anuncio.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">CPC (Costo Por Click)</div>
                    <div class="glossary-definition">Cuánto pagaste en promedio por cada click en tu anuncio.</div>
                </div>
                <div class="glossary-item">
                    <div class="glossary-term">CPM (Costo Por Mil impresiones)</div>
                    <div class="glossary-definition">Cuánto pagaste por cada 1,000 veces que tu anuncio fue mostrado.</div>
                </div>
            </div>
        </div>
"""

    # DETALLE POR CONJUNTO — tablas comparativas
    adset_analysis_map = {a['name']: a for a in adsets_analysis} if adsets_analysis else {}

    html += """
        <div class="section">
            <h2 class="section-title">Comparativa por Campaña</h2>
"""

    for conjunto in conjuntos:
        adset_name = conjunto['adset_name']
        analysis = adset_analysis_map.get(adset_name, {})

        if analysis and 'main_result' in analysis:
            result_label = analysis.get('objective_label', 'Resultados')
            short_label = analysis.get('objective_short_label', 'resultados')
            main_result = analysis.get('main_result', 0)
            cost_per_result = analysis.get('cost_per_result', 0)
        else:
            result_label = 'Conversaciones'
            short_label = 'conversaciones'
            main_result = conjunto.get('actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
            cost_per_result = conjunto.get('cost_per_actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)

        # Obtener action_key del objetivo para usar en la tabla
        objective_type = analysis.get('objective_type', 'onsite_conversion.messaging_conversation_started_7d')

        ads_en_conjunto = anuncios_por_conjunto.get(adset_name, [])

        best_ctr = max((a['ctr'] for a in ads_en_conjunto), default=0)
        best_result = max(
            (a.get('actions', {}).get(objective_type, 0) for a in ads_en_conjunto),
            default=0
        )
        min_cpa = min(
            (a.get('cost_per_actions', {}).get(objective_type, float('inf')) for a in ads_en_conjunto if a.get('cost_per_actions', {}).get(objective_type, 0) > 0),
            default=None
        )

        result_col_label = short_label.capitalize()
        _costo_map = {
            'conversaciones': 'Costo / conv.',
            'reproducciones': 'Costo / reprod.',
            'clics': 'CPC',
            'conversiones': 'Costo / conv.',
            'interacciones': 'Costo / inter.',
        }
        costo_col_label = _costo_map.get(short_label.lower(), f'Costo / {short_label}')

        html += f"""
            <div class="adset-detail">
                <div class="adset-header">
                    <div class="adset-title">{adset_name}</div>
                    <div class="adset-metrics">
                        <div class="adset-metric">
                            <div class="adset-metric-value">{format_number(main_result)}</div>
                            <div class="adset-metric-label">{result_label}</div>
                        </div>
                        <div class="adset-metric">
                            <div class="adset-metric-value">{format_currency(cost_per_result) if cost_per_result else '-'}</div>
                            <div class="adset-metric-label">Costo por resultado</div>
                        </div>
                        <div class="adset-metric">
                            <div class="adset-metric-value">{format_currency(conjunto['spend'])}</div>
                            <div class="adset-metric-label">Inversión Total</div>
                        </div>
                        <div class="adset-metric">
                            <div class="adset-metric-value">{format_number(conjunto['reach'])}</div>
                            <div class="adset-metric-label">Alcance</div>
                        </div>
                        <div class="adset-metric">
                            <div class="adset-metric-value">{conjunto['frequency']:.2f}</div>
                            <div class="adset-metric-label">Frecuencia</div>
                        </div>
                    </div>
                </div>

                <div class="comparison-table-wrap">
                    <table class="comparison-table">
                        <thead>
                            <tr>
                                <th class="col-ad">Anuncio</th>
                                <th>Alcance</th>
                                <th>Impresiones</th>
                                <th>Frecuencia</th>
                                <th>Inversión</th>
                                <th>CTR</th>
                                <th>CPC</th>
                                <th>CPM</th>
                                <th>{result_col_label}</th>
                                <th>{costo_col_label}</th>
                            </tr>
                        </thead>
                        <tbody>
"""

        for anuncio in ads_en_conjunto:
            creative = anuncio.get('creative', {})
            image_path = creative.get('local_image_path', '')
            result_val = anuncio.get('actions', {}).get(objective_type, 0)
            cpa = anuncio.get('cost_per_actions', {}).get(objective_type, 0)

            thumb_html = '<div style="width:60px;height:60px;background:#edf2f7;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#a0aec0;font-size:20px;">📷</div>'
            if image_path and os.path.exists(image_path):
                img_b64 = image_to_base64(image_path)
                if img_b64:
                    thumb_html = f'<div class="ad-thumb"><img src="{img_b64}" alt=""/></div>'

            ctr_tag = '<span class="tag-best">MEJOR</span>' if anuncio['ctr'] == best_ctr and len(ads_en_conjunto) > 1 else ''
            result_tag = '<span class="tag-best">MEJOR</span>' if result_val == best_result and best_result > 0 and len(ads_en_conjunto) > 1 else ''
            cpa_tag = '<span class="tag-best">MENOR</span>' if cpa and cpa == min_cpa and len(ads_en_conjunto) > 1 else ''

            html += f"""
                            <tr>
                                <td class="col-ad">
                                    <div class="ad-cell">
                                        {thumb_html}
                                        <span class="ad-cell-name">{anuncio['ad_name']}</span>
                                    </div>
                                </td>
                                <td class="metric-highlight">{format_number(anuncio['reach'])}</td>
                                <td>{format_number(anuncio['impressions'])}</td>
                                <td>{anuncio['frequency']:.2f}</td>
                                <td class="metric-highlight">{format_currency(anuncio['spend'])}</td>
                                <td>{anuncio['ctr']:.2f}%{ctr_tag}</td>
                                <td>{format_currency(anuncio['cpc'])}</td>
                                <td>{format_currency(anuncio['cpm'])}</td>
                                <td class="metric-highlight">{int(result_val)}{result_tag}</td>
                                <td>{format_currency(cpa) if cpa else '-'}{cpa_tag}</td>
                            </tr>
"""

        html += """
                        </tbody>
                    </table>
                </div>
            </div>
"""

    html += """
        </div>
"""

    # FOOTER
    html += f"""
        <div class="footer">
            Reporte generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}
        </div>

    </div>
</body>
</html>
"""

    return html


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 generate_html_clean.py <archivo_json>")
        sys.exit(1)

    json_path = sys.argv[1]

    if not os.path.exists(json_path):
        print(f"❌ Error: No se encuentra el archivo {json_path}")
        sys.exit(1)

    print(f"\n📄 Generando reporte HTML desde: {json_path}")

    # Leer JSON para obtener cliente y período
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cliente = data['metadata']['cliente'].upper()
    periodo = data['metadata']['periodo'].split('_')[0]
    date_obj = datetime.strptime(periodo, '%Y-%m-%d')
    ano = date_obj.strftime('%Y')
    mes_num = date_obj.strftime('%m')
    _meses_esp = {
        '01': 'ENE', '02': 'FEB', '03': 'MAR', '04': 'ABR',
        '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AGO',
        '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DIC'
    }
    mes_nombre = _meses_esp.get(mes_num, date_obj.strftime('%b').upper())

    # Crear carpeta de salida organizada: ../reportes/YYYY-MM-MES/CLIENTE/meta/
    script_dir = Path(__file__).parent
    reportes_dir = script_dir.parent / "reportes"
    periodo_folder = f"{ano}-{mes_num}-{mes_nombre}"

    output_dir = reportes_dir / periodo_folder / cliente / "meta"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generar HTML
    html_content = generate_html_report(json_path)

    # Guardar en carpeta organizada
    html_path = output_dir / f"{cliente}_REPORTE.html"

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML generado: {html_path}\n")

    return html_path


if __name__ == "__main__":
    main()
