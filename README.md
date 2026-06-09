# Policy Bazar

**Insurance application with AI-based risk scoring for ERPNext v15+**

Compatible with Frappe/ERPNext v15+, built on the ERPNext Core framework.

## Features

- **Master Data**: Insurance Customer, Insurer management
- **Transactions**: Insurance Policy, Policy Claim
- **AI-Powered**:
  - Risk scoring via OpenAI integration
  - Policy recommendations
  - Auto-fill claims from free-text descriptions
  - Fraud detection on claims
  - Editable prompt templates (no code deploy needed)
  - Underwriter feedback loop with caching
- **Reports**:
  - Policies by Insurer
  - Upcoming Policy Expiries (30-day window)
- **Workspace**: Insurance Dashboard with analytics
- **Notifications**: Policy expiry reminders (daily scheduled job)
- **Policy Comparison**: Side-by-side policy comparison page
- **Automated Quotes**: PDF quote generation with email delivery

## Installation

```bash
# from your frappe-bench directory
bench get-app /path/to/policy_bazar
bench --site your-site install-app policy_bazar
bench build
bench migrate
```

## Configuration

### AI Integration (Optional)

1. Add your OpenAI API key to site config:
```json
{
  "openai_api_key": "sk-XXXXXX..."
}
```

2. Configure AI prompts in the "AI Prompt" doctype via Desk UI.
3. AI risk scoring, claim auto-fill, fraud detection, and policy recommendations will activate automatically.

### Roles & Permissions

Default access is granted to **System Manager**. Extend roles via the standard ERPNext Role Permission Manager.

## App Structure

```
policy_bazar/
├── README.md
├── setup.py
├── requirements.txt
└── policy_bazar/
    ├── __init__.py
    ├── hooks.py
    ├── modules.txt
    ├── config/
    │   ├── desk.py
    │   ├── notification.py
    │   └── workspace/
    │       └── insurance_workspace.json
    ├── policies/
    │   ├── doctype/
    │   │   ├── customer/
    │   │   ├── insurer/
    │   │   ├── insurance_policy/
    │   │   ├── policy_claim/
    │   │   ├── ai_prompt/
    │   │   └── ai_feedback/
    │   └── reports/
    │       ├── policies_by_insurer/
    │       └── upcoming_expiries/
    ├── utils/
    │   └── ai_service.py
    ├── public/
    │   └── js/
    ├── page/
    │   └── policy_comparison/
    └── templates/
        └── emails/
```

## Development

- Fork and clone
- Create feature branch
- Submit PR with doctypes, reports, hooks, and workspace changes

## License

MIT
