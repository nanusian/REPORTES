#!/usr/bin/env python3
"""
Meta Ads Analyzer - Sistema de análisis de campañas publicitarias
Conecta directamente con Meta Ads API para extraer datos y generar reportes
"""

import os
import json
import sys
from datetime import datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights

class MetaAdsAnalyzer:
    def __init__(self, access_token, ad_account_id):
        """Inicializa la conexión con Meta Ads API"""
        self.access_token = access_token
        self.ad_account_id = ad_account_id

        # Inicializar API
        FacebookAdsApi.init(access_token=access_token)
        self.account = AdAccount(ad_account_id)

        print(f"✅ Conectado a cuenta: {ad_account_id}")

    def get_campaigns_data(self, date_from, date_until):
        """Extrae datos de todas las campañas en el período especificado"""

        print(f"\n🔍 Extrayendo datos del período: {date_from} a {date_until}\n")

        # Campos a solicitar
        fields = [
            AdsInsights.Field.campaign_name,
            AdsInsights.Field.adset_name,
            AdsInsights.Field.ad_name,
            AdsInsights.Field.impressions,
            AdsInsights.Field.reach,
            AdsInsights.Field.frequency,
            AdsInsights.Field.clicks,
            AdsInsights.Field.spend,
            AdsInsights.Field.cpc,
            AdsInsights.Field.cpm,
            AdsInsights.Field.ctr,
            AdsInsights.Field.actions,
            AdsInsights.Field.action_values,
            AdsInsights.Field.cost_per_action_type,
        ]

        params = {
            'time_range': {
                'since': date_from,
                'until': date_until
            },
            'level': 'ad',  # Nivel de anuncio individual
            'breakdowns': [],
        }

        # Obtener insights
        insights = self.account.get_insights(fields=fields, params=params)

        all_data = []
        for insight in insights:
            data = insight.export_all_data()

            # Procesar acciones (conversaciones, leads, etc)
            actions = {}
            if 'actions' in data:
                for action in data['actions']:
                    action_type = action['action_type']
                    actions[action_type] = int(action['value'])

            # Procesar costos por acción
            cost_per_actions = {}
            if 'cost_per_action_type' in data:
                for cpa in data['cost_per_action_type']:
                    action_type = cpa['action_type']
                    cost_per_actions[action_type] = float(cpa['value'])

            # Crear registro limpio
            record = {
                'campaign_name': data.get('campaign_name', ''),
                'adset_name': data.get('adset_name', ''),
                'ad_name': data.get('ad_name', ''),
                'impressions': int(data.get('impressions', 0)),
                'reach': int(data.get('reach', 0)),
                'frequency': float(data.get('frequency', 0)),
                'clicks': int(data.get('clicks', 0)),
                'spend': float(data.get('spend', 0)),
                'cpc': float(data.get('cpc', 0)),
                'cpm': float(data.get('cpm', 0)),
                'ctr': float(data.get('ctr', 0)),
                'actions': actions,
                'cost_per_actions': cost_per_actions,
            }

            all_data.append(record)

            print(f"   📊 {record['adset_name']} > {record['ad_name']}")
            print(f"      Alcance: {record['reach']:,} | Inversión: ${record['spend']:,.2f}")

        print(f"\n✅ Extraídos {len(all_data)} anuncios\n")

        return all_data

    def get_daily_data(self, date_from, date_until):
        """Obtiene datos diarios para gráficos de evolución"""

        print("📈 Extrayendo datos diarios para gráficos...")

        fields = [
            AdsInsights.Field.date_start,
            AdsInsights.Field.impressions,
            AdsInsights.Field.reach,
            AdsInsights.Field.spend,
            AdsInsights.Field.actions,
        ]

        params = {
            'time_range': {
                'since': date_from,
                'until': date_until
            },
            'level': 'account',
            'time_increment': 1,  # Datos por día
        }

        insights = self.account.get_insights(fields=fields, params=params)

        daily_data = []
        for insight in insights:
            data = insight.export_all_data()

            # Procesar conversaciones
            conversaciones = 0
            if 'actions' in data:
                for action in data['actions']:
                    if action['action_type'] == 'onsite_conversion.messaging_conversation_started_7d':
                        conversaciones = int(action['value'])
                        break

            daily_data.append({
                'date': data.get('date_start', ''),
                'impressions': int(data.get('impressions', 0)),
                'reach': int(data.get('reach', 0)),
                'spend': float(data.get('spend', 0)),
                'conversaciones': conversaciones,
            })

        print(f"✅ {len(daily_data)} días de datos extraídos\n")
        return daily_data

    def get_adsets_summary(self, date_from, date_until):
        """Obtiene resumen agrupado por conjunto de anuncios"""

        fields = [
            AdsInsights.Field.adset_name,
            AdsInsights.Field.impressions,
            AdsInsights.Field.reach,
            AdsInsights.Field.frequency,
            AdsInsights.Field.spend,
            AdsInsights.Field.actions,
            AdsInsights.Field.cost_per_action_type,
        ]

        params = {
            'time_range': {
                'since': date_from,
                'until': date_until
            },
            'level': 'adset',  # Agrupado por conjunto
        }

        insights = self.account.get_insights(fields=fields, params=params)

        adsets_data = []
        for insight in insights:
            data = insight.export_all_data()

            # Procesar acciones
            actions = {}
            if 'actions' in data:
                for action in data['actions']:
                    actions[action['action_type']] = int(action['value'])

            # Procesar costos
            cost_per_actions = {}
            if 'cost_per_action_type' in data:
                for cpa in data['cost_per_action_type']:
                    cost_per_actions[cpa['action_type']] = float(cpa['value'])

            record = {
                'adset_name': data.get('adset_name', ''),
                'impressions': int(data.get('impressions', 0)),
                'reach': int(data.get('reach', 0)),
                'frequency': float(data.get('frequency', 0)),
                'spend': float(data.get('spend', 0)),
                'actions': actions,
                'cost_per_actions': cost_per_actions,
            }

            adsets_data.append(record)

        return adsets_data

    def generate_insights(self, ads_data, adsets_data):
        """Genera insights automáticos basados en métricas"""

        insights = []

        # 1. Detectar frecuencia alta (saturación de audiencia)
        for ad in ads_data:
            if ad['frequency'] > 5:
                insights.append({
                    'tipo': 'ALERTA',
                    'prioridad': 'alta',
                    'titulo': f"Saturación de audiencia en '{ad['ad_name']}'",
                    'descripcion': f"Frecuencia de {ad['frequency']:.1f} indica que las mismas personas ven el anuncio muchas veces. Recomendación: ampliar audiencia o pausar anuncio.",
                    'metrica': f"Frecuencia: {ad['frequency']:.1f}",
                    'accion': 'Ampliar audiencia o rotar creatividad'
                })

        # 2. Detectar CTR bajo
        avg_ctr = sum(ad['ctr'] for ad in ads_data) / len(ads_data) if ads_data else 0
        for ad in ads_data:
            if ad['ctr'] < 1.0 and ad['ctr'] < avg_ctr * 0.5:
                insights.append({
                    'tipo': 'OPORTUNIDAD',
                    'prioridad': 'media',
                    'titulo': f"CTR bajo en '{ad['ad_name']}'",
                    'descripcion': f"CTR de {ad['ctr']:.2f}% está muy por debajo del promedio ({avg_ctr:.2f}%). El anuncio no está generando interés.",
                    'metrica': f"CTR: {ad['ctr']:.2f}%",
                    'accion': 'Testear nuevo copy o creatividad más llamativa'
                })

        # 3. Detectar CPC alto
        avg_cpc = sum(ad['cpc'] for ad in ads_data) / len(ads_data) if ads_data else 0
        for ad in ads_data:
            if ad['cpc'] > avg_cpc * 1.5 and ad['spend'] > 10000:
                insights.append({
                    'tipo': 'ALERTA',
                    'prioridad': 'alta',
                    'titulo': f"Costo por click alto en '{ad['ad_name']}'",
                    'descripcion': f"CPC de ${ad['cpc']:.0f} es 50% más alto que el promedio (${avg_cpc:.0f}). Estás pagando de más por cada click.",
                    'metrica': f"CPC: ${ad['cpc']:.0f}",
                    'accion': 'Optimizar segmentación o pausar si no convierte'
                })

        # 4. Detectar anuncios con buen rendimiento
        for ad in ads_data:
            if ad['ctr'] > 2.0 and ad['frequency'] < 4:
                insights.append({
                    'tipo': 'ÉXITO',
                    'prioridad': 'baja',
                    'titulo': f"Excelente performance en '{ad['ad_name']}'",
                    'descripcion': f"CTR de {ad['ctr']:.2f}% con frecuencia controlada ({ad['frequency']:.1f}). Este anuncio está funcionando muy bien.",
                    'metrica': f"CTR: {ad['ctr']:.2f}% | Frecuencia: {ad['frequency']:.1f}",
                    'accion': 'Escalar presupuesto si hay margen'
                })

        # 5. Analizar conversaciones vs inversión
        for adset in adsets_data:
            conversations = adset['actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)
            cost_per_conv = adset['cost_per_actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)

            if conversations > 0 and cost_per_conv > 5000:
                insights.append({
                    'tipo': 'OPORTUNIDAD',
                    'prioridad': 'media',
                    'titulo': f"Costo por conversación alto en '{adset['adset_name']}'",
                    'descripcion': f"Estás pagando ${cost_per_conv:,.0f} por cada conversación. Hay margen para optimizar.",
                    'metrica': f"{conversations} conversaciones a ${cost_per_conv:,.0f} c/u",
                    'accion': 'Refinar audiencia o mejorar oferta/copy'
                })

        # 6. Detectar anuncios con poca inversión pero buen rendimiento
        total_spend = sum(ad['spend'] for ad in ads_data)
        avg_spend = total_spend / len(ads_data) if ads_data else 0
        for ad in ads_data:
            if ad['spend'] < avg_spend * 0.3 and ad['ctr'] > avg_ctr:
                insights.append({
                    'tipo': 'OPORTUNIDAD',
                    'prioridad': 'alta',
                    'titulo': f"Subinversión en anuncio con potencial: '{ad['ad_name']}'",
                    'descripcion': f"Este anuncio tiene buen CTR ({ad['ctr']:.2f}%) pero recibe poca inversión (${ad['spend']:,.0f}). Podría escalar.",
                    'metrica': f"CTR: {ad['ctr']:.2f}% | Inversión: ${ad['spend']:,.0f}",
                    'accion': 'Aumentar presupuesto para este anuncio'
                })

        return insights

    def analyze_data(self, ads_data, adsets_data):
        """Analiza los datos y genera insights"""

        total_spend = sum(ad['spend'] for ad in ads_data)
        total_reach = sum(ad['reach'] for ad in ads_data)
        total_impressions = sum(ad['impressions'] for ad in ads_data)

        # Encontrar mejor y peor performing
        best_ad = max(ads_data, key=lambda x: x['reach']) if ads_data else None
        worst_ad = min(ads_data, key=lambda x: x['reach']) if ads_data else None

        # Análisis por conjunto
        adsets_analysis = []
        for adset in adsets_data:
            # Extraer conversaciones si existen
            conversations = adset['actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)
            cost_per_conversation = adset['cost_per_actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)

            adsets_analysis.append({
                'name': adset['adset_name'],
                'reach': adset['reach'],
                'frequency': adset['frequency'],
                'spend': adset['spend'],
                'conversations': conversations,
                'cost_per_conversation': cost_per_conversation,
            })

        # Ordenar por inversión
        adsets_analysis.sort(key=lambda x: x['spend'], reverse=True)

        # Generar insights automáticos
        insights = self.generate_insights(ads_data, adsets_data)

        analysis = {
            'total_spend': total_spend,
            'total_reach': total_reach,
            'total_impressions': total_impressions,
            'total_ads': len(ads_data),
            'total_adsets': len(adsets_data),
            'best_ad': best_ad,
            'worst_ad': worst_ad,
            'adsets_analysis': adsets_analysis,
            'insights': insights,
        }

        return analysis

    def save_report(self, ads_data, adsets_data, analysis, daily_data, cliente, periodo):
        """Guarda el reporte en JSON"""

        from pathlib import Path
        # Extraer año-mes del período
        fecha_inicio = periodo.split('_')[0]
        date_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        ano = date_obj.strftime('%Y')
        mes_num = date_obj.strftime('%m')
        mes_nombre = date_obj.strftime('%b').upper()

        # Crear estructura: ../reportes/YYYY-MM-MES/CLIENTE/meta/
        script_dir = Path(__file__).parent
        reportes_dir = script_dir.parent / "reportes"
        periodo_folder = f"{ano}-{mes_num}-{mes_nombre}"
        output_dir = reportes_dir / periodo_folder / cliente / "meta"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{cliente}_{periodo}_analisis_pauta.json"

        report = {
            'metadata': {
                'cliente': cliente,
                'periodo': periodo,
                'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'ad_account_id': self.ad_account_id,
            },
            'resumen': {
                'inversion_total': analysis['total_spend'],
                'alcance_total': analysis['total_reach'],
                'impresiones_totales': analysis['total_impressions'],
                'total_anuncios': analysis['total_ads'],
                'total_conjuntos': analysis['total_adsets'],
            },
            'conjuntos_de_anuncios': adsets_data,
            'anuncios': ads_data,
            'datos_diarios': daily_data,
            'analisis': analysis,
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ Reporte JSON guardado: {output_path}")

        return report


def main():
    """Función principal"""

    # Leer credenciales desde ../config/.env
    from dotenv import load_dotenv
    from pathlib import Path
    script_dir = Path(__file__).parent
    config_dir = script_dir.parent / "config"
    env_path = config_dir / ".env"
    load_dotenv(dotenv_path=env_path)

    access_token = os.getenv('ACCESS_TOKEN')
    ad_account_id = os.getenv('AD_ACCOUNT_ID')

    if not access_token or not ad_account_id:
        print("❌ Error: No se encontraron credenciales en .env")
        sys.exit(1)

    # Pedir datos del reporte
    print("\n" + "="*70)
    print("📊 META ADS ANALYZER - Generador de Reportes de Pauta")
    print("="*70 + "\n")

    cliente = input("Nombre del cliente: ").strip()
    if not cliente:
        cliente = "cliente"

    # Pedir período
    print("\nPeríodo del reporte:")
    print("  Formato: YYYY-MM-DD")
    date_from = input("  Desde (ej: 2025-10-01): ").strip()
    date_until = input("  Hasta (ej: 2025-10-31): ").strip()

    if not date_from or not date_until:
        # Por defecto: mes pasado
        today = datetime.now()
        first_day = today.replace(day=1) - timedelta(days=1)
        date_from = first_day.replace(day=1).strftime('%Y-%m-%d')
        date_until = first_day.strftime('%Y-%m-%d')
        print(f"\n  Usando período por defecto: {date_from} a {date_until}")

    periodo = f"{date_from}_{date_until}"

    # Conectar y extraer datos
    analyzer = MetaAdsAnalyzer(access_token, ad_account_id)

    # Obtener datos
    ads_data = analyzer.get_campaigns_data(date_from, date_until)
    adsets_data = analyzer.get_adsets_summary(date_from, date_until)
    daily_data = analyzer.get_daily_data(date_from, date_until)

    if not ads_data:
        print("⚠️  No se encontraron datos para el período especificado")
        sys.exit(0)

    # Analizar
    analysis = analyzer.analyze_data(ads_data, adsets_data)

    # Mostrar insights
    if analysis['insights']:
        print("\n" + "="*70)
        print("💡 INSIGHTS AUTOMÁTICOS")
        print("="*70)
        for insight in analysis['insights'][:5]:  # Mostrar top 5
            emoji = {'ALERTA': '🔴', 'OPORTUNIDAD': '🟡', 'ÉXITO': '🟢'}.get(insight['tipo'], '📊')
            print(f"\n{emoji} {insight['tipo']} - {insight['titulo']}")
            print(f"   {insight['descripcion']}")
            print(f"   → Acción sugerida: {insight['accion']}")
        print("="*70 + "\n")

    # Guardar reporte
    report = analyzer.save_report(ads_data, adsets_data, analysis, daily_data, cliente, periodo)

    # Mostrar resumen
    print("\n" + "="*70)
    print("📈 RESUMEN DEL PERÍODO")
    print("="*70)
    print(f"  Inversión total: ${analysis['total_spend']:,.2f}")
    print(f"  Alcance total: {analysis['total_reach']:,} personas")
    print(f"  Impresiones: {analysis['total_impressions']:,}")
    print(f"  Anuncios corridos: {analysis['total_ads']}")
    print(f"  Conjuntos de anuncios: {analysis['total_adsets']}")
    print("="*70 + "\n")

    print("✅ Proceso completado!\n")


if __name__ == "__main__":
    main()
