"""ScopeKernel Core Package (Root shortcut)."""

from scopekernel.core import (
    ContractBaseline,
    ScopeAuditResult,
    ScopeAuditSummary,
    is_candidate_feature_request,
    extract_chat_messages,
    ChatMessage,
    OllamaEngine,
    EngineConfig,
    EngineMode,
    ScopeAuditor,
)

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
