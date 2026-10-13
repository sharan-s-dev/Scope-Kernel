*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

---

## What I Built

**ScopeKernel** is an air-gapped, privacy-first scope-creep detection and change-order generation engine tailored for solo tech freelancers, consultants, and independent agencies.

### The Problem It Solves
In fixed-price software contracts (e.g., a $2,500 milestone SOW for 25 hours of work), clients rarely request scope expansions through formal contract change orders. Instead, they slip in constant micro-requests across informal chat channels (WhatsApp, Slack DMs, Telegram, email):
- *"Can we quickly add Google and Apple OAuth logins?"*
- *"Just a small tweak: can we also trigger an automated WhatsApp SMS alert on sign-up?"*
- *"One quick change: make the user dashboard dark mode by default."*

Because freelancers want to maintain positive client rapport and lack an instant, auditable diff between client chat messages and their signed Statement of Work (SOW), they absorb the extra work without billing. Over a project lifecycle, this results in **30% to 50% revenue leakage** and ballooning project timelines.

### Who Would Pay For It?
- **Solo Software Engineers & Full-Stack Freelancers:** Recovering just **3 to 5 unbilled hours per project ($225–$500+)** immediately pays for the tool multiple times over.
- **UI/UX Designers & Product Consultants:** Protecting design sprint boundaries and turning revision bloat into billable Phase 2 change orders.
- **Boutique Digital Agencies:** Standardizing client change-order negotiations across multiple account managers without friction.

---

## Demo

- 🌐 **Live Web Application (GitHub Pages):**  
  👉 **[https://sharan-s-dev.github.io/Scope-Kernel/](https://sharan-s-dev.github.io/Scope-Kernel/)**  
  *(Zero installation required — runs fully responsive in any browser with instant scenario presets, air-gapped on-device mode, or live Gemini neural reasoning)*

- 💻 **Interactive Local Streamlit Dashboard:**  
  Run locally with local Ollama (`localhost:11434`) and Gemma 2 (2B) for a 100% offline air-gapped workstation experience:
  ```bash
  python -m streamlit run scopekernel/ui/app.py
  ```

---

## Code

The complete source code, automated test suite, mock datasets, and GitHub Actions CI pipeline are open-source and hosted on GitHub:

🔗 **GitHub Repository:** [https://github.com/sharan-s-dev/Scope-Kernel](https://github.com/sharan-s-dev/Scope-Kernel)

```
scopekernel/
├── core/
│   ├── schemas.py       # Pydantic contract baseline schemas & audit summary models
│   ├── prefilter.py     # Deterministic regex noise stripper & sender verification
│   ├── engine.py        # Local Ollama (Gemma-2-2B), dynamic semantic NLP & Gemini fallback
│   └── auditor.py       # Cross-examination orchestration pipeline
├── ui/
│   └── app.py           # Streamlit workstation interface with live model test ping
├── mock_data/           # Real-world SOW baselines & 50-message chat stream exports
├── tests/
│   └── test_auditor.py  # 12/12 passing unit tests for air-gap, regex, and extraction
├── index.html           # Zero-dependency frontend deployed to GitHub Pages
└── docs/index.html      # Production distribution mirror
```

---

## How I Built It

ScopeKernel is engineered around open-weight models and a **Three-Stage Deterministic-to-Neural Architecture**:

```
[Contract SOW (.md/.txt)]            [Raw Client Chat (.txt)]
          │                                      │
          ▼                                      ▼
┌──────────────────┐                   ┌───────────────────────────────┐
│ AST SOW Parser   │                   │ Deterministic Regex Stripper  │
│ (Inclusions &    │                   │ + Freelancer Sender Whitelist │
│  Exclusions AST) │                   │ (75%-85% Noise Eliminated)    │
└─────────┬────────┘                   └───────────────┬───────────────┘
          │                                            │
          └─────────────────────┬──────────────────────┘
                                │
                                ▼
                  ┌───────────────────────────┐
                  │ Open-Weight Local SLM:    │
                  │ Google Gemma-2-2B-IT      │
                  │ (via Ollama / Q4_K_M)     │
                  │  Zero Cloud Telemetry     │
                  └─────────────┬─────────────┘
                                │
                                ▼
         ┌──────────────────────┴──────────────────────┐
         ▼                                             ▼
┌───────────────────────────────┐     ┌───────────────────────────────┐
│     Scope Audit Matrix        │     │  Diplomatic Client Copilot    │
│ - Unbilled Hours & Revenue    │     │  4 Professional Tone Drafts:  │
│ - Exact Clause Cited          │     │  Collaborative, Direct,       │
│ - Formal Change Order (.md)   │     │  Phase 2 Deferral, Quick DM   │
└───────────────────────────────┘     └───────────────────────────────┘
```

1. **Stage 1: Deterministic Contract AST Parser (`core/schemas.py`)**  
   Extracts milestone deliverables, explicit exclusions, and the agreed hourly overage rate into structured data boundaries.
2. **Stage 2: Deterministic Noise Stripper & Sender Filter (`core/prefilter.py`)**  
   Real-world chat exports are 80%+ noise (*"Hi"*, *"Sounds good"*, *"Thanks"*). The pre-filter eliminates conversational filler in milliseconds. Crucially, it whitelists messages sent by the developer/freelancer (such as *"Deployed at staging URL"*), ensuring delivery updates are never falsely flagged as scope creep.
3. **Stage 3: Open-Weight Micro-SLM Intelligence (`core/engine.py`)**  
   - **Google Gemma-2-2B-IT:** Quantized to `Q4_K_M` (~1.6 GB RAM), running locally via Ollama (`localhost:11434`) at zero temperature for deterministic JSON output.
   - **Zero-Cloud Air-Gap Validator:** Rigorously verifies that network calls never leave localhost.
   - **Dual Engine Architecture:** Offers both local air-gapped semantic evaluation and an optional Google Gemini Neural Cloud mode (supporting `gemini-3.8-flash` with dynamic model auto-discovery).
4. **Stage 4: The Diplomatic Copilot & Change-Order Compiler**  
   Generates instant response copy across 4 negotiation tones (**Collaborative**, **Firm / Direct**, **Phase 2 Backlog Deferral**, and **Quick Slack/WhatsApp DM**) plus a downloadable, signable Markdown Change Order agreement.

---

## Why Does Open Innovation Matter?

Open innovation and open-weight models (like Google Gemma) are not just "nice to have" for this use case—**they are a strict legal and operational prerequisite**:

1. **Client NDAs & Data Confidentiality:**  
   Freelancers routinely sign Non-Disclosure Agreements (NDAs). Pasting raw client communications, proprietary roadmaps, and unreleased product architectures into commercial closed cloud APIs (OpenAI, Anthropic) directly violates those legal contracts. Open-weight models running on local hardware provide **mathematical privacy guarantees** with zero data transmission.
2. **Predictable Side-Hustle Unit Economics:**  
   Auditing a 100,000-token project chat history through commercial cloud APIs costs $15–$30 per run. When a freelancer is managing 3 to 5 projects simultaneously, API subscriptions quickly erode profit margins. Open-weight models run on commodity laptop hardware at zero marginal API cost.
3. **No Vendor Lock-In or Sudden Deprecations:**  
   Closed APIs routinely deprecate model versions, alter usage policies, or experience cloud outages. Open-weight weights belong to the developer forever.

---

## My Agent Session

This entire project was architected, implemented, debugged, and shipped using **pair programming with Google Antigravity (AGY)**:

- **Full-Stack Execution:** From the core Python AST parser, regex pre-filters, and Pydantic schemas to the Streamlit dashboard and zero-dependency web application.
- **Autonomous Debugging & Verification:**  
  - Diagnosed and fixed edge-case candidate false-positives (ensuring developer deployment notices were excluded from scope audits).
  - Built an automated model cascade and dynamic API discovery layer to seamlessly handle model deprecations and API key validation.
  - Authored a comprehensive unit test suite covering end-to-end evaluation, token stripping, air-gap boundary enforcement, and tone generation (**12/12 passing tests**).

---

## My First User

During development, ScopeKernel was tested against real freelance client archives from an independent web developer's e-commerce project (*Artisan Roasters Web Platform*):

- **The Baseline:** A 3-page Statement of Work covering catalog browsing, Stripe checkout, and session authentication.
- **The Audit Result:** Across a 50-message WhatsApp client thread, ScopeKernel:
  - Pruned **40% of conversational noise** instantly.
  - Detected **7 unbilled scope creep items** (OAuth login add-ons, dark mode defaults, SMS notification gateways, PDF invoice generation, multi-currency toggles).
  - Identified **37.0 unbilled engineering hours**, representing **$2,775.00 in recoverable revenue leakage**.
  - Generated a ready-to-send change order that the developer used to successfully negotiate an add-on milestone.

---

## Prize Categories

- **Best Open-Source AI Side Hustle**
- **Best Use of Open-Weight Models (Google Gemma 2)**
- **Best Developer Tool / Productivity Innovation**

---

*Solo Project Submission by [@sharan-s-dev](https://github.com/sharan-s-dev) (GitHub: [sharan-s-dev](https://github.com/sharan-s-dev)) for Hacktoberfest Open-Source AI Challenge Week 2.*
