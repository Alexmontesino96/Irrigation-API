# Irrigation System API - Documentacion

**Base URL:** `/api`
**Autenticacion:** Bearer Token (JWT) en header `Authorization: Bearer <token>`
**Content-Type:** `application/json`

---

## Respuestas de error globales

| Codigo | Descripcion | Body |
|--------|-------------|------|
| 400 | Solicitud invalida | `{"detail": "mensaje"}` |
| 401 | No autenticado / token invalido | `{"detail": "Could not validate credentials"}` |
| 403 | Acceso denegado | `{"detail": "Acceso denegado"}` |
| 404 | Recurso no encontrado | `{"detail": "Resource not found"}` |
| 422 | Error de validacion (Pydantic) | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |

## Respuesta paginada (generica)

Todos los endpoints de listado (`GET` colecciones) retornan:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "size": 20,
  "pages": 0
}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| items | array | Lista de recursos |
| total | int | Total de registros |
| page | int | Pagina actual |
| size | int | Tamaño de pagina |
| pages | int | Total de paginas |

---

# 1. Auth

Tag: `auth` | Prefix: `/api/auth`

## POST /api/auth/register

Registrar un nuevo usuario.

**Autenticacion:** No

**Request Body:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| email | string (email) | si | Email del usuario |
| password | string | si | Contraseña |
| full_name | string | si | Nombre completo |

```json
{
  "email": "tecnico@example.com",
  "password": "mi_password_seguro",
  "full_name": "Juan Perez"
}
```

**Respuesta:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "tecnico@example.com",
  "full_name": "Juan Perez",
  "is_active": true,
  "created_at": "2026-03-30T18:00:00"
}
```

**Errores:**
- `400` - Email ya registrado

---

## POST /api/auth/login

Iniciar sesion y obtener token JWT.

**Autenticacion:** No

**Request Body:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| email | string (email) | si | Email del usuario |
| password | string | si | Contraseña |

```json
{
  "email": "tecnico@example.com",
  "password": "mi_password_seguro"
}
```

**Respuesta:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errores:**
- `401` - Credenciales invalidas

---

## GET /api/auth/me

Obtener datos del usuario autenticado.

**Autenticacion:** Si

**Respuesta:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "tecnico@example.com",
  "full_name": "Juan Perez",
  "is_active": true,
  "created_at": "2026-03-30T18:00:00"
}
```

### Tipo: UserResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID del usuario |
| email | string (email) | Email |
| full_name | string | Nombre completo |
| is_active | boolean | Si la cuenta esta activa |
| created_at | datetime | Fecha de creacion |

---

# 2. Clients

Tag: `clients` | Prefix: `/api/clients`

**Todos los endpoints requieren autenticacion.** Cada usuario solo ve sus propios clientes.

### Tipo: ClientResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID del cliente |
| owner_id | string (uuid) | ID del usuario dueño |
| first_name | string | Nombre |
| last_name | string | Apellido |
| email | string \| null | Email del cliente |
| phone | string \| null | Telefono |
| address | string \| null | Direccion |
| notes | string \| null | Notas |
| is_active | boolean | Si el cliente esta activo |
| created_at | datetime | Fecha de creacion |
| updated_at | datetime | Ultima actualizacion |

---

## POST /api/clients

Crear un nuevo cliente.

**Request Body:**

| Campo | Tipo | Requerido | Validacion | Descripcion |
|-------|------|-----------|------------|-------------|
| first_name | string | si | 1-100 chars | Nombre |
| last_name | string | si | 1-100 chars | Apellido |
| email | string (email) | no | formato email | Email |
| phone | string | no | max 20 chars | Telefono |
| address | string | no | max 500 chars | Direccion |
| notes | string | no | - | Notas |

```json
{
  "first_name": "Maria",
  "last_name": "Garcia",
  "email": "maria@example.com",
  "phone": "305-555-1234",
  "address": "123 Main St, Miami, FL"
}
```

**Respuesta:** `201 Created` → ClientResponse

---

## GET /api/clients

Listar clientes con paginacion y busqueda.

**Query Parameters:**

| Param | Tipo | Default | Validacion | Descripcion |
|-------|------|---------|------------|-------------|
| page | int | 1 | >= 1 | Pagina |
| size | int | 20 | 1-100 | Tamaño de pagina |
| search | string | null | - | Busca en first_name, last_name, email, phone (ILIKE) |
| active_only | bool | true | - | Solo clientes activos |

**Respuesta:** `200 OK` → PaginatedResponse[ClientResponse]

---

## GET /api/clients/{client_id}

Obtener un cliente por ID.

**Respuesta:** `200 OK` → ClientResponse

**Errores:** `404` - Cliente no encontrado

---

## PATCH /api/clients/{client_id}

Actualizar un cliente. Solo enviar los campos a modificar.

**Request Body:** (todos opcionales)

| Campo | Tipo | Validacion |
|-------|------|------------|
| first_name | string | 1-100 chars |
| last_name | string | 1-100 chars |
| email | string (email) | formato email |
| phone | string | max 20 chars |
| address | string | max 500 chars |
| notes | string | - |

**Respuesta:** `200 OK` → ClientResponse

---

## DELETE /api/clients/{client_id}

Eliminar un cliente (soft delete - marca `is_active = false`).

**Respuesta:** `200 OK` → ClientResponse (con is_active: false)

---

# 3. Properties

Tag: `properties` | Prefix: `/api/clients/{client_id}/properties`

**Todos los endpoints requieren autenticacion.** Las propiedades estan anidadas bajo el cliente.

### Tipo: PropertyResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID de la propiedad |
| client_id | string (uuid) | ID del cliente |
| name | string | Nombre de la propiedad |
| address | string | Direccion |
| city | string \| null | Ciudad |
| state | string \| null | Estado |
| zip_code | string \| null | Codigo postal |
| notes | string \| null | Notas |
| created_at | datetime | Fecha de creacion |
| updated_at | datetime | Ultima actualizacion |

---

## POST /api/clients/{client_id}/properties

Crear una propiedad para un cliente.

**Path Parameters:**
- `client_id` (string, uuid) - ID del cliente

**Request Body:**

| Campo | Tipo | Requerido | Validacion | Descripcion |
|-------|------|-----------|------------|-------------|
| name | string | si | 1-255 chars | Nombre |
| address | string | si | max 500 chars | Direccion |
| city | string | no | max 100 chars | Ciudad |
| state | string | no | max 50 chars | Estado |
| zip_code | string | no | max 10 chars | Codigo postal |
| notes | string | no | - | Notas |

```json
{
  "name": "Casa principal",
  "address": "456 Oak Ave",
  "city": "Miami",
  "state": "FL",
  "zip_code": "33101"
}
```

**Respuesta:** `201 Created` → PropertyResponse

---

## GET /api/clients/{client_id}/properties

Listar propiedades de un cliente.

**Query Parameters:**

| Param | Tipo | Default | Validacion |
|-------|------|---------|------------|
| page | int | 1 | >= 1 |
| size | int | 20 | 1-100 |

**Respuesta:** `200 OK` → PaginatedResponse[PropertyResponse]

---

## GET /api/clients/{client_id}/properties/{property_id}

Obtener una propiedad por ID.

**Respuesta:** `200 OK` → PropertyResponse

---

## PATCH /api/clients/{client_id}/properties/{property_id}

Actualizar una propiedad. Solo enviar campos a modificar.

**Request Body:** (todos opcionales)

| Campo | Tipo | Validacion |
|-------|------|------------|
| name | string | 1-255 chars |
| address | string | max 500 chars |
| city | string | max 100 chars |
| state | string | max 50 chars |
| zip_code | string | max 10 chars |
| notes | string | - |

**Respuesta:** `200 OK` → PropertyResponse

---

## DELETE /api/clients/{client_id}/properties/{property_id}

Eliminar una propiedad (hard delete).

**Respuesta:** `204 No Content`

---

# 4. Irrigation Systems

Tag: `irrigation_systems` | Prefix: `/api/properties/{property_id}/systems`

**Todos los endpoints requieren autenticacion.**

### Tipo: IrrigationSystemResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID del sistema |
| property_id | string (uuid) | ID de la propiedad |
| name | string | Nombre del sistema |
| system_type | string | Tipo (drip, sprinkler, rotor, etc.) |
| zone_count | int \| null | Numero de zonas |
| install_date | date \| null | Fecha de instalacion |
| notes | string \| null | Notas |
| created_at | datetime | Fecha de creacion |
| updated_at | datetime | Ultima actualizacion |

---

## POST /api/properties/{property_id}/systems

Crear un sistema de riego en una propiedad.

**Path Parameters:**
- `property_id` (string, uuid) - ID de la propiedad

**Request Body:**

| Campo | Tipo | Requerido | Validacion | Descripcion |
|-------|------|-----------|------------|-------------|
| name | string | si | 1-255 chars | Nombre |
| system_type | string | si | max 50 chars | Tipo de sistema |
| zone_count | int | no | >= 1 | Numero de zonas |
| install_date | date | no | formato YYYY-MM-DD | Fecha de instalacion |
| notes | string | no | - | Notas |

```json
{
  "name": "Front yard sprinklers",
  "system_type": "sprinkler",
  "zone_count": 4,
  "install_date": "2024-06-15"
}
```

**Respuesta:** `201 Created` → IrrigationSystemResponse

---

## GET /api/properties/{property_id}/systems

Listar sistemas de riego de una propiedad.

**Query Parameters:**

| Param | Tipo | Default | Validacion |
|-------|------|---------|------------|
| page | int | 1 | >= 1 |
| size | int | 20 | 1-100 |

**Respuesta:** `200 OK` → PaginatedResponse[IrrigationSystemResponse]

---

## GET /api/properties/{property_id}/systems/{system_id}

Obtener un sistema por ID.

**Respuesta:** `200 OK` → IrrigationSystemResponse

---

## PATCH /api/properties/{property_id}/systems/{system_id}

Actualizar un sistema. Solo enviar campos a modificar.

**Request Body:** (todos opcionales)

| Campo | Tipo | Validacion |
|-------|------|------------|
| name | string | 1-255 chars |
| system_type | string | max 50 chars |
| zone_count | int | >= 1 |
| install_date | date | formato YYYY-MM-DD |
| notes | string | - |

**Respuesta:** `200 OK` → IrrigationSystemResponse

---

## DELETE /api/properties/{property_id}/systems/{system_id}

Eliminar un sistema (hard delete).

**Respuesta:** `204 No Content`

---

# 5. Jobs (CORE)

Tag: `jobs` | Prefix: `/api/jobs`

**Todos los endpoints requieren autenticacion.** Los trabajos son el modulo principal del sistema.

### Tipos de trabajo (job_type)

| Valor | Descripcion |
|-------|-------------|
| `maintenance` | Mantenimiento regular |
| `repair` | Reparacion |
| `installation` | Instalacion nueva |
| `inspection` | Inspeccion |
| `winterization` | Winterizacion |
| `spring_startup` | Apertura de primavera |

### Estados de trabajo (status)

| Valor | Descripcion |
|-------|-------------|
| `scheduled` | Programado (default al crear) |
| `in_progress` | En progreso |
| `completed` | Completado |
| `cancelled` | Cancelado |

### Tipo: JobResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID del trabajo |
| property_id | string (uuid) | ID de la propiedad |
| title | string | Titulo del trabajo |
| description | string \| null | Descripcion |
| job_type | string | Tipo de trabajo (ver tabla arriba) |
| status | string | Estado (ver tabla arriba) |
| scheduled_date | date | Fecha programada |
| completed_date | date \| null | Fecha de completado |
| price | float \| null | Precio del servicio |
| reminder_days | int[] \| null | Dias para recordatorio post-completado |
| notes | string \| null | Notas |
| created_at | datetime | Fecha de creacion |
| updated_at | datetime | Ultima actualizacion |

### Comportamiento especial: Auto-generacion de recordatorios

Cuando un trabajo se marca como `completed` y tiene `reminder_days` definidos, el sistema **automaticamente** crea recordatorios para cada valor en el array. Los recordatorios se calculan desde `completed_date`.

**Ejemplo:** Si `reminder_days: [30, 90, 180]` y `completed_date: 2026-04-15`:
- Reminder 1: 2026-05-15 (30 dias)
- Reminder 2: 2026-07-14 (90 dias)
- Reminder 3: 2026-10-12 (180 dias)

---

## POST /api/jobs

Crear un nuevo trabajo.

**Request Body:**

| Campo | Tipo | Requerido | Validacion | Descripcion |
|-------|------|-----------|------------|-------------|
| property_id | string (uuid) | si | - | ID de la propiedad |
| title | string | si | 1-255 chars | Titulo |
| description | string | no | - | Descripcion |
| job_type | string | no | default: "maintenance" | Tipo de trabajo |
| scheduled_date | date | si | formato YYYY-MM-DD | Fecha programada |
| price | float | no | >= 0 | Precio |
| reminder_days | int[] | no | - | Dias para recordatorios |
| notes | string | no | - | Notas |

```json
{
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Spring maintenance",
  "job_type": "maintenance",
  "scheduled_date": "2026-04-15",
  "price": 150.00,
  "reminder_days": [30, 90, 180]
}
```

**Respuesta:** `201 Created` → JobResponse

---

## GET /api/jobs

Listar trabajos con filtros.

**Query Parameters:**

| Param | Tipo | Default | Validacion | Descripcion |
|-------|------|---------|------------|-------------|
| page | int | 1 | >= 1 | Pagina |
| size | int | 20 | 1-100 | Tamaño de pagina |
| status | string | null | - | Filtrar por estado |
| job_type | string | null | - | Filtrar por tipo |
| property_id | string | null | - | Filtrar por propiedad |

**Ejemplo:** `GET /api/jobs?status=scheduled&job_type=maintenance&page=1&size=10`

**Respuesta:** `200 OK` → PaginatedResponse[JobResponse]

---

## GET /api/jobs/{job_id}

Obtener un trabajo por ID.

**Respuesta:** `200 OK` → JobResponse

---

## PATCH /api/jobs/{job_id}

Actualizar un trabajo. Solo enviar campos a modificar.

**Request Body:** (todos opcionales)

| Campo | Tipo | Validacion | Descripcion |
|-------|------|------------|-------------|
| title | string | 1-255 chars | Titulo |
| description | string | - | Descripcion |
| job_type | string | - | Tipo de trabajo |
| status | string | - | Estado |
| scheduled_date | date | formato YYYY-MM-DD | Fecha programada |
| completed_date | date | formato YYYY-MM-DD | Fecha completado |
| price | float | >= 0 | Precio |
| reminder_days | int[] | - | Dias para recordatorios |
| notes | string | - | Notas |

**Ejemplo - Completar un trabajo:**

```json
{
  "status": "completed",
  "completed_date": "2026-04-15"
}
```

> Si el job tiene `reminder_days`, esto dispara la creacion automatica de recordatorios.

**Respuesta:** `200 OK` → JobResponse

---

## DELETE /api/jobs/{job_id}

Eliminar un trabajo (hard delete).

**Respuesta:** `204 No Content`

---

# 6. Job Notes

Tag: `job_notes` | Prefix: `/api/jobs/{job_id}/notes`

**Todos los endpoints requieren autenticacion.** Las notas estan anidadas bajo un trabajo.

### Tipo: JobNoteResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID de la nota |
| job_id | string (uuid) | ID del trabajo |
| content | string | Contenido de la nota |
| created_at | datetime | Fecha de creacion |
| updated_at | datetime | Ultima actualizacion |

---

## POST /api/jobs/{job_id}/notes

Crear una nota en un trabajo.

**Path Parameters:**
- `job_id` (string, uuid) - ID del trabajo

**Request Body:**

| Campo | Tipo | Requerido | Validacion | Descripcion |
|-------|------|-----------|------------|-------------|
| content | string | si | min 1 char | Contenido de la nota |

```json
{
  "content": "Found broken sprinkler head in zone 3. Replaced with Rain Bird 1800."
}
```

**Respuesta:** `201 Created` → JobNoteResponse

---

## GET /api/jobs/{job_id}/notes

Listar notas de un trabajo.

**Query Parameters:**

| Param | Tipo | Default | Validacion |
|-------|------|---------|------------|
| page | int | 1 | >= 1 |
| size | int | 20 | 1-100 |

**Respuesta:** `200 OK` → PaginatedResponse[JobNoteResponse]

---

## GET /api/jobs/{job_id}/notes/{note_id}

Obtener una nota por ID.

**Respuesta:** `200 OK` → JobNoteResponse

---

## PATCH /api/jobs/{job_id}/notes/{note_id}

Actualizar una nota.

**Request Body:**

| Campo | Tipo | Requerido | Validacion |
|-------|------|-----------|------------|
| content | string | si | min 1 char |

**Respuesta:** `200 OK` → JobNoteResponse

---

## DELETE /api/jobs/{job_id}/notes/{note_id}

Eliminar una nota (hard delete).

**Respuesta:** `204 No Content`

---

# 7. Reminders

Tag: `reminders` | Prefix: `/api/reminders`

**Todos los endpoints requieren autenticacion.**

### Estados de recordatorio (status)

| Valor | Descripcion |
|-------|-------------|
| `pending` | Pendiente (default) |
| `sent` | Enviado |
| `completed` | Completado |
| `cancelled` | Cancelado |

### Tipo: ReminderResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID del recordatorio |
| job_id | string (uuid) \| null | ID del trabajo asociado (si aplica) |
| property_id | string (uuid) | ID de la propiedad |
| title | string | Titulo |
| description | string \| null | Descripcion |
| remind_date | date | Fecha del recordatorio |
| status | string | Estado (ver tabla arriba) |
| is_auto_generated | boolean | true si fue creado automaticamente al completar un job |
| created_at | datetime | Fecha de creacion |
| updated_at | datetime | Ultima actualizacion |

---

## POST /api/reminders

Crear un recordatorio manual.

**Request Body:**

| Campo | Tipo | Requerido | Validacion | Descripcion |
|-------|------|-----------|------------|-------------|
| property_id | string (uuid) | si | - | ID de la propiedad |
| job_id | string (uuid) | no | - | ID del trabajo asociado |
| title | string | si | 1-255 chars | Titulo |
| description | string | no | - | Descripcion |
| remind_date | date | si | formato YYYY-MM-DD | Fecha del recordatorio |

```json
{
  "property_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Check backflow preventer",
  "remind_date": "2026-06-01"
}
```

**Respuesta:** `201 Created` → ReminderResponse

---

## GET /api/reminders/upcoming

Obtener recordatorios pendientes proximos (no paginado).

**Query Parameters:**

| Param | Tipo | Default | Validacion | Descripcion |
|-------|------|---------|------------|-------------|
| days | int | 30 | 1-365 | Rango de dias a consultar desde hoy |

**Ejemplo:** `GET /api/reminders/upcoming?days=60`

**Respuesta:** `200 OK` → ReminderResponse[] (array, ordenado por remind_date ASC)

> Solo retorna recordatorios con status `pending` entre hoy y hoy + days.

---

## GET /api/reminders

Listar todos los recordatorios con filtro por estado.

**Query Parameters:**

| Param | Tipo | Default | Validacion | Descripcion |
|-------|------|---------|------------|-------------|
| page | int | 1 | >= 1 | Pagina |
| size | int | 20 | 1-100 | Tamaño de pagina |
| status | string | null | - | Filtrar por estado |

**Respuesta:** `200 OK` → PaginatedResponse[ReminderResponse]

---

## GET /api/reminders/{reminder_id}

Obtener un recordatorio por ID.

**Respuesta:** `200 OK` → ReminderResponse

---

## PATCH /api/reminders/{reminder_id}

Actualizar un recordatorio. Solo enviar campos a modificar.

**Request Body:** (todos opcionales)

| Campo | Tipo | Validacion | Descripcion |
|-------|------|------------|-------------|
| title | string | 1-255 chars | Titulo |
| description | string | - | Descripcion |
| remind_date | date | formato YYYY-MM-DD | Fecha |
| status | string | - | Estado |

**Ejemplo - Marcar como completado:**

```json
{
  "status": "completed"
}
```

**Respuesta:** `200 OK` → ReminderResponse

---

## DELETE /api/reminders/{reminder_id}

Eliminar un recordatorio (hard delete).

**Respuesta:** `204 No Content`

---

# 8. Calendar

Tag: `calendar` | Prefix: `/api/calendar`

**Requiere autenticacion.** Vista de lectura que agrega Jobs y Reminders en un rango de fechas. No tiene modelo propio.

### Tipo: CalendarEvent

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | string (uuid) | ID del recurso (job o reminder) |
| type | string | `"job"` o `"reminder"` |
| title | string | Titulo |
| date | date | Fecha del evento |
| status | string | Estado del recurso |
| job_type | string \| null | Tipo de trabajo (solo si type = "job") |
| property_id | string (uuid) | ID de la propiedad |
| job_id | string (uuid) \| null | ID del trabajo asociado (solo si type = "reminder") |

### Tipo: CalendarDay

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| date | date | Fecha del dia |
| events | CalendarEvent[] | Eventos de ese dia |

### Tipo: CalendarResponse

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| start | date | Inicio del rango consultado |
| end | date | Fin del rango consultado |
| days | CalendarDay[] | Solo dias que tienen eventos (ordenados) |
| total_events | int | Total de eventos en el rango |

---

## GET /api/calendar

Obtener eventos del calendario en un rango de fechas.

**Query Parameters:**

| Param | Tipo | Requerido | Validacion | Descripcion |
|-------|------|-----------|------------|-------------|
| start | date | si | formato YYYY-MM-DD | Fecha inicio |
| end | date | si | formato YYYY-MM-DD | Fecha fin |

**Validaciones:**
- `end` debe ser >= `start` (error 400)
- Rango maximo: 366 dias (error 400)

**Ejemplo:** `GET /api/calendar?start=2026-04-01&end=2026-04-30`

**Respuesta:** `200 OK`

```json
{
  "start": "2026-04-01",
  "end": "2026-04-30",
  "days": [
    {
      "date": "2026-04-15",
      "events": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "type": "job",
          "title": "Spring maintenance",
          "date": "2026-04-15",
          "status": "scheduled",
          "job_type": "maintenance",
          "property_id": "660e8400-e29b-41d4-a716-446655440000",
          "job_id": null
        },
        {
          "id": "770e8400-e29b-41d4-a716-446655440000",
          "type": "reminder",
          "title": "Follow-up (90 days) - Winter check",
          "date": "2026-04-15",
          "status": "pending",
          "job_type": null,
          "property_id": "660e8400-e29b-41d4-a716-446655440000",
          "job_id": "880e8400-e29b-41d4-a716-446655440000"
        }
      ]
    }
  ],
  "total_events": 2
}
```

**Errores:**
- `400` - end < start
- `400` - Rango excede 366 dias
