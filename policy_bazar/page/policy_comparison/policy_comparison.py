import frappe


def get_context(context):
    context.title = "Policy Comparison"
    context.policies = frappe.get_all(
        "Insurance Policy",
        fields=["name", "insurer", "policy_type", "premium", "risk_score", "policy_start", "policy_end"],
    )
    return context
