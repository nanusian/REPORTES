# Estructura de Reportes

## Organización por Período → Cliente → Plataforma

Todos los reportes se organizan siguiendo esta estructura jerárquica:

```
reportes/
└── YYYY-MM-MES/           ← Período (ej: 2025-11-NOV)
    └── CLIENTE/           ← Nombre del cliente
        ├── meta/          ← Reportes de Meta Ads (Facebook/Instagram)
        │   ├── *.json     ← Datos extraídos de Meta API
        │   ├── *.html     ← Reporte visual
        │   └── images/    ← Creatividades descargadas
        │
        └── google/        ← Reportes de Google Ads
            ├── *.json     ← Datos extraídos de Google Ads API
            ├── *.html     ← Reporte visual
            └── images/    ← Creatividades descargadas
```

## Ejemplo Real

```
reportes/
├── 2025-09-SEP/
│   └── ASPA/
│       ├── meta/
│       │   ├── ASPA_2025-09-01_2025-09-30_analisis_pauta.json
│       │   ├── ASPA_REPORTE.html
│       │   └── images/
│       └── google/
│           └── (reportes de Google Ads aquí)
│
├── 2025-10-OCT/
│   ├── ASPA/
│   │   ├── meta/
│   │   └── google/
│   └── MEDICAL HAIR/
│       ├── meta/
│       └── google/
│
└── 2025-11-NOV/
    ├── ASPA/
    │   ├── meta/
    │   └── google/
    ├── CREAR/
    │   ├── meta/
    │   └── google/
    └── ...
```

## Ventajas de Esta Estructura

### 1. Organización Cronológica
- Fácil encontrar todos los reportes de un mes específico
- Ordenamiento natural por fecha

### 2. Comparación Multi-Plataforma
- Ver Meta y Google Ads del mismo cliente juntos
- Facilita análisis comparativos de rendimiento

### 3. Escalable
- Agregar nuevas plataformas es simple (ej: `linkedin/`, `tiktok/`)
- Mantiene la consistencia

### 4. Navegación Intuitiva
```bash
# Ver todos los clientes de noviembre
ls reportes/2025-11-NOV/

# Ver reportes de Meta para ASPA en noviembre
ls reportes/2025-11-NOV/ASPA/meta/

# Ver reportes de Google para ASPA en noviembre
ls reportes/2025-11-NOV/ASPA/google/
```

## Generación de Reportes

### Meta Ads (Actual)

```bash
cd scripts/
./run_ads.sh
```

Los reportes se guardan automáticamente en `reportes/YYYY-MM-MES/CLIENTE/meta/`

### Google Ads (Futuro)

Cuando implementes scripts de Google Ads, seguirán el mismo patrón:

```bash
cd scripts/
./run_google_ads.sh  # (futuro)
```

Los reportes se guardarán en `reportes/YYYY-MM-MES/CLIENTE/google/`

## Agregar Nuevas Plataformas

Para agregar una nueva plataforma (ej: LinkedIn, TikTok):

1. Crear carpeta al mismo nivel que `meta/` y `google/`
2. Seguir la misma convención de nombres
3. Usar el mismo formato de archivos (JSON + HTML)

```
reportes/YYYY-MM-MES/CLIENTE/
├── meta/
├── google/
├── linkedin/     ← Nueva plataforma
└── tiktok/       ← Otra plataforma
```

## Notas Importantes

- **Nombres de clientes**: Mantener consistencia en mayúsculas/minúsculas
- **Formato de período**: Siempre `YYYY-MM-MES` (ej: `2025-11-NOV`)
- **Carpetas vacías**: Las carpetas `google/` existen para futura implementación
- **Backup**: Siempre hay backup disponible antes de cambios importantes

## Archivos Típicos por Plataforma

### Meta Ads (`meta/`)
- `{CLIENTE}_{PERIODO}_analisis_pauta.json` - Datos crudos
- `{CLIENTE}_REPORTE.html` - Reporte visual
- `images/` - Creatividades de anuncios

### Google Ads (`google/`) - Futuro
- `{CLIENTE}_{PERIODO}_google_ads.json` - Datos crudos
- `{CLIENTE}_REPORTE_GOOGLE.html` - Reporte visual
- `images/` - Creatividades de anuncios

---

💡 **Tip**: Esta estructura facilita crear reportes consolidados que comparen rendimiento entre plataformas.
