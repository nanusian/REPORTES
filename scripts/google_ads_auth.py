#!/usr/bin/env python3
"""
Script para generar refresh token de Google Ads
Ejecutar una sola vez para obtener el refresh token
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json

def generate_refresh_token():
    """Genera el refresh token para Google Ads API"""

    client_secrets_path = "/Users/laureanomedeot/Documents/REPORTES/config/client_secret_1013023880186-3d80cv632j08mtgphqm1m15vvvv2if5j.apps.googleusercontent.com.json"

    # Scopes necesarios para Google Ads API
    SCOPES = ['https://www.googleapis.com/auth/adwords']

    print("🔐 Generando refresh token para Google Ads API...")
    print("\nSe abrirá una ventana del navegador para que autorices el acceso.")
    print("Seleccioná tu cuenta de Google que tiene acceso a Google Ads.\n")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_path,
            scopes=SCOPES
        )

        # Esto abre el navegador para autenticación
        credentials = flow.run_local_server(port=0)

        print("\n✅ Autenticación exitosa!")
        print(f"\n📋 Refresh Token:")
        print(f"{credentials.refresh_token}")
        print("\n💡 Copiá este token y pegalo en el archivo:")
        print("   /Users/laureanomedeot/Documents/REPORTES/config/google-ads.yaml")
        print("   en la línea 'refresh_token'\n")

        return credentials.refresh_token

    except Exception as e:
        print(f"\n❌ Error durante la autenticación: {e}")
        return None

if __name__ == "__main__":
    generate_refresh_token()
