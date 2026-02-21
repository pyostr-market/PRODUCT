import asyncio
import json
import signal
from datetime import datetime

from dotenv import load_dotenv
from redis.asyncio import Redis

from src.core.conf.settings import get_settings

load_dotenv()


def _pretty_message(raw: str) -> str:
    try:
        payload = json.loads(raw)
        return json.dumps(payload, ensure_ascii=False, indent=2)
    except Exception:
        return raw

settings = get_settings()
async def main() -> None:
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )
    pubsub = redis.pubsub()

    stop_event = asyncio.Event()

    def _stop_handler(*_: object) -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, _stop_handler)
    loop.add_signal_handler(signal.SIGTERM, _stop_handler)

    await pubsub.subscribe(settings.REDIS_USER_EVENTS_CHANNEL)
    print(
        f"[{datetime.now().isoformat()}] Listening Redis Pub/Sub channel: {settings.REDIS_USER_EVENTS_CHANNEL}"
    )
    print("Press Ctrl+C to stop.\n")

    try:
        while not stop_event.is_set():
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if not message:
                continue

            data = message.get("data")
            if data is None:
                continue

            print(f"[{datetime.now().isoformat()}] Event received:")
            print(_pretty_message(str(data)))
            print("-" * 50)
    finally:
        await pubsub.unsubscribe(settings.REDIS_USER_EVENTS_CHANNEL)
        await pubsub.aclose()
        await redis.aclose()
        print(f"[{datetime.now().isoformat()}] Consumer stopped.")


if __name__ == "__main__":
    asyncio.run(main())
