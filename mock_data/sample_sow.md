# Statement of Work (SOW): Artisan Roasters E-Commerce Platform

**Project Title:** Artisan Roasters Direct-to-Consumer Web Platform  
**Client:** Artisan Roasters LLC  
**Contractor:** Independent Freelance Full-Stack Engineer  
**Contract Type:** Fixed-Price Milestone MVP ($2,500.00 Base)  
**Hourly Rate:** $75.00 / hour (Agreed Overage & Change-Order Rate)  
**Milestone Timeline:** 3 Weeks (Estimated 32 Engineering Hours)  

---

## 1. Project Overview & Scope Baseline
This agreement specifies the engineering deliverables for Phase 1 of the Artisan Roasters web storefront. Any features, third-party integrations, or functional changes not explicitly outlined in Section 2 are strictly out of scope and require a formal Change Order billed at the agreed hourly rate of **$75.00/hr**.

---

## 2. Included Deliverables (In-Scope)
The following deliverables constitute the full and final scope of the Phase 1 milestone:

1. **User Authentication & Profiles:**
   - Standard user registration and sign-in using email and password.
   - Secure salted password hashing and JSON Web Token (JWT) session handling.
   - User profile page displaying basic contact details and order history.

2. **Product Catalog & Merchandising:**
   - Responsive product grid displaying coffee bean varieties, roast levels, and pricing.
   - Filter by category (Single Origin, Espresso Blend, Decaf).
   - Product detail modal with descriptions, origin notes, and weight options.

3. **Cart & Payment Processing:**
   - Client-side shopping cart with local persistence.
   - Stripe Checkout redirect integration for single-currency USD transactions.
   - Webhook listener to verify successful Stripe payments.

4. **Merchant Order Management:**
   - Password-protected admin view to view placed orders, status (Pending, Shipped), and customer addresses.

5. **Responsive Light UI Interface:**
   - Clean, modern light-theme user interface optimized for desktop and mobile browsers.

---

## 3. Explicit Exclusions (Out-of-Scope / Deferred to Phase 2)
The client explicitly agrees that the following capabilities are **NOT** included in the Phase 1 fixed fee and will be deferred or billed separately:

1. **Social / OAuth Authentication:**
   - Google Sign-in, Apple ID login, Facebook, or GitHub OAuth buttons.
2. **SMS & WhatsApp Messaging:**
   - Automated WhatsApp order confirmations or transactional SMS notifications via Twilio/Gupshup.
3. **Dark Mode & Dynamic Theming:**
   - Default dark mode appearance, automatic OS theme detection, or customizable user palettes.
4. **Multi-Currency & FX Exchange:**
   - Currency switcher (EUR, GBP, INR, CAD) and dynamic live exchange rate conversion.
5. **Automated PDF Generation:**
   - Server-side generation of downloadable PDF invoices, receipts, or packing slips.
6. **Accounting & Inventory ERP Integration:**
   - Two-way synchronization with QuickBooks, Xero, or custom warehouse software.

---

## 4. Change-Order Terms & Out-of-Scope Governance
Any client request communicated via informal channels (WhatsApp, Slack, Telegram, Email) that amends, expands, or introduces features listed in Section 3 or outside Section 2 will trigger a ScopeKernel change-order quote. Work on requested additions will commence only upon client authorization of the estimated dev hours at the agreed overage rate of **$75.00/hour**.
