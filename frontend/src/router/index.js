import { createRouter, createWebHistory } from 'vue-router'

import ForgotPasswordPage from '../modules/public/pages/ForgotPasswordPage.vue'
import TermsPage from '../modules/public/pages/TermsPage.vue'
import PrivacyPage from '../modules/public/pages/PrivacyPage.vue'
import HomePage from '../modules/public/pages/HomePage.vue'
import ProductsPage from '../modules/public/pages/ProductsPage.vue'
import ProductDetailPage from '../modules/public/pages/ProductDetailPage.vue'
import AboutPage from '../modules/public/pages/AboutPage.vue'
import AnimalCarePage from '../modules/public/pages/AnimalCarePage.vue'
import ContactPage from '../modules/public/pages/ContactPage.vue'
import LoginPage from '../modules/public/pages/LoginPage.vue'
import RegisterPage from '../modules/public/pages/RegisterPage.vue'
import MyPetsPage from '../modules/client/pages/MyPetsPage.vue'
import PetFormPage from '../modules/client/pages/PetFormPage.vue'
import PetDetailPage from '../modules/client/pages/PetDetailPage.vue'
import MyAppointmentsPage from '../modules/client/pages/MyAppointmentsPage.vue'
import AppointmentCalendarPage from '../modules/client/pages/AppointmentCalendarPage.vue'
import AppointmentFormPage from '../modules/client/pages/AppointmentFormPage.vue'
import AppointmentDetailPage from '../modules/client/pages/AppointmentDetailPage.vue'
import MyOrdersPage from '../modules/client/pages/MyOrdersPage.vue'
import OrderDetailPage from '../modules/client/pages/OrderDetailPage.vue'
import CartPage from '../modules/client/pages/CartPage.vue'
import CheckoutPage from '../modules/client/pages/CheckoutPage.vue'
import NotificationsPage from '../modules/client/pages/NotificationsPage.vue'
import MyProfilePage from '../modules/client/pages/MyProfilePage.vue'
import StaffLayout from '../modules/staff/layouts/StaffLayout.vue'
import StaffHomePage from '../modules/staff/pages/StaffHomePage.vue'
import ProductListPage from '../modules/staff/pages/products/ProductListPage.vue'
import ProductFormPage from '../modules/staff/pages/products/ProductFormPage.vue'
import PqrsInboxPage from '../modules/staff/pages/pqrs/PqrsInboxPage.vue'
import PqrsDetailPage from '../modules/staff/pages/pqrs/PqrsDetailPage.vue'
import UserManagementPage from '../modules/staff/pages/users/UserManagementPage.vue'
import StaffAuditLogListPage from '../modules/staff/pages/audit/StaffAuditLogListPage.vue'
import StaffNotificationsPage from '../modules/staff/pages/notifications/StaffNotificationsPage.vue'
import StaffReportsPage from '../modules/staff/pages/reports/StaffReportsPage.vue'
import StaffAppointmentsPage from '../modules/staff/pages/appointments/StaffAppointmentsPage.vue'
import StaffAppointmentDetailPage from '../modules/staff/pages/appointments/StaffAppointmentDetailPage.vue'
import StaffOrdersPage from '../modules/staff/pages/orders/StaffOrdersPage.vue'
import StaffOrderDetailPage from '../modules/staff/pages/orders/StaffOrderDetailPage.vue'
import StaffNewSalePage from '../modules/staff/pages/orders/StaffNewSalePage.vue'
import StaffReturnsListPage from '../modules/staff/pages/returns/StaffReturnsListPage.vue'
import StaffCashRegisterPage from '../modules/staff/pages/cash-register/StaffCashRegisterPage.vue'
import StaffCashRegisterHistoryPage from '../modules/staff/pages/cash-register/StaffCashRegisterHistoryPage.vue'
import StaffCashRegisterDetailPage from '../modules/staff/pages/cash-register/StaffCashRegisterDetailPage.vue'
import AddMedicalRecordPage from '../modules/staff/pages/pets/AddMedicalRecordPage.vue'
import AddVaccinationPage from '../modules/staff/pages/pets/AddVaccinationPage.vue'
import SupplierListPage from '../modules/staff/pages/suppliers/SupplierListPage.vue'
import SupplierDetailPage from '../modules/staff/pages/suppliers/SupplierDetailPage.vue'
import PurchaseOrderListPage from '../modules/staff/pages/purchase-orders/PurchaseOrderListPage.vue'
import PurchaseOrderFormPage from '../modules/staff/pages/purchase-orders/PurchaseOrderFormPage.vue'
import PurchaseOrderDetailPage from '../modules/staff/pages/purchase-orders/PurchaseOrderDetailPage.vue'
import CategoryListPage from '../modules/staff/pages/categories/CategoryListPage.vue'
import ClientListPage from '../modules/staff/pages/clients/ClientListPage.vue'
import ClientDetailPage from '../modules/staff/pages/clients/ClientDetailPage.vue'
import StaffPetListPage from '../modules/staff/pages/pets/StaffPetListPage.vue'
import StaffPetDetailPage from '../modules/staff/pages/pets/StaffPetDetailPage.vue'
import StaffPetFormPage from '../modules/staff/pages/pets/StaffPetFormPage.vue'
import VaccineListPage from '../modules/staff/pages/vaccines/VaccineListPage.vue'
import SpeciesListPage from '../modules/staff/pages/species/SpeciesListPage.vue'
import StockAlertListPage from '../modules/staff/pages/stock-alerts/StockAlertListPage.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
  },

  {
    path: '/productos',
    name: 'products',
    component: ProductsPage,
  },

  {
    path: '/productos/:id',
    name: 'product-detail',
    component: ProductDetailPage,
  },

  {
    path: '/carrito',
    name: 'cart',
    component: CartPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/carrito/pagar',
    name: 'checkout',
    component: CheckoutPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/nosotros',
    name: 'about',
    component: AboutPage,
  },

  {
    path: '/cuidado-animal',
    name: 'animal-care',
    component: AnimalCarePage,
  },

  {
    path: '/contacto',
    name: 'contact',
    component: ContactPage,
  },

  {
    path: '/login',
    name: 'login',
    component: LoginPage,
  },

  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
  },

  {
    path: '/terminos',
    name: 'terms',
    component: TermsPage,
  },

  {
    path: '/privacidad',
    name: 'privacy',
    component: PrivacyPage,
  },

  {
    path: '/olvide-contrasena',
    name: 'forgot-password',
    component: ForgotPasswordPage,
  },

  {
    path: '/mis-mascotas',
    name: 'my-pets',
    component: MyPetsPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-mascotas/nueva',
    name: 'pet-new',
    component: PetFormPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-mascotas/:id/editar',
    name: 'pet-edit',
    component: PetFormPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-mascotas/:id',
    name: 'pet-detail',
    component: PetDetailPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-citas',
    name: 'my-appointments',
    component: MyAppointmentsPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-citas/agendar',
    name: 'appointment-calendar',
    component: AppointmentCalendarPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-citas/nueva',
    name: 'appointment-new',
    component: AppointmentFormPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-citas/:id',
    name: 'appointment-detail',
    component: AppointmentDetailPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-pedidos',
    name: 'my-orders',
    component: MyOrdersPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mis-pedidos/:id',
    name: 'order-detail',
    component: OrderDetailPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/notificaciones',
    name: 'notifications',
    component: NotificationsPage,
    meta: { requiresAuth: true },
  },

  {
    path: '/mi-perfil',
    name: 'my-profile',
    component: MyProfilePage,
    meta: { requiresAuth: true },
  },

  {
    path: '/panel',
    component: StaffLayout,
    meta: { requiresAuth: true, requiresRole: ['admin', 'veterinario', 'bodeguero'] },
    children: [
      {
        path: '',
        name: 'staff-home',
        component: StaffHomePage,
      },
      {
        path: 'notificaciones',
        name: 'staff-notifications',
        component: StaffNotificationsPage,
      },
      {
        path: 'productos',
        name: 'staff-products',
        component: ProductListPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'productos/nuevo',
        name: 'staff-product-new',
        component: ProductFormPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'productos/:id/editar',
        name: 'staff-product-edit',
        component: ProductFormPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'clientes',
        name: 'staff-clients',
        component: ClientListPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'clientes/:id',
        name: 'staff-client-detail',
        component: ClientDetailPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'mascotas',
        name: 'staff-pets',
        component: StaffPetListPage,
        meta: { requiresRole: ['admin', 'veterinario'] },
      },
      {
        path: 'mascotas/:id',
        name: 'staff-pet-detail',
        component: StaffPetDetailPage,
        meta: { requiresRole: ['admin', 'veterinario'] },
      },
      {
        path: 'mascotas/:id/editar',
        name: 'staff-pet-edit',
        component: StaffPetFormPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'mascotas/vacunas',
        name: 'staff-vaccines',
        component: VaccineListPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'mascotas/especies',
        name: 'staff-species',
        component: SpeciesListPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'alertas-stock',
        name: 'staff-stock-alerts',
        component: StockAlertListPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'categorias',
        name: 'staff-categories',
        component: CategoryListPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'proveedores',
        name: 'staff-suppliers',
        component: SupplierListPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'proveedores/:id',
        name: 'staff-supplier-detail',
        component: SupplierDetailPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'ordenes-compra',
        name: 'staff-purchase-orders',
        component: PurchaseOrderListPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'ordenes-compra/nueva',
        name: 'staff-purchase-order-new',
        component: PurchaseOrderFormPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'ordenes-compra/:id',
        name: 'staff-purchase-order-detail',
        component: PurchaseOrderDetailPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'ordenes-compra/:id/editar',
        name: 'staff-purchase-order-edit',
        component: PurchaseOrderFormPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'pedidos',
        name: 'staff-orders',
        component: StaffOrdersPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'pedidos/nueva',
        name: 'staff-new-sale',
        component: StaffNewSalePage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'pedidos/:id',
        name: 'staff-order-detail',
        component: StaffOrderDetailPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'devoluciones',
        name: 'staff-returns',
        component: StaffReturnsListPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'caja',
        name: 'staff-cash-register',
        component: StaffCashRegisterPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'caja/historial',
        name: 'staff-cash-register-history',
        component: StaffCashRegisterHistoryPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'caja/historial/:id',
        name: 'staff-cash-register-detail',
        component: StaffCashRegisterDetailPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'pqrs',
        name: 'staff-pqrs',
        component: PqrsInboxPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'pqrs/:id',
        name: 'staff-pqrs-detail',
        component: PqrsDetailPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'usuarios',
        name: 'staff-users',
        component: UserManagementPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'auditoria',
        name: 'staff-audit',
        component: StaffAuditLogListPage,
        meta: { requiresRole: ['admin'] },
      },
      {
        path: 'reportes',
        name: 'staff-reports',
        component: StaffReportsPage,
        meta: { requiresRole: ['admin', 'bodeguero'] },
      },
      {
        path: 'citas',
        name: 'staff-appointments',
        component: StaffAppointmentsPage,
      },
      {
        path: 'citas/asignadas',
        name: 'staff-appointments-mine',
        component: StaffAppointmentsPage,
      },
      {
        path: 'citas/:id',
        name: 'staff-appointment-detail',
        component: StaffAppointmentDetailPage,
      },
      {
        path: 'mascotas/:petId/historial/nuevo',
        name: 'staff-medical-record-new',
        component: AddMedicalRecordPage,
      },
      {
        path: 'mascotas/:petId/vacunas/nueva',
        name: 'staff-vaccination-new',
        component: AddVaccinationPage,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Al navegar a una pantalla nueva siempre arranca arriba; al usar
    // atrás/adelante del navegador respeta la posición donde estaba.
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth || to.meta.requiresRole) {
    const authStore = useAuthStore()
    if (!authStore.user) {
      return { name: 'login' }
    }
  }

  if (to.meta.requiresRole) {
    const authStore = useAuthStore()
    const allowedRoles = Array.isArray(to.meta.requiresRole)
      ? to.meta.requiresRole
      : [to.meta.requiresRole]
    if (!authStore.hasRole(...allowedRoles)) {
      return { name: 'home' }
    }
  }
})

export default router
