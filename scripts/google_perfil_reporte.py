#!/usr/bin/env python3
"""
Google Ads - Reporte mensual PERFIL SRL
Extrae datos por campaña, genera JSON + HTML con comparación mes anterior.

Uso:
    python3 google_perfil_reporte.py 2026-02-01 2026-02-28
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

CONFIG_PATH = "/Users/laureanomedeot/REPORTES/config/google-ads.yaml"
CUSTOMER_ID = "5022142942"
CLIENTE = "PERFIL SRL"
REPORTES_DIR = "/Users/laureanomedeot/REPORTES/reportes"

MONTH_NAMES = {
    "01": "ENE", "02": "FEB", "03": "MAR", "04": "ABR",
    "05": "MAY", "06": "JUN", "07": "JUL", "08": "AGO",
    "09": "SEP", "10": "OCT", "11": "NOV", "12": "DIC"
}

CAMPAIGN_TYPE_MAP = {
    "SEARCH": "Search",
    "DISPLAY": "Display",
    "PERFORMANCE_MAX": "PMax",
    "VIDEO": "Video",
    "SHOPPING": "Shopping",
}


def format_currency(value):
    if value is None or value == 0:
        return "$0"
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_number(value):
    if value is None:
        return "0"
    return f"{int(value):,}".replace(",", ".")


def calculate_change(old, new):
    if old == 0:
        return ("+∞%" if new > 0 else "0%"), "neutral"
    change = ((new - old) / old) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%", ("positive" if change <= 0 else "negative")


def extract_google_data(date_from, date_until):
    """Extrae datos de campañas de Google Ads a nivel de campaña."""
    client = GoogleAdsClient.load_from_storage(CONFIG_PATH)
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc,
            metrics.average_cpm,
            metrics.cost_per_conversion,
            segments.date
        FROM campaign
        WHERE
            segments.date >= '{date_from}'
            AND segments.date <= '{date_until}'
            AND campaign.status != 'REMOVED'
        ORDER BY segments.date, campaign.name
    """

    print(f"\n🔍 Extrayendo Google Ads {date_from} → {date_until}")
    print(f"   Account: {CUSTOMER_ID}\n")

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query)

    campaigns_agg = {}
    daily_totals = {}
    detailed_records = []

    for row in response:
        camp_id = row.campaign.id
        camp_name = row.campaign.name
        camp_type = row.campaign.advertising_channel_type.name
        date = row.segments.date

        cost = row.metrics.cost_micros / 1_000_000
        avg_cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0
        avg_cpm = row.metrics.average_cpm / 1_000_000 if row.metrics.average_cpm else 0
        cost_per_conv = row.metrics.cost_per_conversion / 1_000_000 if row.metrics.cost_per_conversion else 0
        clicks = row.metrics.clicks
        impressions = row.metrics.impressions
        conversions = row.metrics.conversions
        ctr = row.metrics.ctr * 100

        # Agregado por campaña
        if camp_id not in campaigns_agg:
            campaigns_agg[camp_id] = {
                "campaign_name": camp_name,
                "campaign_type": camp_type,
                "impressions": 0, "clicks": 0, "cost": 0,
                "conversions": 0, "conversions_value": 0,
            }
        campaigns_agg[camp_id]["impressions"] += impressions
        campaigns_agg[camp_id]["clicks"] += clicks
        campaigns_agg[camp_id]["cost"] += cost
        campaigns_agg[camp_id]["conversions"] += conversions
        campaigns_agg[camp_id]["conversions_value"] += row.metrics.conversions_value

        # Diario
        if date not in daily_totals:
            daily_totals[date] = {"date": date, "impressions": 0, "clicks": 0, "cost": 0, "conversions": 0}
        daily_totals[date]["impressions"] += impressions
        daily_totals[date]["clicks"] += clicks
        daily_totals[date]["cost"] += cost
        daily_totals[date]["conversions"] += conversions

        # Detallado (por día y campaña)
        detailed_records.append({
            "campaign_id": camp_id,
            "campaign_name": camp_name,
            "campaign_type": camp_type,
            "date": date,
            "impressions": impressions,
            "clicks": clicks,
            "cost": cost,
            "conversions": conversions,
            "ctr": ctr,
            "avg_cpc": avg_cpc,
            "avg_cpm": avg_cpm,
        })

    # Calcular métricas derivadas por campaña
    campanas = []
    for camp_id, c in campaigns_agg.items():
        c_clicks = c["clicks"]
        c_impr = c["impressions"]
        c_cost = c["cost"]
        c_conv = c["conversions"]
        campanas.append({
            "campaign_name": c["campaign_name"],
            "campaign_type": c["campaign_type"],
            "impressions": c_impr,
            "clicks": c_clicks,
            "cost": c_cost,
            "conversions": c_conv,
            "conversions_value": c["conversions_value"],
            "ctr": (c_clicks / c_impr * 100) if c_impr > 0 else 0,
            "avg_cpc": (c_cost / c_clicks) if c_clicks > 0 else 0,
            "avg_cpm": (c_cost / c_impr * 1000) if c_impr > 0 else 0,
            "cost_per_conversion": (c_cost / c_conv) if c_conv > 0 else 0,
        })

    total_cost = sum(c["cost"] for c in campanas)
    total_clicks = sum(c["clicks"] for c in campanas)
    total_impressions = sum(c["impressions"] for c in campanas)
    total_conversions = sum(c["conversions"] for c in campanas)

    print(f"✅ Extraídos {len(detailed_records)} registros | {len(campanas)} campañas")

    return {
        "campanas": campanas,
        "datos_diarios": sorted(daily_totals.values(), key=lambda x: x["date"]),
        "datos_detallados": sorted(detailed_records, key=lambda x: (x["date"], x["campaign_name"])),
        "totales": {
            "cost": total_cost,
            "clicks": total_clicks,
            "impressions": total_impressions,
            "conversions": total_conversions,
        }
    }


def save_json(data, date_from, date_until):
    """Guarda el JSON en la estructura de carpetas correcta."""
    year = date_from[:4]
    month = date_from[5:7]
    month_name = MONTH_NAMES[month]

    periodo = f"{date_from}_{date_until}"
    out_dir = Path(REPORTES_DIR) / f"{year}-{month}-{month_name}" / CLIENTE / "google"
    out_dir.mkdir(parents=True, exist_ok=True)

    totales = data["totales"]
    report = {
        "metadata": {
            "cliente": CLIENTE,
            "periodo": periodo,
            "customer_id": CUSTOMER_ID,
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "resumen": {
            "inversion_total": totales["cost"],
            "impresiones_totales": totales["impressions"],
            "clicks_totales": totales["clicks"],
            "conversiones_totales": totales["conversions"],
            "total_campanas": len(data["campanas"]),
        },
        "campanas": data["campanas"],
        "datos_diarios": data["datos_diarios"],
        "datos_detallados": data["datos_detallados"],
    }

    out_file = out_dir / f"{CLIENTE}_{periodo}_google_ads.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON guardado: {out_file}")
    return out_file, report


def generate_html(report_new, report_old, date_from):
    """Genera el HTML del reporte con comparación al mes anterior."""
    year = date_from[:4]
    month = date_from[5:7]
    month_name = MONTH_NAMES[month]

    # Nombres de meses para display
    month_display = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }
    mes_actual = month_display[month] + " " + year
    prev_month_num = str(int(month) - 1).zfill(2) if int(month) > 1 else "12"
    mes_anterior_abrev = MONTH_NAMES[prev_month_num]

    resumen_new = report_new["resumen"]
    resumen_old = report_old["resumen"] if report_old else None

    campanas_new = {c["campaign_name"]: c for c in report_new["campanas"]}
    campanas_old = {c["campaign_name"]: c for c in report_old["campanas"]} if report_old else {}

    # Calcular métricas globales
    avg_cpc_new = resumen_new["inversion_total"] / resumen_new["clicks_totales"] if resumen_new["clicks_totales"] > 0 else 0
    cost_per_conv_new = resumen_new["inversion_total"] / resumen_new["conversiones_totales"] if resumen_new["conversiones_totales"] > 0 else 0

    if resumen_old:
        avg_cpc_old = resumen_old["inversion_total"] / resumen_old["clicks_totales"] if resumen_old["clicks_totales"] > 0 else 0
        cost_per_conv_old = resumen_old["inversion_total"] / resumen_old["conversiones_totales"] if resumen_old["conversiones_totales"] > 0 else 0
    else:
        avg_cpc_old = cost_per_conv_old = 0

    def change_badge(old, new, lower_is_better=False):
        if old == 0:
            return ""
        pct = ((new - old) / old) * 100
        sign = "+" if pct >= 0 else ""
        if lower_is_better:
            css = "change-positive" if pct <= 0 else "change-negative"
        else:
            css = "change-positive" if pct >= 0 else "change-negative"
        return f'<div class="change {css}">{sign}{pct:.1f}% vs {mes_anterior_abrev}</div>'

    # --- Resumen cards ---
    summary_html = f"""
        <div class="summary-card">
            <div class="value">{format_currency(resumen_new["inversion_total"])}</div>
            <div class="label">Inversión Total</div>
            {change_badge(resumen_old["inversion_total"] if resumen_old else 0, resumen_new["inversion_total"], lower_is_better=True)}
        </div>
        <div class="summary-card conversions">
            <div class="value">{int(resumen_new["conversiones_totales"])}</div>
            <div class="label">Conversiones</div>
            {change_badge(resumen_old["conversiones_totales"] if resumen_old else 0, resumen_new["conversiones_totales"])}
        </div>
        <div class="summary-card clicks">
            <div class="value">{format_number(resumen_new["clicks_totales"])}</div>
            <div class="label">Clicks</div>
            {change_badge(resumen_old["clicks_totales"] if resumen_old else 0, resumen_new["clicks_totales"])}
        </div>
        <div class="summary-card cost">
            <div class="value">{format_currency(cost_per_conv_new) if cost_per_conv_new > 0 else "-"}</div>
            <div class="label">Costo/Conversión</div>
            {change_badge(cost_per_conv_old, cost_per_conv_new, lower_is_better=True)}
        </div>
        <div class="summary-card">
            <div class="value">{format_currency(avg_cpc_new)}</div>
            <div class="label">CPC Promedio</div>
            {change_badge(avg_cpc_old, avg_cpc_new, lower_is_better=True)}
        </div>
    """

    # --- Campaña cards ---
    type_css = {"SEARCH": "type-search", "DISPLAY": "type-display", "PERFORMANCE_MAX": "type-pmax", "VIDEO": "type-video"}

    campanas_html = ""
    for camp_name, c in campanas_new.items():
        c_old = campanas_old.get(camp_name, {})
        type_label = CAMPAIGN_TYPE_MAP.get(c["campaign_type"], c["campaign_type"])
        type_class = type_css.get(c["campaign_type"], "type-search")
        cost_prev = c_old.get("cost", 0)
        conv_prev = c_old.get("conversions", 0)
        clicks_prev = c_old.get("clicks", 0)
        cpc_prev = c_old.get("avg_cpc", 0)
        cpc_curr_str = format_currency(c["avg_cpc"])
        cpc_prev_str = format_currency(cpc_prev)
        cost_per_conv_curr = format_currency(c["cost_per_conversion"]) if c["cost_per_conversion"] > 0 else "-"
        cost_per_conv_prev = format_currency(c_old.get("cost_per_conversion", 0)) if c_old.get("cost_per_conversion", 0) > 0 else "-"

        def ch(old, new, lower=False):
            if old == 0:
                return ""
            pct = ((new - old) / old) * 100
            sign = "+" if pct >= 0 else ""
            css = ("change-positive" if pct <= 0 else "change-negative") if lower else ("change-positive" if pct >= 0 else "change-negative")
            return f'<div class="change {css}">{sign}{pct:.1f}%</div>'

        campanas_html += f"""
        <div class="campaign-card">
            <div class="campaign-header">
                <div class="campaign-name">{camp_name}</div>
                <span class="campaign-type {type_class}">{type_label}</span>
            </div>
            <div class="metrics-row">
                <div class="metric-box">
                    <div class="value">{format_currency(c["cost"])}</div>
                    <div class="label">Inversión</div>
                    <div class="compare">{mes_anterior_abrev}: {format_currency(cost_prev)}</div>
                    {ch(cost_prev, c["cost"], lower=True)}
                </div>
                <div class="metric-box">
                    <div class="value" style="color: #34A853;">{int(c["conversions"])}</div>
                    <div class="label">Conversiones</div>
                    <div class="compare">{mes_anterior_abrev}: {int(conv_prev)}</div>
                    {ch(conv_prev, c["conversions"])}
                </div>
                <div class="metric-box">
                    <div class="value">{format_number(c["clicks"])}</div>
                    <div class="label">Clicks</div>
                    <div class="compare">{mes_anterior_abrev}: {format_number(clicks_prev)}</div>
                    {ch(clicks_prev, c["clicks"])}
                </div>
                <div class="metric-box">
                    <div class="value" style="color: #FBBC05;">{cpc_curr_str}</div>
                    <div class="label">CPC</div>
                    <div class="compare">{mes_anterior_abrev}: {cpc_prev_str}</div>
                    {ch(cpc_prev, c["avg_cpc"], lower=True)}
                </div>
                <div class="metric-box">
                    <div class="value">{cost_per_conv_curr}</div>
                    <div class="label">Costo/Conv</div>
                    <div class="compare">{mes_anterior_abrev}: {cost_per_conv_prev}</div>
                </div>
                <div class="metric-box">
                    <div class="value">{format_number(c["impressions"])}</div>
                    <div class="label">Impresiones</div>
                </div>
                <div class="metric-box">
                    <div class="value">{c["ctr"]:.2f}%</div>
                    <div class="label">CTR</div>
                </div>
            </div>
        </div>
        """

    # --- Tabla comparativa ---
    table_rows = ""
    for camp_name, c in campanas_new.items():
        c_old = campanas_old.get(camp_name, {})
        type_label = CAMPAIGN_TYPE_MAP.get(c["campaign_type"], c["campaign_type"])
        conv_old = c_old.get("conversions", 0)
        cpc_old = c_old.get("avg_cpc", 0)

        conv_change, conv_dir = calculate_change(conv_old, c["conversions"])
        cpc_change, cpc_dir = calculate_change(cpc_old, c["avg_cpc"])
        # CPC: lower is better → invert direction for CSS
        cpc_css = "change-positive" if cpc_dir == "neutral" or (c["avg_cpc"] <= cpc_old and cpc_old > 0) else "change-negative"

        cost_per_conv_curr = format_currency(c["cost_per_conversion"]) if c["cost_per_conversion"] > 0 else "-"

        table_rows += f"""
                <tr>
                    <td><strong>{camp_name}</strong></td>
                    <td>{type_label}</td>
                    <td>{int(conv_old)}</td>
                    <td>{int(c["conversions"])}</td>
                    <td class="change-{conv_dir}">{conv_change}</td>
                    <td>{format_currency(cpc_old)}</td>
                    <td>{format_currency(c["avg_cpc"])}</td>
                    <td class="{cpc_css}">{cpc_change}</td>
                    <td>{cost_per_conv_curr}</td>
                </tr>
        """

    # --- Insights automáticos ---
    # Buscar mejor campaña por conversiones
    sorted_camps = sorted(campanas_new.values(), key=lambda x: x["conversions"], reverse=True)
    insights_html = ""

    if sorted_camps:
        best = sorted_camps[0]
        if best["conversions"] > 0:
            insights_html += f"""
        <div class="insight-box">
            <h4>✅ Campaña con mayor volumen de conversiones</h4>
            <p><strong>{best["campaign_name"]}</strong> lidera con {int(best["conversions"])} conversiones
            a un costo por conversión de {format_currency(best["cost_per_conversion"])}.</p>
        </div>
        """

    # Campaña de Display sin conversiones
    for c in campanas_new.values():
        if c["campaign_type"] == "DISPLAY" and c["conversions"] == 0:
            insights_html += f"""
        <div class="insight-box warning">
            <h4>⚠️ Display sin conversiones directas</h4>
            <p><strong>{c["campaign_name"]}</strong> tiene CPC de {format_currency(c["avg_cpc"])} pero no registra conversiones.
            Evaluar si el objetivo es branding o reasignar presupuesto.</p>
        </div>
        """
            break

    # Comparación mes anterior global
    if resumen_old and resumen_old["conversiones_totales"] > 0:
        conv_change_pct = ((resumen_new["conversiones_totales"] - resumen_old["conversiones_totales"]) / resumen_old["conversiones_totales"]) * 100
        direction = "mejoró" if conv_change_pct >= 0 else "bajó"
        insights_html += f"""
        <div class="insight-box info">
            <h4>📊 Evolución mensual</h4>
            <p>El total de conversiones {direction} un <strong>{abs(conv_change_pct):.1f}%</strong> respecto a {mes_anterior_abrev}.
            La inversión total fue de {format_currency(resumen_new["inversion_total"])}.</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Google Ads - {CLIENTE} - {mes_actual}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f5f5f5; color: #2d3748; line-height: 1.6; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}

        .header {{ text-align: center; padding: 50px 0; border-bottom: 4px solid #4285F4; margin-bottom: 50px; }}
        .header h1 {{ font-size: 48px; font-weight: 700; color: #1a202c; margin-bottom: 15px; }}
        .header .subtitle {{ font-size: 26px; color: #718096; font-weight: 300; }}
        .header .period {{ font-size: 20px; color: #4285F4; margin-top: 15px; font-weight: 500; }}
        .google-logo {{ display: flex; justify-content: center; gap: 3px; margin-bottom: 20px; }}
        .google-logo span {{ font-size: 36px; font-weight: 700; }}
        .g-blue {{ color: #4285F4; }} .g-red {{ color: #EA4335; }} .g-yellow {{ color: #FBBC05; }} .g-green {{ color: #34A853; }}

        .section {{ margin-bottom: 60px; }}
        .section-title {{ font-size: 28px; font-weight: 700; color: #1a202c; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 3px solid #4285F4; }}

        .summary {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 30px 0; }}
        .summary-card {{ flex: 1; min-width: 160px; background: linear-gradient(135deg, #f8f9fa 0%, #e8f0fe 100%); padding: 22px; border-radius: 12px; border-left: 4px solid #4285F4; }}
        .summary-card.conversions {{ border-left-color: #34A853; }}
        .summary-card.clicks {{ border-left-color: #FBBC05; }}
        .summary-card.cost {{ border-left-color: #EA4335; }}
        .summary-card .value {{ font-size: 26px; font-weight: 700; color: #1a202c; }}
        .summary-card .label {{ font-size: 11px; color: #718096; text-transform: uppercase; margin-top: 5px; }}
        .summary-card .change {{ font-size: 12px; margin-top: 8px; font-weight: 600; }}

        .campaign-card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px; }}
        .campaign-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e2e8f0; }}
        .campaign-name {{ font-size: 20px; font-weight: 700; color: #1a202c; }}
        .campaign-type {{ padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; }}
        .type-search {{ background: #e8f0fe; color: #4285F4; }}
        .type-display {{ background: #fef3e8; color: #EA4335; }}
        .type-pmax {{ background: #e8f5e9; color: #34A853; }}
        .type-video {{ background: #fce4ec; color: #c62828; }}

        .metrics-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 15px; }}
        .metric-box {{ text-align: center; padding: 15px 10px; background: #f8f9fa; border-radius: 8px; }}
        .metric-box .value {{ font-size: 20px; font-weight: 700; color: #1a202c; }}
        .metric-box .label {{ font-size: 10px; color: #718096; text-transform: uppercase; margin-top: 3px; }}
        .metric-box .compare {{ font-size: 10px; color: #718096; margin-top: 5px; }}
        .metric-box .change {{ font-weight: 600; font-size: 11px; }}

        .change-positive {{ color: #34A853; }} .change-negative {{ color: #EA4335; }} .change-neutral {{ color: #718096; }}

        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4285F4; color: white; padding: 12px; text-align: left; font-size: 11px; text-transform: uppercase; }}
        td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; font-size: 13px; }}

        .insight-box {{ background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #34A853; }}
        .insight-box.warning {{ background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-left-color: #FBBC05; }}
        .insight-box.info {{ background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-left-color: #4285F4; }}
        .insight-box h4 {{ color: #1a202c; margin-bottom: 8px; font-size: 15px; }}
        .insight-box p {{ color: #4a5568; font-size: 14px; }}
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <div class="google-logo">
            <span class="g-blue">G</span><span class="g-red">o</span><span class="g-yellow">o</span><span class="g-blue">g</span><span class="g-green">l</span><span class="g-red">e</span>
            <span style="color: #718096; margin-left: 10px;">Ads</span>
        </div>
        <h1>{CLIENTE}</h1>
        <div class="subtitle">Reporte de Performance</div>
        <div class="period">{mes_actual}</div>
    </div>

    <div class="section">
        <h2 class="section-title">📊 Resumen Ejecutivo</h2>
        <div class="summary">
            {summary_html}
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">🎯 Rendimiento por Campaña</h2>
        {campanas_html}
    </div>

    <div class="section">
        <h2 class="section-title">📈 Comparación Mensual ({mes_anterior_abrev} vs {month_display[month][:3]})</h2>
        <table>
            <thead>
                <tr>
                    <th>Campaña</th>
                    <th>Tipo</th>
                    <th>Conv {mes_anterior_abrev}</th>
                    <th>Conv {month_display[month][:3]}</th>
                    <th>Var Conv</th>
                    <th>CPC {mes_anterior_abrev}</th>
                    <th>CPC {month_display[month][:3]}</th>
                    <th>Var CPC</th>
                    <th>Costo/Conv {month_display[month][:3]}</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2 class="section-title">💡 Insights</h2>
        {insights_html}
    </div>

</div>
</body>
</html>"""

    return html


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 google_perfil_reporte.py FECHA_INICIO FECHA_FIN")
        print("Ej:  python3 google_perfil_reporte.py 2026-02-01 2026-02-28")
        sys.exit(1)

    date_from = sys.argv[1]
    date_until = sys.argv[2]

    # Extraer datos del mes actual
    data = extract_google_data(date_from, date_until)

    if not data["campanas"]:
        print("⚠️  Sin datos para el período indicado.")
        sys.exit(0)

    # Guardar JSON
    json_file, report_new = save_json(data, date_from, date_until)

    # Cargar JSON del mes anterior para comparación
    year = date_from[:4]
    month = date_from[5:7]
    prev_month_num = str(int(month) - 1).zfill(2) if int(month) > 1 else "12"
    prev_year = year if int(month) > 1 else str(int(year) - 1)
    prev_month_name = MONTH_NAMES[prev_month_num]
    prev_days = {"01": "31", "02": "28", "03": "31", "04": "30", "05": "31",
                 "06": "30", "07": "31", "08": "31", "09": "30", "10": "31", "11": "30", "12": "31"}
    prev_last_day = prev_days[prev_month_num]

    prev_json_path = (
        Path(REPORTES_DIR)
        / f"{prev_year}-{prev_month_num}-{prev_month_name}"
        / CLIENTE / "google"
        / f"{CLIENTE}_{prev_year}-{prev_month_num}-01_{prev_year}-{prev_month_num}-{prev_last_day}_google_ads.json"
    )

    report_old = None
    if prev_json_path.exists():
        with open(prev_json_path, "r", encoding="utf-8") as f:
            report_old = json.load(f)
        print(f"✅ JSON mes anterior cargado: {prev_json_path.name}")
    else:
        print(f"⚠️  Sin JSON mes anterior (buscado: {prev_json_path})")

    # Generar HTML
    html = generate_html(report_new, report_old, date_from)

    year = date_from[:4]
    month = date_from[5:7]
    month_name = MONTH_NAMES[month]
    out_dir = Path(REPORTES_DIR) / f"{year}-{month}-{month_name}" / CLIENTE / "google"
    html_file = out_dir / f"{CLIENTE}_GOOGLE_ADS_REPORTE.html"

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML guardado: {html_file}")

    # Resumen
    totales = data["totales"]
    print(f"\n{'='*60}")
    print(f"📈 RESUMEN GOOGLE ADS - {CLIENTE}")
    print(f"{'='*60}")
    print(f"  Inversión:    ${totales['cost']:,.2f}")
    print(f"  Clicks:       {totales['clicks']:,}")
    print(f"  Impresiones:  {totales['impressions']:,}")
    print(f"  Conversiones: {totales['conversions']:.0f}")
    print(f"  Campañas:     {len(data['campanas'])}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
