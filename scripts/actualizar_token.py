#!/usr/bin/env python3
"""
Script para actualizar el token de Meta Ads en config.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def actualizar_token():
    """Actualiza el token de Meta en config.json"""

    print("\n" + "="*70)
    print("🔑 ACTUALIZAR TOKEN DE META ADS")
    print("="*70 + "\n")

    config_path = Path(__file__).parent / "config.json"

    # Verificar que existe config.json
    if not config_path.exists():
        print("❌ Error: No se encontró config.json")
        return False

    # Cargar configuración actual
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Mostrar token actual (parcialmente oculto)
    token_actual = config.get('meta_access_token', '')
    if token_actual:
        preview = f"{token_actual[:15]}...{token_actual[-10:]}"
        print(f"Token actual: {preview}")
        if config.get('token_expiracion_nota'):
            print(f"Nota: {config['token_expiracion_nota']}\n")
    else:
        print("⚠️  No hay token configurado actualmente\n")

    # Solicitar nuevo token
    print("Obtén un nuevo token en:")
    print("https://developers.facebook.com/tools/explorer/\n")

    print("Pasos:")
    print("1. Selecciona tu aplicación")
    print("2. Genera un token con permisos 'ads_read'")
    print("3. Copia el token generado\n")

    nuevo_token = input("Ingresa el nuevo token (o presiona Enter para cancelar): ").strip()

    if not nuevo_token:
        print("\n❌ Operación cancelada")
        return False

    # Validación básica
    if len(nuevo_token) < 50:
        print("\n⚠️  El token parece muy corto. ¿Estás seguro que es correcto?")
        confirmar = input("¿Continuar de todos modos? (si/no): ").strip().lower()
        if confirmar not in ['si', 's', 'yes', 'y']:
            print("❌ Operación cancelada")
            return False

    # Actualizar configuración
    config['meta_access_token'] = nuevo_token
    config['token_expiracion_nota'] = f"Última actualización: {datetime.now().strftime('%Y-%m-%d')}"

    # Guardar
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print("\n✅ Token actualizado exitosamente")
        print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Archivo: {config_path}")

        print("\n💡 Recuerda:")
        print("   - Los tokens de Meta expiran cada ~60 días")
        print("   - Actualiza esta fecha en tu calendario para el próximo cambio")

        return True

    except Exception as e:
        print(f"\n❌ Error al guardar: {e}")
        return False


if __name__ == "__main__":
    resultado = actualizar_token()
    print("\n" + "="*70 + "\n")
    sys.exit(0 if resultado else 1)
