#!/usr/bin/env python3
"""
Comparador de campañas entre dos períodos
Enfocado en resultado clave de cada campaña
"""

import json
import sys
import os

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

def get_campaign_key_result(conjunto):
    """Identifica el resultado clave de una campaña basado en su nombre"""
    name = conjunto['adset_name'].lower()

    # Conversaciones (Mensajes)
    if 'mensaje' in name:
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

    # Tráfico (clicks)
    elif 'tráfico' in name or 'trafico' in name:
        clicks = conjunto.get('actions', {}).get('link_click', 0)
        cost = conjunto.get('cost_per_actions', {}).get('link_click', 0)
        if clicks == 0:
            # Fallback a alcance si no hay clicks
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

    # Default: Alcance
    else:
        return {
            'type': 'Alcance',
            'value': conjunto.get('reach', 0),
            'cost': conjunto.get('spend', 0) / conjunto.get('reach', 1) if conjunto.get('reach', 0) > 0 else 0,
            'label': 'personas alcanzadas'
        }

def generate_comparison_html(json_old_path, json_new_path):
    """Genera HTML comparativo"""

    # Leer JSONs
    with open(json_old_path, 'r', encoding='utf-8') as f:
        data_old = json.load(f)

    with open(json_new_path, 'r', encoding='utf-8') as f:
        data_new = json.load(f)

    cliente = data_new['metadata']['cliente'].upper()
    periodo_old = data_old['metadata']['periodo'].split('_')[0]
    periodo_new = data_new['metadata']['periodo'].split('_')[0]

    # Obtener conjuntos
    conjuntos_old = {c['adset_name']: c for c in data_old['conjuntos_de_anuncios']}
    conjuntos_new = {c['adset_name']: c for c in data_new['conjuntos_de_anuncios']}

    # Campañas únicas
    all_campaigns = set(list(conjuntos_old.keys()) + list(conjuntos_new.keys()))

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparación Mensual - {cliente}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            padding: 30px;
            color: #2d3748;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 3px solid #4A5568;
        }}

        .header h1 {{
            font-size: 36px;
            color: #1a202c;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 20px;
            color: #718096;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }}

        .comparison-table th {{
            background: #4A5568;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
        }}

        .comparison-table td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}

        .comparison-table tbody tr:hover {{
            background: #f7fafc;
        }}

        .campaign-name {{
            font-weight: 600;
            color: #1a202c;
            font-size: 15px;
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
            font-size: 20px;
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
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 13px;
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

        .new-badge {{
            display: inline-block;
            background: #90CDF4;
            color: #1A365D;
            padding: 3px 8px;
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
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 8px;
        }}

        .summary {{
            display: flex;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}

        .summary-card {{
            flex: 1;
            min-width: 200px;
            background: #f7fafc;
            padding: 20px;
            border-left: 4px solid #4A5568;
            border-radius: 4px;
        }}

        .summary-title {{
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        .summary-value {{
            font-size: 28px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 5px;
        }}

        .summary-change {{
            font-size: 14px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{cliente}</h1>
            <div class="subtitle">Comparación: Octubre vs Noviembre 2025</div>
        </div>

        <h2 style="font-size: 24px; margin-bottom: 20px; color: #1a202c;">Resumen General</h2>

        <div class="summary">
            <div class="summary-card">
                <div class="summary-title">Inversión Total</div>
                <div class="summary-value">{format_currency(data_new['resumen']['inversion_total'])}</div>
                <div class="summary-change">{calculate_change(data_old['resumen']['inversion_total'], data_new['resumen']['inversion_total'])} vs mes anterior</div>
            </div>
            <div class="summary-card">
                <div class="summary-title">Alcance Total</div>
                <div class="summary-value">{format_number(data_new['resumen']['alcance_total'])}</div>
                <div class="summary-change">{calculate_change(data_old['resumen']['alcance_total'], data_new['resumen']['alcance_total'])} vs mes anterior</div>
            </div>
            <div class="summary-card">
                <div class="summary-title">Anuncios Activos</div>
                <div class="summary-value">{data_new['resumen']['total_anuncios']}</div>
                <div class="summary-change">{calculate_change(data_old['resumen']['total_anuncios'], data_new['resumen']['total_anuncios'])} vs mes anterior</div>
            </div>
        </div>

        <h2 style="font-size: 24px; margin: 40px 0 20px 0; color: #1a202c;">Resultado Clave por Campaña</h2>

        <table class="comparison-table">
            <thead>
                <tr>
                    <th style="width: 30%;">Campaña</th>
                    <th style="width: 15%;">Resultado Clave</th>
                    <th style="width: 15%;">Octubre</th>
                    <th style="width: 15%;">Noviembre</th>
                    <th style="width: 12%;">Cambio</th>
                    <th style="width: 13%;">Costo/Resultado</th>
                </tr>
            </thead>
            <tbody>
"""

    for campaign in sorted(all_campaigns):
        old_data = conjuntos_old.get(campaign)
        new_data = conjuntos_new.get(campaign)

        # Estado de la campaña
        if old_data and new_data:
            # Campaña existe en ambos meses
            old_result = get_campaign_key_result(old_data)
            new_result = get_campaign_key_result(new_data)

            change_pct = calculate_change(old_result['value'], new_result['value'])

            # Determinar clase de cambio
            if new_result['value'] > old_result['value']:
                change_class = 'change-positive'
            elif new_result['value'] < old_result['value']:
                change_class = 'change-negative'
            else:
                change_class = 'change-neutral'

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
                </tr>
"""

        elif new_data:
            # Campaña nueva en noviembre
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
                </tr>
"""

        elif old_data:
            # Campaña removida
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
                </tr>
"""

    html += """
            </tbody>
        </table>

        <div style="margin-top: 60px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #718096; font-size: 13px;">
            Comparación generada automáticamente • PERFIL SRL
        </div>
    </div>
</body>
</html>
"""

    return html


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 generate_comparison.py <json_octubre> <json_noviembre>")
        sys.exit(1)

    json_old = sys.argv[1]
    json_new = sys.argv[2]

    print(f"\n📊 Generando comparación...")
    print(f"   Mes anterior: {json_old}")
    print(f"   Mes actual: {json_new}")

    html = generate_comparison_html(json_old, json_new)

    # Guardar
    output_path = "output/ENTREGABLES/NOV-25/PERFIL_SRL_Comparacion_Oct-Nov.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Comparación generada: {output_path}\n")
    return output_path


if __name__ == "__main__":
    main()
