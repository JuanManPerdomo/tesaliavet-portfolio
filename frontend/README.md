# TesaliaVet — Frontend

Cliente web de la plataforma de Agroveterinaria Tesalia (Tesalia, Huila): catálogo de
productos, autenticación de clientes, PQRS, gestión de mascotas y citas veterinarias, y
panel de personal (admin/veterinario).

Ver [`CLAUDE.md`](../CLAUDE.md) en la raíz del repo para el estado del proyecto,
decisiones técnicas y próximos pasos.

## Stack

Vue 3 (`<script setup>`) + Vite, Vue Router, Pinia, Tailwind 4, Swiper, axios.

## Levantar el proyecto

Requiere el backend corriendo en paralelo (ver "Cómo levantar el proyecto" en
`../CLAUDE.md`).

```bash
npm install
npm run dev
```

Sirve en `http://localhost:5173`.

### Variables de entorno

Crear `frontend/.env` (no está versionado):

```
VITE_API_URL=http://127.0.0.1:5000/api
```

## Scripts

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo con hot-reload |
| `npm run build` | Build de producción |
| `npm run preview` | Sirve el build de producción localmente |
| `npm run lint` | ESLint (falla si hay warnings) |
| `npm run lint:fix` | ESLint con `--fix` |
| `npm run format` | Prettier sobre todo el proyecto |

## Convenciones del proyecto

- Módulos por audiencia en `src/modules/`: `public` (visitantes), `client` (requiere
  sesión), `staff` (requiere rol `admin`/`veterinario`), `auth` (login/registro).
- Iconos propios en `src/components/ui/icons.js` + `AppIcon.vue` — no se usan librerías
  de iconos externas (ver decisión 2 en `CLAUDE.md`).
- Sin comentarios de más: el código se explica solo salvo que haya una razón no obvia
  detrás (un bug ya resuelto, una regla de negocio real, una limitación externa).
