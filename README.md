# Sistema de Reportes Automatizado - LINE Agency

## ✅ Sistema Completado y Configurado

Este directorio contiene un **sistema automatizado de generación de reportes mensuales** para Meta Ads y Google Ads, diseñado para resolver los problemas de:

- ❌ Reportes inconsistentes mes a mes
- ❌ Carpetas en ubicaciones diferentes
- ❌ Olvidar tokens y IDs de clientes
- ❌ Confusión entre estructuras de Meta y Google

## 📁 Estructura del Directorio

```
/Users/laureanomedeot/Documents/REPORTES/
│
├── 📂 reportes/                    ← REPORTES GENERADOS
│   ├── 2025-09-SEP/
│   ├── 2025-10-OCT/
│   ├── 2025-11-NOV/
│   ├── 2025-12-DIC/
│   └── YYYY-MM-MES/
│       └── CLIENTE/
│           ├── meta/              ← Reportes de Meta Ads
│           │   ├── *.json
│           │   └── images/
│           └── google/            ← Reportes de Google Ads
│               └── *.json
│
├── 📂 scripts/                     ← SCRIPTS Y CONFIGURACIÓN
│   │
│   ├── 🔧 config.json             ← CONFIGURACIÓN CENTRAL ⭐
│   │   • Token de Meta Ads
│   │   • IDs de todos los clientes
│   │   • Rutas y configuraciones
│   │
│   ├── 🤖 Scripts Principales:
│   │   ├── generar_reportes_automatico.py   ← Script principal
│   │   ├── meta_ads_analyzer.py
│   │   ├── google_ads_analyzer.py
│   │   ├── generate_full_report.py
│   │   ├── verificar_configuracion.py
│   │   └── actualizar_token.py
│   │
│   └── 📚 Documentación:
│       ├── GUIA_USO_REPORTES.md            ← Guía completa de uso
│       ├── DIFERENCIAS_META_GOOGLE.md      ← Diferencias entre plataformas
│       ├── REFERENCIA_CLIENTES.md          ← IDs y referencia rápida
│       └── INICIO_RAPIDO.md                ← Inicio rápido
│
├── 📂 config/                      ← Configuraciones adicionales
├── 📂 docs/                        ← Documentación extra
├── 📂 templates/                   ← Plantillas HTML
│
└── 📄 README.md                    ← Este archivo
```

## 🚀 Inicio Rápido

### 1. Generar Reportes de Todos los Clientes

```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
python3 generar_reportes_automatico.py --mes 1 --ano 2026 --todos
```

### 2. Generar Reporte de Un Cliente Específico

```bash
python3 generar_reportes_automatico.py --mes 1 --ano 2026 --cliente "PERFIL SRL"
```

### 3. Verificar que Todo Esté Configurado

```bash
python3 verificar_configuracion.py
```

## 📊 Clientes Configurados

| Cliente | Meta Ads | Google Ads | Notas |
|---------|----------|------------|-------|
| **ASPA** | ✅ `act_280276187315030` | ✅ | Único con ambas plataformas |
| **CREAR** | ✅ `act_116915868648801` | ❌ | Lote en Terrazas |
| **FULL + NEW CREST** | ✅ `act_479774061886732` | ❌ | Dos IDs separados |
| **Grupo Bartolomé** | ✅ `act_586457407081824` | ❌ | Clínica Deportiva |
| **HORMIGONERA HDI** | ✅ `act_7705227589601205` | ❌ | Tráfico Instagram |
| **MEDICAL HAIR** | ✅ `act_670505644319970` | ❌ | Mesoterapia, Cirugía, Cejas |
| **PERFIL SRL** | ✅ `act_3047423152189615` | ❌ | VÉNETO, AÑELO, Hormigón |

## 📖 Documentación

### Para Empezar
- **[INICIO_RAPIDO.md](scripts/INICIO_RAPIDO.md)** - Primeros pasos y configuración inicial

### Uso Diario
- **[GUIA_USO_REPORTES.md](scripts/GUIA_USO_REPORTES.md)** - Guía completa de uso mensual
- **[REFERENCIA_CLIENTES.md](scripts/REFERENCIA_CLIENTES.md)** - IDs, comandos y referencia rápida

### Información Técnica
- **[DIFERENCIAS_META_GOOGLE.md](scripts/DIFERENCIAS_META_GOOGLE.md)** - Diferencias entre reportes de Meta y Google
- **[ESTRUCTURA_REPORTES.md](reportes/ESTRUCTURA_REPORTES.md)** - Estructura de carpetas

## 🗓️ Workflow Mensual Recomendado

### Primer día hábil del mes:

```bash
# 1. Ir a la carpeta de scripts
cd /Users/laureanomedeot/Documents/REPORTES/scripts

# 2. Verificar que todo esté OK (opcional)
python3 verificar_configuracion.py

# 3. Generar reportes del mes anterior
python3 generar_reportes_automatico.py --mes 12 --ano 2025 --todos

# 4. Verificar que se generaron
ls -la /Users/laureanomedeot/Documents/REPORTES/reportes/2025-12-DIC/
```

### Cada 60 días (cuando expire el token):

```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
python3 actualizar_token.py
```

## ⚙️ Configuración

### Token de Meta Ads
- **Ubicación:** `scripts/config.json`
- **Última actualización:** 2026-01-09
- **Expiración:** ~60 días (Marzo 2026)
- **Actualizar:** `python3 actualizar_token.py`

### IDs de Clientes
Todos los IDs están configurados en `scripts/config.json`. No es necesario recordarlos.

## 🎯 Características Principales

### ✅ Ventajas del Sistema

1. **Configuración Centralizada**
   - Un solo archivo (`config.json`) con todos los tokens e IDs
   - No más olvidar credenciales

2. **Ubicación Consistente**
   - Siempre en: `reportes/YYYY-MM-MES/CLIENTE/plataforma/`
   - No más carpetas dispersas

3. **Formato Estandarizado**
   - Mismo formato de archivo siempre
   - Fácil de procesar y comparar

4. **Fácil de Usar**
   - Un comando genera todos los reportes
   - Scripts de verificación y ayuda

5. **Bien Documentado**
   - 4 archivos de documentación
   - Ejemplos y comandos listos para copiar

6. **Diferencias Documentadas**
   - Entiendes qué tiene Meta vs Google
   - Sabes qué esperar de cada plataforma

## 🔧 Scripts Disponibles

| Script | Propósito |
|--------|-----------|
| `generar_reportes_automatico.py` | Genera reportes de Meta Ads |
| `verificar_configuracion.py` | Verifica que todo esté OK |
| `actualizar_token.py` | Actualiza el token de Meta |
| `meta_ads_analyzer.py` | Librería para extraer datos de Meta |
| `google_ads_analyzer.py` | Librería para extraer datos de Google |
| `generate_full_report.py` | Genera reportes HTML visuales |

## 📝 Ejemplos de Uso

### Generar reportes de enero 2026 para todos
```bash
python3 generar_reportes_automatico.py --mes 1 --ano 2026 --todos
```

### Generar solo ASPA y PERFIL SRL de diciembre 2025
```bash
python3 generar_reportes_automatico.py --mes 12 --ano 2025 \
  --cliente "ASPA" \
  --cliente "PERFIL SRL"
```

### Ver reportes generados
```bash
# Listar todos los meses
ls /Users/laureanomedeot/Documents/REPORTES/reportes/

# Ver clientes de noviembre
ls /Users/laureanomedeot/Documents/REPORTES/reportes/2025-11-NOV/

# Abrir carpeta en Finder
open /Users/laureanomedeot/Documents/REPORTES/reportes/
```

## ⚠️ Consideraciones Importantes

### Nombres de Clientes
Usar EXACTAMENTE como aparecen en `config.json`:
- ✅ `"PERFIL SRL"` (con espacio)
- ✅ `"FULL + NEW CREST"` (con espacios y +)
- ✅ `"Grupo Bartolomé"` (con mayúscula y acento)

### Token de Meta
- Expira cada ~60 días
- Actualizar con `python3 actualizar_token.py`
- Guardar backup en lugar seguro

### FULL + NEW CREST
- Tiene dos IDs de Meta diferentes
- Puede requerir dos extracciones separadas

## 🆘 Ayuda y Troubleshooting

### Error: Token inválido
```bash
python3 actualizar_token.py
```

### Error: Cliente no encontrado
Verificar que el nombre esté exactamente igual que en `config.json`.

### Error: No se encontró config.json
Asegurarse de estar en la carpeta correcta:
```bash
cd /Users/laureanomedeot/Documents/REPORTES/scripts
```

### Sin datos para un período
Normal si el cliente no tuvo campañas activas ese mes.

## 📞 Soporte

- Consultar documentación en `scripts/`
- Ejecutar `python3 verificar_configuracion.py`
- Revisar logs de error en la salida del script

---

## 📅 Historial de Reportes

### Períodos con Datos:

- **2025-09-SEP:** ASPA
- **2025-10-OCT:** ASPA, MEDICAL HAIR
- **2025-11-NOV:** ASPA, CREAR, PERFIL SRL, MEDICAL HAIR, HORMIGONERA HDI, Grupo Bartolomé
- **2025-12-DIC:** ASPA, PERFIL SRL

---

## 🎉 Sistema Listo

✅ Configuración completada
✅ Todos los IDs actualizados
✅ Scripts listos para usar
✅ Documentación completa

**Próximo paso:** Generar los reportes del mes anterior usando el comando sugerido arriba.

---

**Última actualización:** 2026-01-09
**Versión:** 1.0
**Mantenedor:** LINE Agency
