"""Security utilities: input validation, SSRF protection, rate limiting."""

import re
import time
import hashlib
from typing import Optional, Set
from urllib.parse import urlparse
import ipaddress

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Allowed domains for outbound requests (prevent SSRF)
ALLOWED_DOMAINS = {
    "www.googleapis.com",
    "api.twitter.com",
    "api.linkedin.com",
    "graph.facebook.com",
    "api.whatsapp.com",
    "wa.me",
    "web.whatsapp.com",
    "www.linkedin.com",
    "x.com",
    "twitter.com",
    "www.youtube.com",
    "www.instagram.com",
    "www.facebook.com",
    "www.threads.net",
}

BLOCKED_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

# Rate limiting: max requests per minute per IP
RATE_LIMIT = 30
_rate_limit_store = {}


def validate_url_security(url: str) -> bool:
    """Validate URL for SSRF protection and allowed domains."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname or ""
        if not hostname:
            return False

        # Check against blocked IP ranges
        try:
            import socket
            ips = socket.getaddrinfo(hostname, None)
            for ip_info in ips:
                ip = ip_info[4][0]
                try:
                    addr = ipaddress.ip_address(ip)
                    for blocked in BLOCKED_IP_RANGES:
                        if addr in blocked:
                            return False
                except ValueError:
                    continue
        except Exception:
            # If we can't resolve, be safe and block
            return False

        # Check if domain is allowed (for external API calls)
        # Allow localhost for development
        if hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
            return True

        # Check if domain or parent domain is allowed
        domain_parts = hostname.split(".")
        for i in range(len(domain_parts)):
            domain = ".".join(domain_parts[i:])
            if domain in ALLOWED_DOMAINS:
                return True

        return False
    except Exception:
        return False


def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input to prevent injection."""
    if not text:
        return ""
    # Remove control characters
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    # Limit length
    text = text[:max_length]
    # Strip whitespace
    return text.strip()


def validate_query(query: str) -> str:
    """Validate and sanitize prospect discovery query."""
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    query = sanitize_input(query, max_length=500)
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Query too short (minimum 3 characters)")
    return query


# In-memory rate limiter (use Redis in production)
class RateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_seconds
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        self.requests[client_ip].append(now)
        return True


rate_limiter = RateLimiter(max_requests=30, window_seconds=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        if not rate_limiter.check_rate_limit(client_ip):
            return Response(
                content='{"error": "Rate limit exceeded. Maximum 30 requests per minute."}',
                status_code=429,
                media_type="application/json"
            )
        response = await call_next(request)
        return response


def get_client_ip(request: Request) -> str:
    """Get client IP from request, considering proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"