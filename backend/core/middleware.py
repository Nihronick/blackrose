from urllib.parse import urlparse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logging import get_logger

logger = get_logger("blackrose.core.middleware")

def setup_cors(app: FastAPI):
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://nihronick.github.io",
    ]

    if settings.FRONTEND_URL:
        for origin_entry in settings.FRONTEND_URL.split(","):
            entry = origin_entry.strip()
            if not entry:
                continue
            parsed = urlparse(entry)
            if parsed.scheme and parsed.netloc:
                base_origin = f"{parsed.scheme}://{parsed.netloc}"
                if base_origin not in cors_origins:
                    cors_origins.append(base_origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_origin_regex=r"https://(blackrosesl\.me|nihronick\.github\.io)|https://.*\.app\.github\.dev",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

def setup_honeybadger(app: FastAPI):
    if not settings.HONEYBADGER_API_KEY:
        return
    try:
        from honeybadger import honeybadger
        from honeybadger.contrib.asgi import ASGIHoneybadger
        import honeybadger.contrib.asgi as asgi_hb
        
        # Monkey-patch to fix KeyError caused by duplicate headers
        def patched_get_headers(scope):
            headers = {}
            for raw_key, raw_value in scope.get("headers", []):
                key = raw_key.decode("latin-1").lower()
                value = raw_value.decode("latin-1")
                if key in headers:
                    headers[key] = headers[key] + ", " + value
                else:
                    headers[key] = value
            return headers
        asgi_hb._get_headers = patched_get_headers

        honeybadger.configure(api_key=settings.HONEYBADGER_API_KEY, environment=settings.ENVIRONMENT)
        app.add_middleware(ASGIHoneybadger)
        logger.info("Honeybadger enabled.")
    except ImportError:
        logger.warning("Honeybadger not installed.")
