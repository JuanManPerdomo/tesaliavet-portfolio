function pad(n) {
  return String(n).padStart(2, '0')
}

export function toISO(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

// Los mismos 4 atajos que ofrece ReportDateFilter.vue - centralizados aca
// para que el componente y las pantallas que lo usan (para precargar el
// rango por defecto) calculen exactamente lo mismo.
export function getPresetRange(preset) {
  const now = new Date()
  let from = now
  const to = now
  if (preset === 'semana') {
    const dayOfWeek = now.getDay() || 7
    from = new Date(now)
    from.setDate(now.getDate() - dayOfWeek + 1)
  } else if (preset === 'mes') {
    from = new Date(now.getFullYear(), now.getMonth(), 1)
  } else if (preset === 'anio') {
    from = new Date(now.getFullYear(), 0, 1)
  }
  return { dateFrom: toISO(from), dateTo: toISO(to) }
}
