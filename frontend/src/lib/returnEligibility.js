// Mismo plazo real que valida el backend (RETURN_WINDOW_DAYS en
// orders/routes.py) - se repite aca solo para decidir que mostrar, la
// validacion real siempre la hace el servidor.
export const RETURN_WINDOW_DAYS = 8

export function returnedQuantityByItem(order) {
  const totals = {}
  for (const ret of order?.returns || []) {
    for (const item of ret.items) {
      totals[item.salesOrderItemId] = (totals[item.salesOrderItemId] || 0) + item.quantity
    }
  }
  return totals
}

export function returnableItems(order) {
  const totals = returnedQuantityByItem(order)
  return (order?.items || []).map((item) => ({
    ...item,
    remaining: item.quantity - (totals[item.id] || 0),
  }))
}

export function isOrderReturnable(order) {
  if (!order || order.status !== 'Entregado' || !order.deliveredAt) return false
  const daysSinceDelivery = (Date.now() - new Date(order.deliveredAt)) / (1000 * 60 * 60 * 24)
  return daysSinceDelivery <= RETURN_WINDOW_DAYS && returnableItems(order).some((i) => i.remaining > 0)
}
