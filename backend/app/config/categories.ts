export const CATEGORIES: Record<string, Category> = {
  economia: {
    id: 'economia',
    title: '📊 Datos Económicos',
    description: 'IPC, PBI, desempleo, reservas, política monetaria y FX.',
    icon: '📊',
    indicators: ['ipc', 'pbi', 'emae', 'desempleo', 'reservas_bcra', 'dolar_blue'],
    color: 'blue'
  },
  gobierno: {
    id: 'gobierno', 
    title: '🏛️ Datos de Gobierno',
    description: 'Resultado fiscal, deuda pública, gasto gubernamental.',
    icon: '🏛️',
    indicators: ['resultado_fiscal', 'deuda_publica', 'gasto_publico', 'ingresos_tributarios', 'empleo_publico', 'transferencias_sociales'],
    color: 'purple'
  },
  finanzas: {
    id: 'finanzas',
    title: '🏦 Datos Financieros y Bancos', 
    description: 'Plazos fijos, tasas de crédito, depósitos, liquidez bancaria.',
    icon: '🏦',
    indicators: ['plazo_fijo_30', 'tasa_tarjeta_credito', 'depositos_privados', 'prestamos_sector_privado', 'morosidad_bancaria', 'liquidez_bancaria'],
    color: 'green'
  },
  mercados: {
    id: 'mercados',
    title: '📈 Datos de Mercados',
    description: 'MERVAL, bonos, acciones, CEDEARs, panel BYMA.',
    icon: '📈', 
    indicators: ['merval', 'rendimiento_al30', 'precio_gd30', 'volumen_acciones_cedears', 'dolar_ccl', 'panel_general_byma'],
    color: 'indigo'
  },
  tecnologia: {
    id: 'tecnologia',
    title: '💻 Tecnología y Software',
    description: 'Exportaciones SBC, empleo IT, inversión I+D, startups.',
    icon: '💻',
    indicators: ['exportaciones_sbc', 'empleo_it', 'inversion_id', 'penetracion_internet', 'vc_startups', 'facturacion_software'],
    color: 'cyan'
  },
  industria: {
    id: 'industria', 
    title: '🏭 Datos de Industria',
    description: 'IPI manufacturero, PMI, producción automotriz, acero.',
    icon: '🏭',
    indicators: ['ipi_manufacturero', 'pmi', 'produccion_automotriz', 'exportaciones_moi', 'produccion_acero', 'costo_construccion'],
    color: 'orange'
  }
}

export const COLOR_SCHEMES = {
  blue: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-900 dark:text-blue-100',
    accent: 'text-blue-600 dark:text-blue-400',
    button: 'bg-blue-600 hover:bg-blue-700'
  },
  purple: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    border: 'border-purple-200 dark:border-purple-800', 
    text: 'text-purple-900 dark:text-purple-100',
    accent: 'text-purple-600 dark:text-purple-400',
    button: 'bg-purple-600 hover:bg-purple-700'
  },
  green: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    border: 'border-green-200 dark:border-green-800',
    text: 'text-green-900 dark:text-green-100', 
    accent: 'text-green-600 dark:text-green-400',
    button: 'bg-green-600 hover:bg-green-700'
  },
  indigo: {
    bg: 'bg-indigo-50 dark:bg-indigo-900/20',
    border: 'border-indigo-200 dark:border-indigo-800',
    text: 'text-indigo-900 dark:text-indigo-100',
    accent: 'text-indigo-600 dark:text-indigo-400', 
    button: 'bg-indigo-600 hover:bg-indigo-700'
  },
  cyan: {
    bg: 'bg-cyan-50 dark:bg-cyan-900/20',
    border: 'border-cyan-200 dark:border-cyan-800',
    text: 'text-cyan-900 dark:text-cyan-100',
    accent: 'text-cyan-600 dark:text-cyan-400',
    button: 'bg-cyan-600 hover:bg-cyan-700'
  },
  orange: {
    bg: 'bg-orange-50 dark:bg-orange-900/20', 
    border: 'border-orange-200 dark:border-orange-800',
    text: 'text-orange-900 dark:text-orange-100',
    accent: 'text-orange-600 dark:text-orange-400',
    button: 'bg-orange-600 hover:bg-orange-700'
  }
}