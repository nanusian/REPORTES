#!/usr/bin/env python3
"""
Script puntual: extrae datos de PERFIL SRL Marzo 2026 CON imágenes y regenera HTML completo.
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from meta_ads_analyzer_with_images import MetaAdsAnalyzer

# Config
ACCESS_TOKEN = "EAAKNUcfZCd0MBRNwOiFPoZBwBnZAUQ4exufnm4YbwY7NHsDghsquNPcTqLNLapGhNER21XoVyZCAYRmLTzDkm8bYJrCQKFs6IEDqhKbyFFqwUdKKiINjZCRDHKTbZB9ExFO64ueH5x0X8tbsNIoEharl1yeZAKgIzfFRDY8y0ShMTAeEh2LX7iIVRPosfvdB1u1q20jyHrsKFxm64OubDFdZCYdk0L1NNmcIR6Qxhqo0dXdyRzDeAYdyv8GmoZCbrgZB2olggPQpKR0PKFYlqrclBCu9DSOpPsfEJiJ6MsdsuL3vY4U4vob5hz4PFyoZBjuJprewL9lqXfI92AZD"
AD_ACCOUNT_ID = "act_3047423152189615"
CLIENTE = "PERFIL SRL"
DATE_FROM = "2026-03-01"
DATE_UNTIL = "2026-03-31"
PERIODO = f"{DATE_FROM}_{DATE_UNTIL}"

print("\n" + "="*60)
print("📊 EXTRACCIÓN PERFIL SRL - MARZO 2026 (con imágenes)")
print("="*60 + "\n")

analyzer = MetaAdsAnalyzer(ACCESS_TOKEN, AD_ACCOUNT_ID, CLIENTE, PERIODO)

ads_data     = analyzer.get_campaigns_data(DATE_FROM, DATE_UNTIL)
adsets_data  = analyzer.get_adsets_summary(DATE_FROM, DATE_UNTIL)
daily_data   = analyzer.get_daily_data(DATE_FROM, DATE_UNTIL)

analysis = analyzer.analyze_data(ads_data, adsets_data)
report   = analyzer.save_report(ads_data, adsets_data, analysis, daily_data, CLIENTE, PERIODO)

print(f"\n✅ JSON guardado con creatividades e imágenes.")
print(f"   Imágenes en: {analyzer.images_dir}\n")
