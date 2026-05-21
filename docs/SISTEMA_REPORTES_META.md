# 📊 Sistema de Reportes de Meta Ads - LINE Agency

**Última actualización:** 9 de Diciembre 2025
**Versión:** 2.0 - Con detección dinámica de objetivos

## 🎯 Qué hace este sistema

Este sistema analiza campañas publicitarias en Meta (Facebook/Instagram) y genera reportes HTML profesionales **enfocados en los avisos y el objetivo real de cada campaña**.

### Características principales:
- ✅ **Detección automática de objetivos**: El sistema detecta si la campaña es de tráfico, conversaciones, video, etc.
- ✅ **Enfoque en avisos/creatividades**: Muestra las imágenes y copys de cada aviso
- ✅ **Métricas correctas**: Usa la métrica principal según el objetivo (clics, conversaciones, reproducciones, etc.)
- ✅ **Extracción de imágenes**: Descarga y embebe las creatividades en el reporte
- ✅ **Reportes limpios y profesionales**: HTML responsive con todas las creatividades

## 📁 Estructura de Carpetas

```
/Users/laureanomedeot/Documents/REPORTES/
├── NOV-25/                          # Reportes de Noviembre 2025
│   ├── HORMIGONERA HDI/
│   │   ├── HORMIGONERA HDI_REPORTE-nov.25.html  # Reporte HTML final
│   │   ├── HORMIGONERA HDI_2025-11-01_2025-11-30_analisis_pauta.json  # Datos JSON
│   │   └── images/                  # Imágenes de creatividades
│   ├── Grupo Bartolomé/
│   └── MEDICAL HAIR/
├── OCT-25/                          # Reportes de Octubre 2025
├── meta_ads_analyzer_with_images.py  # ⭐ Extractor de datos (ACTUALIZADO)
├── generate_html_clean.py            # ⭐ Generador de HTML (ACTUALIZADO)
├── regenerar_hdi.py                  # Script para regenerar reportes
├── .env                              # Credenciales de Meta API
└── SISTEMA_REPORTES_META.md          # Esta documentación
```

## 🚀 Cómo usar

### Para generar un nuevo reporte:

```bash
cd /Users/laureanomedeot/Documents/REPORTES

# 1. Ejecutar el analyzer para extraer datos
python3 meta_ads_analyzer_with_images.py

# Te pedirá:
Nombre del cliente: HORMIGONERA HDI
Fecha desde: 2025-12-01
Fecha hasta: 2025-12-31

# 2. Generar el HTML
python3 generate_html_clean.py "output/ENTREGABLES/DIC-25/HORMIGONERA HDI/HORMIGONERA HDI_2025-12-01_2025-12-31_analisis_pauta.json"

# 3. Copiar al lugar correcto
cp "output/ENTREGABLES/DIC-25/HORMIGONERA HDI/HORMIGONERA HDI_REPORTE.html" "DIC-25/HORMIGONERA HDI/HORMIGONERA HDI_REPORTE-dic.25.html"
```

### Para regenerar un reporte existente:

Si ya tienes los datos en Meta pero quieres regenerar el reporte con el sistema actualizado:

```bash
# Editar regenerar_hdi.py con los datos del cliente
# Luego ejecutar:
python3 regenerar_hdi.py
```

## 🎯 Detección Automática de Objetivos

El sistema detecta el objetivo real de cada campaña basándose en:

1. **Nombre de la campaña/conjunto**: Busca palabras clave como "tráfico", "conversación", "video", etc.
2. **Acciones disponibles**: Si no encuentra palabras clave, usa la acción con mayor volumen

### Objetivos soportados:

| Objetivo | Palabras clave | Métrica principal | Etiqueta |
|----------|----------------|-------------------|----------|
| **Tráfico** | tráfico, traffic, clic, click, perfil | `link_click` | Clics al perfil/enlace |
| **Conversaciones** | conversación, mensaje, chat, whatsapp | `messaging_conversation_started_7d` | Conversaciones iniciadas |
| **Video** | video, reproducción, view, thruplay | `video_view` | Reproducciones de video |
| **Reconocimiento** | reconocimiento, awareness, alcance | `estimated_ad_recallers` | Recordación estimada |
| **Interacción** | interacción, engagement, like | `post_engagement` | Interacciones |

## 📊 Ejemplo: HDI (Noviembre 2025)

### Antes (sistema antiguo):
- ❌ Mostraba: "2 conversaciones iniciadas"
- ❌ Objetivo: Conversaciones
- ❌ Enfoque: Métricas generales

### Después (sistema actualizado):
- ✅ Muestra: "2,155 clics al perfil"
  - 1,427 clics (conjunto "Abierto")
  - 728 clics (conjunto "Producto")
- ✅ Objetivo: Tráfico al perfil de Instagram
- ✅ Enfoque: Avisos publicitarios y creatividades

## 🔧 Archivos Clave Modificados

### 1. `meta_ads_analyzer_with_images.py`
**Líneas 432-489:** Nueva función `detect_campaign_objective()` que detecta el objetivo real

```python
def detect_campaign_objective(self, campaign_name, adset_name, actions):
    """Detecta el objetivo principal de la campaña"""
    # Busca palabras clave en nombre de campaña
    # Si no encuentra, usa la acción con mayor volumen
    # Retorna: action_key, label, short_label
```

**Líneas 503-529:** Actualizado `analyze_data()` para usar detección dinámica

### 2. `generate_html_clean.py`
**Líneas 559-603:** Tabla de resumen usa objetivos dinámicos
**Líneas 669-711:** Headers de conjuntos usan objetivos dinámicos

## ⚙️ Configuración

### Credenciales (archivo `.env`):
```
ACCESS_TOKEN=tu_token_de_meta
AD_ACCOUNT_ID=act_7705227589601205
```

### Renovar access token (cada 60 días):
1. Ir a https://developers.facebook.com/tools/explorer/
2. Seleccionar tu app
3. Generar nuevo token con permisos `ads_read`
4. Actualizar `.env`

## 🆕 Diferencias con sistema anterior

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| Detección de objetivo | ❌ Hardcodeado a conversaciones | ✅ Dinámico según campaña |
| Métrica principal | ❌ Siempre conversaciones | ✅ Según objetivo real |
| Enfoque del reporte | ❌ Métricas generales | ✅ Avisos y creatividades |
| Etiquetas | ❌ Fijas | ✅ Dinámicas y descriptivas |

## 📝 Notas importantes

1. **Siempre regenerar desde Meta API**: No editar JSONs manualmente
2. **Un reporte por mes por cliente**: Mantener organización MES-AÑO/CLIENTE/
3. **Backups automáticos**: Los JSONs sirven de backup, no borrar
4. **Imágenes embedidas**: Las creatividades están en base64 dentro del HTML
5. **Sistema documentado**: Este archivo explica todo para el mes que viene

## 🐛 Troubleshooting

### Error: "Invalid OAuth access token"
- El token expiró, renovarlo desde Meta Developers

### Objetivo detectado incorrectamente
- Verificar que el nombre de la campaña tenga palabras clave claras
- Si necesario, agregar palabras clave en `detect_campaign_objective()`

### Imágenes no aparecen
- Verificar que las imágenes se descargaron en la carpeta `/images/`
- Verificar permisos de la API para acceder a creatividades

## 🔄 Para el mes que viene

1. Crear carpeta nueva: `DIC-25/CLIENTE/`
2. Ejecutar `python3 meta_ads_analyzer_with_images.py`
3. Generar HTML con `python3 generate_html_clean.py`
4. Verificar que objetivos estén correctos
5. Entregar reporte HTML al cliente

---

**Sistema desarrollado y documentado:** Diciembre 2025
**Desarrollador:** LINE Agency con Claude Sonnet 4.5
