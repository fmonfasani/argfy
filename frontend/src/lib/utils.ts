// frontend/src/lib/utils.ts - Modificar funciones de formato

export function formatNumber(value: number, withSeparator: boolean = false): string {
  if (withSeparator) {
    return new Intl.NumberFormat('es-AR').format(value)
  } else {
    // Sin separador de miles
    return value.toString()
  }
}

export function formatCurrency(value: number, currency: string = 'ARS', showSymbol: boolean = false): string {
  if (showSymbol) {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value)
  } else {
    // Solo el número sin símbolo
    return value.toFixed(2)
  }
}

export function getIndicatorDisplayValue(indicator: any, simple: boolean = false): string {
  if (simple) {
    // Formato simple sin separadores ni símbolos
    switch (indicator.indicator_type) {
      case 'dolar_blue':
      case 'dolar_oficial':
      case 'dolar_mep':
        return Math.round(indicator.value).toString()
      case 'inflacion_mensual':
        return indicator.value.toFixed(1)
      case 'reservas_bcra':
        return (indicator.value / 1000).toFixed(1)
      case 'riesgo_pais':
        return Math.round(indicator.value).toString()
      case 'merval':
        return Math.round(indicator.value).toString()
      default:
        return indicator.value.toString()
    }
  } else {
    // Formato original con símbolos
    return getIndicatorDisplayValueOriginal(indicator)
  }
}