import frappe
from frappe.model.document import Document
from datetime import date, timedelta
from frappe.utils import now_datetime, add_days

from policy_bazar.utils.ai_service import AIService


class InsurancePolicy(Document):
    def validate(self):
        """Validate policy dates and calculate AI risk score."""
        self.validate_dates()
        self.calculate_risk_score()

    def validate_dates(self):
        """Ensure policy end date is after start date."""
        if self.policy_start and self.policy_end:
            if self.policy_end <= self.policy_start:
                frappe.throw("Policy End Date must be after Policy Start Date")

    def on_update(self):
        """Log AI score overrides to AI Feedback doctype."""
        if self.risk_score_overridden and not frappe.db.exists(
            {
                "doctype": "AI Feedback",
                "linked_doctype": "Insurance Policy",
                "linked_docname": self.name,
            }
        ):
            # Get original value if available
            old_score = self._doc_before_save.risk_score if self._doc_before_save else None
            frappe.get_doc(
                {
                    "doctype": "AI Feedback",
                    "linked_doctype": "Insurance Policy",
                    "linked_docname": self.name,
                    "old_score": old_score,
                    "new_score": self.risk_score,
                    "reason": self.override_reason,
                }
            ).insert()

    def calculate_risk_score(self):
        """
        Calculate risk score using AI service.
        Skips if overridden by user or scored within last 7 days.
        """
        # Skip if user has overridden the score
        if self.risk_score_overridden:
            return

        # Skip if scored in last 7 days (caching)
        if self.risk_score_last_updated and self.risk_score_last_updated > add_days(
            now_datetime(), -7
        ):
            return

        # Build profile and policy dicts for AI
        profile = {
            "customer": self.customer,
            "start": str(self.policy_start),
            "end": str(self.policy_end),
            "premium": self.premium,
        }
        policy_data = {
            "insurer": self.insurer,
            "type": self.policy_type or "General",
            "sum_assured": self.sum_assured or 0,
        }

        score = AIService.calculate_risk_score(profile, policy_data)
        if score is not None:
            self.risk_score = score
            self.risk_score_last_updated = now_datetime()

    @frappe.whitelist()
    def get_recommendations(self):
        """
        Get AI-powered policy recommendations for the customer.
        Called from client-side "Recommend Policies" button.
        """
        cust = frappe.get_doc("Customer", self.customer)

        # Build market data from other policies
        market = frappe.get_all(
            "Insurance Policy",
            filters={"name": ["!=", self.name]},
            fields=["name", "policy_type", "premium", "insurer"],
            limit_page_length=20,
        )
        market_data = [
            {
                "name": m.name,
                "features": f"type={m.policy_type}, premium={m.premium}, insurer={m.insurer}",
            }
            for m in market
        ]

        customer_profile = {
            "age": getattr(cust, "age", "unknown"),
            "history": getattr(cust, "medical_history", "none"),
        }

        return AIService.recommend_policies(customer_profile, market_data)

    @frappe.whitelist()
    def send_quote(self):
        """
        Generate and email a quote PDF for this policy.
        """
        customer = frappe.get_doc("Customer", self.customer)
        if not customer.email:
            frappe.throw("Customer has no email address")

        # Render HTML template
        html = frappe.render_template(
            "policy_bazar/templates/emails/quote_template.html",
            {"customer_name": customer.customer_name, "policy": self},
        )

        # Create PDF
        pdf = frappe.get_print("Insurance Policy", self.name, html=html)

        # Send Email
        frappe.sendmail(
            recipients=customer.email,
            subject=f"Your Insurance Quote ({self.name})",
            message=html,
            attachments=[{"fname": f"{self.name}.pdf", "fcontent": pdf}],
        )

        return "Quote sent successfully"

    @staticmethod
    @frappe.whitelist()
    def send_expiry_reminders():
        """
        Daily scheduled job: send reminder emails for policies expiring within 30 days.
        """
        today = date.today()
        cutoff = today + timedelta(days=30)
        expiring = frappe.get_all(
            "Insurance Policy",
            filters={"policy_end": ["between", [today, cutoff]]},
            fields=["name", "customer", "policy_end"],
        )
        for p in expiring:
            email = frappe.db.get_value("Customer", p.customer, "email")
            if email:
                frappe.sendmail(
                    recipients=email,
                    subject=f"Your policy {p.name} expiring on {p.policy_end}",
                    message=f"Dear {p.customer}, your policy {p.name} expires on {p.policy_end}. "
                    f"Please contact us for renewal.",
                )


def get_notification_context(doc):
    """Return notification context for policy status (Expired / Expiring Soon).

    Called by the Frappe notification framework with the document as argument.
    """
    if doc.policy_end < date.today():
        return ("Expired", 1)
    if doc.policy_end < date.today() + timedelta(days=30):
        return ("Expiring Soon", 1)
    return None
