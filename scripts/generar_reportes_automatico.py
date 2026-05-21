#!/usr/bin/env python3
"""
Sistema Automatizado de Generación de Reportes Mensuales
=========================================================

Este script genera reportes mensuales de Meta Ads de forma consistente,
guardando automáticamente en la estructura correcta de carpetas.

Uso:
    python generar_reportes_automatico.py --mes 12 --ano 2025 --cliente "PERFIL SRL"
    python generar_reportes_automatico.py --mes 01 --ano 2026 --todos
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Importar el analizador de Meta Ads (debe estar en la misma carpeta)
from meta_ads_analyzer import MetaAdsAnalyzer


def cargar_configuracion():
    """Carga la configuración desde config.json"""
    config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        print("❌ Error: No se encontró el archivo config.json")
        print(f"   Buscado en: {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def obtener_periodo_mes(ano, mes):
    """
    Calcula el primer y último día del mes

    Args:
        ano: Año (ej: 2025)
        mes: Mes como número (1-12) o string ("01"-"12")

    Returns:
        tuple: (fecha_inicio, fecha_fin) en formato "YYYY-MM-DD"
    """
    mes_num = int(mes)

    # Primer día del mes
    fecha_inicio = f"{ano}-{mes_num:02d}-01"

    # Último día del mes
    if mes_num == 12:
        proximo_mes = datetime(ano + 1, 1, 1)
    else:
        proximo_mes = datetime(ano, mes_num + 1, 1)

    ultimo_dia = proximo_mes - timedelta(days=1)
    fecha_fin = ultimo_dia.strftime("%Y-%m-%d")

    return fecha_inicio, fecha_fin


def generar_nombre_carpeta_mes(ano, mes, config):
    """
    Genera el nombre de la carpeta del mes según el formato configurado

    Args:
        ano: Año (ej: 2025)
        mes: Mes como número o string
        config: Diccionario de configuración

    Returns:
        str: Nombre de carpeta (ej: "2025-12-DIC")
    """
    mes_num = int(mes)
    mes_str = f"{mes_num:02d}"
    mes_abrev = config['meses'][mes_str]

    return f"{ano}-{mes_str}-{mes_abrev}"


def crear_estructura_carpetas(ruta_base, nombre_carpeta_mes, nombre_cliente):
    """
    Crea la estructura de carpetas necesaria

    Args:
        ruta_base: Ruta base de reportes
        nombre_carpeta_mes: Nombre de la carpeta del mes (ej: "2025-12-DIC")
        nombre_cliente: Nombre del cliente

    Returns:
        Path: Ruta completa a la carpeta meta del cliente
    """
    ruta_completa = Path(ruta_base) / nombre_carpeta_mes / nombre_cliente / "meta"
    ruta_completa.mkdir(parents=True, exist_ok=True)

    # Crear también la carpeta de imágenes
    (ruta_completa / "images").mkdir(exist_ok=True)

    return ruta_completa


def extraer_datos_meta(config, cliente_config, fecha_inicio, fecha_fin):
    """
    Extrae datos de Meta Ads para un cliente

    Args:
        config: Configuración general
        cliente_config: Configuración específica del cliente
        fecha_inicio: Fecha inicio del período
        fecha_fin: Fecha fin del período

    Returns:
        dict: Datos extraídos y analizados
    """
    access_token = config['meta_access_token']
    ad_account_id = cliente_config['meta_ad_account_id']

    print(f"\n🔗 Conectando a Meta Ads...")
    print(f"   Account ID: {ad_account_id}")

    analyzer = MetaAdsAnalyzer(access_token, ad_account_id)

    print(f"📥 Extrayendo datos de campañas ({fecha_inicio} a {fecha_fin})...")
    ads_data = analyzer.get_campaigns_data(fecha_inicio, fecha_fin)

    print(f"📥 Extrayendo datos de conjuntos de anuncios...")
    adsets_data = analyzer.get_adsets_summary(fecha_inicio, fecha_fin)

    if not ads_data:
        print("⚠️  No se encontraron datos para este período")
        return None

    print(f"📊 Analizando datos...")
    analysis = analyzer.analyze_data(ads_data, adsets_data)

    return {
        'ads_data': ads_data,
        'adsets_data': adsets_data,
        'analysis': analysis
    }


def guardar_reporte_json(datos, ruta_carpeta, nombre_cliente, fecha_inicio, fecha_fin):
    """
    Guarda los datos en formato JSON

    Args:
        datos: Diccionario con los datos a guardar
        ruta_carpeta: Ruta donde guardar el archivo
        nombre_cliente: Nombre del cliente
        fecha_inicio: Fecha inicio
        fecha_fin: Fecha fin

    Returns:
        Path: Ruta al archivo guardado
    """
    # Nombre de archivo estandarizado
    nombre_archivo = f"{nombre_cliente}_{fecha_inicio}_{fecha_fin}_analisis_pauta.json"
    ruta_archivo = ruta_carpeta / nombre_archivo

    # Preparar estructura del reporte
    reporte = {
        'metadata': {
            'cliente': nombre_cliente,
            'periodo': f"{fecha_inicio}_{fecha_fin}",
            'fecha_generacion': datetime.now().isoformat(),
        },
        'resumen': {
            'inversion_total': datos['analysis']['total_spend'],
            'alcance_total': datos['analysis']['total_reach'],
            'impresiones_totales': datos['analysis']['total_impressions'],
            'total_anuncios': datos['analysis']['total_ads'],
            'total_conjuntos': datos['analysis']['total_adsets'],
        },
        'conjuntos_de_anuncios': datos['adsets_data'],
        'anuncios': datos['ads_data'],
        'analisis': datos['analysis'],
    }

    # Guardar
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

    return ruta_archivo


def mostrar_resumen(datos, nombre_cliente):
    """Muestra un resumen de los datos extraídos"""
    analysis = datos['analysis']

    print("\n" + "="*70)
    print(f"📈 RESUMEN - {nombre_cliente}")
    print("="*70)
    print(f"  💰 Inversión total: ${analysis['total_spend']:,.2f}")
    print(f"  👥 Alcance total: {analysis['total_reach']:,} personas")
    print(f"  👁️  Impresiones: {analysis['total_impressions']:,}")
    print(f"  📢 Anuncios corridos: {analysis['total_ads']}")
    print(f"  📦 Conjuntos: {analysis['total_adsets']}")
    print("="*70)


def generar_reporte_cliente(config, nombre_cliente, ano, mes):
    """
    Genera el reporte completo para un cliente

    Args:
        config: Configuración completa
        nombre_cliente: Nombre del cliente
        ano: Año
        mes: Mes

    Returns:
        bool: True si se generó exitosamente, False si hubo error
    """
    print("\n" + "="*70)
    print(f"🚀 Generando reporte para: {nombre_cliente}")
    print("="*70)

    # Validar que el cliente exista
    if nombre_cliente not in config['clientes']:
        print(f"❌ Error: Cliente '{nombre_cliente}' no encontrado en la configuración")
        print(f"   Clientes disponibles: {', '.join(config['clientes'].keys())}")
        return False

    cliente_config = config['clientes'][nombre_cliente]

    # Verificar que el cliente esté activo
    if not cliente_config.get('activo', True):
        print(f"⚠️  Cliente '{nombre_cliente}' está marcado como inactivo")
        return False

    # Verificar que tenga configurado el ID de cuenta
    if not cliente_config.get('meta_ad_account_id'):
        print(f"❌ Error: Cliente '{nombre_cliente}' no tiene configurado meta_ad_account_id")
        return False

    # Calcular período
    fecha_inicio, fecha_fin = obtener_periodo_mes(ano, mes)
    nombre_carpeta_mes = generar_nombre_carpeta_mes(ano, mes, config)

    print(f"📅 Período: {fecha_inicio} a {fecha_fin}")
    print(f"📁 Carpeta: {nombre_carpeta_mes}/{nombre_cliente}/meta/")

    # Crear estructura de carpetas
    ruta_carpeta = crear_estructura_carpetas(
        config['ruta_base_reportes'],
        nombre_carpeta_mes,
        nombre_cliente
    )

    # Extraer datos
    try:
        datos = extraer_datos_meta(config, cliente_config, fecha_inicio, fecha_fin)

        if datos is None:
            return False

        # Guardar JSON
        ruta_json = guardar_reporte_json(
            datos,
            ruta_carpeta,
            nombre_cliente,
            fecha_inicio,
            fecha_fin
        )

        print(f"\n✅ Reporte JSON guardado en:")
        print(f"   {ruta_json}")

        # Mostrar resumen
        mostrar_resumen(datos, nombre_cliente)

        return True

    except Exception as e:
        print(f"\n❌ Error al generar reporte: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generador Automático de Reportes Mensuales de Meta Ads',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Generar reporte de un cliente específico
  python generar_reportes_automatico.py --mes 12 --ano 2025 --cliente "PERFIL SRL"

  # Generar reportes de todos los clientes activos
  python generar_reportes_automatico.py --mes 01 --ano 2026 --todos

  # Generar reportes de varios clientes
  python generar_reportes_automatico.py --mes 12 --ano 2025 --cliente ASPA --cliente CREAR
        """
    )

    parser.add_argument('--mes', type=int, required=True,
                       help='Mes (1-12)')
    parser.add_argument('--ano', type=int, required=True,
                       help='Año (ej: 2025)')
    parser.add_argument('--cliente', action='append',
                       help='Nombre del cliente (puede repetirse para múltiples clientes)')
    parser.add_argument('--todos', action='store_true',
                       help='Generar reportes para todos los clientes activos')

    args = parser.parse_args()

    # Validar mes
    if not 1 <= args.mes <= 12:
        print("❌ Error: El mes debe estar entre 1 y 12")
        sys.exit(1)

    # Cargar configuración
    print("\n📋 Cargando configuración...")
    config = cargar_configuracion()
    print(f"✅ Configuración cargada")
    print(f"   Ruta base: {config['ruta_base_reportes']}")
    print(f"   Clientes configurados: {len(config['clientes'])}")

    # Determinar qué clientes procesar
    if args.todos:
        clientes_a_procesar = [
            nombre for nombre, conf in config['clientes'].items()
            if conf.get('activo', True)
        ]
        print(f"\n📊 Procesando TODOS los clientes activos ({len(clientes_a_procesar)})")
    elif args.cliente:
        clientes_a_procesar = args.cliente
        print(f"\n📊 Procesando {len(clientes_a_procesar)} cliente(s)")
    else:
        print("\n❌ Error: Debe especificar --cliente o --todos")
        parser.print_help()
        sys.exit(1)

    # Generar reportes
    exitosos = 0
    fallidos = 0

    for nombre_cliente in clientes_a_procesar:
        resultado = generar_reporte_cliente(config, nombre_cliente, args.ano, args.mes)

        if resultado:
            exitosos += 1
        else:
            fallidos += 1

    # Resumen final
    print("\n" + "="*70)
    print("🏁 PROCESO COMPLETADO")
    print("="*70)
    print(f"  ✅ Exitosos: {exitosos}")
    if fallidos > 0:
        print(f"  ❌ Fallidos: {fallidos}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
