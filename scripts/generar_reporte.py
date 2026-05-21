#!/usr/bin/env python3
"""
Script simplificado para generar reportes por nombre de cliente
Uso: python3 generar_reporte.py CLIENTE FECHA_INICIO FECHA_FIN
Ejemplo: python3 generar_reporte.py CBS 2025-10-01 2025-10-31
"""

import sys
import json
import os
import subprocess
from datetime import datetime, timedelta

def cargar_clientes():
    """Carga la configuración de clientes"""
    with open('clientes.json', 'r', encoding='utf-8') as f:
        return json.load(f)['clientes']

def listar_clientes():
    """Lista todos los clientes disponibles"""
    clientes = cargar_clientes()

    print("\n" + "="*70)
    print("📋 CLIENTES DISPONIBLES")
    print("="*70)

    categorias = {}
    for codigo, info in clientes.items():
        cat = info['categoria']
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append((codigo, info['nombre']))

    for cat, lista in sorted(categorias.items()):
        print(f"\n🏢 {cat}:")
        for codigo, nombre in sorted(lista):
            print(f"   {codigo:15} → {nombre}")

    print("="*70 + "\n")

def generar_reporte(codigo_cliente, fecha_inicio, fecha_fin):
    """Genera reporte para un cliente específico"""

    clientes = cargar_clientes()

    # Buscar cliente (case insensitive)
    codigo_upper = codigo_cliente.upper()
    cliente_info = None

    for codigo, info in clientes.items():
        if codigo.upper() == codigo_upper:
            cliente_info = info
            break

    if not cliente_info:
        print(f"❌ Cliente '{codigo_cliente}' no encontrado.")
        print("\nClientes disponibles:")
        listar_clientes()
        return False

    print(f"\n✅ Cliente encontrado: {cliente_info['nombre']}")
    print(f"   ID de cuenta: {cliente_info['ad_account_id']}")
    print(f"   Categoría: {cliente_info['categoria']}")
    print(f"   Período: {fecha_inicio} a {fecha_fin}\n")

    # Actualizar .env temporalmente
    ad_account_id = cliente_info['ad_account_id']

    # Leer .env actual
    with open('.env', 'r') as f:
        env_lines = f.readlines()

    # Actualizar AD_ACCOUNT_ID
    with open('.env', 'w') as f:
        for line in env_lines:
            if line.startswith('AD_ACCOUNT_ID='):
                f.write(f'AD_ACCOUNT_ID={ad_account_id}\n')
            else:
                f.write(line)

    print("🔄 Ejecutando análisis...")

    # Ejecutar meta_ads_analyzer
    cmd = [
        'python3',
        'meta_ads_analyzer.py'
    ]

    # Pasar inputs
    inputs = f"{cliente_info['nombre']}\n{fecha_inicio}\n{fecha_fin}\n"

    try:
        result = subprocess.run(
            cmd,
            input=inputs,
            text=True,
            capture_output=True,
            timeout=120
        )

        print(result.stdout)

        if result.returncode != 0:
            print(f"\n⚠️ Error en el análisis:")
            print(result.stderr)
            return False

        # Buscar el archivo JSON generado
        json_file = f"output/{cliente_info['nombre']}_{fecha_inicio}_{fecha_fin}_analisis_pauta.json"

        if not os.path.exists(json_file):
            print(f"⚠️ No se generó el archivo JSON esperado: {json_file}")
            return False

        print(f"\n📄 Generando PDF...")

        # Determinar estética según categoría
        cmd = ['python3', 'generate_pdf_report.py', json_file]
        if cliente_info['categoria'] == 'Estética SOMA':
            cmd.append('soma')
            print(f"   → Usando estética SOMA")
        else:
            print(f"   → Usando estética LINE")

        # Generar PDF
        pdf_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        print(pdf_result.stdout)

        if pdf_result.returncode == 0:
            print(f"\n{'='*70}")
            print(f"✅ REPORTE COMPLETADO PARA {cliente_info['nombre'].upper()}")
            print(f"{'='*70}")
            print(f"\n📁 Archivos generados:")
            print(f"   JSON: {json_file}")

            pdf_name = json_file.replace('output/', 'output/ENTREGABLES/Reporte_Pauta_').replace('.json', '.pdf')
            print(f"   PDF:  {pdf_name}")
            print(f"\n{'='*70}\n")
            return True
        else:
            print(f"⚠️ Error generando PDF:")
            print(pdf_result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("⚠️ Timeout: El análisis tomó demasiado tiempo")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) == 1:
        # Sin argumentos, listar clientes
        listar_clientes()
        print("Uso: python3 generar_reporte.py CLIENTE FECHA_INICIO FECHA_FIN")
        print("\nEjemplos:")
        print("  python3 generar_reporte.py CBS 2025-10-01 2025-10-31")
        print("  python3 generar_reporte.py MEDICAL 2025-10-01 2025-10-31")
        print("  python3 generar_reporte.py NATAL 2025-10-01 2025-10-31")
        return

    if len(sys.argv) < 4:
        print("❌ Faltan argumentos")
        print("\nUso: python3 generar_reporte.py CLIENTE FECHA_INICIO FECHA_FIN")
        print("Ejemplo: python3 generar_reporte.py CBS 2025-10-01 2025-10-31")
        print("\nPara ver lista de clientes: python3 generar_reporte.py")
        return

    cliente = sys.argv[1]
    fecha_inicio = sys.argv[2]
    fecha_fin = sys.argv[3]

    generar_reporte(cliente, fecha_inicio, fecha_fin)

if __name__ == "__main__":
    main()
