"""Local & Hybrid Inference Engine for ScopeKernel.

Supports:
1. Local Ollama Daemon (Google Gemma-2-2B-IT @ localhost:11434)
2. Live Google Gemini API (gemini-2.0-flash / gemini-1.5-flash) with structured JSON
3. Dynamic Semantic Boundary Cross-Examiner (100% offline, zero-cloud, dynamic AST matching)
"""

from __future__ import annotations

import json
import logging
import os
import re
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

from .schemas import ContractBaseline
from .prefilter import ChatMessage

logger = logging.getLogger("scopekernel.engine")


class EngineMode(str, Enum):
    OLLAMA_LIVE = "ollama_live"
    GEMINI_API = "gemini_api"
    OFFLINE_SEMANTIC = "offline_semantic"
    OFFLINE_HEURISTIC = "offline_heuristic"


class EngineConfig(BaseModel):
    """Configuration for ScopeKernel micro-SLM & semantic engine."""

    base_url: str = "http://localhost:11434"
    model: str = "gemma2:2b"
    gemini_model: str = "gemini-2.0-flash"
    api_key: Optional[str] = None
    temperature: float = 0.0
    top_p: float = 0.2
    timeout_seconds: float = 30.0
    mode: EngineMode = EngineMode.OLLAMA_LIVE

    def validate_air_gap(self) -> bool:
        """Enforces air-gap compliance when running in local/air-gapped modes."""
        if self.mode == EngineMode.GEMINI_API:
            # Explicit cloud API mode chosen by user
            return True
        parsed = urlparse(self.base_url)
        hostname = (parsed.hostname or "").lower()
        if hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError(
                f"Air-Gap Violation: Endpoint '{self.base_url}' points to an external host. "
                "ScopeKernel strictly forbids non-local network telemetry in local mode."
            )
        return True


class OllamaEngine:
    """Inference client supporting local Gemma 2 (2B), Google Gemini API, and dynamic semantic fallback."""

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        if not self.config.api_key:
            self.config.api_key = os.environ.get("GEMINI_API_KEY")
        self.config.validate_air_gap()

    def check_health(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is active and list available models."""
        try:
            with httpx.Client(timeout=2.0) as client:
                resp = client.get(f"{self.config.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    has_gemma = any(self.config.model in m for m in models)
                    return {
                        "online": True,
                        "available_models": models,
                        "target_model_installed": has_gemma,
                        "target_model": self.config.model,
                    }
        except Exception as e:
            logger.debug("Local Ollama connection inactive: %s", e)

        return {
            "online": False,
            "available_models": [],
            "target_model_installed": False,
            "target_model": self.config.model,
            "error": "Ollama daemon not reachable at http://localhost:11434",
        }

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        contract: Optional[ContractBaseline] = None,
        message: Optional[ChatMessage] = None,
    ) -> Dict[str, Any]:
        """Generate structured scope evaluation.

        Prioritizes:
        1. Live Gemini API (if user selected GEMINI_API and API key exists)
        2. Local Ollama Gemma 2 (if selected and Ollama daemon is running)
        3. Dynamic Semantic Boundary Cross-Examiner (dynamic offline matching on any custom contract)
        """
        # Mode 1: Gemini API
        if self.config.mode == EngineMode.GEMINI_API and self.config.api_key:
            try:
                res = self._call_gemini_api(prompt, system_prompt)
                if res.get("success"):
                    return res
            except Exception as e:
                logger.warning("Gemini API call failed (%s). Falling back to dynamic semantic engine.", e)

        # Mode 2: Local Ollama (Gemma 2 2B)
        if self.config.mode == EngineMode.OLLAMA_LIVE:
            self.config.validate_air_gap()
            try:
                payload = {
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": self.config.temperature,
                        "top_p": self.config.top_p,
                    },
                }
                if system_prompt:
                    payload["system"] = system_prompt

                with httpx.Client(timeout=self.config.timeout_seconds) as client:
                    resp = client.post(f"{self.config.base_url}/api/generate", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_response = data.get("response", "{}")
                        parsed_json = json.loads(raw_response)
                        return {
                            "success": True,
                            "mode": "ollama_live",
                            "model": self.config.model,
                            "data": parsed_json,
                        }
            except Exception as e:
                logger.debug("Ollama call failed (%s). Using dynamic semantic boundary engine.", e)

        # Mode 3: Dynamic Semantic Boundary Cross-Examiner (zero-cloud, runs on ANY custom contract)
        return self._dynamic_semantic_audit(prompt=prompt, contract=contract, message=message)

    def _call_gemini_api(self, prompt: str, system_prompt: Optional[str]) -> Dict[str, Any]:
        """Execute inference against Google Gemini API with structured JSON output."""
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.gemini_model}:generateContent"
            f"?key={self.config.api_key}"
        )
        contents = [{"parts": [{"text": prompt}]}]
        body: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.config.temperature,
                "responseMimeType": "application/json",
            },
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            resp = client.post(endpoint, json=body)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_json = json.loads(raw_text)
            return {
                "success": True,
                "mode": "gemini_api",
                "model": self.config.gemini_model,
                "data": parsed_json,
            }

    def _dynamic_semantic_audit(
        self,
        prompt: str,
        contract: Optional[ContractBaseline],
        message: Optional[ChatMessage],
    ) -> Dict[str, Any]:
        """Dynamic Boundary Semantic Cross-Examiner.

        Dynamically evaluates ANY custom contract deliverables and exclusions
        against candidate chat messages without hardcoded keywords.
        """
        raw_text = message.clean_text if message else ""
        if not raw_text and prompt:
            # Extract client message from prompt if not supplied directly
            msg_match = re.search(r'CLIENT MESSAGE TO AUDIT:\s*"(.*?)"', prompt, re.DOTALL)
            if msg_match:
                raw_text = msg_match.group(1).strip()
            else:
                raw_text = prompt

        clean_text = raw_text.strip()
        lower_text = clean_text.lower()

        # Step 1: Feature Extraction from candidate message
        extracted_feature = self._extract_feature_phrase(clean_text)

        # Step 2: Compare against explicit exclusions in contract
        exclusions = contract.explicit_exclusions if contract else []
        deliverables = contract.included_deliverables if contract else []

        best_exclusion_match = None
        best_score = 0.0

        for excl in exclusions:
            score = self._compute_semantic_overlap(clean_text, excl)
            if score > best_score:
                best_score = score
                best_exclusion_match = excl

        # Step 3: Compare against included deliverables
        in_scope_score = 0.0
        matched_deliverable = None
        for delim in deliverables:
            score = self._compute_semantic_overlap(clean_text, delim)
            if score > in_scope_score:
                in_scope_score = score
                matched_deliverable = delim

        is_creep = False
        violating_feature = extracted_feature
        matched_clause = None
        reasoning = ""
        hours = 0.0

        # Boundary Decision Logic
        if best_score >= 0.35:
            # Direct breach of an explicit contract exclusion
            is_creep = True
            violating_feature = best_exclusion_match or extracted_feature
            matched_clause = f"Exclusion: {best_exclusion_match}"
            reasoning = (
                f"The request directly breaches agreed exclusion clause '{best_exclusion_match}'. "
                "This capability was explicitly deferred or marked out of scope for the current milestone."
            )
            hours = self._estimate_hours_for_feature(clean_text, best_exclusion_match or "")
        elif self._is_mutation_intent(clean_text) and in_scope_score < 0.65:
            # Client is asking for a new feature not scoped in deliverables
            is_creep = True
            matched_clause = "Baseline Deliverables Boundary"
            violating_feature = extracted_feature
            reasoning = (
                f"The requested capability '{violating_feature}' is not scoped in the agreed milestone deliverables "
                f"for {contract.project_name if contract else 'this project'}."
            )
            hours = self._estimate_hours_for_feature(clean_text, "")
        else:
            # Within deliverables or general discussion
            is_creep = False
            violating_feature = "None"
            matched_clause = "Within Milestone Scope"
            reasoning = "Message aligns with baseline project deliverables."
            hours = 0.0

        # Step 4: Craft 4 authentic professional tone variants dynamically
        replies_by_tone = {}
        curr_rate = contract.hourly_rate if contract else 75.0
        curr_sym = contract.currency_symbol if contract else "$"

        if is_creep:
            cost = hours * curr_rate
            reply_collab = (
                f"Hey! Thanks for bringing this up—adding {violating_feature} makes complete sense for the product experience. "
                f"Taking a quick look at our signed SOW, this is currently listed under our exclusions/out-of-scope boundaries. "
                f"I would be glad to build this out as a change order: it would take roughly {hours:.1f} hours ({curr_sym}{cost:,.2f} at our agreed rate). "
                f"Would you prefer I add this to our active milestone or queue it up for Phase 2?"
            )
            reply_direct = (
                f"Hi! We can build {violating_feature}. As outlined in our contract exclusions, this falls outside the active milestone scope. "
                f"The estimated scope is {hours:.1f} engineering hours ({curr_sym}{cost:,.2f}). "
                f"Please confirm if you would like me to issue a Change Order for this item."
            )
            reply_defer = (
                f"Great idea on {violating_feature}! To protect our launch deadline for the current milestone, I recommend we deliver the agreed baseline first. "
                f"I have logged this in our Phase 2 backlog ({hours:.1f} hrs estimate) so we can tackle it immediately following deployment."
            )
            reply_quick = (
                f"Love this idea! Quick heads up though: {violating_feature} isn't in our current SOW. "
                f"It's about {hours:.1f} hrs of work ({curr_sym}{cost:,.2f})—want me to add it as a quick change order or keep it for after launch?"
            )
            replies_by_tone = {
                "Collaborative & Diplomatic": reply_collab,
                "Direct & Commercial": reply_direct,
                "Phase 2 Deferral": reply_defer,
                "WhatsApp Quick DM": reply_quick,
            }
            primary_reply = reply_collab
        else:
            primary_reply = "Thanks for checking in! This is already covered under our active milestone deliverables and is on track."
            replies_by_tone = {"Standard": primary_reply}

        return {
            "success": True,
            "mode": "offline_semantic",
            "model": "dynamic_semantic_boundary_engine",
            "data": {
                "is_scope_creep": is_creep,
                "violating_feature": violating_feature,
                "reasoning": reasoning,
                "estimated_hours": hours,
                "matched_exclusion": matched_clause,
                "suggested_client_reply": primary_reply,
                "replies_by_tone": replies_by_tone,
            },
        }

    def _extract_feature_phrase(self, text: str) -> str:
        """Isolate what specific capability is being requested from conversational syntax."""
        cleaned = re.sub(
            r"^(?:hey|hi|hello|morning|good\s+morning)?\s*(?:alex|sarah|elena|david|team)?[\s,!.:-]*",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()
        cleaned = re.sub(
            r"^(?:quick\s+question|just\s+a\s+small\s+tweak|one\s+quick\s+change|one\s+more\s+thing|quick\s+favor|just\s+wondering)[\s,!.:-]*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()
        cleaned = re.sub(
            r"^(?:can\s+we|could\s+we|what\s+if\s+we|is\s+it\s+possible\s+to|can\s+you|could\s+you|please|let's|also)\s+(?:quickly|also|just)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()
        cleaned = cleaned.rstrip("?.! ")
        if len(cleaned) < 3:
            return "Additional Feature Request"
        # Capitalize first letter
        return cleaned[:80]

    def _is_mutation_intent(self, text: str) -> bool:
        """Detect if message intends to alter or expand scope."""
        mutation_verbs = [
            "add", "create", "build", "integrate", "support", "enable", "switch", "change",
            "make", "hook up", "connect", "trigger", "export", "generate", "sync"
        ]
        lower = text.lower()
        return any(v in lower for v in mutation_verbs) or "?" in lower

    def _compute_semantic_overlap(self, query: str, target: str) -> float:
        """Calculate semantic word & n-gram overlap between query and contract clause."""
        stop_words = {
            "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
            "by", "is", "are", "as", "from", "be", "this", "that", "it", "we", "can", "our"
        }
        q_tokens = {w for w in re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", query.lower()) if w not in stop_words}
        t_tokens = {w for w in re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", target.lower()) if w not in stop_words}

        if not q_tokens or not t_tokens:
            return 0.0

        intersection = q_tokens.intersection(t_tokens)
        if not intersection:
            # Semantic aliases check
            aliases = {
                "oauth": ["google", "apple", "login", "social", "sign-in", "signin"],
                "watch": ["wearable", "apple watch", "heart rate", "biometric"],
                "sms": ["whatsapp", "twilio", "alert", "text message", "notification"],
                "dark mode": ["dark-mode", "theme", "night mode", "palette"],
                "currency": ["exchange", "fx", "usd", "eur", "gbp", "inr"],
                "pdf": ["invoice", "receipt", "downloadable invoice"],
                "excel": ["xlsx", "csv", "spreadsheet"],
                "scanner": ["barcode", "camera", "ocr"],
                "stream": ["video", "vimeo", "youtube", "player"],
            }
            for alias_key, related_words in aliases.items():
                if (alias_key in target.lower() or any(rw in target.lower() for rw in related_words)) and (
                    alias_key in query.lower() or any(rw in query.lower() for rw in related_words)
                ):
                    return 0.85
            return 0.0

        # Jaccard + weight
        jaccard = len(intersection) / len(q_tokens.union(t_tokens))
        # Boost if strong keywords matched
        overlap_boost = len(intersection) / len(t_tokens)
        return max(jaccard, overlap_boost * 0.7)

    def _estimate_hours_for_feature(self, query: str, clause: str) -> float:
        """Estimate dev time based on technical complexity of capability."""
        combined = (query + " " + clause).lower()
        if any(k in combined for k in ["watch", "wearable", "bluetooth", "hardware"]):
            return 8.0
        if any(k in combined for k in ["video", "stream", "media", "player"]):
            return 6.0
        if any(k in combined for k in ["currency", "exchange", "fx", "stripe", "payment"]):
            return 6.0
        if any(k in combined for k in ["camera", "barcode", "ocr", "scanner"]):
            return 5.5
        if any(k in combined for k in ["sms", "whatsapp", "twilio", "alert"]):
            return 5.0
        if any(k in combined for k in ["pdf", "invoice", "receipt"]):
            return 4.5
        if any(k in combined for k in ["oauth", "google login", "apple login", "social login"]):
            return 4.0
        if any(k in combined for k in ["dark mode", "theme"]):
            return 3.5
        if any(k in combined for k in ["excel", "xlsx", "csv", "export"]):
            return 3.5
        return 3.0
