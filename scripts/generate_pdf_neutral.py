#!/usr/bin/env python3
"""
Generador de reportes PDF desde datos de Meta Ads
Versión NEUTRAL - Sin branding - Con imágenes
"""

import json
import sys
import os
import subprocess
import base64
from datetime import datetime
from pathlib import Path

def format_currency(value):
    """Formatea números como moneda ARS"""
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(value):
    """Formatea números con separador de miles"""
    return f"{int(value):,}".replace(",", ".")

def image_to_base64(image_path):
    """Convierte una imagen a base64 para embeber en HTML"""
    try:
        if not os.path.exists(image_path):
            return None

        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')

            # Detectar tipo de imagen
            ext = Path(image_path).suffix.lower()
            mime_type = 'image/jpeg'
            if ext == '.png':
                mime_type = 'image/png'
            elif ext == '.gif':
                mime_type = 'image/gif'

            return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        print(f"⚠️  Error convirtiendo imagen: {e}")
        return None

def generate_html_report(json_path):
    """Genera HTML desde JSON de análisis - Versión neutral"""

    # Leer JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data['metadata']
    resumen = data['resumen']
    conjuntos = data['conjuntos_de_anuncios']
    anuncios = data['anuncios']
    analisis = data['analisis']
    daily_data = data.get('datos_diarios', [])
    insights = analisis.get('insights', [])

    # Colores neutros profesionales
    color_fondo = '#FFFFFF'
    color_texto = '#2d3748'
    color_acento = '#4A5568'
    color_secundario = '#718096'

    cliente = metadata['cliente'].upper()
    periodo_raw = metadata['periodo']

    # Formatear período
    fecha_inicio, fecha_fin = periodo_raw.split('_')
    mes_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%B %Y')
    mes_inicio_esp = {
        'January': 'ENERO', 'February': 'FEBRERO', 'March': 'MARZO',
        'April': 'ABRIL', 'May': 'MAYO', 'June': 'JUNIO',
        'July': 'JULIO', 'August': 'AGOSTO', 'September': 'SEPTIEMBRE',
        'October': 'OCTUBRE', 'November': 'NOVIEMBRE', 'December': 'DICIEMBRE'
    }
    for eng, esp in mes_inicio_esp.items():
        mes_inicio = mes_inicio.replace(eng, esp)

    # Agrupar anuncios por conjunto
    anuncios_por_conjunto = {}
    for anuncio in anuncios:
        adset = anuncio['adset_name']
        if adset not in anuncios_por_conjunto:
            anuncios_por_conjunto[adset] = []
        anuncios_por_conjunto[adset].append(anuncio)

    # HTML Template
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Campaña - {cliente}</title>
    <style>
        @page {{
            margin: 0;
            size: A4 landscape;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
            color: {color_texto};
            background: {color_fondo};
        }}

        /* Portada */
        .cover-page {{
            width: 297mm;
            height: 210mm;
            background: {color_fondo};
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            page-break-after: always;
            border: 1px solid #E2E8F0;
        }}

        .cover-title {{
            font-size: 48px;
            font-weight: 700;
            color: {color_texto};
            margin-bottom: 20px;
            text-align: center;
        }}

        .cover-subtitle {{
            font-size: 32px;
            font-weight: 300;
            color: {color_secundario};
            margin-bottom: 60px;
        }}

        .cover-period {{
            font-size: 24px;
            color: {color_acento};
            font-weight: 500;
        }}

        /* Páginas internas */
        .page {{
            width: 297mm;
            height: 210mm;
            padding: 30mm;
            page-break-after: always;
            background: {color_fondo};
        }}

        .page-title {{
            font-size: 32px;
            font-weight: 700;
            color: {color_texto};
            margin-bottom: 10px;
            padding-bottom: 15px;
            border-bottom: 3px solid {color_acento};
        }}

        .page-subtitle {{
            font-size: 18px;
            color: {color_secundario};
            margin-bottom: 30px;
        }}

        /* Resumen ejecutivo */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}

        .metric-card {{
            background: #F7FAFC;
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid {color_acento};
        }}

        .metric-value {{
            font-size: 36px;
            font-weight: 700;
            color: {color_texto};
            margin-bottom: 8px;
        }}

        .metric-label {{
            font-size: 14px;
            color: {color_secundario};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Tablas */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
        }}

        thead {{
            background: {color_acento};
            color: white;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #E2E8F0;
            color: {color_texto};
            font-size: 14px;
        }}

        tbody tr:hover {{
            background: #F7FAFC;
        }}

        /* Insights */
        .insight {{
            background: #F7FAFC;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid {color_acento};
        }}

        .insight-title {{
            font-size: 16px;
            font-weight: 600;
            color: {color_texto};
            margin-bottom: 10px;
        }}

        .insight-description {{
            font-size: 14px;
            color: {color_secundario};
            margin-bottom: 10px;
            line-height: 1.6;
        }}

        .insight-action {{
            font-size: 13px;
            color: {color_acento};
            font-weight: 500;
        }}

        .insight-alerta {{ border-left-color: #E53E3E; }}
        .insight-oportunidad {{ border-left-color: #D69E2E; }}
        .insight-exito {{ border-left-color: #38A169; }}

        /* Detalles de conjunto */
        .adset-header {{
            background: {color_acento};
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }}

        .adset-title {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .adset-metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
        }}

        .adset-metric {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 4px;
        }}

        .adset-metric-value {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .adset-metric-label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
        }}

        .ad-list {{
            margin-top: 30px;
        }}

        .ad-item {{
            background: #F7FAFC;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid {color_secundario};
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 20px;
            align-items: start;
        }}

        .ad-image-container {{
            width: 250px;
            height: 250px;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #E2E8F0;
        }}

        .ad-image {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}

        .ad-content {{
            flex: 1;
        }}

        .ad-name {{
            font-size: 16px;
            font-weight: 600;
            color: {color_texto};
            margin-bottom: 10px;
        }}

        .ad-copy {{
            font-size: 13px;
            color: {color_secundario};
            line-height: 1.5;
            margin-bottom: 15px;
            font-style: italic;
        }}

        .ad-metrics {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 15px;
        }}

        .ad-metric {{
            text-align: center;
        }}

        .ad-metric-value {{
            font-size: 18px;
            font-weight: 700;
            color: {color_texto};
            margin-bottom: 5px;
        }}

        .ad-metric-label {{
            font-size: 11px;
            color: {color_secundario};
            text-transform: uppercase;
        }}

        /* Glosario */
        .glossary-item {{
            margin-bottom: 20px;
        }}

        .glossary-term {{
            font-size: 16px;
            font-weight: 600;
            color: {color_texto};
            margin-bottom: 5px;
        }}

        .glossary-definition {{
            font-size: 14px;
            color: {color_secundario};
            line-height: 1.6;
        }}
    </style>
</head>
<body>

    <!-- PORTADA -->
    <div class="cover-page">
        <div class="cover-title">{cliente}</div>
        <div class="cover-subtitle">Reporte de Campaña Publicitaria</div>
        <div class="cover-period">{mes_inicio}</div>
    </div>

    <!-- GLOSARIO -->
    <div class="page">
        <h1 class="page-title">Glosario de Métricas</h1>
        <p class="page-subtitle">Definiciones de los términos utilizados en este reporte</p>

        <div class="glossary-item">
            <div class="glossary-term">Impresiones</div>
            <div class="glossary-definition">Cantidad de veces que tu anuncio fue mostrado en pantalla, sin importar si fue clickeado o no.</div>
        </div>

        <div class="glossary-item">
            <div class="glossary-term">Alcance</div>
            <div class="glossary-definition">Número de personas únicas que vieron tu anuncio al menos una vez.</div>
        </div>

        <div class="glossary-item">
            <div class="glossary-term">Frecuencia</div>
            <div class="glossary-definition">Promedio de veces que cada persona vio tu anuncio (Impresiones ÷ Alcance). Idealmente debe estar entre 2-4.</div>
        </div>

        <div class="glossary-item">
            <div class="glossary-term">CTR (Click-Through Rate)</div>
            <div class="glossary-definition">Porcentaje de personas que hicieron click después de ver el anuncio. Mide qué tan atractivo es el contenido.</div>
        </div>

        <div class="glossary-item">
            <div class="glossary-term">CPC (Costo Por Click)</div>
            <div class="glossary-definition">Cuánto pagaste en promedio por cada click en tu anuncio.</div>
        </div>

        <div class="glossary-item">
            <div class="glossary-term">CPM (Costo Por Mil impresiones)</div>
            <div class="glossary-definition">Cuánto pagaste por cada 1,000 veces que tu anuncio fue mostrado.</div>
        </div>

        <div class="glossary-item">
            <div class="glossary-term">Conversaciones iniciadas</div>
            <div class="glossary-definition">Personas que iniciaron una conversación en Messenger o Instagram después de ver el anuncio.</div>
        </div>

        <div class="glossary-item">
            <div class="glossary-term">Costo por conversación</div>
            <div class="glossary-definition">Cuánto pagaste en promedio por cada conversación iniciada.</div>
        </div>
    </div>

    <!-- RESUMEN EJECUTIVO -->
    <div class="page">
        <h1 class="page-title">Resumen Ejecutivo</h1>
        <p class="page-subtitle">Métricas principales del período</p>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{format_currency(resumen['inversion_total'])}</div>
                <div class="metric-label">Inversión Total (ARS)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{format_number(resumen['alcance_total'])}</div>
                <div class="metric-label">Alcance Total</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{format_number(resumen['impresiones_totales'])}</div>
                <div class="metric-label">Impresiones</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{resumen['total_anuncios']}</div>
                <div class="metric-label">Anuncios Corridos</div>
            </div>
        </div>

        <h2 style="font-size: 24px; margin-bottom: 15px; color: {color_texto};">Rendimiento por Conjunto de Anuncios</h2>

        <table>
            <thead>
                <tr>
                    <th>Conjunto de Anuncios</th>
                    <th>Alcance</th>
                    <th>Frecuencia</th>
                    <th>Inversión</th>
                    <th>Conversaciones</th>
                    <th>Costo/Conv.</th>
                </tr>
            </thead>
            <tbody>
"""

    # Tabla de conjuntos
    for conjunto in conjuntos:
        conversations = conjunto.get('actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
        cost_per_conv = conjunto.get('cost_per_actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)

        html += f"""
                <tr>
                    <td><strong>{conjunto['adset_name']}</strong></td>
                    <td>{format_number(conjunto['reach'])}</td>
                    <td>{conjunto['frequency']:.2f}</td>
                    <td>{format_currency(conjunto['spend'])}</td>
                    <td>{conversations}</td>
                    <td>{format_currency(cost_per_conv) if cost_per_conv else '-'}</td>
                </tr>
"""

    html += """
            </tbody>
        </table>
    </div>
"""

    # INSIGHTS
    if insights:
        html += """
    <div class="page">
        <h1 class="page-title">Insights y Recomendaciones</h1>
        <p class="page-subtitle">Análisis automático del rendimiento de las campañas</p>
"""

        for insight in insights[:8]:  # Máximo 8 insights
            tipo_clase = insight['tipo'].lower()
            emoji = {'alerta': '⚠️', 'oportunidad': '💡', 'exito': '✅'}.get(tipo_clase, '📊')

            html += f"""
        <div class="insight insight-{tipo_clase}">
            <div class="insight-title">{emoji} {insight['titulo']}</div>
            <div class="insight-description">{insight['descripcion']}</div>
            <div class="insight-action">→ {insight['accion']}</div>
        </div>
"""

        html += """
    </div>
"""

    # PÁGINAS DE DETALLE POR CONJUNTO
    for conjunto in conjuntos:
        adset_name = conjunto['adset_name']
        conversations = conjunto.get('actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)
        cost_per_conv = conjunto.get('cost_per_actions', {}).get('onsite_conversion.messaging_conversation_started_7d', 0)

        html += f"""
    <div class="page">
        <div class="adset-header">
            <div class="adset-title">{adset_name}</div>
            <div class="adset-metrics">
                <div class="adset-metric">
                    <div class="adset-metric-value">{conversations}</div>
                    <div class="adset-metric-label">Conversaciones</div>
                </div>
                <div class="adset-metric">
                    <div class="adset-metric-value">{format_currency(cost_per_conv) if cost_per_conv else '-'}</div>
                    <div class="adset-metric-label">Costo por Conversación</div>
                </div>
                <div class="adset-metric">
                    <div class="adset-metric-value">{format_currency(conjunto['spend'])}</div>
                    <div class="adset-metric-label">Inversión Total</div>
                </div>
            </div>
        </div>

        <h2 style="font-size: 20px; margin-bottom: 15px; color: {color_texto};">Anuncios en este conjunto</h2>

        <div class="ad-list">
"""

        # Anuncios del conjunto
        for anuncio in anuncios_por_conjunto.get(adset_name, []):
            # Obtener datos de creatividad
            creative = anuncio.get('creative', {})
            image_path = creative.get('local_image_path', '')
            ad_copy = creative.get('body', '')
            ad_title = creative.get('title', '')

            # Convertir imagen a base64 si existe
            image_html = ''
            if image_path and os.path.exists(image_path):
                image_base64 = image_to_base64(image_path)
                if image_base64:
                    image_html = f'<img src="{image_base64}" class="ad-image" alt="Ad Creative"/>'
                else:
                    image_html = '<div style="text-align: center; color: #CBD5E0; padding: 40px;">Sin imagen</div>'
            else:
                image_html = '<div style="text-align: center; color: #CBD5E0; padding: 40px;">Sin imagen</div>'

            # Texto del anuncio (título + copy)
            copy_text = ''
            if ad_title:
                copy_text = f"<strong>{ad_title}</strong><br>"
            if ad_copy:
                # Limitar a 150 caracteres
                if len(ad_copy) > 150:
                    ad_copy = ad_copy[:150] + '...'
                copy_text += ad_copy

            html += f"""
            <div class="ad-item">
                <div class="ad-image-container">
                    {image_html}
                </div>
                <div class="ad-content">
                    <div class="ad-name">{anuncio['ad_name']}</div>
                    {f'<div class="ad-copy">"{copy_text}"</div>' if copy_text else ''}
                    <div class="ad-metrics">
                        <div class="ad-metric">
                            <div class="ad-metric-value">{format_number(anuncio['reach'])}</div>
                            <div class="ad-metric-label">Alcance</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{anuncio['frequency']:.2f}</div>
                            <div class="ad-metric-label">Frecuencia</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{anuncio['ctr']:.2f}%</div>
                            <div class="ad-metric-label">CTR</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{format_currency(anuncio['cpc'])}</div>
                            <div class="ad-metric-label">CPC</div>
                        </div>
                        <div class="ad-metric">
                            <div class="ad-metric-value">{format_currency(anuncio['spend'])}</div>
                            <div class="ad-metric-label">Inversión</div>
                        </div>
                    </div>
                </div>
            </div>
"""

        html += """
        </div>
    </div>
"""

    html += """
</body>
</html>
"""

    return html


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 generate_pdf_neutral.py <archivo_json>")
        sys.exit(1)

    json_path = sys.argv[1]

    if not os.path.exists(json_path):
        print(f"❌ Error: No se encuentra el archivo {json_path}")
        sys.exit(1)

    print(f"\n📄 Generando reporte neutral desde: {json_path}")

    # Generar HTML
    html_content = generate_html_report(json_path)

    # Guardar HTML temporal
    html_path = json_path.replace('.json', '_neutral.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML generado: {html_path}")

    # Generar PDF con Chrome headless
    pdf_filename = os.path.basename(json_path).replace('.json', '_NEUTRAL.pdf')
    pdf_path = f"output/ENTREGABLES/{pdf_filename}"

    # Crear carpeta si no existe
    os.makedirs('output/ENTREGABLES', exist_ok=True)

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    html_full_path = os.path.abspath(html_path)

    cmd = [
        chrome_path,
        '--headless',
        '--disable-gpu',
        f'--print-to-pdf={pdf_path}',
        '--print-to-pdf-no-header',
        '--no-margins',
        f'file://{html_full_path}'
    ]

    print(f"🖨️  Convirtiendo a PDF...")
    subprocess.run(cmd, check=True, capture_output=True)

    print(f"✅ PDF generado: {pdf_path}\n")


if __name__ == "__main__":
    main()
