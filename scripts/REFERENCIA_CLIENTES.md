# Referencia Rápida de Clientes y Configuración

## IDs de Cuentas Publicitarias

### Meta Ads - IDs Actualizados ✅

| Cliente | ID de Cuenta Meta | Nota |
|---------|-------------------|------|
| **ASPA** | `act_280276187315030` | ✅ Google Ads también |
| **CREAR** | `act_116915868648801` | Lote en Terrazas |
| **FULL + NEW CREST** | `act_479774061886732` (FULL)<br>`act_1587930625424690` (NEWCREST) | Dos cuentas separadas |
| **Grupo Bartolomé** | `act_586457407081824` | Clínica Deportiva |
| **HORMIGONERA HDI** | `act_7705227589601205` | Tráfico Instagram |
| **MEDICAL HAIR** | `act_670505644319970` | Mesoterapia, Cirugía, Cejas |
| **PERFIL SRL** | `act_3047423152189615` | VÉNETO, AÑELO, Hormigón |

### Google Ads - IDs

| Cliente | Customer ID | Estado |
|---------|-------------|--------|
| **ASPA** | (pendiente config) | ✅ Tiene reportes |
| Otros | N/A | No configurados |

---

## Estructura de Reportes por Cliente

### ASPA
```
reportes/YYYY-MM-MES/ASPA/
├── meta/
│   ├── ASPA_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
│   └── images/
└── google/
    └── ASPA_YYYY-MM-DD_YYYY-MM-DD_google_ads.json
```
**Períodos con datos:** Sep 2025, Oct 2025, Nov 2025, Dic 2025

### PERFIL SRL
```
reportes/YYYY-MM-MES/PERFIL SRL/
└── meta/
    ├── PERFIL SRL_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
    └── images/
```
**Períodos con datos:** Oct 2025, Nov 2025, Dic 2025
**Campañas:** VÉNETO, PLANTA EN AÑELO, Hormigón 2025, INTERESES

### CREAR
```
reportes/YYYY-MM-MES/CREAR/
└── meta/
    ├── CREAR_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
    └── images/
```
**Períodos con datos:** Nov 2025
**Campaña principal:** Lote en Terrazas inversores (conversaciones)

### MEDICAL HAIR
```
reportes/YYYY-MM-MES/MEDICAL HAIR/
└── meta/
    ├── MEDICAL HAIR_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
    └── images/
```
**Períodos con datos:** Oct 2025, Nov 2025
**Conjuntos:** MESOTERAPIA, CIRUGÍA, CEJAS (mensajes)

### HORMIGONERA HDI
```
reportes/YYYY-MM-MES/HORMIGONERA HDI/
└── meta/
    ├── HORMIGONERA HDI_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
    └── images/
```
**Períodos con datos:** Nov 2025
**Campaña:** Tráfico IG - Nov.25 - Abierto

### Grupo Bartolomé
```
reportes/YYYY-MM-MES/Grupo Bartolomé/
└── meta/
    ├── Grupo Bartolomé_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta.json
    └── images/
```
**Períodos con datos:** Nov 2025
**Campaña:** Views - Clínica Deportiva - Nov.25

### FULL + NEW CREST
```
reportes/YYYY-MM-MES/FULL + NEW CREST/
└── meta/
    └── FULL_YYYY-MM-DD_YYYY-MM-DD_analisis_pauta_REPORTE.html
```
**Períodos con datos:** Nov 2025
**Nota:** Solo HTML encontrado, sin JSON

---

## Comandos Rápidos

### Verificar Configuración
```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
python3 verificar_configuracion.py
```

### Generar Reportes de Todos los Clientes
```bash
python3 generar_reportes_automatico.py --mes 1 --ano 2026 --todos
```

### Generar Reporte de Un Cliente
```bash
python3 generar_reportes_automatico.py --mes 1 --ano 2026 --cliente "PERFIL SRL"
```

### Generar Reportes de Varios Clientes
```bash
python3 generar_reportes_automatico.py --mes 1 --ano 2026 \
  --cliente "ASPA" \
  --cliente "PERFIL SRL" \
  --cliente "MEDICAL HAIR"
```

### Actualizar Token de Meta
```bash
python3 actualizar_token.py
```

### Ver Reportes Generados
```bash
# Listar todos los meses
ls -la /Users/laureanomedeot/Documents/REPORTES/reportes/

# Ver clientes de un mes específico
ls -la /Users/laureanomedeot/Documents/REPORTES/reportes/2025-11-NOV/

# Ver reportes de un cliente
ls -la /Users/laureanomedeot/Documents/REPORTES/reportes/2025-11-NOV/ASPA/meta/
```

---

## Token de Meta Ads

**Token actual:** Configurado en `config.json`
**Última actualización:** 2026-01-09
**Expiración aproximada:** ~60 días (Marzo 2026)

### Cómo obtener nuevo token:
1. Ve a https://developers.facebook.com/tools/explorer/
2. Selecciona tu aplicación
3. Genera token con permisos: `ads_read`, `ads_management`
4. Ejecuta: `python3 actualizar_token.py`

---

## Rutas Importantes

```
/Users/laureanomedeot/Documents/REPORTES/
├── reportes/                    ← Reportes generados
│   └── YYYY-MM-MES/
│       └── CLIENTE/
│           ├── meta/
│           └── google/
│
├── scripts/                     ← Scripts y configuración
│   ├── config.json             ← Configuración central ⭐
│   ├── generar_reportes_automatico.py
│   ├── meta_ads_analyzer.py
│   ├── google_ads_analyzer.py
│   ├── generate_full_report.py
│   ├── verificar_configuracion.py
│   ├── actualizar_token.py
│   ├── GUIA_USO_REPORTES.md
│   ├── DIFERENCIAS_META_GOOGLE.md
│   └── REFERENCIA_CLIENTES.md  ← Este archivo
│
├── config/                      ← Configuraciones adicionales
├── docs/                        ← Documentación
└── templates/                   ← Plantillas HTML
```

---

## Nomenclatura de Períodos

Los nombres de carpetas de meses siguen el formato: `YYYY-MM-MES`

| Mes | Formato |
|-----|---------|
| Enero | `2026-01-ENE` |
| Febrero | `2026-02-FEB` |
| Marzo | `2026-03-MAR` |
| Abril | `2026-04-ABR` |
| Mayo | `2026-05-MAY` |
| Junio | `2026-06-JUN` |
| Julio | `2026-07-JUL` |
| Agosto | `2026-08-AGO` |
| Septiembre | `2026-09-SEP` |
| Octubre | `2026-10-OCT` |
| Noviembre | `2026-11-NOV` |
| Diciembre | `2026-12-DIC` |

---

## Workflow Mensual

### 🗓️ Primer Día Hábil del Mes

1. **Verificar token:**
   ```bash
   grep "token_expiracion_nota" config.json
   ```

2. **Generar reportes del mes anterior:**
   ```bash
   cd /Users/laureanomedeot/Documents/REPORTES/scripts
   python3 generar_reportes_automatico.py --mes 12 --ano 2025 --todos
   ```

3. **Verificar que se generaron:**
   ```bash
   ls -la /Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC/
   ```

4. **Generar HTMLs (opcional):**
   ```bash
   # Usar generate_full_report.py según necesidad
   ```

---

## Notas Importantes

### ⚠️ Cuidados Especiales

1. **FULL + NEW CREST:** Tiene dos IDs de Meta, puede requerir dos extracciones
2. **Nombres de clientes:** Usar EXACTAMENTE como aparecen en `config.json`
   - ✅ `"PERFIL SRL"` (con espacio)
   - ❌ `"PERFIL_SRL"` (con guión bajo)
   - ✅ `"FULL + NEW CREST"` (con espacios y símbolo +)

3. **Token de Meta:** Actualizar cada 60 días o antes si falla

4. **Estructura de carpetas:** NUNCA cambiar manualmente, dejar que el script las cree

### ✅ Buenas Prácticas

- Generar reportes siempre desde `scripts/`
- Usar el script automatizado en lugar de scripts individuales
- Mantener backup de `config.json`
- Documentar cambios en las notas de cada cliente
- Verificar configuración antes de generar reportes masivos

---

## Clientes Activos vs Inactivos

### ✅ Activos (7)
- ASPA
- CREAR
- FULL + NEW CREST
- Grupo Bartolomé
- HORMIGONERA HDI
- MEDICAL HAIR
- PERFIL SRL

### ⏸️ Inactivos
*(Ninguno actualmente)*

Para desactivar un cliente temporalmente, editar `config.json`:
```json
"CLIENTE": {
  "activo": false
}
```

---

## Contacto y Ayuda

**Documentación:**
- Guía completa: `GUIA_USO_REPORTES.md`
- Diferencias plataformas: `DIFERENCIAS_META_GOOGLE.md`
- Inicio rápido: `INICIO_RAPIDO.md`

**Troubleshooting:**
- Verificar config: `python3 verificar_configuracion.py`
- Ver logs de errores en la salida del script
- Confirmar que el token sea válido

---

**Última actualización:** 2026-01-09
**Versión:** 1.0
