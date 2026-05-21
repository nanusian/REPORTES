# Inicio Rápido - Sistema de Reportes

## Generar un Reporte de Meta Ads

**1. Abrí una terminal y navegá a la carpeta scripts:**

```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
```

**2. Ejecutá el script principal:**

```bash
./run_ads.sh
```

**3. Ingresá los datos cuando te los pida:**

- Nombre del cliente: `ASPA`
- Fecha inicio: `2025-12-01`
- Fecha fin: `2025-12-31`

**4. El sistema generará automáticamente:**

- ✅ JSON con datos de Meta API
- ✅ HTML con reporte visual profesional
- ✅ Imágenes de las creatividades

**5. Ubicación del reporte:**

```
reportes/2025-12-DIC/ASPA/meta/
├── ASPA_2025-12-01_2025-12-31_analisis_pauta.json
├── ASPA_REPORTE.html
└── images/
```

## Estructura de Carpetas

```
REPORTES/
├── scripts/      ← Ejecutá los scripts desde aquí
├── config/       ← Credenciales (.env)
├── docs/         ← Documentación completa
└── reportes/     ← Reportes generados automáticamente
    └── YYYY-MM-MES/
        └── CLIENTE/
            └── meta/
```

## Para Google Ads (Futuro)

Cuando agregues reportes de Google Ads, se guardarán en:

```
reportes/YYYY-MM-MES/CLIENTE/
├── meta/       ← Reportes de Meta Ads
└── google/     ← Reportes de Google Ads
```

## Documentación Completa

📖 **Ver `scripts/README.md`** para guía detallada de uso

## Troubleshooting

**Error con credenciales:**
- Verificá que `config/.env` tenga tus tokens de Meta

**No genera el reporte:**
- Asegurate de ejecutar desde la carpeta `scripts/`
- Verificá que las fechas sean correctas

---

💡 **Tip:** Ejecutá siempre desde `scripts/` y todo funcionará automáticamente.
