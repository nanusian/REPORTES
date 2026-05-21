#!/usr/bin/env python3
"""
Meta Ads Analyzer - Sistema de análisis de campañas publicitarias
Versión mejorada: Incluye extracción de creatividades e imágenes
"""

import os
import json
import sys
import requests
import base64
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.adcreative import AdCreative

class MetaAdsAnalyzer:
    def __init__(self, access_token, ad_account_id, cliente=None, periodo=None):
        """Inicializa la conexión con Meta Ads API"""
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.cliente = cliente
        self.periodo = periodo

        # Inicializar API
        FacebookAdsApi.init(access_token=access_token)
        self.account = AdAccount(ad_account_id)

        # Crear estructura de carpetas organizada por año-mes y cliente
        if cliente and periodo:
            # Extraer mes del periodo (formato: 2025-11-01_2025-11-30)
            fecha_inicio = periodo.split('_')[0]
            date_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            ano = date_obj.strftime('%Y')
            mes_num = date_obj.strftime('%m')
            mes_nombre = date_obj.strftime('%b').upper()

            # Crear estructura: ../reportes/YYYY-MM-MES/CLIENTE/meta/
            script_dir = Path(__file__).parent
            reportes_dir = script_dir.parent / "reportes"
            periodo_folder = f"{ano}-{mes_num}-{mes_nombre}"

            self.output_dir = reportes_dir / periodo_folder / cliente / "meta"
            self.images_dir = self.output_dir / "images"
        else:
            # Fallback a estructura antigua en la raíz de REPORTES
            script_dir = Path(__file__).parent
            self.output_dir = script_dir.parent / "reportes" / "output_legacy"
            self.images_dir = self.output_dir / "images"

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        print(f"✅ Conectado a cuenta: {ad_account_id}")
        print(f"📁 Carpeta de salida: {self.output_dir}")

    def download_image(self, url, ad_id):
        """Descarga una imagen y la guarda localmente"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Determinar extensión
                content_type = response.headers.get('content-type', '')
                ext = 'jpg'
                if 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'

                filename = f"{ad_id}.{ext}"
                filepath = self.images_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"      📸 Imagen descargada: {filename}")
                return str(filepath)
        except Exception as e:
            print(f"      ⚠️  Error descargando imagen: {e}")

        return None

    def get_ad_creative(self, ad_id):
        """Obtiene las creatividades de un anuncio"""
        try:
            ad = Ad(ad_id)

            # Obtener creative
            creative = ad.api_get(fields=[
                Ad.Field.creative,
            ])

            if 'creative' in creative:
                creative_id = creative['creative']['id']

                # Obtener detalles del creative
                creative_obj = AdCreative(creative_id)
                creative_data = creative_obj.api_get(fields=[
                    AdCreative.Field.title,
                    AdCreative.Field.body,
                    AdCreative.Field.image_url,
                    AdCreative.Field.thumbnail_url,
                    AdCreative.Field.object_story_spec,
                    AdCreative.Field.link_url,
                ])

                result = {
                    'title': creative_data.get('title', ''),
                    'body': creative_data.get('body', ''),
                    'image_url': creative_data.get('image_url', ''),
                    'thumbnail_url': creative_data.get('thumbnail_url', ''),
                    'link_url': creative_data.get('link_url', ''),
                    'local_image_path': None,
                }

                # Intentar extraer imagen de object_story_spec si no hay image_url directo
                if not result['image_url'] and 'object_story_spec' in creative_data:
                    oss = creative_data['object_story_spec']

                    # Link data
                    if 'link_data' in oss:
                        link_data = oss['link_data']
                        result['body'] = link_data.get('message', result['body'])
                        result['title'] = link_data.get('name', result['title'])
                        result['link_url'] = link_data.get('link', result['link_url'])

                        if 'picture' in link_data:
                            result['image_url'] = link_data['picture']

                    # Video data
                    elif 'video_data' in oss:
                        video_data = oss['video_data']
                        result['body'] = video_data.get('message', result['body'])
                        result['title'] = video_data.get('title', result['title'])
                        if 'image_url' in video_data:
                            result['image_url'] = video_data['image_url']

                # Descargar imagen si existe
                image_url = result['image_url'] or result['thumbnail_url']
                if image_url:
                    local_path = self.download_image(image_url, ad_id)
                    if local_path:
                        result['local_image_path'] = local_path

                return result

        except Exception as e:
            print(f"      ⚠️  Error obteniendo creative: {e}")

        return {
            'title': '',
            'body': '',
            'image_url': '',
            'thumbnail_url': '',
            'link_url': '',
            'local_image_path': None,
        }

    def get_campaigns_data(self, date_from, date_until):
        """Extrae datos de todas las campañas en el período especificado"""

        print(f"\n🔍 Extrayendo datos del período: {date_from} a {date_until}\n")

        # Campos a solicitar
        fields = [
            AdsInsights.Field.campaign_name,
            AdsInsights.Field.adset_name,
            AdsInsights.Field.ad_name,
            AdsInsights.Field.ad_id,
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

            # Obtener creatividades
            ad_id = data.get('ad_id', '')
            print(f"   📊 {data.get('adset_name', '')} > {data.get('ad_name', '')}")
            print(f"      Alcance: {int(data.get('reach', 0)):,} | Inversión: ${float(data.get('spend', 0)):,.2f}")

            creative_data = {}
            if ad_id:
                print(f"      🎨 Extrayendo creatividad...")
                creative_data = self.get_ad_creative(ad_id)

            # Crear registro limpio
            record = {
                'campaign_name': data.get('campaign_name', ''),
                'adset_name': data.get('adset_name', ''),
                'ad_name': data.get('ad_name', ''),
                'ad_id': ad_id,
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
                'creative': creative_data,
            }

            all_data.append(record)

        print(f"\n✅ Extraídos {len(all_data)} anuncios con creatividades\n")

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

        # 5. Analizar conversaciones vs inversión (solo para campañas de mensajería)
        awareness_keywords = ['reconocimiento', 'awareness', 'recordación', 'recordacion', 'views', 'video', 'reproduc']
        traffic_keywords = ['tráfico', 'trafico', 'traffic', 'clic', 'click']
        for adset in adsets_data:
            full_name = unicodedata.normalize('NFC', f"{adset.get('campaign_name', '')} {adset.get('adset_name', '')}").lower()
            is_awareness_or_traffic = any(kw in full_name for kw in awareness_keywords + traffic_keywords)
            conversations = adset['actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)
            cost_per_conv = adset['cost_per_actions'].get('onsite_conversion.messaging_conversation_started_7d', 0)

            if conversations > 0 and cost_per_conv > 5000 and not is_awareness_or_traffic:
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

    def detect_campaign_objective(self, campaign_name, adset_name, actions):
        """Detecta el objetivo principal de la campaña basándose en el nombre y acciones disponibles"""

        full_name = unicodedata.normalize('NFC', f"{campaign_name} {adset_name}").lower()

        # Mapeo de objetivos
        objectives = {
            'link_click': {
                'keywords': ['tráfico', 'trafico', 'traffic', 'clic', 'click', 'perfil', 'profile'],
                'action_key': 'link_click',
                'label': 'Clics al perfil/enlace',
                'short_label': 'clics'
            },
            'messaging': {
                'keywords': ['conversación', 'conversacion', 'mensaje', 'message', 'chat', 'whatsapp'],
                'action_key': 'onsite_conversion.messaging_conversation_started_7d',
                'label': 'Conversaciones iniciadas',
                'short_label': 'conversaciones'
            },
            'awareness': {
                'keywords': ['reconocimiento', 'awareness', 'recordación'],
                'action_key': 'video_view',
                'label': 'Reproducciones de video',
                'short_label': 'reproducciones'
            },
            'video': {
                'keywords': ['video', 'reproducción', 'reproducciones', 'view', 'thruplay'],
                'action_key': 'video_view',
                'label': 'Reproducciones de video',
                'short_label': 'reproducciones'
            },
            'engagement': {
                'keywords': ['interacción', 'interaccion', 'engagement', 'like', 'comment'],
                'action_key': 'post_engagement',
                'label': 'Interacciones con publicación',
                'short_label': 'interacciones'
            }
        }

        # Detectar por nombre de campaña
        for obj_type, obj_data in objectives.items():
            if any(keyword in full_name for keyword in obj_data['keywords']):
                return obj_data

        # Si no se detecta por nombre, usar la acción predominante
        if actions:
            messaging_conv = actions.get('onsite_conversion.messaging_conversation_started_7d', 0)
            link_clicks = actions.get('link_click', 0)
            # Priorizar messaging solo si supera significativamente a los link clicks
            if messaging_conv > 0 and messaging_conv > link_clicks:
                return objectives['messaging']

            # Fallback: acción con mayor valor (excluyendo métricas de engagement masivo)
            exclude = {'clicks', 'post_engagement', 'page_engagement', 'post_interaction_gross',
                       'post_interaction_net', 'video_view', 'post_reaction'}
            relevant_actions = {k: v for k, v in actions.items() if v > 0 and k not in exclude}
            if relevant_actions:
                main_action = max(relevant_actions, key=relevant_actions.get)
                for obj_data in objectives.values():
                    if obj_data['action_key'] == main_action:
                        return obj_data

        # Default: link_click
        return objectives['link_click']

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
            # Detectar objetivo de la campaña
            campaign_name = adset.get('campaign_name', '')
            objective = self.detect_campaign_objective(campaign_name, adset['adset_name'], adset['actions'])

            # Extraer métrica principal según objetivo
            main_result = adset['actions'].get(objective['action_key'], 0)
            cost_per_result = adset['cost_per_actions'].get(objective['action_key'], 0)

            adsets_analysis.append({
                'name': adset['adset_name'],
                'reach': adset['reach'],
                'frequency': adset['frequency'],
                'spend': adset['spend'],
                'objective_type': objective['action_key'],
                'objective_label': objective['label'],
                'objective_short_label': objective['short_label'],
                'main_result': main_result,
                'cost_per_result': cost_per_result,
                # Mantener conversaciones para compatibilidad con reportes antiguos
                'conversations': adset['actions'].get('onsite_conversion.messaging_conversation_started_7d', 0),
                'cost_per_conversation': adset['cost_per_actions'].get('onsite_conversion.messaging_conversation_started_7d', 0),
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

        # Guardar en la carpeta organizada
        output_path = self.output_dir / f"{cliente}_{periodo}_analisis_pauta.json"

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
    print("📊 META ADS ANALYZER - Generador de Reportes de Pauta (CON IMÁGENES)")
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

    # Conectar y extraer datos (con cliente y periodo para estructura de carpetas)
    analyzer = MetaAdsAnalyzer(access_token, ad_account_id, cliente, periodo)

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
