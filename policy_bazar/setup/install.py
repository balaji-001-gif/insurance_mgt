import frappe


def after_install():
    """Run after the app is installed.

    Seeds default AI Prompt records so users can use AI features
    right away without manually creating prompts.
    """
    seed_ai_prompts()
    seed_roles()
    frappe.db.commit()


def seed_ai_prompts():
    """Create default AI Prompt records if they don't exist."""
    prompts = [
        {
            "prompt_name": "Risk Scoring",
            "model": "gpt-4o",
            "temperature": 0.0,
            "prompt_template": (
                "You are an insurance underwriter.\n"
                "Given the following customer profile and policy details, "
                "assign a risk score between 0 (no risk) and 100 (high risk).\n\n"
                "Customer:\n{profile}\n\nPolicy:\n{policy}\n\n"
                "Respond with only the numeric score as a number between 0 and 100."
            ),
        },
        {
            "prompt_name": "Policy Recommendations",
            "model": "gpt-4o",
            "temperature": 0.7,
            "prompt_template": (
                "You are an AI policy recommender.\n"
                "Customer profile:\n{customer_profile}\n\n"
                "Available policies:\n{market_data}\n\n"
                "Recommend the 3 best policies (by name) with a 1-sentence rationale each:"
            ),
        },
        {
            "prompt_name": "Claim Auto-Fill",
            "model": "gpt-4o",
            "temperature": 0.0,
            "prompt_template": (
                "Extract the following fields in JSON from this claim description:\n"
                "- claimant_name\n"
                "- date_of_event (YYYY-MM-DD)\n"
                "- incident_description\n\n"
                "Description:\n{claim_text}\n\nJSON:"
            ),
        },
        {
            "prompt_name": "Fraud Detection",
            "model": "gpt-4o",
            "temperature": 0.0,
            "prompt_template": (
                "You are an insurance fraud detector.\n"
                "Claim details:\n{claim_details}\n\n"
                'Answer in JSON {"fraud": bool, "reason": str}:'
            ),
        },
    ]

    for prompt_data in prompts:
        if not frappe.db.exists("AI Prompt", prompt_data["prompt_name"]):
            doc = frappe.get_doc({"doctype": "AI Prompt", **prompt_data})
            doc.insert(ignore_permissions=True)


def seed_roles():
    """Create custom roles if they don't exist."""
    roles = ["Insurance Manager", "Insurance User"]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            doc = frappe.get_doc(
                {
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1,
                    "is_custom": 1,
                }
            )
            doc.insert(ignore_permissions=True)
