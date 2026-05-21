#!/usr/bin/env python3
"""
Google Ads Analyzer - Sistema de extracción de datos de Google Ads
Conecta con Google Ads API para extraer métricas de campañas
"""

import os
import json
import sys
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

class GoogleAdsAnalyzer:
    def __init__(self, config_path):
        """Inicializa cliente de Google Ads"""
        self.client = GoogleAdsClient.load_from_storage(config_path)
        self.customer_id = "4169558728"
        print(f"✅ Conectado a cuenta: {self.customer_id}")

    def get_campaigns_data(self, date_from, date_until):
        """Extrae datos de campañas en el período especificado"""

        print(f"\n🔍 Extrayendo datos del período: {date_from} a {date_until}\n")

        ga_service = self.client.get_service("GoogleAdsService")

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                ad_group.id,
                ad_group.name,
                ad_group.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.average_cpm,
                metrics.video_views,
                metrics.cost_per_conversion,
                segments.date
            FROM ad_group
            WHERE
                segments.date >= '{date_from}'
                AND segments.date <= '{date_until}'
                AND campaign.status = 'ENABLED'
            ORDER BY segments.date
        """

        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)

            campaigns_data = []
            daily_data = {}

            for row in response:
                campaign_name = row.campaign.name
                ad_group_name = row.ad_group.name
                date = row.segments.date

                # Convertir micros a moneda
                cost = row.metrics.cost_micros / 1_000_000
                avg_cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0
                avg_cpm = row.metrics.average_cpm / 1_000_000 if row.metrics.average_cpm else 0
                cost_per_conv = row.metrics.cost_per_conversion / 1_000_000 if row.metrics.cost_per_conversion else 0

                record = {
                    'campaign_id': row.campaign.id,
                    'campaign_name': campaign_name,
                    'campaign_status': row.campaign.status.name,
                    'ad_group_id': row.ad_group.id,
                    'ad_group_name': ad_group_name,
                    'ad_group_status': row.ad_group.status.name,
                    'date': date,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'cost': cost,
                    'conversions': row.metrics.conversions,
                    'conversions_value': row.metrics.conversions_value,
                    'ctr': row.metrics.ctr,
                    'avg_cpc': avg_cpc,
                    'avg_cpm': avg_cpm,
                    'video_views': row.metrics.video_views,
                    'cost_per_conversion': cost_per_conv
                }

                campaigns_data.append(record)

                # Agrupar por fecha para datos diarios
                if date not in daily_data:
                    daily_data[date] = {
                        'date': date,
                        'impressions': 0,
                        'clicks': 0,
                        'cost': 0,
                        'conversions': 0
                    }

                daily_data[date]['impressions'] += row.metrics.impressions
                daily_data[date]['clicks'] += row.metrics.clicks
                daily_data[date]['cost'] += cost
                daily_data[date]['conversions'] += row.metrics.conversions

                print(f"   📊 {campaign_name} > {ad_group_name}")
                print(f"      Fecha: {date} | Clics: {row.metrics.clicks} | Inversión: ${cost:,.2f}")

            print(f"\n✅ Extraídos {len(campaigns_data)} registros\n")

            # Convertir daily_data dict a lista ordenada
            daily_list = sorted(daily_data.values(), key=lambda x: x['date'])

            return campaigns_data, daily_list

        except GoogleAdsException as ex:
            print(f"❌ Error de Google Ads API:")
            for error in ex.failure.errors:
                print(f"   {error.message}")
            return [], []

    def aggregate_by_ad_group(self, campaigns_data):
        """Agrupa datos por grupo de anuncios"""

        ad_groups = {}

        for record in campaigns_data:
            key = f"{record['campaign_name']}|{record['ad_group_name']}"

            if key not in ad_groups:
                ad_groups[key] = {
                    'campaign_name': record['campaign_name'],
                    'ad_group_name': record['ad_group_name'],
                    'impressions': 0,
                    'clicks': 0,
                    'cost': 0,
                    'conversions': 0,
                    'conversions_value': 0
                }

            ad_groups[key]['impressions'] += record['impressions']
            ad_groups[key]['clicks'] += record['clicks']
            ad_groups[key]['cost'] += record['cost']
            ad_groups[key]['conversions'] += record['conversions']
            ad_groups[key]['conversions_value'] += record['conversions_value']

        # Calcular métricas derivadas
        for ad_group in ad_groups.values():
            if ad_group['clicks'] > 0:
                ad_group['ctr'] = (ad_group['clicks'] / ad_group['impressions']) * 100
                ad_group['avg_cpc'] = ad_group['cost'] / ad_group['clicks']
            else:
                ad_group['ctr'] = 0
                ad_group['avg_cpc'] = 0

            if ad_group['conversions'] > 0:
                ad_group['cost_per_conversion'] = ad_group['cost'] / ad_group['conversions']
            else:
                ad_group['cost_per_conversion'] = 0

        return list(ad_groups.values())

    def save_report(self, campaigns_data, ad_groups_data, daily_data, cliente, periodo):
        """Guarda el reporte en JSON"""

        # Calcular totales
        total_cost = sum(r['cost'] for r in campaigns_data)
        total_clicks = sum(r['clicks'] for r in campaigns_data)
        total_impressions = sum(r['impressions'] for r in campaigns_data)
        total_conversions = sum(r['conversions'] for r in campaigns_data)

        # Determinar mes del reporte para estructura de carpetas
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
                'customer_id': self.customer_id,
                'plataforma': 'Google Ads'
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

        return report


def main():
    """Función principal"""

    config_path = "/Users/laureanomedeot/Documents/REPORTES/config/google-ads.yaml"

    print("\n" + "="*70)
    print("📊 GOOGLE ADS ANALYZER - Generador de Reportes")
    print("="*70 + "\n")

    cliente = input("Nombre del cliente: ").strip() or "ASPA"

    print("\nPeríodo del reporte:")
    print("  Formato: YYYY-MM-DD")
    date_from = input("  Desde (ej: 2025-09-01): ").strip()
    date_until = input("  Hasta (ej: 2025-09-30): ").strip()

    if not date_from or not date_until:
        print("❌ Debes ingresar ambas fechas")
        sys.exit(1)

    periodo = f"{date_from}_{date_until}"

    # Conectar y extraer datos
    analyzer = GoogleAdsAnalyzer(config_path)

    campaigns_data, daily_data = analyzer.get_campaigns_data(date_from, date_until)

    if not campaigns_data:
        print("⚠️  No se encontraron datos para el período especificado")
        sys.exit(0)

    # Agregar por grupo de anuncios
    ad_groups_data = analyzer.aggregate_by_ad_group(campaigns_data)

    # Guardar reporte
    report = analyzer.save_report(campaigns_data, ad_groups_data, daily_data, cliente, periodo)

    # Mostrar resumen
    print("\n" + "="*70)
    print("📈 RESUMEN DEL PERÍODO")
    print("="*70)
    print(f"  Inversión total: ${report['resumen']['inversion_total']:,.2f}")
    print(f"  Clics totales: {report['resumen']['clics_totales']:,}")
    print(f"  Impresiones: {report['resumen']['impresiones_totales']:,}")
    print(f"  Conversiones: {report['resumen']['conversiones_totales']}")
    print(f"  Grupos de anuncios: {report['resumen']['total_grupos']}")
    print("="*70 + "\n")

    print("✅ Proceso completado!\n")


if __name__ == "__main__":
    main()
