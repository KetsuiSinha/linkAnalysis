import ipaddress
import socket
from typing import Optional
from fastapi import HTTPException


PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("169.254.0.0/16"),
]

FORBIDDEN_HOSTS = {"localhost", "localhost.localdomain", "local"}


def is_private_or_localhost(hostname: str) -> bool:
    if not hostname or hostname.lower() in FORBIDDEN_HOSTS:
        return True
    try:
        infos = socket.getaddrinfo(hostname, None)
    except Exception:
        return True
    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        ip = sockaddr[0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if addr.is_private or addr.is_loopback or addr.is_link_local:
            return True
        for net in PRIVATE_NETWORKS:
            if addr in net:
                return True
    return False


def validate_url_for_fetch(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URL must use http or https scheme")
    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL: missing hostname")
    if is_private_or_localhost(parsed.hostname):
        raise HTTPException(
            status_code=400,
            detail="Access to private or internal network addresses is not allowed",
        )
    return url
