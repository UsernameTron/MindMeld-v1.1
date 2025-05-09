import asyncio
import time

import aiohttp
from rich.progress import Progress


async def test_endpoint(url, requests, concurrency):
    semaphore = asyncio.Semaphore(concurrency)
    successes, failures, rate_limited = 0, 0, 0

    async def make_request():
        nonlocal successes, failures, rate_limited
        async with semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    start = time.time()
                    async with session.post(
                        url, json={"text": "Test content"}
                    ) as response:
                        duration = time.time() - start
                        if response.status == 200:
                            successes += 1
                        elif response.status == 429:
                            rate_limited += 1
                            retry_after = response.headers.get("Retry-After", "N/A")
                            print(f"Rate limited! Retry-After: {retry_after}s")
                        else:
                            failures += 1
            except Exception as e:
                failures += 1
                print(f"Error: {e}")

    with Progress() as progress:
        task = progress.add_task("[cyan]Testing rate limits...", total=requests)
        tasks = []
        for i in range(requests):
            tasks.append(asyncio.create_task(make_request()))
            progress.update(task, advance=1)
            await asyncio.sleep(0.05)  # Slight delay to create more realistic load

        await asyncio.gather(*tasks)

    return {"success": successes, "failed": failures, "rate_limited": rate_limited}


async def main():
    base_url = "http://localhost:8000"
    results = {}

    print("\n=== Testing /chat/completion endpoint ===")
    results["chat"] = await test_endpoint(f"{base_url}/chat/completion", 20, 5)

    print("\n=== Testing /analyze endpoint ===")
    results["analyze"] = await test_endpoint(f"{base_url}/analyze", 30, 10)

    print("\n=== Results ===")
    for endpoint, result in results.items():
        print(f"{endpoint}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
