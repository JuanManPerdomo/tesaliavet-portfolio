<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import UserFormModal from './UserFormModal.vue'
import UserEditModal from './UserEditModal.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import { useStaffUsersStore } from '../../../../stores/staffUsers'
import { useToastStore } from '../../../../stores/toast'
import { useAuthStore } from '../../../../stores/auth'

const FILTERS = [
  { value: '', label: 'Todos' },
  { value: 'cliente', label: 'Clientes' },
  { value: 'veterinario', label: 'Veterinarios' },
  { value: 'bodeguero', label: 'Bodegueros' },
  { value: 'admin', label: 'Admins' },
]

const staffUsersStore = useStaffUsersStore()
const toastStore = useToastStore()
const authStore = useAuthStore()
const activeFilter = ref('')
const search = ref('')
const perPage = ref(10)
const savingUserId = ref(null)

const showForm = ref(false)
const creating = ref(false)
const formError = ref('')

const showEditForm = ref(false)
const editingUser = ref(null)
const savingEdit = ref(false)
const editFormError = ref('')

const pendingRoleChange = ref(null)
const showRoleConfirm = ref(false)
const roleConfirmSaving = ref(false)

const deactivatingId = ref(null)
const showDeactivateConfirm = ref(false)
const deactivating = ref(false)
const activatingId = ref(null)

const deletingId = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

function load(page = 1) {
  staffUsersStore.fetchUsers({
    role: activeFilter.value || undefined,
    search: search.value || undefined,
    page,
    perPage: perPage.value,
  })
}

onMounted(async () => {
  await staffUsersStore.fetchRoles()
  load()
})

function handleSearch() {
  load(1)
}

function handlePageChange(page) {
  load(page)
}

function handlePageSizeChange(size) {
  perPage.value = size
  load(1)
}

async function handleCreateUser(payload) {
  creating.value = true
  formError.value = ''
  try {
    await staffUsersStore.createUser(payload)
    toastStore.success('Usuario creado.')
    showForm.value = false
    load()
  } catch (err) {
    formError.value = err.response?.data?.message || 'No se pudo crear el usuario.'
  } finally {
    creating.value = false
  }
}

function askEdit(user) {
  editingUser.value = user
  editFormError.value = ''
  showEditForm.value = true
}

async function handleEditUser(payload) {
  savingEdit.value = true
  editFormError.value = ''
  try {
    const updated = await staffUsersStore.updateUser(editingUser.value.id, payload)
    const user = staffUsersStore.users.find((u) => u.id === editingUser.value.id)
    if (user) Object.assign(user, updated)
    toastStore.success('Usuario actualizado.')
    showEditForm.value = false
  } catch (err) {
    editFormError.value = err.response?.data?.message || 'No se pudo editar el usuario.'
  } finally {
    savingEdit.value = false
  }
}

// Cambiar (agregar o quitar) un rol ahora pide confirmación explícita antes
// de aplicarse - pedido por Juan Manuel, 2026-09-02. El checkbox no se
// mueve solo con el click (@click.prevent en el template): el estado
// mostrado sigue reflejando user.roles hasta que se confirma de verdad.
function askToggleRole(user, roleName, checked) {
  const nextRoles = checked
    ? [...user.roles, roleName]
    : user.roles.filter((r) => r !== roleName)

  if (!checked && !nextRoles.length) {
    toastStore.error('Un usuario debe tener al menos un rol.')
    return
  }

  pendingRoleChange.value = { user, roleName, checked, nextRoles }
  showRoleConfirm.value = true
}

const roleConfirmTitle = computed(() =>
  pendingRoleChange.value?.checked ? 'Agregar rol' : 'Quitar rol'
)

const roleConfirmMessage = computed(() => {
  if (!pendingRoleChange.value) return ''
  const { user, roleName, checked } = pendingRoleChange.value
  const name = `${user.firstName} ${user.lastName}`
  return checked
    ? `¿Agregar el rol "${roleName}" a ${name}? Va a poder acceder a las secciones del panel asociadas a ese rol.`
    : `¿Quitar el rol "${roleName}" a ${name}? Va a perder acceso a las secciones del panel asociadas a ese rol.`
})

async function confirmToggleRole() {
  const { user, nextRoles } = pendingRoleChange.value
  roleConfirmSaving.value = true
  savingUserId.value = user.id
  try {
    const updated = await staffUsersStore.updateRoles(user.id, nextRoles)
    user.roles = updated.roles
    toastStore.success('Roles actualizados.')
    showRoleConfirm.value = false
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudieron actualizar los roles.')
  } finally {
    roleConfirmSaving.value = false
    savingUserId.value = null
  }
}

function askDeactivate(id) {
  deactivatingId.value = id
  showDeactivateConfirm.value = true
}

async function confirmDeactivate() {
  deactivating.value = true
  try {
    const updated = await staffUsersStore.updateStatus(deactivatingId.value, false)
    const user = staffUsersStore.users.find((u) => u.id === deactivatingId.value)
    if (user) user.isActive = updated.isActive
    toastStore.success('Usuario desactivado.')
    showDeactivateConfirm.value = false
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo desactivar el usuario.')
  } finally {
    deactivating.value = false
  }
}

async function handleActivate(id) {
  activatingId.value = id
  try {
    const updated = await staffUsersStore.updateStatus(id, true)
    const user = staffUsersStore.users.find((u) => u.id === id)
    if (user) user.isActive = updated.isActive
    toastStore.success('Usuario activado.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo activar el usuario.')
  } finally {
    activatingId.value = null
  }
}

function askDelete(id) {
  deletingId.value = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await staffUsersStore.deleteUser(deletingId.value)
    toastStore.success('Usuario eliminado permanentemente.')
    showDeleteConfirm.value = false
    load()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar el usuario.')
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Usuarios y roles</h1>
        <p class="text-sm text-slate-500">Gestiona las cuentas y los roles de acceso al sistema.</p>
      </div>
      <PrimaryButton class="gap-2" @click="showForm = true">
        <AppIcon name="plus" :size="16" />
        Nuevo usuario
      </PrimaryButton>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nombre, correo o documento..."
        class="flex-1 min-w-[220px] border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @keyup.enter="handleSearch"
      />
      <button
        class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
        @click="handleSearch"
      >
        Buscar
      </button>
    </div>

    <div class="flex gap-2 mb-5">
      <button
        v-for="f in FILTERS"
        :key="f.value"
        class="px-3.5 py-1.5 rounded-full text-xs font-semibold border transition"
        :class="
          activeFilter === f.value
            ? 'bg-emerald-700 text-white border-emerald-700'
            : 'border-slate-200 text-slate-600 hover:border-emerald-700 hover:text-emerald-700'
        "
        @click="activeFilter = f.value; load()"
      >
        {{ f.label }}
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="staffUsersStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="staffUsersStore.error" class="p-8 text-sm text-red-600">{{ staffUsersStore.error }}</div>
      <div v-else-if="!staffUsersStore.users.length" class="p-8 text-sm text-slate-500 text-center">
        No hay usuarios en este filtro.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="user in staffUsersStore.users" :key="user.id" class="p-4">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="font-semibold text-slate-800 truncate">{{ user.firstName }} {{ user.lastName }}</p>
              <p class="text-xs text-slate-400 truncate">{{ user.email }}</p>
            </div>
            <span
              class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold"
              :class="user.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            >
              {{ user.isActive ? 'Activo' : 'Inactivo' }}
            </span>
          </div>

          <div class="flex flex-wrap gap-x-4 gap-y-1.5 mt-2.5">
            <label
              v-for="role in staffUsersStore.roles"
              :key="role.id"
              class="flex items-center gap-1.5 text-xs text-slate-600"
            >
              <input
                type="checkbox"
                :checked="user.roles.includes(role.name)"
                :disabled="savingUserId === user.id"
                class="w-4 h-4 accent-emerald-700 cursor-pointer"
                @click.prevent="askToggleRole(user, role.name, !user.roles.includes(role.name))"
              />
              {{ role.name }}
            </label>
          </div>

          <div class="flex items-center gap-2 mt-3">
            <button
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-300"
              title="Editar"
              @click="askEdit(user)"
            >
              <AppIcon name="edit" :size="14" />
            </button>
            <span v-if="user.id === authStore.user?.id" class="text-xs text-slate-400 italic">
              (tu cuenta)
            </span>
            <template v-else>
            <template v-if="user.isActive">
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                title="Desactivar"
                @click="askDeactivate(user.id)"
              >
                <AppIcon name="archive" :size="14" />
              </button>
            </template>
            <template v-else>
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                title="Activar"
                :disabled="activatingId === user.id"
                @click="handleActivate(user.id)"
              >
                <AppIcon name="refresh" :size="14" />
              </button>
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                title="Eliminar permanentemente"
                @click="askDelete(user.id)"
              >
                <AppIcon name="x" :size="14" />
              </button>
            </template>
            </template>
          </div>
        </div>
      </div>

      <table v-if="staffUsersStore.users.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Usuario</th>
            <th class="px-5 py-3">Email</th>
            <th v-for="role in staffUsersStore.roles" :key="role.id" class="px-5 py-3 text-center">
              {{ role.name }}
            </th>
            <th class="px-5 py-3">Estado</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="user in staffUsersStore.users"
            :key="user.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3 font-semibold text-slate-800">{{ user.firstName }} {{ user.lastName }}</td>
            <td class="px-5 py-3 text-slate-500">{{ user.email }}</td>
            <td v-for="role in staffUsersStore.roles" :key="role.id" class="px-5 py-3 text-center">
              <input
                type="checkbox"
                :checked="user.roles.includes(role.name)"
                :disabled="savingUserId === user.id"
                class="w-4 h-4 accent-emerald-700 cursor-pointer"
                @click.prevent="askToggleRole(user, role.name, !user.roles.includes(role.name))"
              />
            </td>
            <td class="px-5 py-3">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-bold"
                :class="user.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ user.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3">
              <div class="flex justify-end items-center gap-2">
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-300"
                  title="Editar"
                  @click="askEdit(user)"
                >
                  <AppIcon name="edit" :size="14" />
                </button>
                <span v-if="user.id === authStore.user?.id" class="text-xs text-slate-400 italic">
                  (tu cuenta)
                </span>
                <template v-else>
                  <template v-if="user.isActive">
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                      title="Desactivar"
                      @click="askDeactivate(user.id)"
                    >
                      <AppIcon name="archive" :size="14" />
                    </button>
                  </template>
                  <template v-else>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                      title="Activar"
                      :disabled="activatingId === user.id"
                      @click="handleActivate(user.id)"
                    >
                      <AppIcon name="refresh" :size="14" />
                    </button>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                      title="Eliminar permanentemente"
                      @click="askDelete(user.id)"
                    >
                      <AppIcon name="x" :size="14" />
                    </button>
                  </template>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminPagination
      :pagination="staffUsersStore.pagination"
      item-label="usuarios"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />

    <UserFormModal
      :open="showForm"
      :available-roles="staffUsersStore.roles"
      :saving="creating"
      :server-error="formError"
      @close="showForm = false"
      @submit="handleCreateUser"
    />

    <UserEditModal
      :open="showEditForm"
      :user="editingUser"
      :saving="savingEdit"
      :server-error="editFormError"
      @close="showEditForm = false"
      @submit="handleEditUser"
    />

    <ConfirmDialog
      :open="showRoleConfirm"
      :title="roleConfirmTitle"
      :message="roleConfirmMessage"
      confirm-label="Sí, confirmar"
      :loading="roleConfirmSaving"
      @cancel="showRoleConfirm = false"
      @confirm="confirmToggleRole"
    />

    <ConfirmDialog
      :open="showDeactivateConfirm"
      title="Desactivar usuario"
      message="La cuenta no podrá iniciar sesión mientras esté desactivada. Podrás reactivarla cuando quieras."
      confirm-label="Sí, desactivar"
      :loading="deactivating"
      @cancel="showDeactivateConfirm = false"
      @confirm="confirmDeactivate"
    />

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar usuario permanentemente"
      message="Esta acción no se puede deshacer. Se eliminarán también todas las mascotas de este usuario junto con su historial médico, vacunas y citas. El historial médico que haya creado como personal para mascotas de otros clientes no se borra, solo pierde la autoría."
      confirm-label="Sí, eliminar para siempre"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
