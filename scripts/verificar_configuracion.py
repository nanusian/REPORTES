#!/usr/bin/env python3
"""
Script para verificar que la configuración esté correcta
antes de generar reportes.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def verificar_config():
    """Verifica que config.json esté correctamente configurado"""

    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
    print("="*70 + "\n")

    # 1. Verificar que existe config.json
    config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        print("❌ Error: No se encontró config.json")
        print(f"   Esperado en: {config_path}")
        return False

    print(f"✅ Archivo config.json encontrado")

    # 2. Cargar y parsear JSON
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ config.json es un JSON válido")
    except json.JSONDecodeError as e:
        print(f"❌ Error: config.json tiene errores de sintaxis")
        print(f"   {e}")
        return False

    # 3. Verificar token de Meta
    print("\n📱 Meta Ads:")
    if not config.get('meta_access_token'):
        print("❌ Falta: meta_access_token")
        return False
    else:
        token = config['meta_access_token']
        token_preview = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else token
        print(f"✅ Token configurado: {token_preview}")

        if config.get('token_expiracion_nota'):
            print(f"   Nota: {config['token_expiracion_nota']}")

    # 4. Verificar ruta base
    print("\n📁 Ruta de reportes:")
    ruta_base = config.get('ruta_base_reportes')
    if not ruta_base:
        print("❌ Falta: ruta_base_reportes")
        return False

    ruta_path = Path(ruta_base)
    if not ruta_path.exists():
        print(f"⚠️  La ruta no existe: {ruta_base}")
        print("   Se creará automáticamente al generar reportes")
    else:
        print(f"✅ Ruta existe: {ruta_base}")

    # 5. Verificar clientes
    print("\n👥 Clientes:")
    if not config.get('clientes'):
        print("❌ No hay clientes configurados")
        return False

    clientes = config['clientes']
    print(f"   Total configurados: {len(clientes)}")

    activos = 0
    incompletos = []

    for nombre, datos in clientes.items():
        es_activo = datos.get('activo', True)
        tiene_meta_id = bool(datos.get('meta_ad_account_id'))

        if es_activo:
            activos += 1
            if not tiene_meta_id:
                incompletos.append(nombre)

    print(f"   Activos: {activos}")

    if incompletos:
        print(f"\n⚠️  Clientes sin meta_ad_account_id configurado:")
        for nombre in incompletos:
            print(f"      - {nombre}")

    # 6. Mostrar resumen de clientes
    print("\n📋 Lista de clientes:")
    for nombre, datos in clientes.items():
        es_activo = datos.get('activo', True)
        tiene_meta = bool(datos.get('meta_ad_account_id'))
        tiene_google = bool(datos.get('google_customer_id'))

        status = "✅" if es_activo else "⏸️ "
        meta_icon = "📱" if tiene_meta else "❌"
        google_icon = "🔍" if tiene_google else "⚪"

        print(f"   {status} {nombre}")
        print(f"      Meta: {meta_icon}  Google: {google_icon}")

        if datos.get('meta_ad_account_id'):
            print(f"      ID: {datos['meta_ad_account_id']}")

    # 7. Verificar dependencias
    print("\n📦 Dependencias:")

    # Verificar meta_ads_analyzer.py
    analyzer_path = Path(__file__).parent / "meta_ads_analyzer.py"
    if analyzer_path.exists():
        print("✅ meta_ads_analyzer.py encontrado")
    else:
        print("⚠️  No se encontró meta_ads_analyzer.py")
        print("   Necesario para extraer datos de Meta Ads")

    # Verificar generate_full_report.py
    report_gen_path = Path(__file__).parent / "generate_full_report.py"
    if report_gen_path.exists():
        print("✅ generate_full_report.py encontrado")
    else:
        print("⚠️  No se encontró generate_full_report.py")
        print("   Necesario para generar reportes HTML")

    # 8. Resumen final
    print("\n" + "="*70)
    if incompletos:
        print("⚠️  CONFIGURACIÓN INCOMPLETA")
        print("\nAcciones requeridas:")
        print("1. Completar meta_ad_account_id para los clientes listados arriba")
        print("2. Editar: /Users/laureanomedeot/Documents/REPORTES/scripts/config.json")
        return False
    else:
        print("✅ CONFIGURACIÓN CORRECTA")
        print("\n¡Todo listo para generar reportes!")
        print("\nComando sugerido:")
        print("  python generar_reportes_automatico.py --mes 1 --ano 2026 --todos")

    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    resultado = verificar_config()
    sys.exit(0 if resultado else 1)
