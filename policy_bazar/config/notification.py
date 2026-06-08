from frappe import _


def get_notification_config():
    return {
        "policy_bazar.policies.doctype.insurance_policy.insurance_policy.InsurancePolicy": {
            "statuses": {
                "Expiring Soon": _("Policy expiring within 30 days"),
                "Expired": _("Policy has expired"),
            },
            "get_context": "policy_bazar.policies.doctype.insurance_policy.insurance_policy.get_notification_context",
        }
    }
