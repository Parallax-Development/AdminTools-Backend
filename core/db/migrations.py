from core.db.mongo import get_mongo_database


def run_mongo_migrations():
    db = get_mongo_database()
    db.users.create_index("minecraft_uuid", unique=True, sparse=True)
    db.voice_channels.create_index([("server_id", 1), ("external_id", 1)], unique=True)
    db.voice_sessions.create_index("server_id")
    db.voice_sessions.create_index("ended_at")
    db.moderation_actions.create_index("server_id")
    db.moderation_actions.create_index("action_type")
    db.telemetry_events.create_index("event_type")
    db.telemetry_events.create_index("server_id")
    db.telemetry_events.create_index("occurred_at")
    db.widgets.create_index("widget_type")
    db.dashboards.create_index([("user", 1), ("name", 1)], unique=True)
