from frappe import _

app_name = "policy_bazar"
app_logo_url = "/assets/policy_bazar/images/logo.png"

module_list = [
    {
        "label": _("Policy Bazar"),
        "items": [
            {"type": "doctype", "name": "Customer"},
            {"type": "doctype", "name": "Insurer"},
            {"type": "doctype", "name": "Insurance Policy"},
            {"type": "doctype", "name": "Policy Claim"},
            {"type": "doctype", "name": "AI Prompt"},
            {"type": "doctype", "name": "AI Feedback"},
            {"type": "report", "name": "Policies by Insurer", "doctype": "Insurance Policy"},
            {"type": "report", "name": "Upcoming Policy Expiries", "doctype": "Insurance Policy"},
            {"type": "page", "name": "policy-comparison", "label": _("Policy Comparison")},
        ],
    },
]
