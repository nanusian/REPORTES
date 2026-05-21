# 🎯 Nuevas Funciones - Meta Ads Analyzer v2.0

## ✨ Qué se agregó

### 1. 💡 Insights Automáticos

El sistema ahora analiza automáticamente tus campañas y detecta:

#### 🔴 Alertas (Prioridad Alta)
- **Frecuencia alta (>5)**: Saturación de audiencia. El mismo público ve el anuncio muchas veces.
- **CPC alto (>50% del promedio)**: Estás pagando de más por cada click.

#### 🟡 Oportunidades (Prioridad Media)
- **CTR bajo (<1%)**: El anuncio no genera interés, necesita nuevo copy/creatividad.
- **Costo por conversación alto (>$5,000 ARS)**: Hay margen para optimizar segmentación.
- **Subinversión en anuncio con potencial**: Anuncio con buen CTR pero poca inversión.

#### 🟢 Éxitos (Prioridad Baja)
- **Excelente performance**: CTR >2% con frecuencia controlada. Estos anuncios funcionan bien.

### Ejemplo de insights generados:

```
🔴 ALERTA - Saturación de audiencia en 'Familia 1 | Oferta'
Frecuencia de 8.9 indica que las mismas personas ven el anuncio muchas veces.
Recomendación: ampliar audiencia o pausar anuncio.
→ Acción sugerida: Ampliar audiencia o rotar creatividad

🟡 OPORTUNIDAD - Costo por conversación alto en 'Abierto | Neuquén'
Estás pagando $5,113 por cada conversación. Hay margen para optimizar.
→ Acción sugerida: Refinar audiencia o mejorar oferta/copy

🟢 ÉXITO - Excelente performance en 'Dormir 1 | Oferta'
CTR de 3.14% con frecuencia controlada (1.7). Este anuncio está funcionando muy bien.
→ Acción sugerida: Escalar presupuesto si hay margen
```

---

### 2. 📈 Gráficos de Evolución Temporal

El sistema ahora extrae datos **día por día** y genera gráficos automáticos:

#### Gráficos incluidos:
- **Inversión diaria**: Línea de tiempo mostrando cuánto gastaste cada día
- **Alcance diario**: Barras mostrando a cuántas personas alcanzaste cada día
- **Conversaciones**: Evolución de conversaciones generadas

#### Características:
- Gráficos interactivos con Chart.js
- Colores LINE (turquesa #00D9C1)
- Fondo oscuro consistente con el diseño
- Exportables en PDF

---

## 📊 Nuevas Páginas en el Reporte PDF

El reporte ahora incluye:

### Antes (v1.0):
1. Portada
2. Glosario
3. Resumen ejecutivo
4. Tabla de conjuntos
5. Páginas por conjunto

### Ahora (v2.0):
1. Portada
2. Glosario
3. Resumen ejecutivo
4. **💡 Insights Automáticos** ⭐ NUEVO
5. **📈 Evolución Temporal** ⭐ NUEVO
6. Tabla de conjuntos
7. Páginas por conjunto

---

## 🎯 Qué decisiones podés tomar con esto

### Con Insights Automáticos:

#### Alertas rojas (actuar YA):
- Pausar anuncios con frecuencia >8
- Reducir presupuesto en anuncios con CPC muy alto
- Ampliar audiencias saturadas

#### Oportunidades amarillas (optimizar):
- Testear nuevo copy en anuncios con CTR bajo
- Refinar segmentación en conversaciones caras
- Escalar presupuesto en anuncios subinvertidos

#### Éxitos verdes (escalar):
- Aumentar presupuesto en anuncios que funcionan
- Replicar fórmula ganadora en nuevos anuncios

### Con Gráficos de Evolución:

#### Inversión diaria:
- Detectar días con picos de gasto inusuales
- Identificar si la distribución es pareja o concentrada
- Ver si hay días sin inversión (pausas no planeadas)

#### Alcance diario:
- Identificar días con mejor/peor alcance
- Correlacionar alcance con inversión
- Detectar tendencias de saturación

---

## 🔍 Ejemplo de Análisis Real

### Cliente: CBS TECH (Octubre 2025)

#### Datos generales:
- 6 anuncios corridos
- $391,145 ARS invertidos
- 153,579 personas alcanzadas

#### Insights automáticos detectados:

**🔴 Alerta crítica:**
- "Familia 1 | Oferta" tiene frecuencia 8.9 → audiencia saturada
- Acción: Ampliar segmentación o pausar

**🟡 Oportunidades:**
- "Abierto | Neuquén" genera conversaciones a $5,113 c/u
- Acción: Optimizar copy o refinar audiencia para bajar costo

**🟢 Éxitos:**
- "Dormir 1 | Oferta" tiene CTR 3.14% (excelente)
- Acción: Escalar presupuesto en este anuncio

#### Gráficos mostraron:
- Inversión concentrada en primera quincena de octubre
- Alcance estable pero con pico el 15/10
- 17 conversaciones totales generadas

---

## 🚀 Cómo usar las nuevas funciones

### Ejecutar análisis completo:

```bash
./run_ads.sh
```

El sistema automáticamente:
1. Extrae datos de Meta API
2. Analiza métricas
3. Genera insights
4. Crea gráficos diarios
5. Produce PDF con todo incluido

### Interpretar insights:

Leé la sección **INSIGHTS AUTOMÁTICOS** del PDF:
- Empezá por las **alertas rojas** (actuar urgente)
- Seguí con **oportunidades amarillas** (optimizar)
- Finalmente, escalá **éxitos verdes**

### Usar gráficos:

En la página **EVOLUCIÓN TEMPORAL**:
- Mirá la tendencia de inversión (¿creciente, decreciente, estable?)
- Comparala con alcance (¿estás pagando más por menos?)
- Identificá días excepcionales (picos) para analizar qué cambió

---

## 💡 Tips Profesionales

### Para reportes mensuales:

1. **Primera semana del mes**:
   - Corré el reporte del mes anterior
   - Revisá insights automáticos
   - Implementá acciones sugeridas

2. **Durante el mes**:
   - Monitoreá anuncios con alerta roja
   - Escalá anuncios con éxito verde

3. **Fin de mes**:
   - Generá reporte para cliente
   - Mostrá gráficos de evolución
   - Justificá optimizaciones hechas con insights

### Para presentar al cliente:

**Lo que el cliente ve en el PDF:**
- Resumen ejecutivo (números grandes)
- Insights automáticos (qué mejorar)
- Gráficos de evolución (tendencias visuales)
- Detalles por anuncio (performance individual)

**Cómo presentarlo:**
1. Empezá con resumen ejecutivo
2. Mostrá insights (problemas y oportunidades)
3. Respaldá con gráficos (tendencias)
4. Cerrá con próximos pasos (acciones)

---

## 🔧 Personalización

### Ajustar umbrales de insights:

Editá `meta_ads_analyzer.py` línea 214-291:

```python
# Cambiar umbral de frecuencia alta
if ad['frequency'] > 5:  # Cambiá el 5 por otro número

# Cambiar umbral de CTR bajo
if ad['ctr'] < 1.0:  # Cambiá el 1.0

# Cambiar umbral de costo alto
if cost_per_conv > 5000:  # Cambiá el 5000
```

### Agregar nuevos insights:

En la misma función `generate_insights()`, podés agregar:

```python
# Detectar algo nuevo
if condicion_que_quieras:
    insights.append({
        'tipo': 'ALERTA',  # o 'OPORTUNIDAD' o 'ÉXITO'
        'prioridad': 'alta',
        'titulo': 'Tu título',
        'descripcion': 'Descripción del problema',
        'metrica': 'Métrica relevante',
        'accion': 'Qué hacer'
    })
```

---

## 📋 Checklist Post-Reporte

Después de generar cada reporte:

- [ ] Revisé todas las alertas rojas
- [ ] Implementé al menos 1 oportunidad amarilla
- [ ] Escalé presupuesto en éxitos verdes
- [ ] Analicé gráficos de evolución
- [ ] Documenté cambios realizados
- [ ] Agendé seguimiento para próximo mes

---

**Sistema actualizado:** 8 Nov 2025
**Versión:** 2.0
**Nuevas funciones:** Insights automáticos + Gráficos temporales
