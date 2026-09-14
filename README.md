# TesaliaVet

Plataforma web full-stack para una veterinaria: catálogo de productos, citas,
historiales clínicos, panel administrativo con roles, punto de venta, caja,
reportes y notificaciones — construida desde un diseño de base de datos
preexistente de 29 tablas hasta una aplicación completa en producción.

> **Nota:** este repositorio es la versión pública/portafolio del proyecto
> real. El repo de trabajo original es privado (contiene datos operativos del
> negocio); aquí solo está el código fuente, sin historial de commits ni
> información del negocio real. El detalle de decisiones técnicas está en
> [`TECHNICAL_DECISIONS.md`](./TECHNICAL_DECISIONS.md).

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Vue 3 + Vite, Vue Router, Pinia, Tailwind CSS, Swiper, Axios |
| Backend | Flask + SQLAlchemy + Flask-Migrate (Alembic) + Flask-JWT-Extended |
| Base de datos | MySQL |
| Reportes | ReportLab (PDF con gráficas vectoriales, CSV) |
| Calidad | ESLint + Prettier |

## Funcionalidad

**Sitio público y cliente**
- Catálogo de productos con filtros (categoría, especie, marca, precio,
  búsqueda) y paginación
- Registro/login con JWT (access + refresh token, renovación transparente)
- Carrito, checkout (efectivo o transferencia) y seguimiento de pedidos
- Gestión de mascotas (perfil, historial clínico, vacunas) y agenda de citas
  con reglas de negocio reales (horario de atención, bloqueo de almuerzo,
  cancelación con antelación mínima)
- PQRS con adjuntos, recuperación de contraseña por código de un solo uso,
  notificaciones y correos transaccionales

**Panel administrativo** (roles: admin / veterinario / encargado de bodega,
sin jerarquía cableada en código — los permisos salen de una tabla de roles)
- Inventario, categorías, proveedores y órdenes de compra
- Punto de venta presencial, caja con apertura/cierre de turno y cuadre de
  efectivo, devoluciones
- Auditoría con diff campo por campo de cada edición
- Dashboard con gráficas de ingresos (dibujadas a mano en SVG, sin librería
  de charts) y módulo de reportes exportable a PDF/CSV
- Centro de notificaciones interno y badges de pendientes por módulo

## Cómo levantar el proyecto

### Backend

```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate       |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar con tus propios valores
flask db upgrade
flask run
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

El backend requiere una base de datos MySQL con el esquema aplicado — ver
`backend/migrations/` para el historial completo de cambios de esquema.

## Estructura

```
backend/app/        # Un blueprint de Flask por dominio (products, orders,
                     # appointments, cash_register, audit, ...)
backend/migrations/  # Historial de Alembic
frontend/src/modules/  # public / client / staff — separados por audiencia
frontend/src/stores/   # Pinia, uno por dominio
```

## Licencia

MIT — ver [`LICENSE`](./LICENSE).
