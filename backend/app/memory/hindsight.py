from __future__ import annotations

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional
import httpx
from app.config import get_settings

logger = logging.getLogger("contextiq.hindsight")
settings = get_settings()


class HindsightError(Exception):
    """Base exception for Hindsight Cloud operations."""
    pass


class HindsightAuthError(HindsightError):
    """Raised when Hindsight Cloud authentication fails (401/403)."""
    pass


class HindsightUnavailableError(HindsightError):
    """Raised when Hindsight Cloud is unreachable or times out."""
    pass


class HindsightClient:
    """
    Production adapter for Hindsight Cloud memory engine.
    Handles Retain and Recall operations against the authorized team memory bank.
    
    Architectural boundary: Only backend interacts with Hindsight Cloud.
    The frontend NEVER communicates with Hindsight directly.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.api_key = (api_key or settings.HINDSIGHT_API_KEY).strip()
        self.base_url = (base_url or settings.HINDSIGHT_BASE_URL).rstrip("/")
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        """Check if Hindsight service is configured."""
        return bool(self.base_url)

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers with authentication tokens without logging."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    async def check_health(self) -> bool:
        """Verify connectivity to Hindsight without exposing secrets."""
        if not self.is_configured:
            return False

        url = f"{self.base_url}/health"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers=self._get_headers())
                return res.status_code in (200, 204)
        except Exception:
            return False

    async def retain(
        self,
        bank_id: str,
        content: str,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Retain durable engineering context into the team's Hindsight memory bank.
        Executes one short retry on network/timeout failure before raising.
        """
        if not self.is_configured:
            raise HindsightUnavailableError("Hindsight base URL is not configured.")

        if not bank_id:
            raise ValueError("bank_id is required for Hindsight Retain.")

        clean_metadata = {str(k): str(v) for k, v in (metadata or {}).items()}

        payload = {
            "items": [
                {
                    "content": content,
                    "context": category or "general",
                    "metadata": clean_metadata,
                }
            ],
            "async": False,
            "content": content,
            "metadata": {**clean_metadata, "category": category or "general"},
            "tags": [category] if category else [],
            "context": category or "engineering_context",
        }

        # Official Hindsight endpoints followed by fallback variations
        endpoints = [
            f"{self.base_url}/v1/default/banks/{bank_id}/memories",
            f"{self.base_url}/v1/banks/{bank_id}/memories",
            f"{self.base_url}/v1/default/banks/{bank_id}/memories/retain",
            f"{self.base_url}/v1/banks/{bank_id}/memories/retain",
            f"{self.base_url}/v1/banks/{bank_id}/retain",
        ]

        last_error: Optional[Exception] = None

        # Attempt with 1 short retry
        for attempt in range(2):
            for endpoint in endpoints:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            endpoint,
                            headers=self._get_headers(),
                            json=payload,
                        )

                        if response.status_code in (200, 201, 202):
                            data = response.json() if response.content else {}
                            mem_id = data.get("id") or data.get("operation_id") or data.get("memory_id") or "retained"
                            return {
                                "id": str(mem_id),
                                "category": category or "general",
                                "text": content,
                                "status": "saved",
                            }

                        if response.status_code in (401, 403):
                            raise HindsightAuthError("Authentication to Hindsight Cloud failed. Verify HINDSIGHT_API_KEY.")

                        if response.status_code == 404 and endpoint != endpoints[-1]:
                            # Try next endpoint variation
                            continue

                        response.raise_for_status()

                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    last_error = e
                    if attempt == 0:
                        await asyncio.sleep(0.5)
                        break
                except HindsightAuthError:
                    raise
                except Exception as e:
                    last_error = e
                    if attempt == 0:
                        await asyncio.sleep(0.5)
                        break

        raise HindsightUnavailableError(f"Hindsight Retain failed: {type(last_error).__name__}")

    async def recall(
        self,
        bank_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories from the team's Hindsight memory bank.
        Executes one short retry on timeout/network error.
        Returns a normalized list of memories: [{"id": ..., "category": ..., "text": ...}].
        """
        if not self.is_configured:
            raise HindsightUnavailableError("Hindsight base URL is not configured.")

        if not bank_id:
            raise ValueError("bank_id is required for Hindsight Recall.")

        payload = {
            "query": query,
            "limit": limit,
            "budget": "mid",
        }

        endpoints = [
            f"{self.base_url}/v1/default/banks/{bank_id}/memories/recall",
            f"{self.base_url}/v1/banks/{bank_id}/memories/recall",
            f"{self.base_url}/v1/banks/{bank_id}/recall",
        ]

        last_error: Optional[Exception] = None

        # Attempt with 1 short retry
        for attempt in range(2):
            for endpoint in endpoints:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            endpoint,
                            headers=self._get_headers(),
                            json=payload,
                        )

                        if response.status_code in (401, 403):
                            raise HindsightAuthError("Authentication to Hindsight failed. Verify HINDSIGHT_API_KEY.")

                        if response.status_code == 404 and endpoint != endpoints[-1]:
                            continue

                        response.raise_for_status()
                        data = response.json()
                        return self._normalize_recall_results(data, query=query)

                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    last_error = e
                    if attempt == 0:
                        await asyncio.sleep(0.5)
                        break
                except HindsightAuthError:
                    raise
                except Exception as e:
                    last_error = e
                    if attempt == 0:
                        await asyncio.sleep(0.5)
                        break

        raise HindsightUnavailableError(f"Hindsight Recall failed: {type(last_error).__name__}")

    def _normalize_recall_results(self, data: Any, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Normalize various Hindsight response formats into ContextIQ standard shape."""
        items: List[Any] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            if "results" in data and isinstance(data["results"], list):
                items = data["results"]
            elif "memories" in data and isinstance(data["memories"], list):
                items = data["memories"]
            elif "data" in data and isinstance(data["data"], list):
                items = data["data"]
            elif "items" in data and isinstance(data["items"], list):
                items = data["items"]

        normalized: List[Dict[str, Any]] = []
        seen_texts = set()

        for idx, item in enumerate(items):
            if isinstance(item, str):
                text = item
                mem_id = f"mem_{idx + 1}"
                category = "fact"
                created_at = None
                source = None
            elif isinstance(item, dict):
                mem_id = item.get("id") or item.get("memory_id") or f"mem_{idx + 1}"
                text = item.get("text") or item.get("content") or item.get("summary") or item.get("document") or ""
                metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
                raw_cat = (item.get("category") or item.get("context") or metadata.get("category") or item.get("fact_type") or "").strip()
                created_at = item.get("mentioned_at") or item.get("date") or item.get("created_at") or item.get("updated_at")
                source_ids = item.get("source_memory_ids")
                source = source_ids[0] if (isinstance(source_ids, list) and source_ids) else metadata.get("source")

                # Normalize category taxonomy
                t_lower = text.lower()
                c_lower = raw_cat.lower()
                if any(k in c_lower for k in ["decision", "standardized on", "chose", "rejected"]) or "standardized on" in t_lower or "decision" in t_lower:
                    category = "decision"
                elif any(k in c_lower for k in ["preference", "prefer"]) or "postgres" in t_lower or "database" in t_lower or "preference" in t_lower:
                    category = "preference"
                elif any(k in c_lower for k in ["architecture", "stack", "fastapi", "backend"]) or "fastapi" in t_lower or "backend" in t_lower or "architecture" in t_lower:
                    category = "architecture"
                elif any(k in c_lower for k in ["incident", "outage", "issue", "root cause", "lesson"]) or "operational issue" in t_lower or "incident" in t_lower or "root cause" in t_lower:
                    category = "incident"
                elif any(k in c_lower for k in ["convention", "standard", "lint", "guideline"]):
                    category = "convention"
                elif raw_cat and raw_cat not in ("observation", "world", "general", "engineering_context"):
                    category = raw_cat
                else:
                    category = "fact"
            else:
                continue

            if not text:
                continue

            # Filter out internal extraction artifacts and metadata fragments
            t_lower = text.lower()
            if (
                any(n in t_lower for n in ["extract facts from", "team_id:", "conversation_id:", "test: ", "synthetic:"])
                or t_lower.startswith("context:")
                or t_lower.startswith("source:")
                or t_lower.startswith("event date:")
                or (text.strip().endswith("?") and any(text.strip().lower().startswith(p) for p in ("what ", "why ", "how ", "who ", "when ", "is there ", "do we ", "does ")))
            ):
                continue

            # Deduplicate by base text
            base_text = text.split(" (mentioned_at=")[0].strip()
            if not base_text or base_text in seen_texts:
                continue
            seen_texts.add(base_text)

            normalized.append({
                "id": str(mem_id),
                "category": str(category),
                "text": str(base_text),
                "created_at": str(created_at) if created_at else None,
                "source": str(source) if source else None,
            })

        # Rank by query relevance if query is provided
        if query and normalized:
            q_lower = query.lower()
            stop_words = {"the", "what", "is", "for", "this", "new", "our", "are", "and", "a", "an", "do", "we", "did", "use", "should", "can", "with", "to", "in", "on", "of", "how", "you", "me", "tell", "using"}
            q_tokens = set(re.findall(r"\b[a-z0-9_-]+\b", q_lower))

            scored = []
            for m in normalized:
                s = 0
                txt = m["text"].lower()
                txt_tokens = set(re.findall(r"\b[a-z0-9_-]+\b", txt))

                overlap = q_tokens.intersection(txt_tokens) - stop_words
                s += len(overlap) * 5

                # Specific engineering domain associations
                if any(k in q_tokens for k in ["queue", "queues", "job", "jobs", "bullmq", "background"]):
                    if any(k in txt_tokens for k in ["bullmq", "queue", "queues", "background"]):
                        s += 20
                if any(k in q_tokens for k in ["database", "databases", "db", "postgres", "postgresql", "transactional", "sql"]):
                    if any(k in txt_tokens for k in ["postgres", "postgresql", "database", "sql"]):
                        s += 20
                if any(k in q_tokens for k in ["backend", "api", "apis", "framework", "fastapi", "rest", "service", "services"]):
                    if any(k in txt_tokens for k in ["fastapi", "backend", "service", "services"]):
                        s += 20

                if s > 0:
                    scored.append((s, m))

            if scored:
                scored.sort(key=lambda x: x[0], reverse=True)
                return [m for _, m in scored]
            else:
                # If query is completely unrelated to any memories, return empty list
                return []

        return normalized

    async def list_memories(self, bank_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve accessible team memories from Hindsight.
        Falls back to broad query recall if explicit listing endpoint is unavailable.
        """
        if not self.is_configured:
            raise HindsightUnavailableError("Hindsight base URL is not configured.")

        # Try GET memories endpoint variations
        endpoints = [
            f"{self.base_url}/v1/default/banks/{bank_id}/memories/list",
            f"{self.base_url}/v1/banks/{bank_id}/memories/list",
            f"{self.base_url}/v1/default/banks/{bank_id}/memories",
            f"{self.base_url}/v1/banks/{bank_id}/memories",
        ]
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.get(endpoint, headers=self._get_headers())
                    if res.status_code == 200:
                        return self._normalize_recall_results(res.json())
            except Exception:
                pass

        # Fallback to broad recall
        try:
            return await self.recall(bank_id=bank_id, query="team decisions architecture preferences", limit=limit)
        except Exception:
            return []
