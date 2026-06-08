import frappe
from frappe.model.document import Document
from policy_bazar.utils.ai_service import AIService


class PolicyClaim(Document):
    def before_save(self):
        """Auto-fill claim fields from free-text description using AI."""
        if self.claim_description and not self.claimant_name:
            data = AIService.auto_fill_claim(self.claim_description)
            if data:
                self.claimant_name = data.get("claimant_name") or self.claimant_name
                if not self.date_of_claim:
                    self.date_of_claim = data.get("date_of_event")
                self.incident_description = data.get("incident_description") or self.incident_description

    def on_submit(self):
        """Run fraud detection on claim submission."""
        fraud = AIService.detect_fraud(
            {
                "claim_id": self.name,
                "amount": self.claim_amount,
                "description": self.incident_description or self.claim_description,
            }
        )
        if fraud:
            self.db_set("fraud_flag", 1)
            self.db_set("status", "Rejected")
            frappe.throw(
                "Claim marked as potential fraud – please review manually. "
                "The claim status has been set to Rejected."
            )
