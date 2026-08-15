"""
AIO Sandbox client — обёртка над agent-sandbox SDK.

Даёт агентам BlackRose доступ к изолированному окружению:
  - Shell: выполнение команд
  - File: чтение/запись файлов
  - Browser: автоматизация и скриншоты
  - Code: безопасное выполнение Python/Node.js

Пример использования:
    from services.sandbox.client import sandbox_client
    result = await sandbox_client.run_shell("ls -la /workspace")
    print(result)
"""
from __future__ import annotations

import logging
from typing import Optional

from core.config import settings

logger = logging.getLogger("blackrose.sandbox")


class SandboxClient:
    """Ленивый singleton-клиент для AIO Sandbox."""

    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        """Lazy-инициализация SDK-клиента."""
        if self._client is None:
            try:
                from agent_sandbox import Sandbox
                self._client = Sandbox(
                    base_url=settings.SANDBOX_URL,
                    api_key=settings.SANDBOX_API_KEY,
                )
                logger.info(
                    "Sandbox client initialized",
                    extra={"url": settings.SANDBOX_URL},
                )
            except ImportError:
                logger.warning(
                    "agent-sandbox SDK not installed. "
                    "Install with: pip install agent-sandbox"
                )
                raise
            except Exception as exc:
                logger.error(
                    "Failed to init sandbox client: %s", exc,
                    exc_info=True,
                )
                raise
        return self._client

    # ── Shell ──────────────────────────────────────────────

    async def run_shell(self, command: str) -> str:
        """Выполнить shell-команду в sandbox и вернуть stdout."""
        client = self._get_client()
        result = client.shell.exec_command(command=command)
        output = result.data.output if result.data else ""
        logger.debug("shell: %s → %s", command, output[:200])
        return output

    # ── File ───────────────────────────────────────────────

    async def read_file(self, path: str) -> str:
        """Прочитать файл из sandbox."""
        client = self._get_client()
        result = client.file.read_file(file=path)
        return result.data.content if result.data else ""

    async def write_file(self, path: str, content: str) -> bool:
        """Записать файл в sandbox."""
        client = self._get_client()
        try:
            client.file.write_file(file=path, content=content)
            return True
        except Exception as exc:
            logger.error("write_file failed: %s", exc)
            return False

    # ── Browser ────────────────────────────────────────────

    async def screenshot(self) -> Optional[bytes]:
        """Сделать скриншот браузера в sandbox."""
        client = self._get_client()
        try:
            result = client.browser.screenshot()
            return result.data if result.data else None
        except Exception as exc:
            logger.warning("screenshot failed: %s", exc)
            return None

    async def navigate(self, url: str) -> bool:
        """Перейти на URL в браузере sandbox."""
        client = self._get_client()
        try:
            client.browser.goto(url=url)
            return True
        except Exception as exc:
            logger.warning("navigate failed: %s", exc)
            return False

    # ── Code Execution ─────────────────────────────────────

    async def run_python(self, code: str) -> str:
        """Выполнить Python-код в изолированном sandbox."""
        client = self._get_client()
        try:
            result = client.shell.exec_command(
                command=f'python3 -c "{code}"'
            )
            return result.data.output if result.data else ""
        except Exception as exc:
            logger.error("run_python failed: %s", exc)
            return f"Error: {exc}"

    # ── Health ─────────────────────────────────────────────

    async def health_check(self) -> dict:
        """Проверить доступность sandbox."""
        try:
            client = self._get_client()
            ctx = client.sandbox.get_context()
            return {
                "status": "ok",
                "home_dir": ctx.home_dir if ctx else "unknown",
                "url": settings.SANDBOX_URL,
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
                "url": settings.SANDBOX_URL,
            }


# Singleton
sandbox_client = SandboxClient()
