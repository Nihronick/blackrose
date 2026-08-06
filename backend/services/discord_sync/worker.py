import asyncio
import json
import random
import aiohttp
from core.logging import get_logger
from services.discord_sync.service import discord_sync_service

logger = get_logger("blackrose.services.discord_sync.worker")

class StealthDiscordWorker:
    """
    Stealth Passive Listener for Discord Gateway WebSocket.
    Spoofs standard Chrome Desktop client payload (op: 2) to passively listen to MESSAGE_CREATE / MESSAGE_UPDATE.
    Sends 0 outbound messages to guarantee account safety.
    """
    def __init__(self):
        self.user_token: str | None = None
        self.running: bool = False
        self.task: asyncio.Task | None = None

    def set_token(self, token: str):
        self.user_token = token.strip()

    async def start(self, user_token: str | None = None):
        if user_token:
            self.user_token = user_token
        if not self.user_token:
            logger.warning("Discord worker start requested without user_token")
            return False

        if self.running:
            logger.info("Discord worker is already running")
            return True

        self.running = True
        self.task = asyncio.create_task(self._run_loop())
        logger.info("Stealth Discord Gateway worker started")
        return True

    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
        logger.info("Stealth Discord Gateway worker stopped")

    async def _run_loop(self):
        ws_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        retry_delay = 5

        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(ws_url, headers=headers) as ws:
                        logger.info("Connected to Discord Gateway WebSocket")
                        
                        # Wait for HELLO (op: 10)
                        hello_msg = await ws.receive_json()
                        if hello_msg.get("op") != 10:
                            logger.error(f"Unexpected initial op: {hello_msg}")
                            await asyncio.sleep(retry_delay)
                            continue

                        heartbeat_interval = hello_msg["d"]["heartbeat_interval"] / 1000.0

                        # Send IDENTIFY (op: 2) spoofing Chrome Desktop
                        identify_payload = {
                            "op": 2,
                            "d": {
                                "token": self.user_token,
                                "capabilities": 16381,
                                "properties": {
                                    "os": "Windows",
                                    "browser": "Chrome",
                                    "device": "",
                                    "system_locale": "en-US",
                                    "browser_user_agent": headers["User-Agent"],
                                    "browser_version": "122.0.0.0",
                                    "os_version": "10",
                                },
                                "presence": {
                                    "status": "online",
                                    "since": 0,
                                    "activities": [],
                                    "afk": False,
                                },
                                "compress": False,
                            },
                        }
                        await ws.send_json(identify_payload)

                        # Start heartbeat task
                        heartbeat_task = asyncio.create_task(self._heartbeat_loop(ws, heartbeat_interval))

                        try:
                            # Event listening loop
                            async for msg in ws:
                                if not self.running:
                                    break
                                if msg.type == aiohttp.WSMsgType.TEXT:
                                    data = json.loads(msg.data)
                                    op = data.get("op")
                                    event_type = data.get("t")
                                    payload = data.get("d")

                                    if op == 1:
                                        # Server requested immediate heartbeat
                                        await ws.send_json({"op": 1, "d": None})

                                    elif op == 0 and event_type in ("MESSAGE_CREATE", "MESSAGE_UPDATE", "THREAD_CREATE", "THREAD_UPDATE"):
                                        # Inbound message event!
                                        if isinstance(payload, dict):
                                            asyncio.create_task(
                                                discord_sync_service.process_discord_message(payload)
                                            )
                                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                    break
                        finally:
                            heartbeat_task.cancel()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Discord Gateway connection error: {e}. Reconnecting in {retry_delay}s...")
                await asyncio.sleep(retry_delay + random.uniform(1, 3))
                retry_delay = min(retry_delay * 2, 60)

    async def _heartbeat_loop(self, ws: aiohttp.ClientWebSocketResponse, interval: float):
        sequence = None
        while self.running:
            try:
                await asyncio.sleep(interval)
                await ws.send_json({"op": 1, "d": sequence})
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Discord heartbeat error: {e}")
                break


stealth_discord_worker = StealthDiscordWorker()
