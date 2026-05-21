#!/usr/bin/env python3
"""
Procesador de CSV de Google Ads
Convierte reportes exportados desde Google Ads a formato JSON
"""

import csv
import json
import sys
import os
from datetime import datetime
from collections import defaultdict

def process_csv(csv_path, cliente, periodo):
    """Procesa CSV de Google Ads y genera JSON estructurado"""

    print(f"\n📊 Procesando CSV de Google Ads: {csv_path}\n")

    campaigns_data = []
    daily_data = defaultdict(lambda: {
        'impressions': 0,
        'clicks': 0,
        'cost': 0,
        'conversions': 0
    })

    # Detectar encoding del archivo
    encodings_to_try = ['utf-16', 'utf-8', 'latin-1']

    for encoding in encodings_to_try:
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                content = f.read()
                if content:
                    print(f"✅ Archivo leído con encoding: {encoding}")
                    break
        except:
            continue
    else:
        print("❌ No se pudo leer el archivo con ningún encoding conocido")
        return None

    # Parsear el CSV
    lines = content.split('\n')

    # Encontrar la línea del header (la que contiene "Grupo de anuncios")
    header_line = None
    data_start = 0

    for i, line in enumerate(lines):
        if 'Grupo de anuncios' in line or 'Ad group' in line:
            header_line = line.strip()
            data_start = i + 1
            break

    if not header_line:
        print("❌ No se encontró el header en el CSV")
        return None

    print(f"✅ Header encontrado en línea {data_start}")

    # Separar por tabs
    headers = header_line.split('\t')

    # Procesar filas de datos
    for i in range(data_start, len(lines)):
        line = lines[i].strip()

        # Saltar líneas vacías y líneas de total
        if not line or 'Total:' in line or line.startswith('Total'):
            continue

        # Separar valores por tab
        values = line.split('\t')

        if len(values) < len(headers):
            continue

        # Crear diccionario de la fila
        row = {}
        for j, header in enumerate(headers):
            if j < len(values):
                row[header] = values[j]

        # Extraer valores clave
        campaign_name = row.get('Campaña', row.get('Campaign', '')).strip()
        ad_group_name = row.get('Grupo de anuncios', row.get('Ad group', '')).strip()

        if not campaign_name or not ad_group_name:
            continue

        # Estado - solo procesar habilitados
        estado = row.get('Estado del grupo de anuncios', row.get('Ad group state', '')).strip()

        # Extraer métricas
        try:
            # Limpiar valores numéricos
            def clean_number(value):
                if not value or value == '--':
                    return '0'
                # Remover comillas y espacios
                cleaned = value.replace('"', '').replace(' ', '')
                # Si tiene coma, es separador de miles en formato US: "43,251" → 43251
                # Si solo tiene punto, es decimal: 313780.35 → 313780.35
                # Si tiene ambos, punto es miles y coma es decimal: "3.780,35" → 3780.35
                if ',' in cleaned and '.' not in cleaned:
                    # Formato US: coma como separador de miles
                    cleaned = cleaned.replace(',', '')
                elif ',' in cleaned and '.' in cleaned:
                    # Formato europeo: punto=miles, coma=decimal
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                # Si solo tiene punto, dejarlo como decimal
                return cleaned

            impressions_str = clean_number(row.get('Impr.', row.get('Impressions', '0')))
            impressions = int(float(impressions_str)) if impressions_str else 0

            clicks_str = clean_number(row.get('Clics', row.get('Clicks', '0')))
            clicks = int(float(clicks_str)) if clicks_str else 0

            cost_str = clean_number(row.get('Costo', row.get('Cost', '0')))
            cost = float(cost_str) if cost_str else 0

            conversions_str = clean_number(row.get('Conversiones', row.get('Conversions', '0')))
            conversions = float(conversions_str) if conversions_str else 0

            # CTR y CPC
            ctr_str = clean_number(row.get('CTR', '0')).replace('%', '')
            ctr = float(ctr_str) if ctr_str else 0

            avg_cpc_str = clean_number(row.get('Prom. CPC', row.get('Avg. CPC', '0')))
            avg_cpc = float(avg_cpc_str) if avg_cpc_str else 0

            # Costo por conversión
            cost_per_conv_str = clean_number(row.get('Costo/conv.', row.get('Cost/conv.', '0')))
            cost_per_conversion = float(cost_per_conv_str) if cost_per_conv_str else 0

        except (ValueError, AttributeError) as e:
            print(f"⚠️  Error procesando fila: {ad_group_name}")
            print(f"    Error: {e}")
            continue

        # Si no hay datos (impresiones = 0), saltar
        if impressions == 0:
            continue

        record = {
            'campaign_name': campaign_name,
            'ad_group_name': ad_group_name,
            'estado': estado,
            'impressions': impressions,
            'clicks': clicks,
            'cost': cost,
            'conversions': conversions,
            'ctr': ctr,
            'avg_cpc': avg_cpc,
            'cost_per_conversion': cost_per_conversion
        }

        campaigns_data.append(record)

        # Agregar a datos diarios (usar fecha de inicio del período)
        date_key = periodo.split('_')[0]
        daily_data[date_key]['impressions'] += impressions
        daily_data[date_key]['clicks'] += clicks
        daily_data[date_key]['cost'] += cost
        daily_data[date_key]['conversions'] += conversions

        print(f"   📊 {campaign_name} > {ad_group_name}")
        print(f"      Estado: {estado} | Clics: {clicks:,} | Inversión: ${cost:,.2f} | Conversiones: {conversions}")

    print(f"\n✅ Procesados {len(campaigns_data)} grupos de anuncios\\n")

    # Agregar por grupo de anuncios (si hay duplicados)
    ad_groups = {}
    for record in campaigns_data:
        key = f"{record['campaign_name']}|{record['ad_group_name']}"

        if key not in ad_groups:
            ad_groups[key] = record.copy()
        else:
            ad_groups[key]['impressions'] += record['impressions']
            ad_groups[key]['clicks'] += record['clicks']
            ad_groups[key]['cost'] += record['cost']
            ad_groups[key]['conversions'] += record['conversions']

    ad_groups_data = list(ad_groups.values())

    # Recalcular métricas agregadas
    for ag in ad_groups_data:
        if ag['impressions'] > 0:
            ag['ctr'] = (ag['clicks'] / ag['impressions']) * 100
        if ag['clicks'] > 0:
            ag['avg_cpc'] = ag['cost'] / ag['clicks']
        if ag['conversions'] > 0:
            ag['cost_per_conversion'] = ag['cost'] / ag['conversions']

    # Convertir daily_data a lista
    daily_list = [{'date': k, **v} for k, v in daily_data.items()]

    return campaigns_data, ad_groups_data, daily_list


def save_report(campaigns_data, ad_groups_data, daily_data, cliente, periodo):
    """Guarda el reporte en JSON"""

    # Calcular totales
    total_cost = sum(r['cost'] for r in campaigns_data)
    total_clicks = sum(r['clicks'] for r in campaigns_data)
    total_impressions = sum(r['impressions'] for r in campaigns_data)
    total_conversions = sum(r['conversions'] for r in campaigns_data)

    # Determinar mes para carpeta
    date_parts = periodo.split('_')[0].split('-')
    year = date_parts[0]
    month_num = date_parts[1]

    month_names = {
        '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DIC',
        '01': 'ENE', '02': 'FEB', '03': 'MAR', '04': 'ABR',
        '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AGO'
    }
    month_name = month_names.get(month_num, month_num)

    output_dir = f"/Users/laureanomedeot/Documents/REPORTES/reportes/{year}-{month_num}-{month_name}/{cliente}/google"
    os.makedirs(output_dir, exist_ok=True)

    output_path = f"{output_dir}/{cliente}_{periodo}_google_ads.json"

    report = {
        'metadata': {
            'cliente': cliente,
            'periodo': periodo,
            'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'plataforma': 'Google Ads',
            'fuente': 'CSV Export'
        },
        'resumen': {
            'inversion_total': total_cost,
            'clics_totales': total_clicks,
            'impresiones_totales': total_impressions,
            'conversiones_totales': total_conversions,
            'total_grupos': len(ad_groups_data)
        },
        'grupos_de_anuncios': ad_groups_data,
        'datos_detallados': campaigns_data,
        'datos_diarios': daily_data
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ Reporte JSON guardado: {output_path}")

    # Mostrar resumen
    print("\n" + "="*70)
    print("📈 RESUMEN DEL PERÍODO")
    print("="*70)
    print(f"  Inversión total: ${total_cost:,.2f}")
    print(f"  Clics totales: {total_clicks:,}")
    print(f"  Impresiones: {total_impressions:,}")
    print(f"  Conversiones: {total_conversions:.1f}")
    print(f"  Grupos de anuncios: {len(ad_groups_data)}")
    print("="*70 + "\n")

    return report


def main():
    """Función principal"""

    if len(sys.argv) < 4:
        print("❌ Uso: python3 google_ads_csv_processor.py <csv_path> <cliente> <periodo>")
        print("   Ejemplo: python3 google_ads_csv_processor.py sep.csv ASPA 2025-09-01_2025-09-30")
        sys.exit(1)

    csv_path = sys.argv[1]
    cliente = sys.argv[2]
    periodo = sys.argv[3]

    if not os.path.exists(csv_path):
        print(f"❌ No se encuentra el archivo: {csv_path}")
        sys.exit(1)

    print("\n" + "="*70)
    print("📊 GOOGLE ADS CSV PROCESSOR")
    print("="*70)

    result = process_csv(csv_path, cliente, periodo)

    if result:
        campaigns_data, ad_groups_data, daily_data = result
        save_report(campaigns_data, ad_groups_data, daily_data, cliente, periodo)
        print("✅ Proceso completado!\n")
    else:
        print("❌ No se pudieron procesar los datos\n")


if __name__ == "__main__":
    main()
