def map_user(item):
    return {
        "id": item.id,
        "external_id": str(item.external_id) if getattr(item, "external_id", None) else None,
        "username": item.username,
        "display_name": item.display_name,
        "minecraft_uuid": str(item.minecraft_uuid) if item.minecraft_uuid else None,
        "is_online": item.is_online,
        "last_seen_at": item.last_seen_at,
        "current_channel": item.current_channel_id,
    }


def map_voice_channel(item):
    return {
        "id": item.id,
        "server_id": item.server_id,
        "external_id": item.external_id,
        "name": item.name,
        "is_active": item.is_active,
        "metadata": item.metadata,
    }


def map_voice_session(item):
    return {
        "id": item.id,
        "user": item.user_id,
        "channel": item.channel_id,
        "server_id": item.server_id,
        "started_at": item.started_at,
        "ended_at": item.ended_at,
        "metadata": item.metadata,
    }


def map_moderation_action(item):
    return {
        "id": item.id,
        "target_user": item.target_user_id,
        "actor_user": item.actor_user_id if item.actor_user_id else None,
        "server_id": item.server_id,
        "action_type": item.action_type,
        "reason": item.reason,
        "created_at": item.created_at,
        "expires_at": item.expires_at,
        "metadata": item.metadata,
    }


def map_telemetry_event(item):
    return {
        "id": item.id,
        "event_id": item.event_id,
        "event_type": item.event_type,
        "server_id": item.server_id,
        "user": item.user_id if item.user_id else None,
        "session": item.session_id if item.session_id else None,
        "payload": item.payload,
        "occurred_at": item.occurred_at,
    }


def map_widget_definition(item):
    return {
        "id": item.id,
        "key": item.key,
        "name": item.name,
        "description": item.description,
        "widget_type": item.widget_type,
        "schema": item.schema,
        "is_active": item.is_active,
        "required_permissions": [p.id for p in item.required_permissions.all()],
        "allowed_roles": [r.id for r in item.allowed_roles.all()],
    }


def map_dashboard_layout(item):
    return {
        "id": item.id,
        "user": item.user_id,
        "name": item.name,
        "layout": item.layout,
        "is_default": item.is_default,
        "updated_at": item.updated_at,
    }
