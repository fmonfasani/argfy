# valuarty Pipeline — Reproducible dataset de CEDEARs + BYMA locales
#
# Uso:
#   make all         -> ejecuta pipeline completo (pasos 1-8)
#   make dataset     -> solo pasos 6-8 (precios históricos + locales + ETL)
#   make prices      -> solo paso 6 (precios históricos US)
#   make locales     -> solo paso 7 (BYMA locales)
#   make etl         -> solo paso 8 (generar dataset)
#   make clean       -> limpiar outputs generados (pero no cedears_con_cik ni financials_sec)
#   make clean-all   -> limpiar TODO (incluye financials_sec)
#   make zip         -> empaqueta data_export.zip
#
# Requisitos:
#   Python 3.10+ con pip install PyOBD yfinance requests openpyxl

PYTHON = python

.PHONY: all pasos dataset prices locales etl clean clean-all zip help

help:
	@echo "valuarty Pipeline"
	@echo ""
	@echo "  make all         -> Pipeline completo (pasos 1-8)"
	@echo "  make dataset     -> Dataset final (pasos 6-8, requiere pasos 1-5 ya corridos)"
	@echo "  make prices      -> Solo precios históricos (paso 6)"
	@echo "  make locales     -> Solo BYMA locales (paso 7)"
	@echo "  make etl         -> Solo generar dataset ETL (paso 8)"
	@echo "  make zip         -> Empaquetar data_export.zip"
	@echo "  make clean       -> Limpiar outputs generados"
	@echo "  make clean-all   -> Limpiar todo (incluye financials_sec)"

# ── Pipeline completo ──────────────────────────────────────
all: paso1 paso2 paso3 paso4 paso5 paso6 paso7 paso8 zip
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║  PIPELINE COMPLETO — Dataset listo en data_export.zip    ║"
	@echo "╚══════════════════════════════════════════════════════════╝"

paso1: cedears_download.py
	$(PYTHON) cedears_download.py

paso2: 02_mapear_cedears_sec.py
	$(PYTHON) 02_mapear_cedears_sec.py

paso3: 03_descargar_financials_sec.py
	$(PYTHON) 03_descargar_financials_sec.py

paso4: 04_descargar_precios.py
	$(PYTHON) 04_descargar_precios.py

paso5: 05_calcular_ratios.py
	$(PYTHON) 05_calcular_ratios.py

paso6: 06_descargar_precios_historicos.py
	$(PYTHON) 06_descargar_precios_historicos.py

paso7: 07_descargar_byma_locales.py
	$(PYTHON) 07_descargar_byma_locales.py

paso8: 08_generar_dataset_etl.py
	$(PYTHON) 08_generar_dataset_etl.py

# ── Atajos ──────────────────────────────────────────────────
dataset: paso6 paso7 paso8
	@echo "Dataset listo en data_export/"
prices: paso6
locales: paso7
etl: paso8

# ── Empaquetar ──────────────────────────────────────────────
zip:
	$(PYTHON) -c "import shutil; shutil.make_archive('data_export', 'zip', 'data_export'); print('OK data_export.zip')"

# ── Limpieza ────────────────────────────────────────────────
clean:
	rm -rf precios_historicos/ precios_historicos_errores.json
	rm -rf byma_locales* byma_locales_precios/
	rm -rf data_export/ data_export.zip
	rm -f precios_errores.json
	@echo "Outputs generados limpiados."

clean-all: clean
	rm -rf financials_sec/ financials_index.json financials_errores.json
	rm -f cedears_con_cik.json cedears_con_cik.csv cedears_sin_cik.txt
	rm -f seguimiento.csv seguimiento.json
	rm -f precios.json
	@echo "Todo limpiado."
