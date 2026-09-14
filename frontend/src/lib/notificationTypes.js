// Metadata (icono/colores/etiqueta) por tipo real de notificacion - una sola
// fuente compartida por el Centro de Notificaciones (StaffNotificationsPage),
// el widget "Atencion Requerida" del dashboard y el popup de "cosas
// pendientes" al entrar al panel (StaffLayout) - antes cada uno tenia su
// propia copia del mismo mapeo.
export const NOTIFICATION_TYPE_META = {
  stock: {
    icon: 'alert-triangle',
    badge: 'STOCK CRÍTICO',
    badgeClass: 'bg-red-50 text-red-600',
    iconBgClass: 'bg-red-50',
    iconColorClass: 'text-red-600',
  },
  pqrs: {
    icon: 'message-circle',
    badge: 'PQRS',
    badgeClass: 'bg-purple-50 text-purple-600',
    iconBgClass: 'bg-purple-50',
    iconColorClass: 'text-purple-600',
  },
  cita: {
    icon: 'calendar',
    badge: 'CITA PENDIENTE',
    badgeClass: 'bg-sky-50 text-sky-700',
    iconBgClass: 'bg-sky-50',
    iconColorClass: 'text-sky-700',
  },
  compra: {
    icon: 'shopping-bag',
    badge: 'NUEVA COMPRA',
    badgeClass: 'bg-emerald-50 text-emerald-700',
    iconBgClass: 'bg-emerald-50',
    iconColorClass: 'text-emerald-700',
  },
  entrega: {
    icon: 'truck',
    badge: 'PEDIDO PAGADO',
    badgeClass: 'bg-teal-50 text-teal-700',
    iconBgClass: 'bg-teal-50',
    iconColorClass: 'text-teal-700',
  },
  vacuna: {
    icon: 'droplet',
    badge: 'VACUNA',
    badgeClass: 'bg-amber-50 text-amber-700',
    iconBgClass: 'bg-amber-50',
    iconColorClass: 'text-amber-700',
  },
}
