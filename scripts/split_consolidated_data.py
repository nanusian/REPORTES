#!/usr/bin/env python3
"""
Divide el archivo consolidado sep-dic en archivos mensuales individuales
Útil cuando el archivo consolidado tiene datos que los mensuales no tienen
"""

import json
import os
from collections import defaultdict
from datetime import datetime

# Archivo consolidado
CONSOLIDATED_FILE = "/Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC/ASPA/meta/ASPA_2025-09-01_2025-12-28_analisis_pauta.json"

# Directorios de salida
OUTPUT_DIRS = {
    '09': "/Users/laureanomedeot/Documents/REPORTES/reportes/2025-09-SEP/ASPA/meta",
    '10': "/Users/laureanomedeot/Documents/REPORTES/reportes/2025-10-OCT/ASPA/meta",
    '11': "/Users/laureanomedeot/Documents/REPORTES/reportes/2025-11-NOV/ASPA/meta",
    '12': "/Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC/ASPA/meta",
}

def load_consolidated_data():
    """Carga el archivo consolidado"""
    with open(CONSOLIDATED_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def split_by_month(consolidated_data):
    """Divide los datos por mes basándose en datos_diarios"""

    # Agrupar datos diarios por mes
    daily_by_month = defaultdict(list)

    for day_data in consolidated_data.get('datos_diarios', []):
        date = day_data['date']
        month = date[5:7]  # Extrae el mes (formato: 2025-09-01)
        daily_by_month[month].append(day_data)

    # Como los datos de conjuntos y anuncios son agregados de TODO el período,
    # necesitamos crear archivos mensuales que contengan TODOS los grupos
    # pero con métricas del período completo (ya que no podemos separar por mes)

    monthly_data = {}

    for month in ['09', '10', '11', '12']:
        # Calcular totales del mes desde datos diarios
        month_days = daily_by_month.get(month, [])

        if not month_days:
            continue

        total_impressions = sum(d['impressions'] for d in month_days)
        total_reach = sum(d['reach'] for d in month_days)
        total_spend = sum(d['spend'] for d in month_days)
        total_conv = sum(d.get('conversaciones', 0) for d in month_days)

        # Crear estructura mensual
        first_day = month_days[0]['date']
        last_day = month_days[-1]['date']

        monthly_data[month] = {
            'metadata': {
                'cliente': 'ASPA',
                'periodo': f"{first_day}_{last_day}",
                'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'ad_account_id': consolidated_data['metadata']['ad_account_id'],
                'nota': 'Generado desde archivo consolidado - Los conjuntos y anuncios muestran métricas del período completo'
            },
            'resumen': {
                'inversion_total': total_spend,
                'alcance_total': total_reach,
                'impresiones_totales': total_impressions,
                'total_anuncios': len(consolidated_data.get('anuncios', [])),
                'total_conjuntos': len(consolidated_data.get('conjuntos_de_anuncios', []))
            },
            'conjuntos_de_anuncios': consolidated_data.get('conjuntos_de_anuncios', []),
            'anuncios': consolidated_data.get('anuncios', []),
            'datos_diarios': month_days,
            'analisis': consolidated_data.get('analisis', {})
        }

    return monthly_data

def save_monthly_files(monthly_data):
    """Guarda archivos mensuales"""

    month_names = {
        '09': 'Septiembre',
        '10': 'Octubre',
        '11': 'Noviembre',
        '12': 'Diciembre'
    }

    for month, data in monthly_data.items():
        output_dir = OUTPUT_DIRS[month]
        os.makedirs(output_dir, exist_ok=True)

        period = data['metadata']['periodo']
        output_file = f"{output_dir}/ASPA_{period}_analisis_pauta_CONSOLIDADO.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ {month_names[month]}: {output_file}")
        print(f"   - Inversión: ${data['resumen']['inversion_total']:,.0f}")
        print(f"   - Alcance: {data['resumen']['alcance_total']:,}")
        print(f"   - Conjuntos: {data['resumen']['total_conjuntos']}")
        print()

def main():
    print("\n" + "="*70)
    print("📊 DIVISIÓN DE DATOS CONSOLIDADOS POR MES")
    print("="*70 + "\n")

    # Cargar datos
    print("📂 Cargando archivo consolidado...")
    consolidated_data = load_consolidated_data()
    print(f"✅ Cargado: {len(consolidated_data.get('datos_diarios', []))} días de datos\n")

    # Dividir por mes
    print("✂️  Dividiendo datos por mes...")
    monthly_data = split_by_month(consolidated_data)
    print(f"✅ Generados {len(monthly_data)} meses\n")

    # Guardar archivos
    print("💾 Guardando archivos mensuales...\n")
    save_monthly_files(monthly_data)

    print("="*70)
    print("✅ Proceso completado!")
    print("="*70 + "\n")

    print("⚠️  IMPORTANTE:")
    print("Los archivos generados contienen TODOS los grupos de anuncios (La Alborada, Torre Aura, etc)")
    print("pero las métricas de conjuntos y anuncios son del período COMPLETO sep-dic.")
    print("Solo los datos_diarios están correctamente separados por mes.")
    print()

if __name__ == "__main__":
    main()
