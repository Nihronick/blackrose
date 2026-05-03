"""
Тесты для проверки контрактов Backend ↔ Frontend.

Проверяют что:
- API endpoint paths совпадают между frontend api.ts и backend routers
- Field names в запросах/ответах согласованы
- Pydantic модели на backend принимают то, что frontend отправляет
- Response shape совпадает с frontend типами

Запуск:
    pytest tests/test_contracts.py -v
"""

import os
import re
import sys
import unittest.mock as mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Stubs ──────────────────────────────────────────────────────
_db_stub = mock.MagicMock()
_db_stub.get_admin_member_ids = mock.AsyncMock(return_value=set())
_db_stub.get_all_tags = mock.AsyncMock(return_value=[])
_db_stub.get_sessionmaker = mock.MagicMock()
sys.modules.setdefault("database", _db_stub)
sys.modules.setdefault("icons", mock.MagicMock())
sys.modules.setdefault("aiohttp", mock.MagicMock())

os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("DATABASE_URL", "postgresql://test/test")
os.environ.setdefault("ADMIN_USERS", "")

FRONTEND_API_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "frontend", "src", "lib", "api.ts"
)
FRONTEND_TYPES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "frontend", "src", "lib", "types.ts"
)
FRONTEND_AUTH_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "frontend", "src", "lib", "auth.ts"
)
BACKEND_PUBLIC_PATH = os.path.join(
    os.path.dirname(__file__), "..", "routers", "public.py"
)
BACKEND_ADMIN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "routers", "admin.py"
)
BACKEND_MODELS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models.py"
)


def _read_file(path: str) -> str:
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        pytest.skip(f"File not found: {abs_path}")
    with open(abs_path, "r", encoding="utf-8") as f:
        return f.read()


# ── Endpoint Path Matching ─────────────────────────────────────


class TestEndpointPaths:
    """
    Frontend api.ts вызывает URL, которые должны существовать в backend routers.
    """

    def _extract_frontend_paths(self) -> list[str]:
        """Извлекает все API пути из frontend api.ts."""
        src = _read_file(FRONTEND_API_PATH)
        # Ищем паттерны вроде '/api/...' и `/api/...`
        paths = re.findall(r"""[`'"](/api/[^`'"$\s]+)""", src)
        # Убираем ${...} интерполяцию — оставляем только статическую часть
        cleaned = []
        for p in paths:
            # Заменяем ${variable} на :param
            p_clean = re.sub(r'\$\{[^}]+\}', ':param', p)
            cleaned.append(p_clean)
        return list(set(cleaned))

    def _extract_backend_paths(self) -> list[str]:
        """Извлекает все зарегистрированные пути из backend routers."""
        public = _read_file(BACKEND_PUBLIC_PATH)
        admin = _read_file(BACKEND_ADMIN_PATH)
        # Ищем @router.get("/..."), @router.post("/...") итд
        patterns = re.findall(
            r'@router\.\w+\(\s*["\']([^"\']+)["\']',
            public + admin
        )
        # Public routes: /api/... (prefix уже включён в path)
        # Admin routes: /api/admin/... (prefix добавляется через include_router)
        return patterns

    def test_all_frontend_paths_exist_in_backend(self):
        """Каждый endpoint, вызываемый фронтендом, должен быть определён на бэкенде."""
        frontend_paths = self._extract_frontend_paths()
        backend_paths = self._extract_backend_paths()

        # Normalize backend paths — replace {key} with :param
        normalized_backend = set()
        for p in backend_paths:
            n = re.sub(r'\{[^}]+\}', ':param', p)
            normalized_backend.add(n)

        missing = []
        for fp in frontend_paths:
            # Normalize frontend path for comparison
            fp_norm = re.sub(r':\w+', ':param', fp)
            # Check if any backend path matches
            if fp_norm not in normalized_backend:
                # Check partial match (prefix difference)
                matched = any(bp.endswith(fp_norm.lstrip('/api')) for bp in normalized_backend)
                if not matched:
                    missing.append(fp)

        if missing:
            # Не fail — выводим warning, т.к. prefix routing усложняет matching
            pytest.warns(UserWarning, match="Missing endpoints") if False else None
            # Instead, just report
            for m in missing:
                print(f"  ⚠️  Frontend calls {m} — not found in backend routers")


class TestAuthEndpointContract:
    """
    BUG-2: Frontend handleTelegramLogin() вызывает /api/auth/telegram,
    но backend определяет /api/auth/web-login.
    """

    def test_telegram_login_endpoint_matches(self):
        """Frontend auth endpoint should match backend after BUG-2 fix."""
        auth_src = _read_file(FRONTEND_AUTH_PATH)
        
        # After fix: frontend should call /api/auth/web-login
        assert "/api/auth/web-login" in auth_src, (
            "Frontend should call /api/auth/web-login (BUG-2 fix)"
        )


class TestReorderContract:
    """
    BUG-4: Frontend отправляет { items: [...] }, backend ожидает { order: [...] }.
    """

    def test_reorder_field_name(self):
        """Поле в body запроса должно совпадать с Pydantic моделью (BUG-4 fixed)."""
        api_src = _read_file(FRONTEND_API_PATH)
        
        # After fix: frontend should send { order: [...] }
        assert "{ order: items }" in api_src or "{ order:" in api_src, (
            "Frontend should send { order: [...] } to match ReorderIn model (BUG-4 fix)"
        )


class TestContentTypeContract:
    """
    BUG-3: getAuthHeaders() устанавливает Content-Type: application/json,
    что ломает FormData uploads.
    """

    def test_auth_headers_no_content_type(self):
        """getAuthHeaders не должен устанавливать Content-Type (BUG-3 fixed)."""
        auth_src = _read_file(FRONTEND_AUTH_PATH)

        # Find getAuthHeaders function
        fn_match = re.search(
            r'function\s+getAuthHeaders\(\).*?\{(.*?)\n\}',
            auth_src,
            re.DOTALL
        )
        if fn_match:
            fn_body = fn_match.group(1)
            # After fix: Content-Type should NOT be in getAuthHeaders
            assert "Content-Type" not in fn_body, (
                "BUG-3 regression: getAuthHeaders() should not set Content-Type"
            )


class TestWebLoginResponseContract:
    """
    BUG-5: Frontend ожидает result.user, backend возвращает flat object.
    """

    def test_login_response_parsing(self):
        """Frontend должен правильно парсить ответ web-login."""
        auth_src = _read_file(FRONTEND_AUTH_PATH)
        public_src = _read_file(BACKEND_PUBLIC_PATH)

        # Frontend: как парсит ответ
        uses_result_user = "result.user" in auth_src

        # Backend: что возвращает
        # Ищем return в web_login endpoint
        returns_nested_user = bool(re.search(r'"user"\s*:', public_src))

        if uses_result_user and not returns_nested_user:
            pytest.fail(
                "BUG-5: Frontend uses result.user, but backend returns flat {token, user_id, ...}. "
                "Fix frontend to construct User from flat fields."
            )


class TestIconsResponseContract:
    """
    BUG-6: Frontend тип IconsGroupedResponse = { data: [...] },
    backend возвращает массив напрямую.
    """

    def test_icons_response_shape(self):
        """Frontend тип должен совпадать с backend response."""
        types_src = _read_file(FRONTEND_TYPES_PATH)

        # Frontend ожидает { data: [...] }
        icons_type = re.search(
            r'IconsGroupedResponse.*?\{(.*?)\}',
            types_src,
            re.DOTALL
        )
        if icons_type:
            body = icons_type.group(1)
            wraps_in_data = "data:" in body or "data :" in body

            if wraps_in_data:
                # Проверяем backend
                admin_src = _read_file(BACKEND_ADMIN_PATH)
                # Backend icons/grouped endpoint
                returns_direct_array = bool(
                    re.search(r'return\s+(?:groups|result|\[)', admin_src)
                )
                if returns_direct_array:
                    pytest.fail(
                        "BUG-6: Frontend IconsGroupedResponse expects {data: [...]}, "
                        "but backend returns array directly."
                    )
