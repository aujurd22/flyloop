"""Memory leg: async MCP client to the sandbox FlyMemory instance + local mirror.

The facade is the only thing the cycle loop touches. If the HTTP service dies,
it degrades to an in-process keyword mirror so the 10h loop never stops, and
probes the service in the background to switch back.
"""
import asyncio
import re
import time

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from . import config as C


class ServiceDown(Exception):
    pass


class MemClient:
    """Persistent MCP streamable-http session with one-shot reconnect."""

    def __init__(self):
        self._http_ctx = None
        self.session = None

    async def connect(self):
        self._http_ctx = streamablehttp_client(C.MEM_URL)
        read, write, _ = await self._http_ctx.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await asyncio.wait_for(self.session.initialize(), timeout=20)

    async def close(self):
        for obj in (getattr(self, "session", None), getattr(self, "_http_ctx", None)):
            try:
                if obj is not None:
                    await obj.__aexit__(None, None, None)
            except Exception:
                pass
        self.session = None
        self._http_ctx = None

    async def call(self, name: str, args: dict, timeout: float = 30.0) -> str:
        if self.session is None:
            await self.connect()
        try:
            res = await asyncio.wait_for(self.session.call_tool(name, args), timeout=timeout)
        except Exception:
            await self.close()
            try:
                await self.connect()
                res = await asyncio.wait_for(self.session.call_tool(name, args), timeout=timeout)
            except Exception as e:
                raise ServiceDown(f"{name}: {e}") from e
        if getattr(res, "isError", False):
            raise ServiceDown(f"{name} tool error: {str(res.content)[:200]}")
        return "".join(getattr(c, "text", "") for c in res.content)


class LocalMirror:
    """Crude in-process fallback: token-overlap recall over stored texts."""

    def __init__(self):
        self.texts = {}
        self._next = 900000

    @staticmethod
    def _tok(s: str):
        return set(re.findall(r"[a-z0-9]{2,}", s.lower()))

    def remember(self, text: str, **kw) -> str:
        for t in self.texts.values():
            a, b = self._tok(text), self._tok(t)
            if a and b and len(a & b) / len(a | b) > 0.9:
                return f"[MERGED into #{next(iter('0'))}] dedup-local"
        i = self._next
        self._next += 1
        self.texts[i] = text
        return f"[NEW #{i}] stored-local"

    def recall(self, query: str, top_k: int = 5, compartment: str = "") -> str:
        q = self._tok(query)
        scored = []
        for i, t in self.texts.items():
            ov = len(q & self._tok(t))
            if ov:
                scored.append((ov, i, t))
        scored.sort(reverse=True)
        if not scored:
            return "No relevant memories found."
        return "\n".join(f"[#{i} | active | sim={min(1.0, ov / max(len(q), 1)):.2f} | "
                         f"just now | src=local | decay=0%] {t[:80]}"
                         for ov, i, t in scored[:top_k])

    def stats(self) -> str:
        return f"local-mirror entries={len(self.texts)}"


_ID = re.compile(r"\[#?(\d+)")


def parse_ids(resp: str):
    return [int(m) for m in _ID.findall(resp or "")]


def parse_recall(block: str):
    """-> list of (id, text) from recall output lines."""
    out = []
    for line in (block or "").splitlines():
        m = re.match(r"\[?#?(\d+)\s*\|.*?\]\s*(.*)", line)
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out


class MemFacade:
    def __init__(self, log=print):
        self.client = MemClient()
        self.local = LocalMirror()
        self.mode = "local"
        self.log = log
        self.stats_cache = {}

    async def start(self):
        try:
            await self.client.connect()
            self.mode = "http"
            self.log(f"[mem] connected to {C.MEM_URL}")
        except Exception as e:
            self.mode = "local"
            self.log(f"[mem] service down at start ({e}); degrading to local mirror")

    async def probe(self):
        """Background probe: switch back to http when the service returns."""
        if self.mode == "http":
            return
        try:
            await self.client.call("flymemory_stats", {}, timeout=10)
            self.mode = "http"
            self.log("[mem] service recovered; switching back to http mode")
        except Exception:
            pass

    async def remember(self, text, tags="", compartment="", state_key="", state_value=""):
        args = {"text": text, "tags": tags, "compartment": compartment,
                "state_key": state_key, "state_value": state_value}
        if self.mode == "http":
            try:
                return await self.client.call("flymemory_remember", args), "http"
            except ServiceDown as e:
                self.log(f"[mem] remember failed ({e}); degrading to local")
                self.mode = "local"
        return self.local.remember(text), "local"

    async def recall(self, query, top_k=C.RECALL_TOPK, compartment=""):
        if self.mode == "http":
            try:
                block = await self.client.call(
                    "flymemory_recall", {"query": query, "top_k": top_k,
                                         "compartment": compartment})
                return block, "http"
            except ServiceDown as e:
                self.log(f"[mem] recall failed ({e}); degrading to local")
                self.mode = "local"
        return self.local.recall(query, top_k, compartment), "local"
    async def consolidate(self, memory_ids, conclusion):
        if self.mode == "http":
            try:
                return await self.client.call(
                    "flymemory_consolidate",
                    {"memory_ids": [int(i) for i in memory_ids],
                     "conclusion": conclusion}), "http"
            except ServiceDown:
                self.mode = "local"
        return f"[local-skip] consolidate({list(memory_ids)[:4]}...)", "local"

    async def supersede(self, old_id, new_id):
        if self.mode == "http":
            try:
                return await self.client.call(
                    "flymemory_supersede",
                    {"old_memory_id": int(old_id), "new_memory_id": int(new_id)}), "http"
            except ServiceDown:
                self.mode = "local"
        return "[local-skip] supersede", "local"

    async def stats(self):
        if self.mode == "http":
            try:
                return await self.client.call("flymemory_stats", {}), "http"
            except ServiceDown:
                self.mode = "local"
        return self.local.stats(), "local"

    async def state_lookup(self, state_key):
        """V4 direct entity-state lookup (no truncation on this path)."""
        if self.mode == "http":
            try:
                return await self.client.call("flymemory_state_lookup",
                                              {"state_key": state_key}), "http"
            except ServiceDown:
                self.mode = "local"
        # local mirror has no state tier: degrade to keyword recall by key
        return self.local.recall(state_key, top_k=1), "local"

    async def close(self):
        """Must be awaited from the same task that opened the connection."""
        try:
            await self.client.close()
        except Exception:
            pass
