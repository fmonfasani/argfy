# backend/app/config/indicators_mapping.py
"""
Mapeo completo de todos los indicadores del demo HTML a fuentes de datos reales
"""

# SECCIÓN 1: DATOS ECONÓMICOS
ECONOMIC_INDICATORS = {
    "ipc": {
        "name": "IPC (Inflación)",
        "description": "Índice de Precios al Consumidor mensual",
        "source": "INDEC",
        "api": "https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "inflation"
    },
    "pbi": {
        "name": "PBI",
        "description": "Producto Bruto Interno",
        "source": "INDEC", 
        "api": "https://apis.datos.gob.ar/series/api/series/?ids=143.3_NO_PR_2004_A_21",
        "frequency": "quarterly",
        "unit": "percentage",
        "category": "growth"
    },
    "emae": {
        "name": "EMAE",
        "description": "Estimador Mensual de Actividad Económica",
        "source": "INDEC",
        "api": "https://apis.datos.gob.ar/series/api/series/?ids=143.3_NO_PR_2004_A_21",
        "frequency": "monthly",
        "unit": "index",
        "category": "activity"
    },
    "desempleo": {
        "name": "Desempleo",
        "description": "Tasa de desempleo",
        "source": "INDEC",
        "api": "https://apis.datos.gob.ar/series/api/series/?ids=148.3_TASDESRED_NOAG_D_22_36",
        "frequency": "quarterly",
        "unit": "percentage",
        "category": "employment"
    },
    "reservas_bcra": {
        "name": "Reservas BCRA",
        "description": "Reservas internacionales",
        "source": "BCRA",
        "api": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias/1",
        "frequency": "daily",
        "unit": "usd_millions",
        "category": "monetary"
    },
    "dolar_blue": {
        "name": "Dólar Blue",
        "description": "Cotización mercado paralelo",
        "source": "BLUELYTICS",
        "api": "https://api.bluelytics.com.ar/v2/latest",
        "frequency": "real_time",
        "unit": "ars",
        "category": "exchange"
    }
}

# SECCIÓN 2: DATOS DE GOBIERNO  
GOVERNMENT_INDICATORS = {
    "resultado_fiscal": {
        "name": "Resultado Fiscal Primario",
        "description": "Balance fiscal primario",
        "source": "MECON",
        "api": "scraping_mecon",
        "frequency": "monthly",
        "unit": "percentage_gdp",
        "category": "fiscal"
    },
    "deuda_publica": {
        "name": "Deuda Pública",
        "description": "Deuda pública sobre PBI",
        "source": "MECON",
        "api": "scraping_mecon",
        "frequency": "quarterly",
        "unit": "percentage_gdp",
        "category": "debt"
    },
    "gasto_publico": {
        "name": "Gasto Público Total",
        "description": "Gasto público total",
        "source": "MECON",
        "api": "scraping_mecon",
        "frequency": "monthly",
        "unit": "percentage_gdp",
        "category": "spending"
    },
    "ingresos_tributarios": {
        "name": "Ingresos Tributarios",
        "description": "Ingresos tributarios",
        "source": "AFIP",
        "api": "scraping_afip",
        "frequency": "monthly",
        "unit": "percentage_gdp",
        "category": "revenue"
    },
    "empleo_publico": {
        "name": "Empleo Público",
        "description": "Empleados públicos",
        "source": "INDEC",
        "api": "manual_update",
        "frequency": "quarterly",
        "unit": "thousands",
        "category": "employment"
    },
    "transferencias_sociales": {
        "name": "Transferencias Sociales",
        "description": "Transferencias sociales",
        "source": "ANSES",
        "api": "scraping_anses",
        "frequency": "monthly",
        "unit": "percentage_gdp",
        "category": "social"
    }
}

# SECCIÓN 3: DATOS FINANCIEROS Y BANCOS
FINANCIAL_INDICATORS = {
    "plazo_fijo_30": {
        "name": "Plazo Fijo 30 días",
        "description": "Tasa nominal anual promedio",
        "source": "BCRA",
        "api": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias/29",
        "frequency": "daily",
        "unit": "percentage",
        "category": "rates"
    },
    "tasa_tarjeta_credito": {
        "name": "Tasa Tarjeta de Crédito",
        "description": "Tasa efectiva anual",
        "source": "BCRA",
        "api": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias/31",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "rates"
    },
    "depositos_privados": {
        "name": "Depósitos Privados",
        "description": "Depósitos del sector privado",
        "source": "BCRA",
        "api": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias/18",
        "frequency": "daily",
        "unit": "ars_billions",
        "category": "deposits"
    },
    "prestamos_sector_privado": {
        "name": "Préstamos Sector Privado",
        "description": "Préstamos al sector privado",
        "source": "BCRA", 
        "api": "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias/19",
        "frequency": "daily",
        "unit": "ars_billions",
        "category": "credit"
    },
    "morosidad_bancaria": {
        "name": "Morosidad Bancaria",
        "description": "Cartera irregular",
        "source": "BCRA",
        "api": "scraping_bcra_morosidad",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "risk"
    },
    "liquidez_bancaria": {
        "name": "Liquidez Bancaria",
        "description": "Ratio de liquidez",
        "source": "BCRA",
        "api": "scraping_bcra_liquidez",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "liquidity"
    }
}

# SECCIÓN 4: DATOS DE MERCADOS
MARKET_INDICATORS = {
    "merval": {
        "name": "S&P Merval",
        "description": "Índice bursátil principal",
        "source": "BYMA",
        "api": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/index",
        "frequency": "real_time",
        "unit": "index",
        "category": "equity"
    },
    "rendimiento_al30": {
        "name": "Rendimiento AL30",
        "description": "TIR del bono AL30",
        "source": "BYMA",
        "api": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/bond",
        "frequency": "daily",
        "unit": "percentage",
        "category": "bonds"
    },
    "precio_gd30": {
        "name": "Precio GD30",
        "description": "Cotización del bono GD30",
        "source": "BYMA",
        "api": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/bond",
        "frequency": "daily",
        "unit": "ars",
        "category": "bonds"
    },
    "volumen_acciones_cedears": {
        "name": "Volumen Acciones + CEDEARs",
        "description": "Volumen diario operado",
        "source": "BYMA",
        "api": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/equity",
        "frequency": "daily",
        "unit": "ars_billions",
        "category": "volume"
    },
    "dolar_ccl": {
        "name": "Dólar CCL",
        "description": "Contado con liquidación",
        "source": "BYMA",
        "api": "calculated_from_al30",
        "frequency": "real_time",
        "unit": "ars",
        "category": "exchange"
    },
    "panel_general_byma": {
        "name": "Panel General BYMA",
        "description": "Especies listadas",
        "source": "BYMA",
        "api": "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/",
        "frequency": "daily",
        "unit": "count",
        "category": "market_stats"
    }
}

# SECCIÓN 5: TECNOLOGÍA Y SOFTWARE
TECH_INDICATORS = {
    "exportaciones_sbc": {
        "name": "Exportaciones SBC",
        "description": "Servicios basados en conocimiento",
        "source": "INDEC",
        "api": "manual_quarterly",
        "frequency": "quarterly",
        "unit": "usd_billions",
        "category": "exports"
    },
    "empleo_it": {
        "name": "Empleo IT",
        "description": "Crecimiento del empleo IT",
        "source": "CESSI",
        "api": "manual_update",
        "frequency": "yearly",
        "unit": "percentage",
        "category": "employment"
    },
    "inversion_id": {
        "name": "Inversión I+D",
        "description": "Inversión en investigación y desarrollo",
        "source": "MINCYT",
        "api": "manual_update",
        "frequency": "yearly",
        "unit": "percentage_gdp",
        "category": "innovation"
    },
    "penetracion_internet": {
        "name": "Penetración de Internet",
        "description": "Hogares con acceso a internet",
        "source": "ENACOM",
        "api": "scraping_enacom",
        "frequency": "quarterly",
        "unit": "percentage",
        "category": "connectivity"
    },
    "vc_startups": {
        "name": "VC en Startups",
        "description": "Inversión venture capital",
        "source": "LAVCA",
        "api": "manual_update",
        "frequency": "yearly",
        "unit": "usd_millions",
        "category": "investment"
    },
    "facturacion_software": {
        "name": "Facturación Software",
        "description": "Facturación del sector software",
        "source": "CESSI",
        "api": "manual_update",
        "frequency": "yearly",
        "unit": "usd_billions",
        "category": "revenue"
    }
}

# SECCIÓN 6: DATOS DE INDUSTRIA
INDUSTRY_INDICATORS = {
    "ipi_manufacturero": {
        "name": "IPI Manufacturero",
        "description": "Índice de producción industrial",
        "source": "INDEC",
        "api": "https://apis.datos.gob.ar/series/api/series/?ids=11.3_VMATOTAL_2004_M_22",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "production"
    },
    "pmi": {
        "name": "PMI Manufacturero", 
        "description": "Índice de gerentes de compras",
        "source": "CIPPES",
        "api": "scraping_cippes",
        "frequency": "monthly",
        "unit": "index",
        "category": "sentiment"
    },
    "produccion_automotriz": {
        "name": "Producción Automotriz",
        "description": "Unidades producidas",
        "source": "ADEFA",
        "api": "scraping_adefa",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "automotive"
    },
    "exportaciones_moi": {
        "name": "Exportaciones MOI",
        "description": "Manufacturas de origen industrial",
        "source": "INDEC",
        "api": "manual_monthly",
        "frequency": "monthly",
        "unit": "usd_billions",
        "category": "exports"
    },
    "produccion_acero": {
        "name": "Producción de Acero",
        "description": "Producción siderúrgica",
        "source": "CAA",
        "api": "scraping_caa",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "steel"
    },
    "costo_construccion": {
        "name": "Costo de la Construcción",
        "description": "Índice de costos de construcción",
        "source": "INDEC",
        "api": "https://apis.datos.gob.ar/series/api/series/?ids=115.1_ICC_2004_M_16",
        "frequency": "monthly",
        "unit": "percentage",
        "category": "construction"
    }
}

# COMPILACIÓN DE TODOS LOS INDICADORES
ALL_INDICATORS = {
    **ECONOMIC_INDICATORS,
    **GOVERNMENT_INDICATORS, 
    **FINANCIAL_INDICATORS,
    **MARKET_INDICATORS,
    **TECH_INDICATORS,
    **INDUSTRY_INDICATORS
}

# CATEGORÍAS PARA NAVEGACIÓN
CATEGORIES = {
    "economia": {
        "title": "📊 Datos Económicos",
        "description": "IPC, PBI, desempleo, reservas, política monetaria y FX.",
        "indicators": list(ECONOMIC_INDICATORS.keys())
    },
    "gobierno": {
        "title": "🏛️ Datos de Gobierno", 
        "description": "Resultado fiscal, deuda pública, gasto gubernamental.",
        "indicators": list(GOVERNMENT_INDICATORS.keys())
    },
    "finanzas": {
        "title": "🏦 Datos Financieros y Bancos",
        "description": "Plazos fijos, tasas de crédito, depósitos, liquidez bancaria.",
        "indicators": list(FINANCIAL_INDICATORS.keys())
    },
    "mercados": {
        "title": "📈 Datos de Mercados",
        "description": "MERVAL, bonos, acciones, CEDEARs, panel BYMA.",
        "indicators": list(MARKET_INDICATORS.keys())
    },
    "tecnologia": {
        "title": "💻 Tecnología y Software",
        "description": "Exportaciones SBC, empleo IT, inversión I+D, startups.",
        "indicators": list(TECH_INDICATORS.keys())
    },
    "industria": {
        "title": "🏭 Datos de Industria",
        "description": "IPI manufacturero, PMI, producción automotriz, acero.",
        "indicators": list(INDUSTRY_INDICATORS.keys())
    }
}

# PRIORIDADES DE IMPLEMENTACIÓN (APIs más fáciles primero)
IMPLEMENTATION_PRIORITY = {
    "phase_1_immediate": [
        "reservas_bcra", "dolar_blue", "ipc", "merval", 
        "plazo_fijo_30", "emae", "ipi_manufacturero"
    ],
    "phase_2_apis": [
        "pbi", "desempleo", "depositos_privados", "prestamos_sector_privado",
        "rendimiento_al30", "precio_gd30", "costo_construccion"
    ],
    "phase_3_scraping": [
        "resultado_fiscal", "deuda_publica", "gasto_publico",
        "morosidad_bancaria", "liquidez_bancaria", "pmi"
    ],
    "phase_4_manual": [
        "empleo_publico", "exportaciones_sbc", "empleo_it",
        "inversion_id", "vc_startups", "facturacion_software"
    ]
}