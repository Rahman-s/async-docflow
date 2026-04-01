import json
import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
CHANNEL_NAME = "document_progress"


def publish_progress(document_id: int, status: str, progress: int, message: str):
    payload = {
        "document_id": document_id,
        "status": status,
        "progress": progress,
        "message": message,
    }
    redis_client.publish(CHANNEL_NAME, json.dumps(payload))