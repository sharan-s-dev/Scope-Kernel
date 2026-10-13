"""ScopeKernel Core Package.

Air-gapped scope-creep & change-order engine for tech freelancers.
Zero cloud telemetry, deterministic pre-filtering, and Gemma-2-2B micro-SLM intelligence.
"""

from .schemas import ContractBaseline, ScopeAuditResult, ScopeAuditSummary
from .prefilter import is_candidate_feature_request, extract_chat_messages, ChatMessage
from .engine import OllamaEngine, EngineConfig, EngineMode
from .auditor import ScopeAuditor

__all__ = [
    "ContractBaseline",
    "ScopeAuditResult",
    "ScopeAuditSummary",
    "is_candidate_feature_request",
    "extract_chat_messages",
    "ChatMessage",
    "OllamaEngine",
    "EngineConfig",
    "EngineMode",
    "ScopeAuditor",
]
