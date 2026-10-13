"""Local Ollama client optimized for Google Gemma-2-2B.

Target Model: Google Gemma 2 (2B-IT) via Ollama (http://localhost:11434)
Zero Cloud Telemetry | Temp=0.0 | Top_p=0.2 | Structured JSON Format
Air-Gapped Enforcement: Strictly localhost/127.0.0.1.
"""

from __future__ import annotations

import json
import logging
from enum import Enum
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

logger = logging.getLogger("scopekernel.engine")


class EngineMode(str, Enum):
    OLLAMA_LIVE = "ollama_live"
    OFFLINE_HEURISTIC = "offline_heuristic"


class EngineConfig(BaseModel):
    """Configuration for the local micro-SLM engine."""

    base_url: str = "http://localhost:11434"
    model: str = "gemma2:2b"
    temperature: float = 0.0
    top_p: float = 0.2
    timeout_seconds: float = 30.0
    mode: EngineMode = EngineMode.OLLAMA_LIVE

    def validate_air_gap(self) -> bool:
        """Enforces air-gap compliance: strictly verifies host is local."""
        parsed = urlparse(self.base_url)
        hostname = (parsed.hostname or "").lower()
        if hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError(
                f"Air-Gap Violation: Endpoint '{self.base_url}' points to an external host. "
                "ScopeKernel strictly forbids non-local network telemetry."
            )
        return True


class OllamaEngine:
    """Air-gapped inference client for local Gemma 2 (2B-IT)."""

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self.config.validate_air_gap()

    def check_health(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is active and list available models."""
        self.config.validate_air_gap()
        try:
            with httpx.Client(timeout=3.0) as client:
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
            logger.warning("Local Ollama connection failed: %s", e)

        return {
            "online": False,
            "available_models": [],
            "target_model_installed": False,
            "target_model": self.config.model,
            "error": "Ollama daemon not reachable at http://localhost:11434",
        }

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured JSON response using local Gemma 2 (2B).

        Falls back gracefully to deterministic analysis if Ollama is unreachable.
        """
        self.config.validate_air_gap()

        if self.config.mode == EngineMode.OLLAMA_LIVE:
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
                    resp.raise_for_status()
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
                logger.warning(
                    "Ollama call failed (%s). Falling back to deterministic offline engine.", e
                )

        # Fallback / Offline deterministic mode
        return self._heuristic_fallback(prompt)

    def _heuristic_fallback(self, prompt: str) -> Dict[str, Any]:
        """Deterministic fallback when Ollama is offline or in evaluation mode.

        Maintains complete compatibility with Gemma-2-2B JSON schema.
        """
        prompt_lower = prompt.lower()

        # Check for known scope violations
        is_creep = False
        feature = "General Inquiry"
        hours = 0.0
        reasoning = "Message aligns with baseline project requirements."
        matched_clause = None

        if "oauth" in prompt_lower or "google" in prompt_lower or "apple" in prompt_lower:
            is_creep = True
            feature = "Third-Party Social Authentication (Google / Apple OAuth)"
            hours = 4.0
            matched_clause = "Exclusion: Social/OAuth Sign-in"
            reasoning = (
                "The agreed SOW specifies basic Email/Password authentication. "
                "OAuth requires third-party developer consoles, token refresh routines, and security callbacks."
            )
        elif "whatsapp" in prompt_lower or "sms" in prompt_lower or "alert" in prompt_lower:
            is_creep = True
            feature = "Automated WhatsApp / SMS Notification Gateway"
            hours = 5.0
            matched_clause = "Exclusion: Automated SMS/WhatsApp Notifications"
            reasoning = (
                "The initial SOW covers standard web views. Integrating transactional SMS/WhatsApp gateways "
                "requires webhook endpoints, provider credentials, and delivery state handling."
            )
        elif "dark mode" in prompt_lower or "dark-mode" in prompt_lower:
            is_creep = True
            feature = "Default Dark Mode Theming Engine"
            hours = 3.5
            matched_clause = "Exclusion: Dark Mode default and custom UI theming"
            reasoning = (
                "The SOW scoped a standard responsive light interface. Full dark mode requires palette tokens, "
                "contrast audits, and persistent theme switching across all views."
            )
        elif "currency" in prompt_lower or "multi-currency" in prompt_lower or "fx" in prompt_lower:
            is_creep = True
            feature = "Dynamic Multi-Currency & FX Conversion"
            hours = 6.0
            matched_clause = "Exclusion: Multi-Currency dynamic conversion"
            reasoning = (
                "The baseline contract specifies single-currency checkout. Real-time FX conversion requires "
                "currency rates API integration, rounding logic, and localized checkout flows."
            )
        elif "pdf" in prompt_lower or "invoice" in prompt_lower or "downloadable invoice" in prompt_lower:
            is_creep = True
            feature = "Automated PDF Invoice & Receipt Generator"
            hours = 4.5
            matched_clause = "Exclusion: Automated PDF Invoice Generation"
            reasoning = (
                "The SOW scoped standard in-app order view. Server-side or client-side PDF rendering "
                "with custom styling and download triggers is an explicit add-on."
            )
        elif "watch" in prompt_lower or "wearable" in prompt_lower or "heart rate" in prompt_lower:
            is_creep = True
            feature = "Apple Watch & Wearable Biometric Sync"
            hours = 8.0
            matched_clause = "Exclusion: Apple Watch / Wearable Sync"
            reasoning = (
                "The agreed SOW specifies standalone iOS mobile app functionality. Real-time watchOS connectivity "
                "requires companion WatchKit target, background HealthKit sessions, and dual-device state synchronization."
            )
        elif "video" in prompt_lower or "stream" in prompt_lower or "vimeo" in prompt_lower or "player" in prompt_lower:
            is_creep = True
            feature = "In-App Video Streaming Player & CDN Pipeline"
            hours = 6.0
            matched_clause = "Exclusion: Video Streaming & Exercise Demos"
            reasoning = (
                "The milestone covers local static exercise cards. Video streaming introduces AVPlayer caching, "
                "bandwidth buffering, CDN token authorization, and network error state recovery."
            )
        elif "barcode" in prompt_lower or "scanner" in prompt_lower or "camera" in prompt_lower:
            is_creep = True
            feature = "Camera Barcode Scanner & Food Database OCR"
            hours = 5.5
            matched_clause = "Exclusion: Barcode Food Scanner"
            reasoning = (
                "The SOW specified manual macro entry. Barcode scanning requires AVFoundation camera capture, "
                "symbology decoding, and remote OpenFoodFacts API payload parsing."
            )
        elif "excel" in prompt_lower or "xlsx" in prompt_lower or "export" in prompt_lower:
            is_creep = True
            feature = "Automated Excel / CSV Data Export Pipeline"
            hours = 3.5
            matched_clause = "Exclusion: External Accounting / ERP Export"
            reasoning = (
                "The contract specified web table filtering. Generating formatted multi-sheet Excel workbooks "
                "with formulas and downloadable MIME attachments is an additional reporting module."
            )
        elif any(
            k in prompt_lower
            for k in ["can we add", "could we add", "also add", "quick tweak", "tweak", "what if we add"]
        ):
            # Generic detected mutation
            is_creep = True
            feature = "Additional Feature Request"
            hours = 3.0
            matched_clause = "Exclusion: Out-of-Scope Milestone Additions"
            reasoning = (
                "The client requested a functional addition not specified in the agreed Deliverables section."
            )

        # Generate 4 authentic, non-robotic tone variants
        replies_by_tone = {}
        if is_creep:
            reply_collab = (
                f"Hey! Thanks for bringing this up—adding {feature} makes complete sense for the product experience. "
                f"Taking a quick look at our signed SOW, this is currently listed as an out-of-scope addition or deferred item. "
                f"I'd love to build this out as a change order: it would take roughly {hours:.1f} hours at our agreed rate. "
                f"Would you prefer I add this to our active milestone or queue it up for Phase 2?"
            )
            reply_direct = (
                f"Hi! We can certainly build {feature}. As outlined in our contract exclusions, this falls outside the Phase 1 milestone deliverables. "
                f"The estimated scope is {hours:.1f} engineering hours. Please reply to confirm if you would like me to issue a Change Order for this item."
            )
            reply_defer = (
                f"Great idea on {feature}! To protect our launch deadline for the current milestone, I recommend we deliver the agreed MVP deliverables first. "
                f"I have logged this in our Phase 2 backlog ({hours:.1f} hrs estimate) so we can tackle it immediately following deployment."
            )
            reply_quick = (
                f"Love this idea! Quick heads up though: {feature} isn't in our current SOW. "
                f"It's about {hours:.1f} hrs of work—want me to add it as a quick change order or keep it for after launch?"
            )
            replies_by_tone = {
                "Collaborative & Diplomatic": reply_collab,
                "Direct & Commercial": reply_direct,
                "Phase 2 Deferral": reply_defer,
                "WhatsApp Quick DM": reply_quick,
            }
            primary_reply = reply_collab
        else:
            primary_reply = "Thanks for checking in! This is already covered under our active milestone deliverables and is actively being built."
            replies_by_tone = {
                "Standard": primary_reply
            }

        return {
            "success": True,
            "mode": "offline_heuristic",
            "model": "deterministic_fallback",
            "data": {
                "is_scope_creep": is_creep,
                "violating_feature": feature if is_creep else "None",
                "reasoning": reasoning,
                "estimated_hours": hours,
                "matched_exclusion": matched_clause,
                "suggested_client_reply": primary_reply,
                "replies_by_tone": replies_by_tone,
            },
        }
