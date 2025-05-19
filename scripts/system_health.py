import asyncio
import sys
from pathlib import Path

import httpx
from app.core.config import redis, settings


async def check_system_health():
    errors = []
    # Check FastAPI
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/health")
            if resp.status_code != 200:
                errors.append(f"API health check failed: {resp.status_code}")
            else:
                print("✅ API responding")
    except Exception as e:
        errors.append(f"API connection error: {e}")
    # Check Redis
    try:
        await redis.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        errors.append(f"Redis connection failed: {e}")
    # Check file integrity
    core_files = ["app/main.py", "app/core/middleware.py", "app/core/config.py"]
    for file in core_files:
        if not Path(file).exists():
            errors.append(f"Missing core file: {file}")
    # Report results
    if errors:
        print("❌ System health check failed")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ All systems operational")
        return True


if __name__ == "__main__":
    result = asyncio.run(check_system_health())
    sys.exit(0 if result else 1)
