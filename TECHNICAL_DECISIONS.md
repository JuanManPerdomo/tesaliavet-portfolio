# Decisiones técnicas

Selección curada de decisiones de arquitectura, bugs reales encontrados y
por qué se resolvieron como se resolvieron — tomada de la bitácora interna
del proyecto (113 decisiones registradas), con nombres, credenciales y
datos del negocio removidos. El objetivo es mostrar el tipo de problemas
reales que aparecieron construyendo esto, no una lista de features.

## Autorización por rol validada en cada request, no en el JWT

El sistema tiene roles planos (`admin`, `veterinario`, `bodeguero`,
`cliente`) sin jerarquía cableada en código — un usuario puede tener varios
roles a la vez y la tabla `roles` es simplemente datos, no un enum. Lo
importante: el backend valida el rol **contra la base de datos en cada
request** (`@role_required(...)`), no contra los claims que vengan en el
JWT. Esto significa que revocar un rol tiene efecto inmediato sin esperar a
que el usuario vuelva a loguearse — el costo es una consulta extra por
request, aceptado a propósito por la garantía de seguridad que da. El
frontend sí cachea los roles del login para decidir qué mostrar en el
sidebar (nunca para autorizar nada), así que un cambio de rol requiere
volver a entrar solo para que la UI se refresque, no para que la
protección real funcione.

Cuando se agregó un rol nuevo meses después (bodeguero, con acceso a
inventario/proveedores/caja pero no a clientes/mascotas/citas), no hizo
falta ninguna migración ni tocar la lógica de permisos existente — solo
insertar la fila en `roles` y agregar el nombre del rol a los decoradores
de los endpoints correspondientes.

## Incidente real de migración: FK contra columnas unsigned

Al crear la primera tabla nueva (con FK contra el esquema existente), el
`CREATE TABLE` falló con `Foreign key constraint is incorrectly formed`.
Causa: todas las columnas `BIGINT` del esquema real eran `bigint(20)
unsigned`, pero `sa.BigInteger()` de SQLAlchemy genera `signed` por
defecto — un FK contra un tipo distinto (signed vs. unsigned) es inválido
en MySQL. Hacía falta `mysql.BIGINT(unsigned=True)` explícito.

Lo más caro no fue el error en sí, sino lo que pasó al deshacerlo: como la
migración fallida nunca había avanzado el marcador de versión de Alembic,
un `flask db downgrade` retrocedió **un paso más de lo esperado** y
ejecutó el downgrade de la migración *anterior*, borrando de verdad
columnas y datos que ya estaban en producción. MySQL no es transaccional
para DDL, así que ese downgrade sí se aplicó. Se corrigió la migración con
el tipo unsigned explícito y se restauró el dato a mano — pero la lección
quedó como regla del proyecto: antes de un `downgrade` sobre una
migración a medias, revisar qué DDL ya se aplicó de verdad, no asumir que
solo retrocede un paso.

## Auditoría con diff campo-por-campo, sin depender del historial interno de SQLAlchemy

El primer intento de mostrar "qué cambió, de qué valor a cuál" en cada
edición usó `inspect(obj).attrs[campo].history` de SQLAlchemy — parecía
suficiente sin tocar cada endpoint. En la verificación, el diff salía
vacío en varios casos aunque los valores sí habían cambiado: cualquier
query intermedia entre aplicar los cambios y armar el diff (una
validación de unicidad, una sincronización de alertas de stock) dispara
un autoflush que resetea ese historial.

Se resolvió con un snapshot manual propio: copiar los valores de las
columnas justo después de cargar el objeto, y compararlos contra el
estado final justo antes de guardar el log — sin depender de cuántas
queries intermedias haya. La función es genérica (itera las columnas
mapeadas del modelo), así que se reutiliza igual en cualquier endpoint sin
duplicar lógica, con exclusiones automáticas para columnas de archivos y
hashes de contraseña.

## Caja física: turno único, responsabilidad no delegable

El módulo de caja simula una caja física real: apertura con un monto base,
un solo turno abierto a la vez para toda la tienda, y cierre con cuadre
(efectivo esperado vs. contado, con justificación obligatoria ante
cualquier diferencia). Dos decisiones de seguridad que valió la pena
endurecer después de la primera versión:

- El responsable del turno es **siempre** quien lo abre — el backend
  ignora cualquier intento de asignarlo a otra persona en el payload,
  aunque se mande a mano en la request.
- Cerrar un turno solo lo puede hacer quien lo abrió, o un administrador
  como respaldo — no cualquier cuenta con acceso al módulo.

Mientras no hay turno abierto, registrar un pago o una devolución queda
bloqueado con un aviso explícito, en vez de fallar silenciosamente o
dejar el dinero sin turno asociado.

## Sidebar responsive: un bug de layout, no de CSS

Al hacer responsive el panel administrativo, el menú lateral en mobile
(un cajón que entra desde la izquierda) se quedaba invisible fuera de
pantalla aunque la clase de posición estuviera aplicada correctamente —
verificado exhaustivamente que la clase, la regla CSS y el valor
computado eran todos correctos. La causa real: el elemento con
`position: fixed` era hijo directo de un contenedor `flex`, y el
navegador no recalculaba su layout de forma confiable tras el cambio de
posición en esa combinación específica.

La solución no fue seguir ajustando clases, sino sacar el elemento del
árbol flex con `<Teleport to="body">` — activo solo en mobile, desactivado
en escritorio donde el elemento vuelve a su lugar normal como item flex.
Quedó como regla general del proyecto: un elemento `fixed` que es a la vez
hijo de un flex container es sospechoso de este bug antes que de un error
de CSS.

## Curvas de gráfico sin sobrepaso, con datos reales dispersos

El dashboard dibuja sus gráficas de ingresos a mano en SVG (sin librería
de charts). La primera versión de curvas suaves usó una variante estándar
de Catmull-Rom — con datos reales de un negocio pequeño (casi todo en
cero, con picos aislados) la curva se pasaba por debajo de la línea base
entre dos puntos con pendientes muy distintas, un "overshoot" visible y
engañoso.

Se resolvió implementando el algoritmo completo de interpolación monótona
de Fritsch-Carlson (no solo el primer paso, que alcanza para un pico
aislado pero no para dos tramos consecutivos con pendientes dispares) —
limita las tangentes de cada segmento en función de la pendiente real,
garantizando matemáticamente cero sobrepaso sin importar el patrón de los
datos. Verificado muestreando cientos de puntos de la curva ya renderizada
en el navegador, no solo revisando los comandos del `path` (que incluyen
puntos de control y no reflejan la curva visual real).

## Autoplay de carrusel sin confiar en el estado interno de la librería

Un carrusel con autoplay y loop mostraba indicadores ("01/02/03") que a
veces no coincidían con la imagen realmente visible en pantalla —
verificado comparando el índice que la librería reportaba como activo
contra qué elemento estaba físicamente encima en ese punto de la pantalla,
la única forma confiable de confirmarlo. La librería desincronizaba su
propio índice interno del DOM real bajo loop + autoplay combinados.

Se resolvió quitando el autoplay y el loop de la librería por completo:
un `setInterval` propio controla el avance llamando al método de
navegación directo por índice, y el estado "cuál slide está activo" vive
en el estado de la aplicación, nunca leído de la librería.

## Recibos/PDFs exportables con gráficas reales, no simuladas

Los reportes exportables empezaron siendo tabulares (título + KPIs de
texto + una tabla) — no intentaban replicar las gráficas SVG que sí se ven
en pantalla. Se rediseñaron para incluir gráficas vectoriales reales
dentro del PDF, con la misma librería de generación ya en uso (sin sumar
ninguna dependencia nueva). Dos bugs reales aparecieron recién con datos
reales largos: nombres de producto/cliente que se superponían en el eje
de categorías (se truncan con elipsis), y "&"/"<" en un nombre real que
rompía el render porque el motor de PDF interpreta ese texto como XML
liviano (se escapa explícitamente en todo texto interpolado).

## Política de "no reservar stock" con freno explícito, no bloqueo

El stock se descuenta al confirmar el pago, no al crear el pedido —
significa que dos clientes pueden comprar el mismo producto con stock
limitado antes de que ninguno de los dos pague. Se evaluó reservar stock
en el checkout y se descartó a propósito para el volumen real del
negocio: la complejidad de reservar/liberar stock no se justificaba
todavía. El único freno real es que el descuento nunca baja de cero —
preferible dejar el stock en 0 (y generar la alerta correspondiente) antes
que rechazar un pago ya confirmado en caja por una carrera de stock poco
probable.

## Patrón de borrado en dos pasos, repetido de forma consistente

Para cualquier entidad de inventario propio del negocio (productos,
proveedores, categorías), el borrado permanente solo está disponible
sobre un registro ya desactivado — "Eliminar" siempre exige "Desactivar"
primero. Para entidades que pertenecen al usuario (una cuenta con sus
mascotas), borrar sí hace cascada real sobre lo que le pertenece; para
personal que solo *autoró* un registro ajeno (un historial médico escrito
por un veterinario, por ejemplo), borrar la cuenta nunca borra ese
registro — solo pierde la autoría, aprovechando que esas relaciones ya
estaban diseñadas en el esquema como `SET NULL` en vez de `CASCADE`.

## Cierre de sesión por inactividad, sin backend involucrado

El sistema no tiene invalidación de tokens del lado del servidor (sin
blacklist), así que el cierre de sesión siempre fue una operación 100%
del cliente. El requisito de "cerrar sesión tras inactividad" se resolvió
completo en el frontend: un listener throttleado de eventos de
interacción, un aviso previo con cuenta regresiva antes del cierre real
(para que "seguir conectado" sea una decisión explícita del usuario, no
un efecto secundario de un movimiento de mouse accidental), y reuso
directo de la misma función de logout que ya usa el cierre de sesión
manual.
