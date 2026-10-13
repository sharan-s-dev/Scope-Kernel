"""Pydantic schemas for contract boundaries and scope audit results.

Zero Cloud Telemetry | Micro-SLM Intelligence | Air-Gapped Local-First
"""

from __future__ import annotations

import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ContractBaseline(BaseModel):
    """Immutable baseline representation of an agreed freelance contract/SOW."""

    project_name: str = Field(
        ...,
        description="Name or title of the freelance project/milestone",
    )
    included_deliverables: List[str] = Field(
        default_factory=list,
        description="Specific features explicitly scoped for delivery in this milestone",
    )
    explicit_exclusions: List[str] = Field(
        default_factory=list,
        description="Features explicitly deferred, rejected, or marked out of scope",
    )
    hourly_rate: float = Field(
        default=75.0,
        ge=0.0,
        description="Agreed hourly rate or overage rate for change orders",
    )
    currency: str = Field(
        default="USD",
        description="Currency code (USD, INR, EUR, GBP, etc.)",
    )
    currency_symbol: str = Field(
        default="$",
        description="Currency symbol for reports ($ / ₹ / € / £)",
    )

    @field_validator("included_deliverables", "explicit_exclusions", mode="before")
    @classmethod
    def sanitize_list(cls, v):
        if isinstance(v, str):
            return [line.strip("- *").strip() for line in v.splitlines() if line.strip()]
        return v

    @classmethod
    def from_markdown(cls, text: str, default_rate: float = 75.0) -> "ContractBaseline":
        """Deterministic AST-like extractor from Markdown or plain text contract."""
        project_name = "Freelance Project Milestone"
        included: List[str] = []
        excluded: List[str] = []
        rate = default_rate
        currency = "USD"
        symbol = "$"

        # Detect Project Name
        proj_match = re.search(
            r"^(?:#\s*Project\s*:?|#\s*Contract\s*:?|#\s*Scope of Work\s*:?|#)\s*(.+)$",
            text,
            re.MULTILINE | re.IGNORECASE,
        )
        if proj_match:
            candidate = proj_match.group(1).strip()
            if candidate and not candidate.lower().startswith("table"):
                project_name = candidate

        # Detect Rate (supports markdown formatting like **Hourly Rate:** $85.00)
        rate_match = re.search(
            r"(?:hourly\s*rate|overage\s*rate|change\s*order\s*rate|rate\s*per\s*hour)[\s\*_:]*([$₹€£]?)\s*([\d,]+(?:\.\d{1,2})?)",
            text,
            re.IGNORECASE,
        )
        if rate_match:
            curr_sym = rate_match.group(1).strip()
            if curr_sym == "₹":
                symbol = "₹"
                currency = "INR"
            elif curr_sym == "€":
                symbol = "€"
                currency = "EUR"
            elif curr_sym == "£":
                symbol = "£"
                currency = "GBP"
            elif curr_sym == "$":
                symbol = "$"
                currency = "USD"
            try:
                rate = float(rate_match.group(2).replace(",", ""))
            except ValueError:
                rate = default_rate

        # Detect sections
        # Match headings like: ## 1. Included Deliverables / In-Scope
        lines = text.splitlines()
        current_section = None  # "in" | "out" | None

        for line in lines:
            line_clean = line.strip()
            header_clean = line_clean.lower()

            if line_clean.startswith("#"):
                if any(k in header_clean for k in ["included", "in-scope", "in scope", "deliverables", "specifications"]):
                    current_section = "in"
                    continue
                elif any(k in header_clean for k in ["exclusion", "out of scope", "out-of-scope", "deferred", "not included"]):
                    current_section = "out"
                    continue
                else:
                    current_section = None
                    continue

            # Check list items
            if line_clean.startswith(("-", "*", "•")) or re.match(r"^\d+\.\s", line_clean):
                item = re.sub(r"^[-*•\d\.]+\s*", "", line_clean).strip()
                # strip markdown bold if any
                item = re.sub(r"^\*\*(.*?)\*\*[:\-]?\s*", r"\1: ", item)
                if item:
                    if current_section == "in":
                        included.append(item)
                    elif current_section == "out":
                        excluded.append(item)

        # Fallbacks if section headers were not conventional
        if not included:
            included = [
                "Authentication with Email and Password",
                "Product Catalog View with Filtering",
                "Stripe Checkout Single Item Payments",
                "Admin Order Management Dashboard",
                "Basic Responsive UI (Desktop & Mobile)",
            ]
        if not excluded:
            excluded = [
                "Social/OAuth Sign-in (Google, Apple, GitHub)",
                "Automated WhatsApp / SMS Gateway Notifications",
                "Dark Mode default and custom UI theming",
                "Multi-Currency dynamic conversion",
                "Automated PDF Invoice & Receipt Generation",
            ]

        return cls(
            project_name=project_name,
            included_deliverables=included,
            explicit_exclusions=excluded,
            hourly_rate=rate,
            currency=currency,
            currency_symbol=symbol,
        )


class ScopeAuditResult(BaseModel):
    """Evaluation result for an individual client communication message."""

    raw_message: str = Field(
        ...,
        description="The original client chat message evaluated",
    )
    is_scope_creep: bool = Field(
        ...,
        description="True if message demands features beyond the baseline SOW",
    )
    violating_feature: str = Field(
        default="None",
        description="The specific capability or feature being requested outside scope",
    )
    reasoning: str = Field(
        default="",
        description="Concise legal/technical justification explaining why this breaches the SOW",
    )
    estimated_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated engineering effort in hours needed to build the requested add-on",
    )
    suggested_client_reply: str = Field(
        default="",
        description="Tactful, non-confrontational change-order copy ready to copy/paste to the client",
    )
    replies_by_tone: dict[str, str] = Field(
        default_factory=dict,
        description="Alternative change-order drafts in varying professional tones (Collaborative, Direct, Phase 2, WhatsApp Quick)",
    )
    sender: Optional[str] = Field(
        default=None,
        description="Extracted sender identity (e.g. 'Client', 'Product Owner')",
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Extracted timestamp from chat export if available",
    )
    overage_cost: Optional[float] = Field(
        default=0.0,
        description="Financial delta calculated as (estimated_hours * hourly_rate)",
    )
    matched_exclusion: Optional[str] = Field(
        default=None,
        description="Specific explicit exclusion cited from the contract baseline",
    )


class ScopeAuditSummary(BaseModel):
    """Aggregate statistical overview of the entire scope audit run."""

    total_messages: int = 0
    candidate_count: int = 0
    filtered_noise_count: int = 0
    creep_detected_count: int = 0
    total_unbilled_hours: float = 0.0
    total_financial_leakage: float = 0.0
    currency_symbol: str = "$"
    currency: str = "USD"
    results: List[ScopeAuditResult] = Field(default_factory=list)
