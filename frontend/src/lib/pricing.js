// Margen bruto = (precio de venta - precio de compra) / precio de venta * 100
// (margen sobre precio de venta, definicion estandar de retail).
export function calcMargin(purchasePrice, sellingPrice) {
  const purchase = Number(purchasePrice) || 0
  const selling = Number(sellingPrice) || 0
  if (selling <= 0) return { amount: 0, percent: 0 }
  const amount = selling - purchase
  const percent = (amount / selling) * 100
  return { amount, percent }
}

export function formatCOP(value) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(value || 0)
}

// Version compacta para tooltips/espacios chicos: "847000" -> "$847k",
// "5280000" -> "$5.3M".
export function formatCompactCOP(value) {
  const num = Number(value) || 0
  const abs = Math.abs(num)
  if (abs >= 1_000_000) return `$${(num / 1_000_000).toFixed(1)}M`
  if (abs >= 1_000) return `$${Math.round(num / 1_000)}k`
  return formatCOP(num)
}

export const TAX_RATE_OPTIONS = [
  { value: 19, label: '19% - IVA estándar' },
  { value: 5, label: '5% - IVA reducido' },
  { value: 0, label: '0% - IVA exento' },
]

// Catalogo fijo de unidades de medida (ver decision 33 en CLAUDE.md) -
// espejo de VALID_UNITS en backend/app/products/routes.py.
export const UNIT_OPTIONS = ['Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro', 'Onza']

// Unidad "de paquete": el stock cuenta CUANTOS hay (ej. 20 Bultos), y el
// peso por unidad (si se llena) multiplica para mostrar el total en kg.
// Las demas (Kg/Gramo/Arroba/Litro/Mililitro/Onza) son unidad "de medida
// total": el stock YA es la cantidad completa, nunca se multiplica (decision
// 33/84 en CLAUDE.md) - confundir las dos es un error real que ya paso dos
// veces con datos reales del catalogo (Agility Gold con Kg, Hills con Onza).
export const PACKAGE_UNITS = ['Unidad', 'Bulto', 'Caja']

// "2 Bultos" o, si el producto tiene peso por unidad, "2 Bultos (= 4 kg)".
export function formatQuantity(quantity, unitLabel, unitWeightKg) {
  const qty = Number(quantity) || 0
  const label = unitLabel || 'Unidad'
  const base = `${qty} ${label}`
  if (!unitWeightKg) return base
  const totalKg = qty * Number(unitWeightKg)
  return `${base} (= ${totalKg.toLocaleString('es-CO', { maximumFractionDigits: 2 })} kg)`
}
