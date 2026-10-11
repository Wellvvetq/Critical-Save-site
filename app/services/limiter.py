import time
from collections import defaultdict
from flask import request

# In-memory timestamp cache: ip -> list of timestamps
_submissions = defaultdict(list)

def is_rate_limited(ip_address: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
    """
    Sliding window rate limiter per IP address.
    Returns True if limit exceeded, False otherwise.
    """
    if not ip_address:
        return False
        
    now = time.time()
    # Filter out entries older than window
    _submissions[ip_address] = [ts for ts in _submissions[ip_address] if now - ts < window_seconds]
    
    if len(_submissions[ip_address]) >= max_requests:
        return True
        
    _submissions[ip_address].append(now)
    return False

def reset_rate_limiter():
    """Testing helper to clear rate limit state."""
    _submissions.clear()
