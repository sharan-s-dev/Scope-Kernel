"""Cross-examination orchestration pipeline for ScopeKernel.

Pairs deterministic contract AST boundaries with high-speed regex pre-filtering
and micro-SLM inference (Google Gemma-2-2B-IT) to detect unbilled scope creep.
"""

from __future__ import annotations

import json
import logging
from typing import Callable, List, Optional

from .engine import OllamaEngine
from .prefilter import ChatMessage, extract_chat_messages
from .schemas import ContractBaseline, ScopeAuditResult, ScopeAuditSummary

logger = logging.getLogger("scopekernel.auditor")


class ScopeAuditor:
    """Orchestrates end-to-end scope auditing between contract baselines and chat streams."""

    def __init__(self, engine: Optional[OllamaEngine] = None):
        self.engine = engine or OllamaEngine()

    def construct_audit_prompt(
        self,
        message: ChatMessage,
        contract: ContractBaseline,
    ) -> str:
        """Construct a compact, instruction-tuned prompt optimized for Gemma-2-2B.

        Gemma-2-2B achieves highest JSON schema compliance when given minimal,
        dense prompt instructions with explicit JSON keys.
        """
        included_bullets = "\n".join(f"- {item}" for item in contract.included_deliverables)
        excluded_bullets = "\n".join(f"- {item}" for item in contract.explicit_exclusions)

        prompt = f"""You are ScopeKernel, an expert contract auditor for freelance software engineers.
Evaluate whether the following client message constitutes OUT-OF-SCOPE WORK (scope creep).

CONTRACT BASELINE FOR: {contract.project_name}
HOURLY OVERAGE RATE: {contract.currency_symbol}{contract.hourly_rate:.2f}/hr

INCLUDED DELIVERABLES (IN-SCOPE):
{included_bullets}

EXPLICIT EXCLUSIONS (OUT-OF-SCOPE):
{excluded_bullets}

CLIENT MESSAGE TO AUDIT:
"{message.clean_text}"

INSTRUCTIONS:
1. Determine if this message requests a new feature, integration, or functional alteration outside the agreed scope.
2. If it is within scope or a general inquiry, set is_scope_creep to false and estimated_hours to 0.0.
3. If it is out of scope (scope creep), set is_scope_creep to true, name the violating_feature, cite any matched exclusion, estimate realistic dev hours (e.g. 2.0 to 12.0), and draft a tactful, non-confrontational change-order reply the freelancer can send back.

OUTPUT STRICT JSON WITH THIS EXACT STRUCTURE:
{{
  "is_scope_creep": true,
  "violating_feature": "Name of feature",
  "reasoning": "Why this breaches the SOW boundary",
  "matched_exclusion": "Exclusion clause cited or null",
  "estimated_hours": 4.0,
  "suggested_client_reply": "Diplomatic proposal for a paid change order..."
}}
"""
        return prompt

    def audit_message(
        self,
        message: ChatMessage,
        contract: ContractBaseline,
    ) -> ScopeAuditResult:
        """Audit an individual candidate message using the local Gemma-2 engine."""
        prompt = self.construct_audit_prompt(message, contract)
        system_prompt = (
            "You are an air-gapped contract auditor. Respond strictly in valid JSON format. "
            "Never output introductory or concluding conversational prose."
        )

        response = self.engine.generate(prompt=prompt, system_prompt=system_prompt)
        data = response.get("data", {})

        is_creep = bool(data.get("is_scope_creep", False))
        feature = str(data.get("violating_feature", "None"))
        reasoning = str(data.get("reasoning", ""))
        hours = float(data.get("estimated_hours", 0.0))
        matched_exclusion = data.get("matched_exclusion")
        reply = str(data.get("suggested_client_reply", ""))
        replies_by_tone = data.get("replies_by_tone", {})

        # Calculate financial delta
        overage_cost = round(hours * contract.hourly_rate, 2) if is_creep else 0.0

        return ScopeAuditResult(
            raw_message=message.clean_text,
            is_scope_creep=is_creep,
            violating_feature=feature,
            reasoning=reasoning,
            estimated_hours=hours,
            suggested_client_reply=reply,
            replies_by_tone=replies_by_tone,
            sender=message.sender,
            timestamp=message.timestamp,
            overage_cost=overage_cost,
            matched_exclusion=matched_exclusion,
        )

    def audit_chat_stream(
        self,
        contract: ContractBaseline,
        raw_chat_text: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> ScopeAuditSummary:
        """Execute the full Three-Stage Deterministic-to-Neural Pipeline.

        Stage 1: Ingest contract boundary.
        Stage 2: Deterministic regex noise stripper & candidate filtering.
        Stage 3: Gemma-2-2B micro-SLM cross-examination.
        """
        all_messages: List[ChatMessage] = extract_chat_messages(raw_chat_text)
        total_messages = len(all_messages)

        candidate_messages = [m for m in all_messages if m.is_candidate]
        candidate_count = len(candidate_messages)
        filtered_noise_count = total_messages - candidate_count

        results: List[ScopeAuditResult] = []
        total_hours = 0.0
        total_leakage = 0.0
        creep_count = 0

        for idx, candidate in enumerate(candidate_messages, start=1):
            if progress_callback:
                progress_callback(idx, candidate_count, candidate.clean_text[:60])

            result = self.audit_message(candidate, contract)
            results.append(result)

            if result.is_scope_creep:
                creep_count += 1
                total_hours += result.estimated_hours
                total_leakage += result.overage_cost or 0.0

        return ScopeAuditSummary(
            total_messages=total_messages,
            candidate_count=candidate_count,
            filtered_noise_count=filtered_noise_count,
            creep_detected_count=creep_count,
            total_unbilled_hours=round(total_hours, 1),
            total_financial_leakage=round(total_leakage, 2),
            currency_symbol=contract.currency_symbol,
            currency=contract.currency,
            results=results,
        )
