# Policy Bazar — Standard Operating Procedure (SOP)

> **Version:** 0.1.0  
> **Platform:** Frappe / ERPNext v15+  
> **GitHub:** https://github.com/balaji-001-gif/insurance_mgt  
> **Last Updated:** June 2026

---

## Table of Contents

1. [Prerequisites & System Requirements](#1-prerequisites--system-requirements)
2. [Installation](#2-installation)
3. [Post-Installation Setup](#3-post-installation-setup)
4. [Architecture Overview](#4-architecture-overview)
5. [Working with Master Data](#5-working-with-master-data)
   - [5.1 Creating an Insurance Customer](#51-creating-an-insurance-customer)
   - [5.2 Creating an Insurer](#52-creating-an-insurer)
6. [Working with Insurance Policies](#6-working-with-insurance-policies)
   - [6.1 Creating a Policy](#61-creating-a-policy)
   - [6.2 AI Risk Scoring](#62-ai-risk-scoring)
   - [6.3 Policy Recommendations](#63-policy-recommendations)
   - [6.4 Sending a Quote](#64-sending-a-quote)
7. [Working with Policy Claims](#7-working-with-policy-claims)
   - [7.1 Creating a Claim](#71-creating-a-claim)
   - [7.2 AI Auto-Fill](#72-ai-auto-fill)
   - [7.3 Fraud Detection](#73-fraud-detection)
8. [AI Configuration](#8-ai-configuration)
   - [8.1 Setting Up OpenAI](#81-setting-up-openai)
   - [8.2 Managing AI Prompts](#82-managing-ai-prompts)
   - [8.3 Underwriter Feedback Loop](#83-underwriter-feedback-loop)
9. [Workspace & Dashboard](#9-workspace--dashboard)
10. [Reports](#10-reports)
11. [Policy Comparison Page](#11-policy-comparison-page)
12. [Notifications & Scheduled Jobs](#12-notifications--scheduled-jobs)
13. [User Roles & Permissions](#13-user-roles--permissions)
14. [Testing](#14-testing)
15. [Troubleshooting](#15-troubleshooting)
16. [FAQs](#16-faqs)

---

## 1. Prerequisites & System Requirements

### 1.1 Software Requirements

| Component | Version | Notes |
|---|---|---|
| **Frappe Framework** | ≥ 15, < 16 | ERPNext v15+ ships with this |
| **ERPNext** | v15+ | Core app installed |
| **Python** | ≥ 3.10 | Check with `python3 --version` |
| **Node.js** | ≥ 18 | Required for `bench build` |
| **Redis** | ≥ 6.x | For background jobs & caching |
| **MariaDB** | ≥ 10.6 | Or PostgreSQL ≥ 13 |
| **OpenAI (optional)** | Python package ≥ 1.0.0 | Only if using AI features |

### 1.2 Hardware Requirements

| Environment | Minimum | Recommended |
|---|---|---|
| **Development** | 4 GB RAM, 2 vCPU, 20 GB SSD | 8 GB RAM, 4 vCPU |
| **Production** | 8 GB RAM, 4 vCPU, 50 GB SSD | 16 GB RAM, 8 vCPU |

### 1.3 Required Knowledge

- Basic familiarity with **Frappe Bench** commands
- Understanding of **ERPNext** navigation (Desk, modules, doctypes)
- (Optional) OpenAI API key for AI features

---

## 2. Installation

### 2.1 Get the App from GitHub

```bash
# Navigate to your frappe-bench directory
cd ~/frappe-bench

# Download the app
bench get-app https://github.com/balaji-001-gif/insurance_mgt.git

# This creates an `insurance_mgt` directory with the `policy_bazar` app inside
```

> ⚠️ The repo name on GitHub is `insurance_mgt`, but the Frappe app name is `policy_bazar`.

### 2.2 Install on a Site

```bash
# Replace "your-site" with your actual site name
bench --site your-site install-app policy_bazar

# Build frontend assets
bench build

# Run migrations to apply fixtures
bench migrate
```

### 2.3 Verify Installation

1. Open your site in the browser: `https://your-site:8000`
2. Log in as **Administrator** (or a user with System Manager role)
3. You should see **"Insurance"** in the ERPNext module list (desktop grid)
4. Click the Insurance icon to open the **Insurance Dashboard** workspace

![Installation Check](https://via.placeholder.com/400x200?text=Insurance+Module+Visible)

### 2.4 Update the App (Future Versions)

```bash
bench get-app --branch main https://github.com/balaji-001-gif/insurance_mgt.git
bench --site your-site migrate
bench build
```

---

## 3. Post-Installation Setup

### 3.1 What Gets Auto-Created

On `bench migrate` (or first `install-app`), the following are seeded automatically:

| Fixture | Records Created |
|---|---|
| **AI Prompts** | 4 defaults (Risk Scoring, Policy Recommendations, Claim Auto-Fill, Fraud Detection) |
| **Roles** | Insurance Manager, Insurance User |
| **Dashboard Charts** | Average Risk by Insurer (bar), Monthly Fraud Rate (line) |
| **Number Cards** | Active Policies, Total Premium Written, Pending Claims |

### 3.2 Assign User Roles

Navigate to: **Home → Users → User** → select a user → add roles:

| Role | Access Level |
|---|---|
| **Insurance Manager** | Full create/read/write/delete on all Policy Bazar doctypes |
| **Insurance User** | Create and read access (limited) |
| **System Manager** | Full access (always has it by default) |

**Steps:**
1. Go to: `https://your-site:8000/app/user`
2. Open a user (or create one)
3. In the **Roles & Permissions** section, add **Insurance Manager** or **Insurance User**
4. Save

### 3.3 Configure OpenAI (Optional but Recommended)

To unlock AI features:

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Add it to your site config:

```bash
bench --site your-site set-config openai_api_key "sk-XXXXX..."
```

Or manually edit `sites/your-site/site_config.json`:

```json
{
  "db_name": "...",
  "db_password": "...",
  "openai_api_key": "sk-XXXXX..."
}
```

3. Restart the bench:

```bash
bench restart
```

> If running behind supervisor (production), also run `sudo supervisorctl restart all` or restart the relevant processes to pick up the API key.

> If no API key is configured, all AI features gracefully fall back to deterministic logic (e.g., risk score based on premium/sum-assured ratio).

---

## 4. Architecture Overview

### 4.1 Doctypes at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                     Policy Bazar App                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌─────────┐    ┌──────────────────┐        │
│  │ Insurance │◄───│ Policy  │───►│   Policy Claim    │        │
│  └──────────┘    │         │    └──────────────────┘        │
│                  │ Policy  │                                 │
│  ┌──────────┐    │         │    ┌──────────────────┐        │
│  │ Insurer  │───►│         │    │    AI Prompt      │        │
│  └──────────┘    └─────────┘    └──────────────────┘        │
│                                          │                   │
│                                 ┌────────▼────────┐         │
│                                 │   AI Feedback    │         │
│                                 └─────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Key Fields per Doctype

| Doctype | Key Fields |
|---|---|
| **Insurance Customer** | customer_id, customer_name, email, phone, address, age, medical_history |
| **Insurer** | insurer_code, insurer_name, website, email, phone |
| **Insurance Policy** | policy_number, customer (link), insurer (link), policy_start, policy_end, premium, sum_assured, policy_type, risk_score, risk_score_last_updated, risk_score_overridden, override_reason |
| **Policy Claim** | claim_id, policy (link), claimant_name, date_of_claim, claim_amount, claim_description, incident_description, status, fraud_flag |
| **AI Prompt** | prompt_name, model, temperature, prompt_template |
| **AI Feedback** | linked_doctype, linked_docname, old_score, new_score, reason |

---

## 5. Working with Master Data

### 5.1 Creating an Insurance Customer

**Navigation:** Insurance Dashboard → **Insurance Customers** card → Click **+ Add Insurance Customer**

**Form Fields:**

| Field | Required | Description |
|---|---|---|
| Customer ID | ✅ | Unique identifier (auto-set by the field value) |
| Customer Name | ✅ | Full name of the customer |
| Email | ❌ | Email address (validated on save) |
| Phone | ❌ | Contact number |
| Address | ❌ | Physical address |
| Age | ❌ | Customer's age (used for AI risk scoring) |
| Medical History | ❌ | Pre-existing conditions (used for AI recommendations) |

**Validation Rules:**
- Email is validated for correct format on save
- Customer ID must be unique

**Step-by-Step:**
1. Click → **+ Add Insurance Customer** (top-right or via the master data section)
2. Fill in **Customer ID** (e.g., `CUST-001`)
3. Fill in **Customer Name** (e.g., `John Doe`)
4. (Optional) Enter **Email**, **Phone**, **Address**
5. (Optional) Enter **Age** and **Medical History** for better AI results
6. Click **Save**

### 5.2 Creating an Insurer

**Navigation:** Insurance Dashboard → **Insurers** card → Click **+ Add Insurer**

**Form Fields:**

| Field | Required | Description |
|---|---|---|
| Insurer Code | ✅ | Unique code (e.g., `ICICI-LOMBARD`) |
| Insurer Name | ✅ | Full company name |
| Website | ❌ | Company website URL |
| Email | ❌ | Contact email |
| Phone | ❌ | Contact phone |

**Step-by-Step:**
1. Click → **+ Add Insurer**
2. Fill in **Insurer Code** (e.g., `HDFC-ERGO`)
3. Fill in **Insurer Name** (e.g., `HDFC Ergo General Insurance`)
4. (Optional) Add **Website**, **Email**, **Phone**
5. Click **Save**

---

## 6. Working with Insurance Policies

### 6.1 Creating a Policy

**Navigation:** Insurance Dashboard → **Insurance Policies** card → Click **+ Add Insurance Policy**

**Form Fields:**

| Field | Required | Description |
|---|---|---|
| Policy Number | ✅ | Unique policy number |
| Customer | ✅ | Link to Insurance Customer doctype |
| Insurer | ✅ | Link to Insurer doctype |
| Policy Type | ✅ | Life / Health / Vehicle / Home / Travel |
| Start Date | ✅ | When coverage begins |
| End Date | ✅ | When coverage ends (must be after start date) |
| Premium | ✅ | Premium amount in currency |
| Sum Assured | ❌ | Total coverage amount |
| AI Risk Score | — | Read-only, auto-calculated by AI |
| Risk Score Last Updated | — | Read-only timestamp of last AI scoring |
| Overridden by User | ❌ | Check if manually overriding AI score |
| Override Reason | ❌ | Reason for manual override |

**Step-by-Step:**
1. Click → **+ Add Insurance Policy**
2. Select an existing **Insurance Customer** from the dropdown
3. Select an existing **Insurer** from the dropdown
4. Choose **Policy Type** (Life, Health, Vehicle, Home, Travel)
5. Enter **Policy Number** (e.g., `POL-2026-001`)
6. Set **Start Date** and **End Date** (end must be after start)
7. Enter **Premium** (e.g., `50000`)
8. (Optional) Enter **Sum Assured**
9. Click **Save**

![Insurance Policy Form](https://via.placeholder.com/600x400?text=Insurance+Policy+Form)

**Validation:**
- End date must be after start date — save will fail otherwise
- Risk score is auto-calculated on save

### 6.2 AI Risk Scoring

On every save, the policy's **risk score** is automatically calculated:

1. **If OpenAI is configured:** The AI analyzes customer profile + policy data to generate a score (0–100)
2. **If OpenAI is NOT configured:** A deterministic fallback uses the premium/sum-assured ratio
3. **Caching:** Risk score is cached for **7 days** — it won't be recalculated within that window
4. **Override:** A user with Insurance Manager role can:
   - Check **"Overridden by User"**
   - Manually set a **risk score**
   - Provide an **Override Reason**
   - This locks the score (no AI recalculation)

The override is logged in the **AI Feedback** doctype for audit trail.

### 6.3 Policy Recommendations

From any saved Insurance Policy form:

1. Click the **"Recommend Policies"** button (top-right menu)
2. The AI analyzes the customer's profile against other policies in the system
3. A dialog shows the **top 3 recommended policies** with rationale
4. (Fallback: returns raw policy list if AI is unavailable)

### 6.4 Sending a Quote

From any saved Insurance Policy form:

1. Click the **"Send Quote"** button (top-right menu)
2. The system generates a **PDF quote** using the email template
3. The quote is **emailed** to the customer's email address
4. A confirmation message: *"Quote sent successfully!"*

**Prerequisites:**
- Customer must have an email address
- Email must be configured in ERPNext (Outgoing Email Settings)

---

## 7. Working with Policy Claims

### 7.1 Creating a Claim

**Navigation:** Insurance Dashboard → **Policy Claims** card → Click **+ Add Policy Claim**

**Form Fields:**

| Field | Required | Description |
|---|---|---|
| Claim ID | ✅ | Unique claim identifier |
| Policy | ✅ | Link to Insurance Policy |
| Claimant Name | ✅ * | Name (may be auto-filled by AI) |
| Date of Claim | ✅ * | Claim date (may be auto-filled by AI) |
| Claim Amount | ✅ | Amount being claimed |
| Claim Description | ❌ | Free-text description of the incident |
| Incident Description | ❌ | Structured description (may be auto-filled) |
| Status | — | Draft / Submitted / Approved / Rejected |
| Fraud Flag | — | Read-only, auto-set by fraud detection |

**Step-by-Step:**
1. Click → **+ Add Policy Claim**
2. Select an existing **Policy**
3. Enter **Claim ID** (e.g., `CL-2026-001`)
4. Enter **Claim Amount**
5. Set **Status** (default: Draft)
6. (Optional) Type a free-text **Claim Description** for AI auto-fill
7. Click **Save**

### 7.2 AI Auto-Fill

If you enter a **Claim Description** (e.g., *"John had a car accident on 2026-03-15, rear-ended at a traffic signal, moderate damage to the bumper"*) **without filling** Claimant Name, Date of Claim, or Incident Description:

1. On save, the AI parses the text
2. Extracts: **claimant_name**, **date_of_event**, **incident_description**
3. Auto-fills those fields in the claim form

> If AI is unavailable, the fields remain blank — no error is thrown.

### 7.3 Fraud Detection

When a claim is **Submitted** (status changed from Draft to Submitted):

1. The AI runs a fraud detection check on the claim
2. **If potential fraud detected:**
   - Status is set to **Rejected**
   - **Fraud Flag** is set to **1**
   - User sees: *"Claim marked as potential fraud – please review manually."*
3. **If no fraud:**
   - Status stays as **Submitted** for manual approval
   - **Fraud Flag** stays **0**

**Fallback (no AI):** Claims above ₹1,00,000 are flagged as potential fraud.

---

## 8. AI Configuration

### 8.1 Setting Up OpenAI

**Step 1: Get an API Key**
1. Go to https://platform.openai.com/api-keys
2. Click **+ Create new secret key**
3. Copy the key (starts with `sk-...`)

**Step 2: Add to Site Config**

```bash
bench --site your-site set-config openai_api_key "sk-XXXXX..."
```

**Step 3: Verify**

```bash
bench --site your-site console
```

In the console:

```python
import frappe
frappe.conf.get("openai_api_key")  # Should return your key
```

### 8.2 Managing AI Prompts

AI Prompts are editable via the UI — no code changes needed:

**Navigation:** Insurance Dashboard → **AI Prompts** card

| Default Prompt | Purpose | Model |
|---|---|---|
| **Risk Scoring** | Assigns 0–100 risk score to each policy | gpt-4o (temp: 0.0) |
| **Policy Recommendations** | Recommends top 3 policies for a customer | gpt-4o (temp: 0.7) |
| **Claim Auto-Fill** | Extracts structured data from free-text | gpt-4o (temp: 0.0) |
| **Fraud Detection** | Flags potentially fraudulent claims | gpt-4o (temp: 0.0) |

**To customize a prompt:**
1. Open an **AI Prompt** record
2. Edit the **Prompt Template** (use `{variable}` placeholders)
3. Change the **Model** (e.g., `gpt-4o-mini` for lower cost)
4. Adjust **Temperature** (0.0 = deterministic, 1.0 = creative)
5. Save — changes take effect immediately (no deploy)

**Important:** Do not rename the default prompt names, as the code references them by name.

### 8.3 Underwriter Feedback Loop

When an underwriter (Insurance Manager) overrides an AI risk score:

1. Check **"Overridden by User"** on the Insurance Policy
2. Set a new **Risk Score** manually
3. Fill in **Override Reason** (e.g., "Customer has excellent health records")
4. Save

This creates an **AI Feedback** record with:
- Old score (AI's value)
- New score (manual override)
- Reason for override

This data can be exported to retrain custom AI models.

---

## 9. Workspace & Dashboard

### 9.1 Accessing the Insurance Dashboard

1. From the ERPNext desktop, click the **Insurance** (shield) icon
2. OR go directly to: `https://your-site:8000/app/workspace/Insurance%20Dashboard`

### 9.2 Dashboard Sections

```
┌───────────────────────────────────────────────────┐
│            Insurance Dashboard                     │
├───────────────────────────────────────────────────┤
│   Master Data              │  Operations           │
│   ┌────────┐ ┌────────┐   │  ┌────────┐ ┌───────┐│
│   │Insurance│ │Insurer │   │  │Policies│ │Claims ││
│   └────────┘ └────────┘   │  └────────┘ └───────┘│
│   ┌────────┐              │  ┌──────────────┐     │
│   │AI      │              │  │Policy Compare│     │
│   │Prompts │              │  └──────────────┘     │
│   └────────┘              │                        │
├───────────────────────────┴────────────────────────┤
│   Analytics                                         │
│   ┌────────────────────┐  ┌────────────────────┐    │
│   │Avg Risk by Insurer│  │Monthly Fraud Rate  │    │
│   │   [Bar Chart]     │  │   [Line Chart]     │    │
│   └────────────────────┘  └────────────────────┘    │
├────────────────────────────────────────────────────┤
│   Number Cards                                       │
│   ┌──────────────┐ ┌─────────────────┐ ┌───────────┐│
│   │Active        │ │Total Premium    │ │Pending    ││
│   │Policies: 42  │ │Written: ₹2.1Cr  │ │Claims: 5  ││
│   └──────────────┘ └─────────────────┘ └───────────┘│
├────────────────────────────────────────────────────┤
│   Reports                                           │
│   ┌──────────────────┐ ┌─────────────────────────┐  │
│   │Policies by       │ │Upcoming Policy Expiries │  │
│   │Insurer           │ │                         │  │
│   └──────────────────┘ └─────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 10. Reports

### 10.1 Policies by Insurer

**Navigation:** Insurance Dashboard → **Policies by Insurer** card

A summary report showing:
- **Insurer** — Name of the insurance company
- **Total Policies** — Count of policies per insurer
- **Total Premium** — Sum of all premiums per insurer

**Use Case:** Understand which insurers have the most business and revenue.

### 10.2 Upcoming Policy Expiries

**Navigation:** Insurance Dashboard → **Upcoming Expiries** card

Lists policies expiring within the next **30 days**:
- Policy number (clickable link)
- Customer
- Expiry Date
- Premium

**Use Case:** Proactive renewal outreach to customers.

---

## 11. Policy Comparison Page

**Navigation:** Insurance Dashboard → **Policy Comparison** card

A side-by-side table view of **all policies** with:
- Policy (clickable link to the form)
- Insurer
- Type
- Premium
- Risk Score (color-coded badge)
  - 🟢 **Green** (≤ 40) — Low risk
  - 🟡 **Yellow** (41–70) — Medium risk
  - 🔴 **Red** (> 70) — High risk
- Start Date & End Date

**Direct URL:** `https://your-site:8000/app/policy-comparison`

---

## 12. Notifications & Scheduled Jobs

### 12.1 Policy Expiry Reminders

The system runs a **daily scheduled job** that:
1. Checks all policies expiring within the **next 30 days**
2. Sends an **email reminder** to each customer
3. Email includes: policy number, expiry date, renewal prompt

**Email Content:**
```
Subject: Your policy POL-2026-001 expiring on 2026-07-15

Dear CUST-001, your policy POL-2026-001 expires on 2026-07-15.
Please contact us for renewal.
```

### 12.2 In-App Notifications

When a policy is about to expire or has expired, users with Insurance Manager role see **notifications** in the ERPNext notification bell:
- **Expiring Soon** — Policy expiring within 30 days
- **Expired** — Policy has expired

### 12.3 Checking Scheduled Jobs

```bash
bench --site your-site scheduler run-daily
```

To view pending jobs:
```bash
bench --site your-site console
```

```python
import frappe
frappe.get_all("Scheduled Job Log", filters={"scheduled_job_type": "policy_bazar.policies.doctype.insurance_policy.insurance_policy.send_expiry_reminders"})
```

---

## 13. User Roles & Permissions

### 13.1 Role Definitions

| Role | Description | Default |
|---|---|---|
| **System Manager** | Full access to everything | Yes (pre-existing) |
| **Insurance Manager** | Full CRUD on all Policy Bazar doctypes | Created on install |
| **Insurance User** | Create + Read access on Policy Bazar doctypes | Created on install |

### 13.2 Permission Matrix

| Doctype | Insurance Manager | Insurance User |
|---|---|---|
| Insurance Customer | Create, Read, Write, Delete | Create, Read |
| Insurer | Create, Read, Write, Delete | Create, Read |
| Insurance Policy | Create, Read, Write, Delete | Create, Read |
| Policy Claim | Create, Read, Write, Delete | Create, Read |
| AI Prompt | Create, Read, Write, Delete | Read only |
| AI Feedback | Create, Read | Create (auto), Read |

### 13.3 Assigning a Role

1. Go to: **Home → Users → User**
2. Open the target user
3. Under **Roles & Permissions**, add the role
4. Save

---

## 14. Testing

### 14.1 Running Unit Tests

```bash
# From your frappe-bench directory
bench --site your-site run-tests --module "Policy Bazar"
```

### 14.2 Test Coverage

| Test File | Tests |
|---|---|
| `tests/test_insurance_policy.py` | Policy creation, date validation, customer email validation, risk score caching, notification context |
| `tests/test_policy_claim.py` | Claim creation, default status |
| `tests/test_ai_service.py` | Risk score fallback, deterministic fallback, policy recommendations fallback, claim auto-fill fallback, fraud detection fallback |

### 14.3 Manual Testing Checklist

After installation, verify:

- [ ] Can create an Insurance Customer
- [ ] Customer email validation works (invalid emails rejected)
- [ ] Can create an Insurer
- [ ] Can create an Insurance Policy with valid dates
- [ ] Policy with invalid dates (end ≤ start) is rejected
- [ ] Risk score is auto-populated on save
- [ ] Risk score persists after re-saving (cached for 7 days)
- [ ] Can override risk score with reason (Insurance Manager)
- [ ] "Recommend Policies" button shows on saved policies
- [ ] "Send Quote" button shows on saved policies
- [ ] Can create a Policy Claim linked to a policy
- [ ] Claim with fraud_flag=1 gets rejected on submit (for amounts > ₹1L or via AI)
- [ ] AI Prompt prompts are editable from UI
- [ ] Insurance Dashboard loads with charts
- [ ] Policies by Insurer report runs
- [ ] Upcoming Expiries report runs
- [ ] Policy Comparison page shows all policies

---

## 15. Troubleshooting

### 15.1 Installation Issues

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'policy_bazar'` | Run `bench build` and restart bench |
| App not showing in module list | Verify `modules.txt` has correct format. Run `bench migrate` |
| `frappe.exceptions.DoesNotExistError: DocType Insurance Customer` | Check that Insurance Customer doctype JSON is valid. Re-install app |
| Desktop icon not appearing | Run `bench build` and clear browser cache |

### 15.2 AI Features Not Working

| Problem | Solution |
|---|---|
| OpenAI API key missing | Add `openai_api_key` to `site_config.json` → `bench restart` |
| `openai` package not installed | Run `pip install openai>=1.0.0` in bench environment |
| AI returns unexpected scores | Edit prompt template in **AI Prompt** doctype |
| Rate limit errors from OpenAI | Check OpenAI usage dashboard. Reduce temperature or use `gpt-4o-mini` |
| Fraud detection too sensitive | Increase fallback threshold in `ai_service.py` or edit prompt |

### 15.3 Policy/Claim Issues

| Problem | Solution |
|---|---|
| Policy end date validation fails | Ensure end date is strictly after start date |
| Claim submission blocked by fraud | Manual review needed — if false positive, clear fraud_flag and set status to Submitted |
| Quote email not sending | Configure **Outgoing Email Settings** in ERPNext |
| Customer email not found | Ensure customer has a valid email address |

### 15.4 Common Bench Commands

```bash
# Check app list
bench --site your-site list-apps

# Re-install app (caution: data loss)
bench --site your-site reinstall

# Clear cache
bench clear-cache

# Restart bench
bench restart

# View logs
bench --site your-site console
bench --site your-site show-logs
```

---

## 16. FAQs

### Q1: Do I need an OpenAI key to use the app?

**No.** The app works fully without it. AI features gracefully fall back to deterministic logic:
- Risk scoring uses premium/sum-assured ratio
- Recommendations return raw policy list
- Fraud detection flags claims > ₹1,00,000

### Q2: Can I use a different AI model?

**Yes.** Edit any **AI Prompt** record and change the `model` field to any OpenAI model (e.g., `gpt-4o-mini`, `gpt-3.5-turbo`).

### Q3: How do I add custom fields to a doctype?

Use the standard ERPNext **Customize Form** feature:
1. Go to **Settings → Customize Form**
2. Select the doctype (e.g., Insurance Policy)
3. Add your custom fields
4. Save

### Q4: Can I integrate this with other ERPNext modules?

**Yes.** The **Insurance Customer** doctype is independent, but you can link ERPNext's native Customer doctype to policies via standard customization if needed.

### Q5: How do I export data?

Use the standard ERPNext **Data Export** tool:
1. Go to any doctype list view
2. Click **Menu → Export**
3. Choose format (CSV, Excel)

### Q6: Why does the risk score not update when I edit a policy?

The risk score is cached for **7 days** to avoid repeated API calls. To force a recalculation:
1. Clear the **Risk Score Last Updated** field
2. Uncheck **Overridden by User** (if checked)
3. Save

### Q7: Can I run this in production?

**Yes.** The app follows all ERPNext v15+ standards. For production:
- Set up proper email configuration
- Configure OpenAI with a production API key
- Assign appropriate roles to users
- Set up regular site backups

---

## Appendix A: File Structure Reference

```
policy_bazar/
├── .gitignore
├── LICENSE                    # MIT License
├── README.md                  # Quick-start readme
├── SOP.md                     # ← You are here
├── patches.txt                # Migration patches
├── requirements.txt           # Python dependencies
├── setup.py                   # Package configuration
├── fixtures/
│   ├── ai_prompt.json         # Default AI prompts
│   ├── charts.json            # Dashboard charts
│   ├── number_cards.json      # Number card definitions
│   └── roles.json             # Custom roles
├── tests/
│   ├── __init__.py
│   ├── test_ai_service.py
│   ├── test_insurance_policy.py
│   └── test_policy_claim.py
└── policy_bazar/
    ├── __init__.py
    ├── hooks.py               # App manifest
    ├── modules.txt
    ├── policy_bazar.js
    ├── config/
    │   ├── desk.py
    │   ├── notification.py
    │   └── workspace/
    │       └── insurance_workspace.json
    ├── desktop_icon/
    │   └── insurance.json
    ├── page/
    │   └── policy_comparison/
    │       ├── policy_comparison.html
    │       └── policy_comparison.py
    ├── policies/
    │   ├── doctype/
    │   │   ├── ai_feedback/
    │   │   ├── ai_prompt/
    │   │   ├── insurance_customer/
    │   │   ├── insurance_policy/
    │   │   ├── insurer/
    │   │   └── policy_claim/
    │   └── reports/
    │       ├── policies_by_insurer/
    │       └── upcoming_expiries/
    ├── public/js/
    │   ├── insurance_policy.js
    │   └── policy_comparison.js
    ├── setup/
    │   └── install.py
    ├── templates/emails/
    │   └── quote_template.html
    └── utils/
        └── ai_service.py
```

## Appendix B: Quick Reference Commands

```bash
# ─── Installation ───
bench get-app https://github.com/balaji-001-gif/insurance_mgt.git
bench --site your-site install-app policy_bazar
bench build
bench migrate

# ─── Configuration ───
bench --site your-site set-config openai_api_key "sk-XXXXX..."

# ─── Updates ───
bench get-app --branch main https://github.com/balaji-001-gif/insurance_mgt.git
bench --site your-site migrate
bench build

# ─── Testing ───
bench --site your-site run-tests --module "Policy Bazar"

# ─── Troubleshooting ───
bench clear-cache
bench restart
bench --site your-site console
```

---

> **End of SOP — Policy Bazar v0.1.0**  
> For questions or feature requests, reach out to the project maintainer or open an issue on GitHub.
