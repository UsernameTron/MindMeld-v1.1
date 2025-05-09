import asyncio

from app.core.config import redis


async def test_redis_connection():
    try:
        await redis.ping()
        print("✅ Redis connection successful")
        # Test rate limit key operations
        test_key = "test:ratelimit:diagnostic"
        await redis.set(test_key, 1)
        await redis.expire(test_key, 10)
        ttl = await redis.ttl(test_key)
        print(f"✅ Redis TTL operations working: {ttl}")
        await redis.delete(test_key)
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_redis_connection())
