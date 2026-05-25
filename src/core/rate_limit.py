import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._storage: dict[str, deque[float]] = defaultdict(deque)

    def hit(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        bucket = self._storage[key]
        threshold = now - window_seconds
        while bucket and bucket[0] < threshold:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        bucket.append(now)


def build_rate_limit_dependency(scope: str, limit: int, window_seconds: int):
    async def dependency(request: Request) -> None:
        client = request.client.host if request.client else "anonymous"
        key = f"{scope}:{client}"
        request.app.state.rate_limiter.hit(key, limit, window_seconds)

    return dependency
