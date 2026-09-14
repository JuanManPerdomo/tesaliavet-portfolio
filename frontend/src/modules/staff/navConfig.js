// Estructura del sidebar del panel de personal, calcada del mockup de Admin
// (ver decisión 17/CLAUDE.md): fija cómo se ve el panel terminado, aunque
// hoy la mayoría de los items sean placeholder "Próximamente" porque su
// backend está fuera del alcance de esta fase.

// Grupos compartidos entre ADMIN_NAV y BODEGUERO_NAV - un Bodeguero ve
// exactamente lo mismo que un admin en estas 2 secciones (decision de
// alcance confirmada con Juan Manuel), asi que se arman una sola vez en vez
// de duplicar los items en los 2 arrays.
const INVENTARIO_GROUP = {
  label: 'Inventario',
  items: [
    {
      label: 'Productos',
      icon: 'package',
      to: { name: 'staff-products' },
      children: [
        { label: 'Lista de productos', to: { name: 'staff-products' } },
        { label: 'Categorías', to: { name: 'staff-categories' } },
        { label: 'Alertas de stock', to: { name: 'staff-stock-alerts' } },
      ],
    },
  ],
}

const PROVEEDORES_GROUP = {
  label: 'Proveedores',
  items: [
    { label: 'Proveedores', icon: 'truck', to: { name: 'staff-suppliers' } },
    { label: 'Órdenes de compra', icon: 'clipboard', to: { name: 'staff-purchase-orders' } },
  ],
}

const BASE_GROUP = {
  items: [
    { label: 'Inicio', icon: 'home', to: { name: 'staff-home' } },
    { label: 'Notificaciones', icon: 'bell', to: { name: 'staff-notifications' } },
  ],
}

const REPORTES_GROUP = {
  label: 'Reportes',
  items: [{ label: 'Reportes', icon: 'chart-bar', to: { name: 'staff-reports' } }],
}

export const ADMIN_NAV = [
  BASE_GROUP,
  INVENTARIO_GROUP,
  PROVEEDORES_GROUP,
  {
    label: 'Clientes y mascotas',
    items: [
      { label: 'Clientes', icon: 'users', to: { name: 'staff-clients' } },
      {
        label: 'Mascotas',
        icon: 'paw',
        to: { name: 'staff-pets' },
        children: [
          { label: 'Mascotas registradas', to: { name: 'staff-pets' } },
          { label: 'Catálogo de vacunas', to: { name: 'staff-vaccines' } },
          { label: 'Especies', to: { name: 'staff-species' } },
        ],
      },
    ],
  },
  {
    label: 'Atención veterinaria',
    items: [{ label: 'Citas', icon: 'calendar', to: { name: 'staff-appointments' } }],
  },
  {
    label: 'Ventas',
    items: [
      { label: 'Pedidos', icon: 'shopping-bag', to: { name: 'staff-orders' } },
      { label: 'Devoluciones', icon: 'arrow-back-up', to: { name: 'staff-returns' } },
      { label: 'Caja', icon: 'cash', to: { name: 'staff-cash-register' } },
    ],
  },
  REPORTES_GROUP,
  {
    items: [
      { label: 'Usuarios y roles', icon: 'user-check', to: { name: 'staff-users' } },
      { label: 'PQRS', icon: 'message-circle', to: { name: 'staff-pqrs' } },
      { label: 'Auditoría', icon: 'shield-check', to: { name: 'staff-audit' } },
    ],
  },
]

// El mockup solo cubrió Admin; el sidebar de Veterinario no tiene mockup
// propio (ver decisión 17) — se reutiliza el mismo lenguaje visual con las
// secciones que sí están en el alcance aprobado (Next Steps #1).
export const VET_NAV = [
  {
    items: [
      { label: 'Inicio', icon: 'home', to: { name: 'staff-home' } },
      { label: 'Notificaciones', icon: 'bell', to: { name: 'staff-notifications' } },
    ],
  },
  {
    label: 'Atención veterinaria',
    items: [{ label: 'Citas asignadas', icon: 'calendar', to: { name: 'staff-appointments' } }],
  },
  {
    label: 'Pacientes',
    items: [{ label: 'Mascotas', icon: 'paw', to: { name: 'staff-pets' } }],
  },
]

// Sin mockup propio (mismo criterio que VET_NAV). Bodeguero nunca ve
// Clientes/Mascotas/Citas/Usuarios/PQRS/Auditoría - fuera de su terreno.
// Ventas es un caso especial: puede vender (Pedidos + Caja, para cuando
// queda a cargo sin el admin presente) pero NO Devoluciones, mas sensible
// (decision Bodeguero ampliada, 2026-09-02) - por eso no reusa el grupo
// "Ventas" completo de ADMIN_NAV, es una version propia sin ese item.
const VENTAS_GROUP_BODEGUERO = {
  label: 'Ventas',
  items: [
    { label: 'Pedidos', icon: 'shopping-bag', to: { name: 'staff-orders' } },
    { label: 'Caja', icon: 'cash', to: { name: 'staff-cash-register' } },
  ],
}

export const BODEGUERO_NAV = [
  BASE_GROUP,
  INVENTARIO_GROUP,
  PROVEEDORES_GROUP,
  VENTAS_GROUP_BODEGUERO,
  REPORTES_GROUP,
]

const ATENCION_VETERINARIA_LABEL = 'Atención veterinaria'

export function navForRoles(roles) {
  const isAdmin = roles.includes('admin')
  const isVet = roles.includes('veterinario')
  const isBodeguero = roles.includes('bodeguero')

  if (isAdmin && isVet) {
    // Cuenta con ambos roles (decisión 16): admin ve su sidebar completo
    // ("Citas" = todas), pero se le agrega "Citas asignadas" (solo las
    // propias) para que el panel de Admin se sienta completo sin perder la
    // vista de veterinario puro. No muta ADMIN_NAV — solo un admin sin rol
    // veterinario seguiría viendo esa sección vacía siempre, así que este
    // ítem extra solo aparece cuando de verdad aplica.
    return ADMIN_NAV.map((group) =>
      group.label === ATENCION_VETERINARIA_LABEL
        ? {
            ...group,
            items: [
              ...group.items,
              { label: 'Citas asignadas', icon: 'calendar', to: { name: 'staff-appointments-mine' } },
            ],
          }
        : group
    )
  }

  // Admin ya incluye Inventario/Proveedores (los mismos grupos que
  // BODEGUERO_NAV) - un admin que además sea Bodeguero no necesita nada
  // extra, a diferencia de veterinario que sí le agrega "Citas asignadas".
  if (isAdmin) return ADMIN_NAV
  if (isVet) return VET_NAV
  if (isBodeguero) return BODEGUERO_NAV
  return []
}
