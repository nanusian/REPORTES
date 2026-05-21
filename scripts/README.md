# Scripts de Generación de Reportes Meta Ads

Sistema automatizado para extraer datos de Meta Ads API y generar reportes HTML profesionales.

## Estructura de Archivos

La nueva estructura organizada garantiza que todos los reportes se guarden de forma consistente:

```
REPORTES/
├── scripts/           ← Ejecutar scripts desde aquí
├── config/            ← Credenciales y configuración
│   └── .env
├── docs/              ← Documentación del sistema
└── reportes/          ← Reportes organizados automáticamente
    └── YYYY-MM-MES/   ← Por ejemplo: 2025-11-NOV
        └── CLIENTE/
            └── meta/
                ├── datos.json
                ├── reporte.html
                └── images/
```

## Configuración Inicial

1. **Configurar credenciales**

Editá el archivo `config/.env` con tus credenciales de Meta Ads:

```env
ACCESS_TOKEN=tu_token_de_acceso
AD_ACCOUNT_ID=act_tu_account_id
```

2. **Instalar dependencias Python**

```bash
pip3 install facebook-business python-dotenv requests
```

## Uso

### Opción 1: Script automatizado (Recomendado)

Ejecutá el script bash que maneja todo el proceso:

```bash
cd scripts/
./run_ads.sh
```

El script te pedirá:
- Nombre del cliente
- Fecha de inicio (YYYY-MM-DD)
- Fecha de fin (YYYY-MM-DD)

Y generará automáticamente:
- JSON con datos extraídos de Meta API
- HTML con reporte visual profesional
- Imágenes de las creatividades

**Ubicación del reporte:**
`../reportes/YYYY-MM-MES/CLIENTE/meta/`

### Opción 2: Scripts individuales

**1. Extraer datos de Meta Ads (con imágenes):**

```bash
cd scripts/
python3 meta_ads_analyzer_with_images.py
```

**2. Generar HTML desde JSON:**

```bash
python3 generate_html_clean.py ../reportes/2025-11-NOV/CLIENTE/meta/datos.json
```

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `run_ads.sh` | Script principal que ejecuta todo el flujo |
| `meta_ads_analyzer_with_images.py` | Extrae datos de Meta API + descarga imágenes |
| `meta_ads_analyzer.py` | Extrae datos de Meta API (versión sin imágenes) |
| `generate_html_clean.py` | Genera reporte HTML limpio y responsive |
| `generate_comparison.py` | Compara rendimiento entre períodos |
| `generate_full_report.py` | Reporte completo con todos los detalles |

## Nueva Estructura de Reportes

Todos los reportes ahora se guardan automáticamente en:

```
reportes/
├── 2025-09-SEP/
│   └── ASPA/
│       └── meta/
│           ├── ASPA_2025-09-01_2025-09-30_analisis_pauta.json
│           ├── ASPA_REPORTE.html
│           └── images/
├── 2025-10-OCT/
│   ├── ASPA/meta/
│   └── MEDICAL-HAIR/meta/
└── 2025-11-NOV/
    ├── ASPA/meta/
    ├── CREAR/meta/
    └── ...
```

### ¿Por qué esta estructura?

- **Por período primero**: Fácil ver todos los clientes de un mes
- **Subcarpeta `meta/`**: Preparado para agregar reportes de `google/` en el futuro
- **Formato YYYY-MM-MES**: Ordenamiento natural por fecha

## Agregar Reportes de Google Ads (Futuro)

Cuando agregues reportes de Google Ads, simplemente creá la carpeta `google/` al lado de `meta/`:

```
reportes/2025-11-NOV/ASPA/
├── meta/       ← Reportes de Meta Ads
└── google/     ← Reportes de Google Ads
```

## Notas Importantes

- **Siempre ejecutá desde `scripts/`**: Los scripts usan rutas relativas basadas en esta ubicación
- **Credenciales en `config/`**: Nunca commitear el archivo `.env` al repositorio
- **Backup disponible**: Si algo sale mal, hay un backup en `/Users/laureanomedeot/Documents/REPORTES_backup_*.zip`

## Troubleshooting

**Error: "No se encontraron credenciales en .env"**
- Verificá que `config/.env` existe y tiene las credenciales correctas
- Ejecutá desde la carpeta `scripts/`

**Error: "No se pudo generar el análisis"**
- Verificá que el período de fechas es correcto
- Confirmá que hay campañas corriendo en ese período
- Revisá que el ACCESS_TOKEN no haya expirado

**El reporte no muestra imágenes**
- Usá `meta_ads_analyzer_with_images.py` en vez de `meta_ads_analyzer.py`
- Las imágenes se descargan automáticamente durante la extracción

## Soporte

Para más información consultá la documentación en `../docs/`:
- `README.md` - Documentación general del sistema
- `SISTEMA_REPORTES_META.md` - Guía detallada del sistema
- `NUEVAS_FUNCIONES.md` - Características y actualizaciones
- `RENOVAR_TOKEN.md` - Cómo renovar el token de acceso
