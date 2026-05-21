# 📊 Meta Ads Analyzer - LINE Ad Studio

Sistema automatizado para generar reportes profesionales de campañas publicitarias en Meta (Facebook/Instagram) conectándose directamente a la API de Meta.

## ✅ Qué hace este sistema

1. **Conecta con Meta Ads API** automáticamente
2. **Extrae datos** de campañas, conjuntos y anuncios en un período específico
3. **Analiza métricas**: alcance, inversión, frecuencia, conversaciones, CTR, CPC, CPM
4. **Genera reporte PDF** profesional listo para enviar al cliente
5. **Branding LINE Ad Studio** - fondo oscuro con acentos turquesa

## 🚀 Cómo usar

### Ejecución simple (recomendada):

```bash
./run_ads.sh
```

Te va a pedir:
- Nombre del cliente
- Fecha inicio (YYYY-MM-DD)
- Fecha fin (YYYY-MM-DD)

Y automáticamente:
- Extrae datos de Meta
- Genera JSON de análisis
- Crea PDF profesional en `output/ENTREGABLES/`

### Ejemplo:

```bash
./run_ads.sh

Nombre del cliente: CBS TECH
Fecha inicio: 2025-10-01
Fecha fin: 2025-10-31
```

Resultado:
- `output/CBS TECH_2025-10-01_2025-10-31_analisis_pauta.json`
- `output/ENTREGABLES/Reporte_Pauta_CBS TECH_2025-10-01_2025-10-31.pdf`

## 📋 Qué incluye el reporte PDF

1. **Portada** con branding LINE Ad Studio
2. **Glosario** de métricas (impresiones, alcance, frecuencia, etc)
3. **Resumen ejecutivo** con métricas principales:
   - Inversión total
   - Alcance total
   - Impresiones
   - Anuncios corridos
   - Frecuencia promedio
4. **Tabla de conjuntos de anuncios** con resultados y costos
5. **Páginas individuales por conjunto** mostrando:
   - Conversaciones generadas
   - Costo por conversación
   - Detalle de cada anuncio
   - CTR, CPC, alcance, frecuencia

## 🔧 Configuración inicial

### 1. Credenciales de Meta (ya configuradas)

El archivo `.env` contiene:
```
ACCESS_TOKEN=tu_token_aqui
AD_ACCOUNT_ID=act_1082529013650791
```

**IMPORTANTE:** El access token expira cada 60 días. Cuando deje de funcionar:
1. Andá a https://developers.facebook.com/tools/explorer/
2. Seleccioná tu app
3. Generá nuevo token
4. Actualizá el `.env`

### 2. Dependencias (ya instaladas)

```bash
pip3 install facebook-business python-dotenv
```

## 📁 Estructura del proyecto

```
meta_ads_analyzer_LINE/
├── .env                      # Credenciales de Meta API
├── meta_ads_analyzer.py      # Script de extracción de datos
├── generate_pdf_report.py    # Generador de PDF
├── run_ads.sh                # Ejecutor automático ⭐
├── output/
│   ├── *.json                # Análisis en JSON
│   └── ENTREGABLES/
│       └── Reporte_Pauta_*.pdf  # PDFs para clientes
└── README.md
```

## 🎯 Métricas que analiza

### Por conjunto de anuncios:
- Conversaciones iniciadas
- Costo por conversación
- Alcance
- Frecuencia
- Inversión total

### Por anuncio individual:
- Alcance
- Frecuencia
- CTR (Click-Through Rate)
- CPC (Costo por Click)
- CPM (Costo por Mil impresiones)
- Conversaciones (si aplica)
- Clicks
- Landing page views

## 💡 Tips

### Renovar access token

Cuando el token expire (error de autenticación):

1. https://developers.facebook.com/tools/explorer/
2. App: tu app
3. Permissions: `ads_read`, `ads_management`
4. Generate Access Token
5. Copiar y pegar en `.env`

### Cambiar cuenta publicitaria

Editá `.env` y cambiá:
```
AD_ACCOUNT_ID=act_NUEVO_ID
```

### Períodos comunes

```bash
Octubre 2025:  2025-10-01  a  2025-10-31
Noviembre 2025: 2025-11-01  a  2025-11-30
Últimos 7 días: calcular desde hoy
```

## 🔍 Troubleshooting

### Error: "No se encontraron datos"
- Verificá que el período tiene campañas activas
- Verificá que el AD_ACCOUNT_ID es correcto
- Verificá que el token tiene permisos de lectura

### Error: "Invalid OAuth access token"
- El token expiró, renovalo desde Meta Developers

### Error: "No se encuentra .env"
- Creá el archivo `.env` en la raíz del proyecto

## 📊 Diferencia con sistema orgánico

Este sistema es para **solo pauta publicitaria** (Meta Ads Manager).

Para análisis de **contenido orgánico** (posts sin pauta), usá:
- `instagram_analytics_system_LINE/`

Este sistema es específico para clientes donde **solo corrés pauta** sin gestionar contenido orgánico.

## 🎨 Branding

- **Fondo:** Gris oscuro (#2d3748)
- **Acentos:** Turquesa LINE (#00D9C1)
- **Logo:** LINE AD STUDIO
- **Estilo:** Minimalista, profesional

---

**Sistema creado:** Noviembre 2025
**Última actualización:** 8 Nov 2025
