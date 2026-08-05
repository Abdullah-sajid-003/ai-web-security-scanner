import redis
from rq import Queue

from app.core.config import settings

redis_conn = redis.from_url(settings.REDIS_URL)
scan_queue = Queue("scans", connection=redis_conn)
