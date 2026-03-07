# Plataforma de administración de voicechat

## Descripción funcional
Plataforma backend con panel admin desacoplado que centraliza estado, sesiones, moderación, telemetría y widgets dinámicos para un sistema de voicechat conectado a servidores Minecraft mediante WebSocket autenticado con HMAC.

## Panel frontend (React)
Consola administrativa en tiempo real construida en React + TypeScript con arquitectura modular por dominios. Consume la API REST y el WebSocket de eventos, renderiza dashboards dinámicos basados en widgets JSON y persiste el layout por usuario.

### Configuración frontend
- VITE_API_BASE_URL: URL base de la API REST (ej: http://localhost:8000)
- VITE_WS_URL: URL del WebSocket admin (ej: ws://localhost:8000/ws/admin/)

### Permisos requeridos (UI)
- moderation.mute: habilita mute en tabla de usuarios
- moderation.kick: habilita kick en tabla de usuarios
- moderation.ban: habilita ban en tabla de usuarios
- dashboard.edit: permite drag & resize del layout

### Ejemplo de login
El panel requiere token, user_id, server_id y permisos disponibles:

```text
Token: <token>
User ID: 12
Server ID: lobby-1
Permisos: moderation.mute,moderation.kick,moderation.ban,dashboard.edit
Roles: admin
```

### WebSocket admin
- URL: ws://<host>/ws/admin/?token=<token>
- Payload recibido:

```json
{
  "type": "event",
  "event": "voice.user_connected",
  "payload": {
    "user_id": 12,
    "session_id": 88,
    "server_id": "lobby-1",
    "channel_id": 3
  }
}
```

### Persistencia de layout
- El panel guarda el layout por usuario en /api/dashboards/.
- Si no hay layout remoto disponible, usa el layout local en localStorage.

## Admin de Django
Interfaz de administración para gestionar usuarios, roles, permisos y modelos internos.

### URL
- /admin/

### Parámetros
- DJANGO_ALLOWED_HOSTS debe incluir el dominio donde se expone el admin.
- Credenciales de un usuario con acceso al admin.

### Permisos requeridos
- is_staff=true para iniciar sesión.
- is_superuser=true para acceso total a todos los módulos.

### Ejemplo de uso
```bash
python manage.py createsuperuser
```

Accede luego a `https://<tu-dominio>/admin/` e inicia sesión con el superusuario creado.

## Parámetros y configuración
- DJANGO_SECRET_KEY: clave secreta de Django
- DJANGO_DEBUG: true|false
- DJANGO_ALLOWED_HOSTS: lista separada por coma
- DJANGO_CSRF_TRUSTED_ORIGINS: lista separada por coma con https://dominio
- DOMAIN_DB_BACKEND: postgres|mysql|sqlite|oracle|sqlserver|mongodb
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- SQLITE_PATH: ruta del archivo SQLite
- MYSQL_DRIVER: pymysql
- DJANGO_DB_BACKEND: backend SQL para Django cuando DOMAIN_DB_BACKEND=mongodb
- MONGO_URI, MONGO_DB
- REDIS_URL: URL de Redis para caché y canales
- PLUGIN_SHARED_SECRETS: JSON con api_key:secret
- PLUGIN_ALLOWED_DRIFT_SECONDS: ventana de tiempo para firmas
- PLUGIN_EVENT_TTL_SECONDS: TTL para idempotencia de eventos

## Capa de abstracción multi‑DB
La lógica de negocio consume DAOs comunes y el motor se selecciona por variables de entorno. Para motores SQL se usan migraciones de Django y para MongoDB se crean índices y colecciones vía `db_migrate`.

### Ejemplo de configuración PostgreSQL
```env
DOMAIN_DB_BACKEND=postgres
DB_NAME=parallax_admin
DB_USER=parallax
DB_PASSWORD=strong-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

### Ejemplo de configuración MongoDB
```env
DOMAIN_DB_BACKEND=mongodb
DJANGO_DB_BACKEND=sqlite
SQLITE_PATH=/opt/parallax/backend/db.sqlite3
MONGO_URI=mongodb://127.0.0.1:27017
MONGO_DB=parallax_admin
```

### Migraciones unificadas
```bash
python manage.py db_migrate
```

## Permisos requeridos
- moderation.mute: requerido para mutear usuarios

## Endpoints REST iniciales

### Usuarios activos
- GET /api/users/active/
- Respuesta:

```json
{
  "count": 1,
  "results": [
    {
      "id": 12,
      "external_id": "9d2c3c9a-4e0b-4d07-a91f-1a5f3c2f2b2b",
      "username": "steve",
      "display_name": "Steve",
      "minecraft_uuid": "2b7f2e7c-1f9d-4f5b-9b7f-2f2a5d7b7f7a",
      "is_online": true,
      "last_seen_at": "2026-03-03T12:00:00Z",
      "current_channel": 3
    }
  ],
  "timestamp": "2026-03-03T12:01:00Z"
}
```

### Mutear usuario
- POST /api/moderation/mute/
- Permiso: moderation.mute
- Payload:

```json
{
  "target_user_id": 12,
  "server_id": "lobby-1",
  "reason": "spam",
  "duration_seconds": 300
}
```

### Eventos de telemetría
- GET /api/telemetry/
- Respuesta:

```json
{
  "count": 10,
  "results": [
    {
      "id": 55,
      "event_id": "evt-123",
      "event_type": "packet_loss",
      "server_id": "lobby-1",
      "user": 12,
      "session": 22,
      "payload": {"loss": 0.05},
      "occurred_at": "2026-03-03T12:00:30Z"
    }
  ]
}
```

## WebSocket plugin ↔ backend

### Autenticación HMAC
- Query params:
  - api_key
  - server_id
  - timestamp
  - nonce
  - signature
- String firmado: api_key.server_id.timestamp.nonce
- Algoritmo: HMAC-SHA256

### Eventos enviados por el plugin

```json
{
  "event_id": "evt-001",
  "event_type": "voice.user_connected",
  "payload": {
    "minecraft_uuid": "2b7f2e7c-1f9d-4f5b-9b7f-2f2a5d7b7f7a",
    "username": "steve",
    "display_name": "Steve",
    "channel_id": "spawn",
    "channel_name": "Spawn"
  }
}
```

```json
{
  "event_id": "evt-002",
  "event_type": "voice.user_disconnected",
  "payload": {
    "minecraft_uuid": "2b7f2e7c-1f9d-4f5b-9b7f-2f2a5d7b7f7a",
    "username": "steve"
  }
}
```

```json
{
  "event_id": "evt-003",
  "event_type": "telemetry.event",
  "payload": {
    "type": "packet_loss",
    "occurred_at": "2026-03-03T12:00:30Z",
    "loss": 0.05
  }
}
```

### Comandos enviados por el backend

```json
{
  "type": "command",
  "command": "moderation.mute",
  "payload": {
    "target_user_id": 12,
    "minecraft_uuid": "2b7f2e7c-1f9d-4f5b-9b7f-2f2a5d7b7f7a",
    "duration_seconds": 300,
    "reason": "spam"
  }
}
```

### Reconexion e idempotencia
- El cliente debe reintentar conexión con el mismo api_key y un nonce nuevo.
- Los eventos incluyen event_id único; el backend ignora duplicados dentro del TTL.

## Widgets dinámicos

### Esquema JSON declarativo

```json
{
  "type": "chart",
  "title": "Sesiones activas",
  "query": {
    "metric": "active_sessions",
    "window": "5m"
  },
  "ui": {
    "chart_type": "line",
    "color": "#6D28D9"
  }
}
```

### Tipos soportados
- datatable
- chart
- counter
- button
- feed

### Esquema UI usado por el panel
Parámetros principales:
- title: título visible
- metric: clave para counters o charts (active_users, events)
- endpoint: endpoint REST opcional para button
- payload: payload opcional para button
- required_permissions: lista de permisos para renderizar

```json
{
  "title": "Usuarios activos",
  "metric": "active_users",
  "required_permissions": ["dashboard.view"]
}
```

### Vinculación a roles
- WidgetDefinition.allowed_roles y WidgetDefinition.required_permissions determinan visibilidad.

### Renderizado dinámico
- El panel recibe la definición y decide el render según type y schema.
