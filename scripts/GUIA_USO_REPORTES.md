# Guía de Uso - Sistema de Reportes Automatizado

## Descripción

Este sistema genera reportes mensuales de Meta Ads de forma **consistente y automatizada**, garantizando que:
- Los reportes siempre tengan el mismo formato
- Se guarden en la ubicación correcta
- Los tokens y configuraciones estén centralizados
- No tengas que recordar IDs de clientes cada mes

## Archivos Principales

```
/Users/laureanomedeot/Documents/REPORTES/scripts/
├── config.json                         ← Configuración central (tokens, IDs, clientes)
├── generar_reportes_automatico.py      ← Script principal
├── meta_ads_analyzer.py                ← Librería de Meta Ads
└── GUIA_USO_REPORTES.md               ← Esta guía
```

## Configuración Inicial (Solo Una Vez)

### 1. Completar IDs de Clientes en config.json

Abre `/Users/laureanomedeot/Documents/REPORTES/scripts/config.json` y completa los `meta_ad_account_id` para cada cliente:

```json
{
  "clientes": {
    "ASPA": {
      "meta_ad_account_id": "act_XXXXXXXXXX",  ← Completar aquí
      "activo": true
    },
    "CREAR": {
      "meta_ad_account_id": "act_XXXXXXXXXX",  ← Completar aquí
      "activo": true
    }
  }
}
```

**¿Cómo encontrar el ID de cuenta?**
1. Ve a Meta Business Manager
2. Abre la cuenta publicitaria del cliente
3. En la URL verás algo como: `act_1234567890`
4. Ese es el ID que debes usar

### 2. Actualizar Token de Meta (Cada 60 días)

Cuando el token expire, actualízalo en `config.json`:

```json
{
  "meta_access_token": "NUEVO_TOKEN_AQUI",
  "token_expiracion_nota": "Última actualización: 2026-01-15"
}
```

**¿Cómo obtener un nuevo token?**
1. Ve a https://developers.facebook.com/tools/explorer/
2. Selecciona tu app
3. Genera un nuevo token con permisos de `ads_read`
4. Copia y pega en `config.json`

## Uso Mensual

### Generar Reporte de UN Cliente

```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts

python generar_reportes_automatico.py --mes 1 --ano 2026 --cliente "PERFIL SRL"
```

### Generar Reportes de TODOS los Clientes

```bash
python generar_reportes_automatico.py --mes 1 --ano 2026 --todos
```

### Generar Reportes de VARIOS Clientes Específicos

```bash
python generar_reportes_automatico.py --mes 1 --ano 2026 --cliente "ASPA" --cliente "CREAR" --cliente "MEDICAL HAIR"
```

## Estructura de Salida

Los reportes se guardan automáticamente en:

```
/Users/laureanomedeot/Documents/REPORTES/reportes/
└── 2026-01-ENE/                    ← Carpeta del mes
    └── PERFIL SRL/                 ← Carpeta del cliente
        └── meta/                   ← Plataforma
            ├── PERFIL SRL_2026-01-01_2026-01-31_analisis_pauta.json
            └── images/             ← Creatividades (futuro)
```

**Siempre** se sigue esta estructura:
- `YYYY-MM-MES/CLIENTE/meta/`
- Nombres consistentes
- Misma ubicación

## Ejemplo Completo: Reportes de Enero 2026

```bash
# Ir a la carpeta de scripts
cd /Users/laureanomedeot/Documents/REPORTES/scripts

# Generar reportes de todos los clientes de enero 2026
python generar_reportes_automatico.py --mes 1 --ano 2026 --todos
```

**Resultado:**
```
📋 Cargando configuración...
✅ Configuración cargada
   Clientes configurados: 7

📊 Procesando TODOS los clientes activos (7)

======================================================================
🚀 Generando reporte para: ASPA
======================================================================
📅 Período: 2026-01-01 a 2026-01-31
📁 Carpeta: 2026-01-ENE/ASPA/meta/

🔗 Conectando a Meta Ads...
📥 Extrayendo datos de campañas...
📊 Analizando datos...

✅ Reporte JSON guardado

... [continúa con los demás clientes] ...

======================================================================
🏁 PROCESO COMPLETADO
======================================================================
  ✅ Exitosos: 7
======================================================================
```

## Mantenimiento

### Agregar un Nuevo Cliente

Edita `config.json`:

```json
"NUEVO CLIENTE": {
  "nombre_completo": "Nombre Completo del Cliente",
  "meta_ad_account_id": "act_1234567890",
  "google_customer_id": "",
  "activo": true,
  "notas": "Cliente desde enero 2026"
}
```

### Desactivar un Cliente Temporalmente

```json
"CLIENTE": {
  "activo": false  ← Cambiar a false
}
```

Cuando uses `--todos`, los clientes inactivos serán omitidos.

### Verificar la Configuración

```bash
# Ver contenido de config.json
cat /Users/laureanomedeot/Documents/REPORTES/scripts/config.json
```

## Resolución de Problemas

### Error: "No se encontró config.json"
**Solución:** Asegúrate de estar en la carpeta correcta:
```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
```

### Error: "Token inválido" o "Error de autenticación"
**Solución:** El token de Meta expiró. Genera uno nuevo y actualiza `config.json`.

### Error: "Cliente no encontrado"
**Solución:** Verifica que el nombre del cliente esté exactamente igual que en `config.json` (incluyendo mayúsculas/minúsculas).

### No hay datos para el período
**Causa:** El cliente no tuvo campañas activas en ese mes.
**Solución:** Esto es normal, no es un error.

## Workflow Mensual Recomendado

**Primer día hábil del mes:**

1. **Actualizar token si es necesario** (cada 60 días)
   ```bash
   # Verificar última actualización en config.json
   grep "token_expiracion_nota" config.json
   ```

2. **Generar reportes del mes anterior**
   ```bash
   cd /Users/laureanomedeot/Documents/REPORTES/scripts
   python generar_reportes_automatico.py --mes 12 --ano 2025 --todos
   ```

3. **Verificar que se generaron correctamente**
   ```bash
   ls -la /Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC/
   ```

4. **Generar reportes HTML** (próximo paso)
   ```bash
   # Usar generate_full_report.py para crear HTMLs visuales
   ```

## Próximos Pasos

Este sistema actualmente genera:
- ✅ Archivos JSON con todos los datos

**Pendiente:**
- [ ] Generación automática de reportes HTML
- [ ] Descarga de imágenes de creatividades
- [ ] Integración con Google Ads

## Notas Importantes

1. **Backup del token:** Guarda una copia del token en un lugar seguro
2. **Seguridad:** No compartas el archivo `config.json` - contiene datos sensibles
3. **Consistencia:** Siempre usa este script en lugar de crear scripts individuales
4. **Nomenclatura:** Los nombres de clientes en `config.json` deben coincidir EXACTAMENTE con los nombres de las carpetas

## Ayuda y Soporte

Si tienes problemas:

1. Verifica que el token sea válido
2. Confirma que los IDs de cuenta sean correctos
3. Revisa que la estructura de carpetas exista
4. Consulta los logs de error que muestra el script

---

**Última actualización:** 2026-01-09
**Versión:** 1.0
