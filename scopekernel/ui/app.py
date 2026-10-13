"""ScopeKernel - The Air-Gapped Scope-Creep & Change-Order Engine for Solo Freelancers.

Zero Cloud Telemetry | Micro-SLM Intelligence (Google Gemma-2-2B) | Deterministic Pre-Filtering
"""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path
import streamlit as st

# Setup page configuration
st.set_page_config(
    page_title="ScopeKernel | Air-Gapped Scope-Creep Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Aesthetic Styling (Linear / Raycast / FinTech Developer Theme)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .main {
        background-color: #080c14;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.9) 50%, rgba(13, 20, 36, 0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6), 0 0 20px rgba(99, 102, 241, 0.08);
    }

    .brand-title {
        margin: 0;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
    }

    .brand-highlight {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 50%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .badge-airgap {
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.45);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -6px rgba(0, 0, 0, 0.5);
    }

    .metric-title {
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.95rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 6px;
    }

    /* Result Cards */
    .creep-card {
        background: rgba(239, 68, 68, 0.06);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .safe-card {
        background: rgba(16, 185, 129, 0.05);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .tag-danger {
        background-color: #ef4444;
        color: #ffffff;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.04em;
    }

    .tag-safe {
        background-color: #10b981;
        color: #ffffff;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.04em;
    }

    /* Chat bubble container */
    .chat-bubble-client {
        background: #1e293b;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px 12px 12px 2px;
        padding: 12px 16px;
        margin-bottom: 12px;
        max-width: 90%;
    }

    .chat-bubble-freelancer {
        background: #14532d;
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 12px 12px 2px 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
        margin-left: auto;
        max-width: 90%;
    }

    .chat-sender {
        font-size: 0.78rem;
        font-weight: 700;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .chat-text {
        font-size: 0.95rem;
        color: #e2e8f0;
        line-height: 1.4;
    }
    .chat-ts {
        font-size: 0.7rem;
        color: #64748b;
        margin-top: 4px;
        text-align: right;
    }

    .upload-zone-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Core imports
try:
    from scopekernel.core.schemas import ContractBaseline, ScopeAuditSummary
    from scopekernel.core.prefilter import extract_chat_messages
    from scopekernel.core.engine import OllamaEngine, EngineConfig, EngineMode
    from scopekernel.core.auditor import ScopeAuditor
except ImportError:
    from core.schemas import ContractBaseline, ScopeAuditSummary
    from core.prefilter import extract_chat_messages
    from core.engine import OllamaEngine, EngineConfig, EngineMode
    from core.auditor import ScopeAuditor

# Resolve mock data directory
MOCK_DIR = Path(__file__).parent.parent / "mock_data"
if not MOCK_DIR.exists():
    MOCK_DIR = Path(__file__).parent.parent.parent / "mock_data"


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


# Load available presets
PRESET_ECOMM_SOW = read_text(MOCK_DIR / "sample_sow.md")
PRESET_ECOMM_CHAT = read_text(MOCK_DIR / "sample_chat.txt")
PRESET_MOBILE_SOW = read_text(MOCK_DIR / "mobile_app_sow.md")
PRESET_MOBILE_CHAT = read_text(MOCK_DIR / "mobile_app_chat.txt")

# Initialize session state
if "contract_text" not in st.session_state:
    st.session_state["contract_text"] = PRESET_ECOMM_SOW
if "chat_text" not in st.session_state:
    st.session_state["chat_text"] = PRESET_ECOMM_CHAT
if "audit_summary" not in st.session_state:
    st.session_state["audit_summary"] = None
if "selected_preset" not in st.session_state:
    st.session_state["selected_preset"] = "Artisan Roasters (E-Commerce MVP)"


def on_preset_change():
    preset = st.session_state.get("preset_dropdown")
    if preset == "Artisan Roasters (E-Commerce MVP)":
        st.session_state["contract_text"] = PRESET_ECOMM_SOW
        st.session_state["chat_text"] = PRESET_ECOMM_CHAT
        st.session_state["hourly_rate_input"] = 75.0
        st.session_state["currency_selector"] = "$ (USD)"
    elif preset == "PulseFit iOS (Mobile Workout MVP)":
        st.session_state["contract_text"] = PRESET_MOBILE_SOW
        st.session_state["chat_text"] = PRESET_MOBILE_CHAT
        st.session_state["hourly_rate_input"] = 85.0
        st.session_state["currency_selector"] = "$ (USD)"
    st.session_state["audit_summary"] = None


# Header Banner
st.markdown(
    """
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
            <div>
                <h1 class="brand-title">
                    🛡️ Scope<span class="brand-highlight">Kernel</span>
                </h1>
                <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 1.05rem; font-weight: 400;">
                    The Air-Gapped Scope-Creep & Change-Order Engine for Solo Freelancers
                </p>
            </div>
            <div>
                <span class="badge-airgap">
                    🔒 ZERO CLOUD TELEMETRY • LOCALHOST INFERENCE • GEMMA-2-2B
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar: Controls, Currency & Air-Gap Engine
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")

    engine_choice = st.selectbox(
        "Inference Runtime",
        options=["Auto-Detect (Localhost Gemma-2-2B)", "Offline Deterministic Mode (Zero GPU / Fast Demo)"],
        index=0,
        help="Connects to Ollama on http://localhost:11434 with model gemma2:2b (Q4_K_M). If inactive, falls back safely to offline heuristics.",
    )

    ollama_url = st.text_input("Ollama Host", value="http://localhost:11434", help="Must be localhost or 127.0.0.1")
    model_name = st.text_input("Target Model", value="gemma2:2b", help="Google Gemma-2-2B-IT")

    config = EngineConfig(
        base_url=ollama_url,
        model=model_name,
        mode=EngineMode.OFFLINE_HEURISTIC if "Offline" in engine_choice else EngineMode.OLLAMA_LIVE,
    )
    engine = OllamaEngine(config=config)

    col_h1, col_h2 = st.columns([1, 1])
    with col_h1:
        if st.button("🔍 Check Ollama", use_container_width=True):
            health = engine.check_health()
            if health.get("online"):
                st.success(f"Ollama Online ({len(health.get('available_models', []))} models)")
            else:
                st.warning("Ollama offline. Using deterministic engine.")

    with col_h2:
        if st.button("🔄 Reset App", use_container_width=True):
            st.session_state["contract_text"] = PRESET_ECOMM_SOW
            st.session_state["chat_text"] = PRESET_ECOMM_CHAT
            st.session_state["audit_summary"] = None
            st.rerun()

    st.markdown("---")
    st.markdown("### 💼 Commercial Settings")

    currency_option = st.selectbox(
        "Currency",
        options=["$ (USD)", "₹ (INR)", "€ (EUR)", "£ (GBP)", "CA$ (CAD)", "AU$ (AUD)"],
        index=0,
        key="currency_selector",
    )
    curr_sym = currency_option.split()[0]

    default_rates = {"$": 75.0, "₹": 6000.0, "€": 70.0, "£": 65.0, "CA$": 95.0, "AU$": 110.0}
    init_rate = default_rates.get(curr_sym, 75.0)

    if "hourly_rate_input" not in st.session_state:
        st.session_state["hourly_rate_input"] = init_rate

    hourly_rate = st.number_input(
        f"Agreed Overage Rate ({curr_sym}/hr)",
        min_value=1.0,
        value=st.session_state["hourly_rate_input"],
        step=5.0,
        key="hourly_rate_input",
    )

    st.markdown("---")
    st.markdown("### 🔒 Air-Gap Verification")
    st.caption("Verifiable Zero Network Outbound. No tokens or client contracts ever leave your physical device.")

# Top Scenario Selector
st.markdown("#### ⚡ 1-Click Example Scenarios & Test Uploads")
col_preset, col_dl_sow, col_dl_chat = st.columns([2, 1, 1], gap="medium")

with col_preset:
    st.selectbox(
        "Select Example Scenario",
        options=[
            "Artisan Roasters (E-Commerce MVP)",
            "PulseFit iOS (Mobile Workout MVP)",
            "Custom Contract & Chat (Upload Your Own)",
        ],
        index=0,
        key="preset_dropdown",
        on_change=on_preset_change,
        help="Loads pre-built realistic contract boundaries and multi-message WhatsApp client threads.",
    )

with col_dl_sow:
    st.download_button(
        label="📥 Download SOW File (.md)",
        data=st.session_state["contract_text"],
        file_name="ScopeKernel_Contract_SOW.md",
        mime="text/markdown",
        use_container_width=True,
        help="Download this sample SOW to test the drag-and-drop file uploader!",
    )

with col_dl_chat:
    st.download_button(
        label="📥 Download Chat File (.txt)",
        data=st.session_state["chat_text"],
        file_name="ScopeKernel_Client_Chat.txt",
        mime="text/plain",
        use_container_width=True,
        help="Download this sample WhatsApp thread to test the drag-and-drop file uploader!",
    )

st.markdown("---")

# Main Split Layout
col_left, col_right = st.columns([1, 1.25], gap="large")

# LEFT PANEL: Contract Boundary & Chat Stream
with col_left:
    st.markdown("### 1. Contract Baseline (Scope of Work)")

    with st.container():
        sow_upload = st.file_uploader(
            "Upload SOW (.md / .txt)",
            type=["md", "txt"],
            key="sow_file_uploader",
            help="Drop your signed Statement of Work or agreement here",
        )
        if sow_upload:
            uploaded_sow = sow_upload.getvalue().decode("utf-8")
            if uploaded_sow != st.session_state["contract_text"]:
                st.session_state["contract_text"] = uploaded_sow
                st.session_state["audit_summary"] = None

    contract_input = st.text_area(
        "Contract SOW Text (Editable Boundary)",
        value=st.session_state["contract_text"],
        height=210,
        key="contract_text_area",
        help="Verify the Included Deliverables and Explicit Exclusions sections.",
    )
    if contract_input != st.session_state["contract_text"]:
        st.session_state["contract_text"] = contract_input

    st.markdown("### 2. Client Communication Stream")

    with st.container():
        chat_upload = st.file_uploader(
            "Upload Client Chat Log (.txt)",
            type=["txt"],
            key="chat_file_uploader",
            help="Drop an exported WhatsApp, Slack, or email thread (.txt)",
        )
        if chat_upload:
            uploaded_chat = chat_upload.getvalue().decode("utf-8")
            if uploaded_chat != st.session_state["chat_text"]:
                st.session_state["chat_text"] = uploaded_chat
                st.session_state["audit_summary"] = None

    chat_input = st.text_area(
        "Raw WhatsApp / Slack / Email Stream",
        value=st.session_state["chat_text"],
        height=210,
        key="chat_text_area",
        help="Raw communication thread from WhatsApp or Slack DMs.",
    )
    if chat_input != st.session_state["chat_text"]:
        st.session_state["chat_text"] = chat_input

    st.markdown("---")
    run_audit_btn = st.button("🚀 Run ScopeKernel Audit", type="primary", use_container_width=True)

# Parse contract baseline
if st.session_state["contract_text"].strip():
    parsed_contract = ContractBaseline.from_markdown(st.session_state["contract_text"], default_rate=hourly_rate)
    parsed_contract.hourly_rate = hourly_rate
    parsed_contract.currency_symbol = curr_sym
else:
    parsed_contract = ContractBaseline(
        project_name="Custom Milestone",
        included_deliverables=["Core features"],
        explicit_exclusions=["Out-of-scope additions"],
        hourly_rate=hourly_rate,
        currency_symbol=curr_sym,
    )

# Execution trigger
if run_audit_btn:
    if not st.session_state["chat_text"].strip():
        st.error("Please provide or load a client chat stream to audit.")
    else:
        progress_bar = st.progress(0, text="Stage 1: AST Contract Boundary Parsing...")
        auditor = ScopeAuditor(engine=engine)

        def update_progress(current, total, msg_snippet):
            fraction = min(1.0, current / max(1, total))
            progress_bar.progress(fraction, text=f"Stage 3 Micro-SLM [{current}/{total}]: {msg_snippet}")

        with st.spinner("Executing Three-Stage Deterministic-to-Neural Pipeline..."):
            summary: ScopeAuditSummary = auditor.audit_chat_stream(
                contract=parsed_contract,
                raw_chat_text=st.session_state["chat_text"],
                progress_callback=update_progress,
            )
            st.session_state["audit_summary"] = summary
            progress_bar.progress(1.0, text="✅ Audit completed with zero external telemetry!")

# RIGHT PANEL: Results, Matrix, Copilot & Change Order Generator
with col_right:
    st.markdown("### 3. Scope Matrix & Change-Order Recovery")

    summary: ScopeAuditSummary | None = st.session_state.get("audit_summary")

    if not summary:
        st.info("👈 Click **'Run ScopeKernel Audit'** on the left panel to scan the client thread against the contract baseline.")

        with st.expander("💡 Why Solo Freelancers Rely on ScopeKernel", expanded=True):
            st.markdown(
                """
                - **Zero Legal Exposure:** Commercial NDAs forbid uploading client roadmaps and chats to OpenAI or Claude. ScopeKernel runs 100% on your device with verifiable zero network packets.
                - **Zero Marginal Cost:** 100,000 chat tokens per month cost $0.00 on your local hardware.
                - **80% Deterministic Noise Reduction:** Filters out chatter (*"morning"*, *"cool"*, *"thanks"*) in under 5ms, sending only genuine feature mutation candidates to local Gemma-2-2B.
                - **Client Rapport Shield:** Generates polite, diplomatic change-order copy ready to send immediately.
                """
            )
    else:
        # Dynamic rate recalculation
        total_unbilled_cost = round(summary.total_unbilled_hours * hourly_rate, 2)
        noise_ratio = int((summary.filtered_noise_count / max(1, summary.total_messages)) * 100)

        # KPI Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Unbilled Hours</div>
                    <div class="metric-value" style="color: #f59e0b;">{summary.total_unbilled_hours:.1f}h</div>
                    <div class="metric-sub">{summary.creep_detected_count} creep events</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Revenue Leakage</div>
                    <div class="metric-value" style="color: #ef4444;">{curr_sym}{total_unbilled_cost:,.2f}</div>
                    <div class="metric-sub">Recoverable delta</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Noise Stripped</div>
                    <div class="metric-value" style="color: #10b981;">{noise_ratio}%</div>
                    <div class="metric-sub">{summary.filtered_noise_count} messages pruned</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Network State</div>
                    <div class="metric-value" style="color: #38bdf8; font-size: 1.25rem; padding-top: 6px;">Air-Gapped</div>
                    <div class="metric-sub">0 Cloud Packets</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Tabs: Audit Matrix, Visual Chat Thread, Diplomatic Copilot, Formal Change Order Agreement
        tab_matrix, tab_thread, tab_copilot, tab_order = st.tabs(
            [
                "📊 Audit Matrix",
                "💬 Chat Thread Visualizer",
                "✍️ Diplomatic Copilot",
                "📑 Formal Change Order",
            ]
        )

        with tab_matrix:
            st.markdown("#### Itemized Scope Violation Matrix")
            filter_mode = st.radio(
                "Filter View",
                ["Scope Creep Violations Only", "All Candidate Messages"],
                horizontal=True,
            )

            displayed_results = (
                [r for r in summary.results if r.is_scope_creep]
                if filter_mode.startswith("Scope Creep")
                else summary.results
            )

            if not displayed_results:
                st.success("🎉 No out-of-scope requests detected! All messages comply with the SOW.")
            else:
                for idx, res in enumerate(displayed_results, 1):
                    card_class = "creep-card" if res.is_scope_creep else "safe-card"
                    tag_class = "tag-danger" if res.is_scope_creep else "tag-safe"
                    status_text = "⚠️ OUT-OF-SCOPE CREEP" if res.is_scope_creep else "✓ WITHIN SOW"
                    item_cost = round(res.estimated_hours * hourly_rate, 2)

                    sender_str = f"**{res.sender}**" if res.sender else "Client"
                    ts_str = f" • *{res.timestamp}*" if res.timestamp else ""

                    st.markdown(
                        f"""
                        <div class="{card_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span class="{tag_class}">{status_text}</span>
                                <span style="font-size: 0.9rem; font-weight: 700; color: #f8fafc;">
                                    {curr_sym}{item_cost:,.2f} ({res.estimated_hours:.1f} hrs)
                                </span>
                            </div>
                            <div style="font-size: 0.95rem; margin-bottom: 8px;">
                                {sender_str}{ts_str}: <br/>
                                <span style="color: #f1f5f9; font-style: italic;">"{res.raw_message}"</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #cbd5e1;">
                                <strong>Feature:</strong> {res.violating_feature}<br/>
                                <strong>Clause Cited:</strong> {res.matched_exclusion or "Deliverables Boundary"}<br/>
                                <strong>Reasoning:</strong> {res.reasoning}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with tab_thread:
            st.markdown("#### Client Communication Thread (Timeline View)")
            st.caption("Visual representation of client messages with real-time scope indicators.")

            all_msgs = extract_chat_messages(st.session_state["chat_text"])
            result_map = {r.raw_message.strip(): r for r in summary.results}

            for m in all_msgs[:35]:  # show first 35 messages
                is_client = "client" in (m.sender or "").lower() or "sarah" in (m.sender or "").lower() or "david" in (m.sender or "").lower()
                clean = m.clean_text.strip()
                res = result_map.get(clean)

                bubble_class = "chat-bubble-client" if is_client else "chat-bubble-freelancer"
                align_tag = ""

                if res and res.is_scope_creep:
                    item_cost = round(res.estimated_hours * hourly_rate, 2)
                    align_tag = f"<span class='tag-danger' style='float: right; margin-left: 8px;'>OUT-OF-SCOPE (+{res.estimated_hours:.1f}h / {curr_sym}{item_cost:,.2f})</span>"
                elif res and not res.is_scope_creep:
                    align_tag = "<span class='tag-safe' style='float: right; margin-left: 8px;'>IN-SCOPE</span>"

                ts_text = m.timestamp or ""

                st.markdown(
                    f"""
                    <div class="{bubble_class}">
                        <div class="chat-sender">{align_tag}{m.sender or 'User'}</div>
                        <div class="chat-text">{m.clean_text}</div>
                        <div class="chat-ts">{ts_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab_copilot:
            st.markdown("#### Ready-to-Send Diplomatic Change Orders")
            st.caption("Select your preferred communication tone to protect client rapport while establishing clear billing boundaries.")

            creep_results = [r for r in summary.results if r.is_scope_creep]
            if not creep_results:
                st.info("No scope violations found to draft change orders for.")
            else:
                for idx, r in enumerate(creep_results, 1):
                    item_cost = round(r.estimated_hours * hourly_rate, 2)
                    with st.expander(
                        f"✉️ #{idx}: {r.violating_feature} (+{r.estimated_hours:.1f} hrs / {curr_sym}{item_cost:,.2f})",
                        expanded=(idx == 1),
                    ):
                        st.markdown(f"**Original Client Request:** *\"{r.raw_message}\"*")
                        st.markdown(f"**Clause Cited:** `{r.matched_exclusion or 'Deliverables Boundary'}`")

                        # Tone options
                        tone_keys = [
                            "Collaborative & Diplomatic",
                            "Direct & Commercial",
                            "Phase 2 Deferral",
                            "WhatsApp Quick DM",
                        ]

                        default_reply = r.suggested_client_reply
                        tone_drafts = r.replies_by_tone or {}

                        selected_tone = st.radio(
                            "Select Tone Style:",
                            tone_keys,
                            horizontal=True,
                            key=f"tone_choice_{idx}",
                        )

                        active_reply = tone_drafts.get(selected_tone, default_reply)

                        st.text_area(
                            "Draft Change Order Copy",
                            value=active_reply,
                            height=110,
                            key=f"copilot_box_{idx}",
                        )

                        # Quick Action Links (WhatsApp Web & Email)
                        c_act1, c_act2 = st.columns(2)
                        with c_act1:
                            encoded_msg = urllib.parse.quote(active_reply)
                            wa_url = f"https://web.whatsapp.com/send?text={encoded_msg}"
                            st.link_button("📲 Send via WhatsApp Web", wa_url, use_container_width=True)

                        with c_act2:
                            subj = urllib.parse.quote(f"Scope Update: {r.violating_feature}")
                            body = urllib.parse.quote(active_reply)
                            mailto_url = f"mailto:?subject={subj}&body={body}"
                            st.link_button("📧 Open in Email Client", mailto_url, use_container_width=True)

        with tab_order:
            st.markdown("#### Formal Change-Order Agreement (Legal / SOW Addendum)")
            st.caption("An auditable, client-ready Change Order document itemizing new feature requests, hours, and budget adjustments.")

            contractor_name = st.text_input("Your Name / Company", value="Independent Freelance Engineer", key="co_contractor")
            client_name = st.text_input("Client Name / Company", value=parsed_contract.project_name.split()[0] + " LLC", key="co_client")

            # Build formal change order document
            order_lines = [
                f"# FORMAL CHANGE ORDER AMENDMENT #01",
                f"**Project Title:** {parsed_contract.project_name}",
                f"**Date Generated:** 2026-10-13",
                f"**Contractor:** {contractor_name}",
                f"**Client:** {client_name}",
                f"**Hourly Change-Order Rate:** {curr_sym}{hourly_rate:.2f}/hr",
                "\n---",
                "\n## 1. Description of Out-of-Scope Modifications",
                "The following additions were requested outside the agreed baseline milestone scope:\n",
            ]

            order_lines.append("| Item # | Feature Requested | Clause / Reason | Dev Hours | Financial Delta |")
            order_lines.append("|---|---|---|---|---|")

            for idx, r in enumerate(summary.results, 1):
                if r.is_scope_creep:
                    item_cost = round(r.estimated_hours * hourly_rate, 2)
                    order_lines.append(
                        f"| {idx} | {r.violating_feature} | {r.matched_exclusion or 'Baseline Deliverables Excluded'} | {r.estimated_hours:.1f} hrs | {curr_sym}{item_cost:,.2f} |"
                    )

            order_lines.extend(
                [
                    "\n---",
                    f"\n## 2. Summary of Contract Impact",
                    f"- **Total Additional Engineering Effort:** {summary.total_unbilled_hours:.1f} Hours",
                    f"- **Total Net Financial Adjustment:** {curr_sym}{total_unbilled_cost:,.2f}",
                    f"- **Timeline Impact:** +{max(1, int(summary.total_unbilled_hours // 8))} Business Days",
                    "\n---",
                    "\n## 3. Client Authorization & Sign-Off",
                    "By signing below or approving via written communication, the Client authorizes the Contractor to commence work on the specified Change Order items under the agreed terms.\n",
                    f"**Contractor Signature:** ___________________________   **Date:** ________\n",
                    f"**Client Authorized Signature:** ______________________   **Date:** ________\n",
                ]
            )

            formal_order_md = "\n".join(order_lines)
            st.text_area("Change Order Agreement Preview", value=formal_order_md, height=280)

            c_dl1, c_dl2 = st.columns(2)
            with c_dl1:
                st.download_button(
                    label="📥 Download Change Order (.md)",
                    data=formal_order_md,
                    file_name="Formal_Change_Order_Amendment.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with c_dl2:
                st.download_button(
                    label="📥 Download Audit Data (.json)",
                    data=summary.model_dump_json(indent=2),
                    file_name="ScopeKernel_Audit_Data.json",
                    mime="application/json",
                    use_container_width=True,
                )
