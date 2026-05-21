#!/bin/bash

# Script de ejecución simplificado para Meta Ads Analyzer
# Extrae datos de Meta API y genera reporte PDF automáticamente

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║  📊 META ADS ANALYZER - Sistema de Reportes de Pauta                   ║"
echo "║  LINE Ad Studio                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar que existe .env en config/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTES_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$REPORTES_DIR/config/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  No se encuentra archivo .env con credenciales en config/${NC}"
    echo ""
    echo "Creá un archivo config/.env con:"
    echo "  ACCESS_TOKEN=tu_token"
    echo "  AD_ACCOUNT_ID=act_123456"
    echo ""
    exit 1
fi

# Pedir datos
echo -e "${GREEN}📋 Datos del reporte:${NC}"
echo ""

read -p "Nombre del cliente: " CLIENTE
if [ -z "$CLIENTE" ]; then
    CLIENTE="cliente"
fi

read -p "Fecha inicio (YYYY-MM-DD, ej: 2025-10-01): " FECHA_INICIO
read -p "Fecha fin (YYYY-MM-DD, ej: 2025-10-31): " FECHA_FIN

echo ""
echo -e "${CYAN}🔄 Procesando...${NC}"
echo ""

# Ejecutar extracción de datos
python3 meta_ads_analyzer_with_images.py <<EOF
$CLIENTE
$FECHA_INICIO
$FECHA_FIN
EOF

# Detectar la carpeta donde se guardó el reporte
# Extraer año-mes del período
YEAR=$(echo $FECHA_INICIO | cut -d'-' -f1)
MONTH=$(echo $FECHA_INICIO | cut -d'-' -f2)
MONTH_NAME=$(date -j -f "%Y-%m-%d" "$FECHA_INICIO" "+%b" 2>/dev/null | tr '[:lower:]' '[:upper:]' || echo "")

PERIODO_FOLDER="${YEAR}-${MONTH}-${MONTH_NAME}"
JSON_FILE="$REPORTES_DIR/reportes/$PERIODO_FOLDER/$CLIENTE/meta/${CLIENTE}_${FECHA_INICIO}_${FECHA_FIN}_analisis_pauta.json"

if [ ! -f "$JSON_FILE" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  No se pudo generar el análisis. Verificá las credenciales y el período.${NC}"
    echo ""
    echo -e "   Buscando en: $JSON_FILE"
    exit 1
fi

echo ""
echo -e "${CYAN}📄 Generando HTML...${NC}"
echo ""

# Generar HTML
python3 generate_html_clean.py "$JSON_FILE"

HTML_FILE="$REPORTES_DIR/reportes/$PERIODO_FOLDER/$CLIENTE/meta/${CLIENTE}_REPORTE.html"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ REPORTE COMPLETADO                                                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📁 Archivos generados:"
echo -e "   JSON: ${CYAN}$JSON_FILE${NC}"
echo -e "   HTML: ${CYAN}$HTML_FILE${NC}"
echo ""
echo -e "📂 Ubicación: ${CYAN}reportes/$PERIODO_FOLDER/$CLIENTE/meta/${NC}"
echo ""
