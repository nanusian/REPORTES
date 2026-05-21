# Diferencias entre Reportes de Meta Ads y Google Ads

## Estructura de Carpetas

Ambas plataformas siguen la misma estructura jerárquica:

```
/Users/laureanomedeot/Documents/REPORTES/reportes/
└── YYYY-MM-MES/           ← Período (ej: 2025-11-NOV, 2025-12-DIC)
    └── CLIENTE/           ← Nombre del cliente
        ├── meta/          ← Reportes de Meta Ads (Facebook/Instagram)
        └── google/        ← Reportes de Google Ads
```

## Meta Ads (`meta/`)

### Archivos Generados

```
meta/
├── CLIENTE_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
├── CLIENTE_REPORTE.html (opcional)
└── images/
    ├── creative_123456789.jpg
    └── creative_987654321.jpg
```

### Estructura del JSON

```json
{
  "metadata": {
    "cliente": "NOMBRE_CLIENTE",
    "periodo": "2025-11-01_2025-11-30",
    "fecha_generacion": "2025-12-29 19:23",
    "ad_account_id": "act_280276187315030"
  },
  "resumen": {
    "inversion_total": 848705.7,
    "alcance_total": 572325,
    "impresiones_totales": 1379300,
    "total_anuncios": 20,
    "total_conjuntos": 6
  },
  "conjuntos_de_anuncios": [
    {
      "adset_name": "Torre Bela",
      "impressions": 108150,
      "reach": 45348,
      "frequency": 2.38489,
      "spend": 54120.55,
      "actions": {
        "link_click": 1273,
        "page_engagement": 3245,
        "landing_page_view": 106,
        "lead": 1,
        "video_view": 1831
      },
      "cost_per_actions": {
        "link_click": 42.514179,
        "landing_page_view": 510.571226,
        "lead": 54120.55
      }
    }
  ],
  "anuncios": [...],
  "analisis": {...}
}
```

### Métricas Clave de Meta

- **inversion_total**: Gasto total en la moneda de la cuenta
- **alcance_total**: Personas únicas alcanzadas
- **impresiones_totales**: Veces que se mostró el anuncio
- **frequency**: Frecuencia promedio (impresiones / alcance)
- **actions**: Diccionario con todas las acciones (clicks, leads, views, etc.)
- **cost_per_actions**: Costo por cada tipo de acción

### Características Específicas

- ✅ Tiene carpeta `images/` con creatividades descargadas
- ✅ Incluye datos de **alcance** (reach)
- ✅ Incluye **frecuencia** (frequency)
- ✅ Múltiples tipos de acciones en un diccionario flexible
- ✅ Costo por acción para cada tipo de métrica

---

## Google Ads (`google/`)

### Archivos Generados

```
google/
├── CLIENTE_YYYY-MM-DD_YYYY-MM-DD_google_ads.json
└── CLIENTE_REPORTE_GOOGLE.html (opcional)
```

**Nota:** Google Ads NO incluye carpeta de imágenes.

### Estructura del JSON

```json
{
  "metadata": {
    "cliente": "NOMBRE_CLIENTE",
    "periodo": "2025-11-01_2025-11-30",
    "fecha_generacion": "2025-12-29 19:07",
    "plataforma": "Google Ads",
    "fuente": "CSV Export"
  },
  "resumen": {
    "inversion_total": 1175454.08,
    "clics_totales": 5338,
    "impresiones_totales": 1076112,
    "conversiones_totales": 211.52,
    "total_grupos": 5
  },
  "grupos_de_anuncios": [
    {
      "campaign_name": "Gran Alameda 2025",
      "ad_group_name": "Grupo Anuncio 01",
      "estado": "Detenido",
      "impressions": 98103,
      "clicks": 1206,
      "cost": 266805.02,
      "conversions": 73.0,
      "ctr": 1.23,
      "avg_cpc": 221.23,
      "cost_per_conversion": 3655.05
    }
  ],
  "datos_detallados": [...],
  "datos_diarios": [
    {
      "date": "2025-11-01",
      "impressions": 1076112,
      "clicks": 5338,
      "cost": 1175454.08,
      "conversions": 211.52
    }
  ]
}
```

### Métricas Clave de Google

- **inversion_total**: Gasto total (cost)
- **clics_totales**: Total de clicks
- **impresiones_totales**: Total de impresiones
- **conversiones_totales**: Total de conversiones
- **ctr**: Click-through rate (%)
- **avg_cpc**: Costo promedio por clic
- **cost_per_conversion**: Costo por conversión

### Características Específicas

- ❌ NO tiene carpeta `images/`
- ❌ NO incluye datos de **alcance** (reach)
- ❌ NO incluye **frecuencia** (frequency)
- ✅ Incluye **CTR** (Click-Through Rate)
- ✅ Incluye **CPC promedio**
- ✅ Métricas más enfocadas en conversiones y clicks
- ✅ Incluye sección `datos_diarios` con evolución día a día
- ✅ Incluye **estado** de cada grupo de anuncios

---

## Comparación Directa

| Aspecto | Meta Ads | Google Ads |
|---------|----------|------------|
| **Nombre de archivo** | `_analisis_pauta.json` | `_google_ads.json` |
| **Carpeta de imágenes** | ✅ Sí (`images/`) | ❌ No |
| **Alcance (Reach)** | ✅ Sí | ❌ No |
| **Frecuencia** | ✅ Sí | ❌ No |
| **CTR** | ⚠️ Calculable | ✅ Incluido |
| **CPC promedio** | ⚠️ Calculable | ✅ Incluido |
| **Conversiones** | ✅ En `actions` | ✅ Campo dedicado |
| **Estado de anuncios** | ⚠️ Via API | ✅ Incluido |
| **Datos diarios** | ❌ No | ✅ Sí |
| **Grupos de anuncios** | `conjuntos_de_anuncios` | `grupos_de_anuncios` |
| **Número de anuncios** | `total_anuncios` | No directo |

---

## Clientes por Plataforma

### Solo Meta Ads

- CREAR
- FULL + NEW CREST
- Grupo Bartolomé
- HORMIGONERA HDI
- MEDICAL HAIR
- PERFIL SRL

### Meta + Google Ads

- **ASPA** (único cliente con ambas plataformas configuradas)

---

## Nomenclatura de Archivos

### Meta Ads
```
CLIENTE_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
```
Ejemplo:
```
ASPA_2025-11-01_2025-11-30_analisis_pauta.json
```

### Google Ads
```
CLIENTE_YYYY-MM-DD_YYYY-MM-DD_google_ads.json
```
Ejemplo:
```
ASPA_2025-11-01_2025-11-30_google_ads.json
```

---

## Scripts de Generación

### Meta Ads

**Script:** `generar_reportes_automatico.py`

**Uso:**
```bash
python3 generar_reportes_automatico.py --mes 11 --ano 2025 --cliente "ASPA"
```

**Proceso:**
1. Conecta a Meta Ads API usando el token de `config.json`
2. Extrae datos de campañas y conjuntos
3. Analiza y estructura los datos
4. Guarda JSON en `reportes/YYYY-MM-MES/CLIENTE/meta/`
5. (Opcional) Descarga imágenes de creatividades

### Google Ads

**Script:** `google_ads_analyzer.py` o `google_ads_csv_processor.py`

**Proceso:**
1. Exporta datos desde Google Ads (manual o via API)
2. Procesa CSV o conecta via Google Ads API
3. Estructura datos en formato JSON
4. Guarda en `reportes/YYYY-MM-MES/CLIENTE/google/`

**Nota:** Google Ads requiere exportación CSV o configuración de API separada.

---

## Generar Reportes HTML

Ambas plataformas pueden generar reportes HTML visuales:

### Meta Ads HTML
**Script:** `generate_full_report.py`

```bash
python3 generate_full_report.py \
  --json-old reportes/2025-10-OCT/ASPA/meta/ASPA_..._analisis_pauta.json \
  --json-new reportes/2025-11-NOV/ASPA/meta/ASPA_..._analisis_pauta.json \
  --output reportes/2025-11-NOV/ASPA/meta/ASPA_REPORTE.html
```

### Google Ads HTML
**Script:** `generate_aspa_google_report.py` (específico de ASPA)

---

## Consideraciones Importantes

### Al Generar Reportes

1. **Verificar token de Meta:** Expira cada ~60 días
2. **Confirmar IDs de cuenta:** Están en `config.json`
3. **Estructura de carpetas:** Siempre `YYYY-MM-MES/CLIENTE/plataforma/`
4. **Nombres consistentes:** Usar los mismos nombres de clientes siempre

### Al Comparar Plataformas

- **No puedes comparar alcance:** Google no lo reporta
- **Conversiones difieren:** Meta tiene múltiples tipos, Google es más simple
- **Impresiones:** Ambas lo tienen pero pueden diferir en definición
- **Costo:** Ambas lo reportan en la misma moneda (ARS generalmente)

### Limitaciones

- **Meta:** Requiere token válido y permisos de Business Manager
- **Google:** Requiere exportación CSV o configuración de Google Ads API
- **Imágenes:** Solo Meta descarga creatividades automáticamente

---

## Troubleshooting

### Meta Ads

**Error: Invalid OAuth token**
- Token expirado, actualizar en `config.json`

**Error: Account not found**
- Verificar `meta_ad_account_id` en `config.json`

**Sin datos:**
- El cliente no tuvo campañas activas en ese período

### Google Ads

**Sin datos:**
- Verificar que existe el CSV exportado
- Confirmar que el cliente tiene campañas en Google Ads

**Métricas en 0:**
- Grupos de anuncios desactivados aparecen pero sin datos

---

## Ejemplo Completo: ASPA Noviembre 2025

### Estructura de carpetas:
```
reportes/2025-11-NOV/ASPA/
├── meta/
│   ├── ASPA_2025-11-01_2025-11-30_analisis_pauta.json  (55 KB)
│   └── images/
│       ├── creative_123.jpg
│       └── creative_456.jpg
└── google/
    └── ASPA_2025-11-01_2025-11-30_google_ads.json      (3.8 KB)
```

### Comparación de métricas:

**Meta Ads:**
- Inversión: $848,705.70
- Impresiones: 1,379,300
- Alcance: 572,325 personas
- Anuncios: 20

**Google Ads:**
- Inversión: $1,175,454.08
- Impresiones: 1,076,112
- Clicks: 5,338
- Conversiones: 211.52

**Total combinado:**
- Inversión: $2,024,159.78
- Impresiones: 2,455,412

---

**Última actualización:** 2026-01-09
**Versión:** 1.0
