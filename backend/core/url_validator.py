"""
SSRF Protection — URL validator for media fetching endpoints.
Prevents Server-Side Request Forgery by validating URLs against allowlists
and blocking private/internal IP ranges.
"""
import ipaddress
import socket
from urllib.parse import urlparse
from core.logging import get_logger

logger = get_logger("blackrose.core.url_validator")

# Whitelisted domains for media fetching
ALLOWED_DOMAINS = {
    "cdn.discordapp.com",
    "media.discordapp.net",
    "images-ext-1.discordapp.net",
    "images-ext-2.discordapp.net",
}

# Private/internal IP ranges that must be blocked
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # AWS metadata
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 private
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]


class SSRFError(Exception):
    """Raised when a URL fails SSRF validation."""
    pass


def validate_url(url: str, *, allow_any_https: bool = False) -> str:
    """
    Validate a URL against SSRF attacks.
    
    Args:
        url: The URL to validate
        allow_any_https: If True, allow any HTTPS domain (not just whitelisted ones)
    
    Returns:
        The validated URL (stripped of query params)
    
    Raises:
        SSRFError: If the URL fails validation
    """
    if not url or not isinstance(url, str):
        raise SSRFError("URL is empty or invalid")

    parsed = urlparse(url)

    # 1. Scheme validation — only HTTPS allowed
    if parsed.scheme not in ("https",):
        raise SSRFError(f"Only HTTPS URLs are allowed, got: {parsed.scheme}")

    # 2. Domain validation
    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL has no hostname")

    # Block IP-based URLs (e.g. https://169.254.169.254/)
    try:
        ipaddress.ip_address(hostname)
        raise SSRFError(f"Direct IP addresses are not allowed: {hostname}")
    except ValueError:
        pass  # Not an IP, it's a hostname — continue

    # 3. Domain whitelist check
    if not allow_any_https and hostname not in ALLOWED_DOMAINS:
        raise SSRFError(
            f"Domain '{hostname}' is not in the allowed list. "
            f"Allowed: {', '.join(sorted(ALLOWED_DOMAINS))}"
        )

    # 4. DNS resolution check — ensure resolved IP is not private
    try:
        addrinfo = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, _, _, _, sockaddr in addrinfo:
            ip_str = sockaddr[0]
            ip_addr = ipaddress.ip_address(ip_str)
            for network in BLOCKED_NETWORKS:
                if ip_addr in network:
                    raise SSRFError(
                        f"Domain '{hostname}' resolves to private IP {ip_str} "
                        f"(blocked network: {network})"
                    )
    except socket.gaierror:
        raise SSRFError(f"Cannot resolve domain: {hostname}")

    logger.debug(f"URL validated: {hostname}{parsed.path}")
    return url


def validate_media_url(url: str) -> str:
    """Convenience wrapper for media URL validation (Discord CDN only)."""
    return validate_url(url, allow_any_https=False)
