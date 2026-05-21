# Inicio Rápido - Sistema de Reportes

## ¿Qué se ha creado?

He configurado un **sistema automatizado** que resuelve tus problemas de reportes mensuales:

### Archivos Nuevos

```
/Users/laureanomedeot/Documents/REPORTES/scripts/
├── config.json                         ← Configuración central
├── generar_reportes_automatico.py      ← Script principal
├── verificar_configuracion.py          ← Verifica que todo esté OK
├── actualizar_token.py                 ← Actualiza el token de Meta
├── GUIA_USO_REPORTES.md               ← Guía completa
└── INICIO_RAPIDO.md                   ← Este archivo
```

## Acción Inmediata Requerida

### Completar IDs de Clientes

Actualmente solo **PERFIL SRL** tiene el ID correcto. Necesitas completar los demás.

**Editar archivo:**
```bash
code /Users/laureanomedeot/Documents/REPORTES/scripts/config.json
```

O desde Finder: `Documents/REPORTES/scripts/config.json`

**Buscar el ID de cada cliente:**
1. Ve a Meta Business Manager (business.facebook.com)
2. Abre cada cuenta publicitaria
3. En la URL verás: `act_1234567890` ← ese es el ID
4. Actualiza `config.json`:

```json
"ASPA": {
  "meta_ad_account_id": "act_XXXXXXXXXX",  ← Reemplazar aquí
  "activo": true
},
```

Haz esto para:
- ASPA
- CREAR
- FULL + NEW CREST
- Grupo Bartolomé
- HORMIGONERA HDI
- MEDICAL HAIR

## Verificar Configuración

Después de completar los IDs:

```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
python3 verificar_configuracion.py
```

Debe decir: ✅ CONFIGURACIÓN CORRECTA

## Primer Uso: Generar Reportes

### Opción 1: Todos los clientes del mes

```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
python3 generar_reportes_automatico.py --mes 1 --ano 2026 --todos
```

### Opción 2: Un solo cliente

```bash
python3 generar_reportes_automatico.py --mes 1 --ano 2026 --cliente "PERFIL SRL"
```

## ¿Dónde se guardan los reportes?

Automáticamente en:
```
/Users/laureanomedeot/Documents/REPORTES/reportes/2026-01-ENE/CLIENTE/meta/
```

**Siempre en la misma ubicación, mismo formato, misma estructura.**

## Cada Mes (Workflow)

1. **Primer día hábil del mes**:
   ```bash
   cd /Users/laureanomedeot/Documents/REPORTES/scripts
   python3 generar_reportes_automatico.py --mes 12 --ano 2025 --todos
   ```

2. **Verificar resultados**:
   ```bash
   open /Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC
   ```

3. **Listo** - Los reportes están en la carpeta correcta, con el formato correcto.

## Cada 60 Días: Actualizar Token

Cuando el token expire:

```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
python3 actualizar_token.py
```

Sigue las instrucciones para obtener un nuevo token de Meta.

## Beneficios de Este Sistema

✅ **Configuración centralizada**: Un solo archivo con todo
✅ **Misma ubicación siempre**: No más carpetas dispersas
✅ **Mismo formato siempre**: Reportes consistentes
✅ **No más olvidos**: IDs y tokens guardados
✅ **Fácil de usar**: Un comando y listo
✅ **Escalable**: Agregar clientes es trivial

## Próximos Pasos

1. ✅ Sistema de generación JSON creado
2. ⏳ Completar IDs de clientes en config.json
3. ⏳ Generar primer set de reportes
4. ⏳ (Opcional) Automatizar generación de HTMLs

## Ayuda

- **Guía completa**: Ver `GUIA_USO_REPORTES.md`
- **Verificar config**: `python3 verificar_configuracion.py`
- **Actualizar token**: `python3 actualizar_token.py`

---

**Última actualización:** 2026-01-09
