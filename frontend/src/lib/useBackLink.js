import { useRouter } from 'vue-router'

/**
 * Botón "volver" inteligente para páginas a las que se llega desde varios
 * lugares (ej. Términos/Privacidad: desde el registro o desde el footer de
 * cualquier página).
 *
 * Si la página anterior real del historial coincide con `specialPath`
 * (ej. "/register"), vuelve ahí con `specialLabel`. Si no, vuelve a la
 * página anterior real (`router.back()`) — así el footer siempre regresa a
 * donde estaba el usuario, no a un destino fijo. Sin historial (ej. entrar
 * por URL directa) cae a home.
 */
export function useBackLink({ specialPath, specialLabel, specialTo, defaultLabel = 'Volver' } = {}) {
  const router = useRouter()
  const backPath = window.history.state?.back || null
  const cameFromSpecial = !!specialPath && backPath === specialPath

  const label = cameFromSpecial ? specialLabel : defaultLabel

  function goBack() {
    if (cameFromSpecial && specialTo) {
      router.push(specialTo)
    } else if (backPath) {
      router.back()
    } else {
      router.push({ name: 'home' })
    }
  }

  return { label, goBack }
}
