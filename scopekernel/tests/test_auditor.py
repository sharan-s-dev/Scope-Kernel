"""Unit tests for ScopeKernel filter, extraction, schema, and audit logic.

Verifies:
1. Deterministic noise stripper eliminates non-actionable chatter.
2. Feature alteration signals are accurately isolated.
3. Contract baseline AST parser accurately extracts inclusions, exclusions, and rates.
4. Air-gap guarantee strictly blocks remote hostnames.
5. End-to-end audit detects scope violations, calculates financial leakage, and generates diplomatic replies.
"""

from pathlib import Path
import pytest

from scopekernel.core.schemas import ContractBaseline, ScopeAuditResult, ScopeAuditSummary
from scopekernel.core.prefilter import (
    is_candidate_feature_request,
    extract_chat_messages,
    parse_chat_line,
)
from scopekernel.core.engine import OllamaEngine, EngineConfig, EngineMode
from scopekernel.core.auditor import ScopeAuditor


def test_prefilter_noise_stripping():
    """Verify that pure conversational filler is filtered out."""
    noise_samples = [
        "Good morning!",
        "Thanks!",
        "ok",
        "cool",
        "yep sounds good",
        "will test tomorrow",
        "ping me when free",
        "<Media omitted>",
        "Messages and calls are end-to-end encrypted",
        "see you later",
        "perfect, verified.",
    ]
    for msg in noise_samples:
        assert not is_candidate_feature_request(msg), f"Expected noise to be filtered: {msg}"


def test_prefilter_feature_signal_detection():
    """Verify that mutation signals and scope-expanding requests are detected."""
    candidate_samples = [
        "Can we quickly add Google and Apple OAuth logins?",
        "Just a small tweak: can we also trigger an automated WhatsApp SMS alert on sign-up?",
        "One quick change: make the user dashboard dark-mode by default.",
        "What if we let users switch currencies from USD to EUR and GBP?",
        "Could we generate a downloadable PDF invoice for each order?",
        "Can we also hook up an automated export to Excel for the inventory counts?",
        "Is it possible to integrate Razorpay alongside Stripe?",
    ]
    for msg in candidate_samples:
        assert is_candidate_feature_request(msg), f"Expected candidate to be caught: {msg}"


def test_chat_message_extraction_and_timestamps():
    """Verify chat line parser extracts timestamp, sender, and clean message body."""
    line = "[10/14/24, 9:02:15 AM] Sarah (Client): Good morning! Hope you had a great weekend."
    ts, sender, msg = parse_chat_line(line)
    assert ts == "10/14/24, 9:02:15 AM"
    assert sender == "Sarah (Client)"
    assert msg == "Good morning! Hope you had a great weekend."


def test_contract_baseline_markdown_parsing():
    """Verify markdown contract baseline AST extractor."""
    sample_md = """# Statement of Work: Artisan Roasters Platform
Hourly Rate: $75.00 / hour

## Included Deliverables
- User Authentication with Email and Password
- Product Catalog Grid with category filter
- Stripe Single-Item Checkout

## Explicit Exclusions
- Social/OAuth Logins (Google, Apple)
- Automated WhatsApp/SMS Notifications
- Dark Mode Default Theme
"""
    contract = ContractBaseline.from_markdown(sample_md)
    assert "Artisan Roasters Platform" in contract.project_name
    assert contract.hourly_rate == 75.0
    assert contract.currency_symbol == "$"
    assert len(contract.included_deliverables) >= 3
    assert len(contract.explicit_exclusions) >= 3
    assert any("OAuth" in item for item in contract.explicit_exclusions)


def test_airgap_guarantee_enforcement():
    """Verify zero cloud calls: strictly rejects external hosts."""
    # Localhost and 127.0.0.1 must pass
    local_cfg = EngineConfig(base_url="http://localhost:11434")
    assert local_cfg.validate_air_gap() is True

    ip_cfg = EngineConfig(base_url="http://127.0.0.1:11434")
    assert ip_cfg.validate_air_gap() is True

    # Cloud endpoints must raise an Air-Gap Violation
    cloud_endpoints = [
        "https://api.openai.com/v1",
        "https://api.anthropic.com/v1",
        "https://generativelanguage.googleapis.com",
        "http://remote-server.io:11434",
    ]
    for endpoint in cloud_endpoints:
        with pytest.raises(ValueError, match="Air-Gap Violation"):
            bad_cfg = EngineConfig(base_url=endpoint)
            bad_cfg.validate_air_gap()


def test_auditor_end_to_end_mock_data():
    """Run full end-to-end pipeline on sample SOW and sample WhatsApp chat thread."""
    sow_path = Path(__file__).parent.parent / "mock_data" / "sample_sow.md"
    chat_path = Path(__file__).parent.parent / "mock_data" / "sample_chat.txt"

    assert sow_path.exists(), f"Sample SOW not found at {sow_path}"
    assert chat_path.exists(), f"Sample chat not found at {chat_path}"

    sow_text = sow_path.read_text(encoding="utf-8")
    chat_text = chat_path.read_text(encoding="utf-8")

    contract = ContractBaseline.from_markdown(sow_text)
    assert contract.hourly_rate == 75.0

    # Initialize auditor with deterministic offline fallback mode for reliable testing
    engine = OllamaEngine(
        config=EngineConfig(mode=EngineMode.OFFLINE_HEURISTIC)
    )
    auditor = ScopeAuditor(engine=engine)

    summary: ScopeAuditSummary = auditor.audit_chat_stream(
        contract=contract,
        raw_chat_text=chat_text,
    )

    # Verifications
    assert summary.total_messages >= 30, f"Expected >30 messages, got {summary.total_messages}"
    assert summary.filtered_noise_count > 0, "Noise filter should eliminate conversational filler"
    assert summary.candidate_count < summary.total_messages, "Candidate stream should be smaller than raw"
    assert summary.creep_detected_count >= 4, f"Expected at least 4 creep events, got {summary.creep_detected_count}"
    assert summary.total_unbilled_hours > 10.0, f"Expected >10 hours, got {summary.total_unbilled_hours}"
    assert summary.total_financial_leakage > 500.0, f"Expected >$500 leakage, got {summary.total_financial_leakage}"

    # Verify diplomatic reply was drafted for flagged items
    flagged = [r for r in summary.results if r.is_scope_creep]
    for item in flagged:
        assert item.violating_feature != "None"
        assert item.estimated_hours > 0.0
        assert len(item.suggested_client_reply) > 20
        assert "change order" in item.suggested_client_reply.lower() or "sow" in item.suggested_client_reply.lower()


def test_multi_tone_replies_generation():
    """Verify that all four professional tones are generated for scope creep items."""
    engine = OllamaEngine(config=EngineConfig(mode=EngineMode.OFFLINE_HEURISTIC))
    auditor = ScopeAuditor(engine=engine)

    contract = ContractBaseline(
        project_name="Web Store",
        included_deliverables=["Email Login", "Products"],
        explicit_exclusions=["OAuth Login", "Dark Mode"],
        hourly_rate=75.0,
    )

    from scopekernel.core.prefilter import ChatMessage

    candidate = ChatMessage(
        raw="Can we add Google and Apple login?",
        clean_text="Can we add Google and Apple login?",
        sender="Sarah (Client)",
        is_candidate=True,
    )

    result = auditor.audit_message(candidate, contract)
    assert result.is_scope_creep is True
    assert "OAuth" in result.violating_feature or "Social" in result.violating_feature
    assert len(result.replies_by_tone) >= 4
    assert "Collaborative & Diplomatic" in result.replies_by_tone
    assert "Direct & Commercial" in result.replies_by_tone
    assert "Phase 2 Deferral" in result.replies_by_tone
    assert "WhatsApp Quick DM" in result.replies_by_tone


def test_mobile_app_preset_audit():
    """Verify auditing on the mobile app preset (PulseFit iOS)."""
    sow_path = Path(__file__).parent.parent / "mock_data" / "mobile_app_sow.md"
    chat_path = Path(__file__).parent.parent / "mock_data" / "mobile_app_chat.txt"

    assert sow_path.exists()
    assert chat_path.exists()

    contract = ContractBaseline.from_markdown(sow_path.read_text(encoding="utf-8"))
    assert "PulseFit" in contract.project_name
    assert contract.hourly_rate == 85.0

    engine = OllamaEngine(config=EngineConfig(mode=EngineMode.OFFLINE_HEURISTIC))
    auditor = ScopeAuditor(engine=engine)

    summary = auditor.audit_chat_stream(contract, chat_path.read_text(encoding="utf-8"))
    assert summary.creep_detected_count >= 2
    assert summary.total_unbilled_hours >= 10.0
    assert summary.total_financial_leakage > 800.0


def test_arbitrary_custom_contract_dynamic_audit():
    """Verify that ANY completely unknown custom contract and message are dynamically audited without hardcoded keywords."""
    from scopekernel.core.prefilter import ChatMessage

    custom_contract = ContractBaseline(
        project_name="Rust CLI Utility",
        included_deliverables=["JSON file parsing", "CSV conversion stdout"],
        explicit_exclusions=["Kafka real-time streaming pipeline", "Cloud S3 bucket upload"],
        hourly_rate=120.0,
        currency_symbol="$",
    )

    candidate = ChatMessage(
        raw="Hey dev! Can we add Kafka real-time streaming pipeline for live telemetry?",
        clean_text="Can we add Kafka real-time streaming pipeline for live telemetry?",
        sender="Lead Engineer",
        is_candidate=True,
    )

    engine = OllamaEngine(config=EngineConfig(mode=EngineMode.OFFLINE_SEMANTIC))
    auditor = ScopeAuditor(engine=engine)

    result = auditor.audit_message(candidate, custom_contract)

    assert result.is_scope_creep is True
    assert "Kafka" in result.violating_feature or "Kafka" in (result.matched_exclusion or "")
    assert "Kafka" in result.reasoning or "breaches agreed exclusion" in result.reasoning
    assert result.estimated_hours >= 3.0
    assert result.overage_cost == result.estimated_hours * 120.0
    assert "Kafka" in result.suggested_client_reply or "change order" in result.suggested_client_reply.lower()


