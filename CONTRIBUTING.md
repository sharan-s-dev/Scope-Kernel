# Contributing to ScopeKernel 🛡️

Welcome to **ScopeKernel**! Thank you for taking the time to contribute. ScopeKernel is an open-source, air-gapped contract auditor and scope creep copilot built for Hacktoberfest.

Whether you're fixing a bug, adding new contract scenarios, or improving detection heuristics, your help is welcome!

---

## 🏷️ Hacktoberfest Quickstart

1. **Fork** this repository to your GitHub account.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/sharan-s-dev/Scope-Kernel.git
   cd Scope-Kernel
   ```
3. Set up dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the test suite to ensure everything is working:
   ```bash
   npm test
   # Or: python -m pytest
   ```
5. Start the web dashboard:
   ```bash
   npm run web
   # Open http://localhost:8080
   ```

---

## 🎯 Good First Issues (Hacktoberfest Ideas)

Here are high-impact areas where contributions are actively welcome:

### 1. Additional Contract & Chat Scenarios
Currently, the repo includes sample contracts for an e-commerce platform and a mobile app in `mock_data/`.
- **Goal:** Add more real-world contract baselines (e.g. Next.js SaaS, Flutter mobile app, or backend API).
- **How:** Add `.md` SOW files and sample chat logs in `mock_data/`.

### 2. Conversational Noise Pruning
- **Goal:** Catch more informal filler messages before model inference.
- **How:** Improve regex patterns in `scopekernel/core/prefilter.py` to prune routine chit-chat without dropping real feature requests.

### 3. Diplomatic Response Templates
- **Goal:** Improve the phrasing and helpfulness of the reply drafts.
- **How:** Refine the response tone generators in `scopekernel/core/engine.py`.

### 4. Web UI Polish
- **Goal:** Improve usability, keyboard shortcuts, or styling in the web interface.
- **How:** Edit `index.html` or `scopekernel/ui/app.py`.

---

## 🧪 Testing Your Changes

Before submitting your pull request, ensure all tests pass:

```bash
# Run unit tests
npm test
# Or: python -m pytest
```

---

## 📬 Pull Request Guidelines

1. **Branch Naming:** `feat/add-saas-sow`, `fix/prefilter-regex`, `docs/update-readme`
2. **Commit Messages:** Use clear, descriptive commit messages (e.g. `feat(prefilter): add common chat acknowledgment patterns`).
3. **Keep PRs Focused:** Small, single-purpose pull requests are reviewed and merged much faster.

Happy Hacking! 🚀
