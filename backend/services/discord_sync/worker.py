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

    async def fetch_channel_history(self, channel_id: str, limit: int = 30) -> dict:
        """
        Fetch recent messages or forum posts from Discord channel/forum via REST API using stealth user token.
        Supports: Forum Channels (Type 15), Threads (Type 11/12), and Text Channels (Type 0/5).
        Returns {"ok": True, "processed": N, "message": "..."} or {"ok": False, "error": "..."}
        """
        if not self.user_token:
            return {"ok": False, "error": "Токен Discord не указан"}

        headers = {
            "Authorization": self.user_token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # 1. Fetch channel metadata to determine type
                ch_url = f"https://discord.com/api/v10/channels/{channel_id}"
                async with session.get(ch_url, headers=headers) as ch_resp:
                    if ch_resp.status == 401:
                        return {"ok": False, "error": "Недействительный токен Discord (HTTP 401)"}
                    if ch_resp.status == 403:
                        return {"ok": False, "error": f"Нет доступа к каналу {channel_id} (HTTP 403 - аккаунт не состоит на сервере или нет прав)"}
                    if ch_resp.status == 404:
                        return {"ok": False, "error": f"Канал {channel_id} не найден в Discord (HTTP 404)"}
                    if ch_resp.status != 200:
                        err_body = await ch_resp.text()
                        return {"ok": False, "error": f"Ошибка Discord API (HTTP {ch_resp.status}): {err_body[:100]}"}

                    ch_data = await ch_resp.json()

                ch_type = ch_data.get("type", 0)
                guild_id = ch_data.get("guild_id")
                processed_count = 0

                # 2. Case A: Forum Channel (Type 15)
                if ch_type == 15:
                    logger.info(f"Channel {channel_id} is a Discord Forum Channel (Type 15). Fetching forum posts/threads...")
                    threads_to_process = []

                    # Fetch active threads
                    if guild_id:
                        active_url = f"https://discord.com/api/v10/guilds/{guild_id}/threads/active"
                        async with session.get(active_url, headers=headers) as t_resp:
                            if t_resp.status == 200:
                                t_data = await t_resp.json()
                                for th in t_data.get("threads", []):
                                    if str(th.get("parent_id")) == str(channel_id):
                                        threads_to_process.append(th)

                    # Fetch archived public threads
                    archived_url = f"https://discord.com/api/v10/channels/{channel_id}/threads/archived/public"
                    async with session.get(archived_url, headers=headers) as a_resp:
                        if a_resp.status == 200:
                            a_data = await a_resp.json()
                            for th in a_data.get("threads", []):
                                if not any(t["id"] == th["id"] for t in threads_to_process):
                                    threads_to_process.append(th)

                    logger.info(f"Found {len(threads_to_process)} forum threads in channel {channel_id}")

                    for th in threads_to_process:
                        thread_id = th.get("id")
                        thread_name = th.get("name", "Форум Гайд")
                        msgs_url = f"https://discord.com/api/v10/channels/{thread_id}/messages?limit=50"
                        async with session.get(msgs_url, headers=headers) as m_resp:
                            if m_resp.status == 200:
                                msgs = await m_resp.json()
                                if isinstance(msgs, list) and msgs:
                                    msgs.sort(key=lambda x: x.get("id", ""))
                                    starter_msg = msgs[0]
                                    combined_content = "\n\n".join(
                                        m.get("content", "") for m in msgs if m.get("content")
                                    )
                                    starter_msg["content"] = combined_content or starter_msg.get("content", "")
                                    res = await discord_sync_service.process_discord_message(
                                        starter_msg, parent_channel_id=channel_id, custom_title=thread_name
                                    )
                                    if not res.get("skipped"):
                                        processed_count += 1

                    return {
                        "ok": True,
                        "processed": processed_count,
                        "message": f"Форум-канал {channel_id} обработан: получено {len(threads_to_process)} тем, импортировано {processed_count} гайдов",
                    }

                # 3. Case B: Single Thread / Post (Type 11 or 12)
                elif ch_type in (11, 12):
                    thread_name = ch_data.get("name", "Гайд")
                    parent_id = ch_data.get("parent_id")
                    msgs_url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=50"
                    async with session.get(msgs_url, headers=headers) as m_resp:
                        if m_resp.status == 200:
                            msgs = await m_resp.json()
                            if isinstance(msgs, list) and msgs:
                                msgs.sort(key=lambda x: x.get("id", ""))
                                starter_msg = msgs[0]
                                combined_content = "\n\n".join(m.get("content", "") for m in msgs if m.get("content"))
                                starter_msg["content"] = combined_content or starter_msg.get("content", "")
                                res = await discord_sync_service.process_discord_message(
                                    starter_msg, parent_channel_id=parent_id or channel_id, custom_title=thread_name
                                )
                                if not res.get("skipped"):
                                    processed_count += 1
                    return {
                        "ok": True,
                        "processed": processed_count,
                        "message": f"Тема {channel_id} обработана: импортировано {processed_count} гайдов",
                    }

                # 4. Case C: Standard Text / Announcement Channel (Type 0, 5, etc.)
                else:
                    msgs_url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
                    async with session.get(msgs_url, headers=headers) as m_resp:
                        if m_resp.status != 200:
                            err_body = await m_resp.text()
                            return {"ok": False, "error": f"Ошибка получения сообщений (HTTP {m_resp.status}): {err_body[:100]}"}

                        messages = await m_resp.json()
                        if isinstance(messages, list):
                            for msg in reversed(messages):
                                if isinstance(msg, dict) and msg.get("content"):
                                    res = await discord_sync_service.process_discord_message(msg)
                                    if not res.get("skipped"):
                                        processed_count += 1

                    return {
                        "ok": True,
                        "processed": processed_count,
                        "message": f"Текстовый канал {channel_id} обработан: импортировано {processed_count} новых гайдов",
                    }

        except Exception as e:
            logger.error(f"Exception during fetch_channel_history for {channel_id}: {e}", exc_info=True)
            return {"ok": False, "error": f"Исключение при сканировании: {str(e)}"}

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

                        # Reset retry delay on successful connection
                        retry_delay = 5

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
