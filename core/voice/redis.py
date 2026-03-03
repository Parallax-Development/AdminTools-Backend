import json
import os

import redis


def get_redis_client():
    return redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)


def add_active_user(server_id, user_id, payload):
    client = get_redis_client()
    client.hset(f"voice:active_users:{server_id}", user_id, json.dumps(payload))


def remove_active_user(server_id, user_id):
    client = get_redis_client()
    client.hdel(f"voice:active_users:{server_id}", user_id)


def list_active_users(server_id):
    client = get_redis_client()
    data = client.hgetall(f"voice:active_users:{server_id}")
    return {user_id: json.loads(payload) for user_id, payload in data.items()}


def is_duplicate_event(event_id, ttl_seconds):
    client = get_redis_client()
    created = client.set(f"voice:event:{event_id}", "1", nx=True, ex=ttl_seconds)
    return created is None
