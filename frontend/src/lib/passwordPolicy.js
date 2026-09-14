// Misma politica que valida el backend (auth/routes.py,
// validate_password_strength) - aplica solo a contraseñas nuevas
// (registro/cambio/reseteo/creacion desde el panel), nunca se fuerza a
// las cuentas ya existentes a actualizar la suya.
export const PASSWORD_HINT = 'Mínimo 8 caracteres, con una mayúscula, un número y un carácter especial.'

export function validatePasswordStrength(password) {
  if (password.length < 8) return 'La contraseña debe tener al menos 8 caracteres'
  if (!/[A-Z]/.test(password)) return 'La contraseña debe incluir al menos una letra mayúscula'
  if (!/[0-9]/.test(password)) return 'La contraseña debe incluir al menos un número'
  if (!/[^A-Za-z0-9]/.test(password)) return 'La contraseña debe incluir al menos un carácter especial (ej. !@#$%)'
  return null
}
