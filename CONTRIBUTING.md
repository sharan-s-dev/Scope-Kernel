# Contributing to ScopeKernel 🛡️

Thank you for your interest in contributing to **ScopeKernel**! I am participating in **Hacktoberfest 2026** and welcome contributions from developers, technical writers, and freelance consultants worldwide.

ScopeKernel is an air-gapped contract auditor and scope creep copilot built with open-weight models (Google Gemma-2-2B, Llama 3) to protect independent software engineers and agencies from unbilled scope creep under strict NDAs.

---

## 🌟 How You Can Contribute

I have curated several key areas where your contributions will make an immediate impact:

### 1. Statement of Work (SOW) Scenario Baselines 📄
Help expand our contract test suite in `mock_data/`:
- **New Tech Stacks:** Shopify D2C stores, Flutter/React Native mobile apps, FastAPI backends, Next.js SaaS platforms, or Machine Learning pipelines.
- **Realistic Chat Logs:** Real-world chat threads (with all confidential client names and URLs anonymized) simulating tricky scope expansion (e.g., *"Can we just add Apple Pay?"*, *"Need automated QuickBooks sync by Monday"*).

### 2. Regional Diplomatic Response Templates 💬
Scope creep requires culturally nuanced negotiation:
- **Indian Tech Ecosystem:** Respectful, milestone-aligned phrasing (*"Namaste! Happy to incorporate this into Phase 2 or scope a quick Change Order"*).
- **Silicon Valley Enterprise:** Formal SOW amendment terminology (*"Pursuant to Clause 4.2 of our signed agreement, this requires an Addendum"*).
- **European / Direct:** Direct, transparent budget and timeline adjustment phrasing.
- **Async Slack/WhatsApp Quick DMs:** 2-line polite pushback messages that keep client relationships warm without giving away free labor.

### 3. Regex Pre-Filter & Whitelist Heuristics 🧹
Improve our sub-5ms pre-filter in `scopekernel/core/auditor.py`:
- Expand conversational noise pruning patterns (*"noted"*, *"will check with my team"*, *"sounds good"*).
- Enhance developer delivery whitelist logic so legitimate milestone updates (*"Pushed to staging"*, *"Updated API docs"*) are never flagged as scope creep.

### 4. Local Open-Weight Model Harnesses 🤖
- Optimize prompts and temperature configurations for `gemma2:2b`, `llama3.2:3b`, and `qwen2.5:3b`.
- Add local inference harnesses (e.g. llama.cpp GGUF bindings, vLLM, or browser-local WebLLM).

### 5. Web Cockpit & UX Improvements 🎨
- Enhance the interactive browser cockpit in `index.html` (accessible also via GitHub Pages).
- Add keyboard shortcuts, responsive layout polish, or dark/light theme refinements.

---

## 🛠️ Development Setup

### 1. Fork & Clone
```bash
git clone https://github.com/sharan-s-dev/Scope-Kernel.git
cd Scope-Kernel
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Automated Tests
Ensure all existing tests pass before making changes:
```bash
python -m pytest
```

### 4. Run the Local Cockpit
```bash
# Launch Streamlit local dashboard:
streamlit run scopekernel/ui/app.py

# Or launch local web cockpit:
python -m http.server 8080 --directory docs
```

---

## 📋 Pull Request Guidelines

1. **Keep it Air-Gapped:** ScopeKernel must never send client contract text or chat logs to third-party endpoints by default. Any cloud integration (like optional Gemini API) must remain strictly opt-in with explicit user-provided API keys.
2. **Include Tests:** If you add new detection rules or parsing logic, add corresponding test cases in `scopekernel/tests/test_auditor.py`.
3. **Follow Conventional Commits:**
   - `feat: add Shopify D2C SOW scenario and chat benchmark`
   - `fix: prevent false positive on staging server status updates`
   - `docs: improve quickstart instructions for Windows PowerShell`
4. **Be Kind & Respectful:** We follow standard open-source community standards.

Happy Hacking! 🚀
