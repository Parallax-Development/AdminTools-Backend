# Plataforma de administración de voicechat

## Descripción funcional
Plataforma backend con panel admin desacoplado que centraliza estado, sesiones, moderación, telemetría y widgets dinámicos para un sistema de voicechat conectado a servidores Minecraft mediante WebSocket autenticado con HMAC.

## Parámetros y configuración
- DJANGO_SECRET_KEY: clave secreta de Django
- DJANGO_DEBUG: true|false
- DJANGO_ALLOWED_HOSTS: lista separada por coma
- USE_POSTGRES: true|false
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
- REDIS_URL: URL de Redis para caché y canales
- PLUGIN_SHARED_SECRETS: JSON con api_key:secret
- PLUGIN_ALLOWED_DRIFT_SECONDS: ventana de tiempo para firmas
- PLUGIN_EVENT_TTL_SECONDS: TTL para idempotencia de eventos

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

### Vinculación a roles
- WidgetDefinition.allowed_roles y WidgetDefinition.required_permissions determinan visibilidad.

### Renderizado dinámico
- El panel recibe la definición y decide el render según type y schema.
