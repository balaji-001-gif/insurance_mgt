import frappe
import frappe.utils
from frappe.tests.utils import FrappeTestCase


class TestInsurancePolicy(FrappeTestCase):
    """Unit tests for Insurance Policy doctype."""

    def setUp(self):
        """Set up test dependencies."""
        self.customer = frappe.get_doc(
            {
                "doctype": "Insurance Customer",
                "customer_id": "TEST-CUST-001",
                "customer_name": "Test Customer",
                "email": "test@example.com",
            }
        ).insert(ignore_permissions=True)

        self.insurer = frappe.get_doc(
            {
                "doctype": "Insurer",
                "insurer_code": "TEST-INS-001",
                "insurer_name": "Test Insurer",
            }
        ).insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test documents."""
        frappe.db.rollback()

    def test_policy_creation(self):
        """Test that a basic insurance policy can be created."""
        policy = frappe.get_doc(
            {
                "doctype": "Insurance Policy",
                "policy_number": "POL-TEST-001",
                "customer": self.customer.name,
                "insurer": self.insurer.name,
                "policy_type": "Life",
                "premium": 5000,
                "sum_assured": 500000,
                "policy_start": frappe.utils.today(),
                "policy_end": frappe.utils.add_days(frappe.utils.today(), 365),
            }
        ).insert(ignore_permissions=True)

        self.assertEqual(policy.policy_number, "POL-TEST-001")
        self.assertEqual(policy.policy_type, "Life")
        self.assertIsNotNone(policy.risk_score)
        self.assertGreaterEqual(policy.risk_score, 0)
        self.assertLessEqual(policy.risk_score, 100)

    def test_policy_date_validation(self):
        """Test that end date must be after start date."""
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(
                {
                    "doctype": "Insurance Policy",
                    "policy_number": "POL-TEST-INVALID",
                    "customer": self.customer.name,
                    "insurer": self.insurer.name,
                    "policy_type": "Health",
                    "premium": 3000,
                    "policy_start": "2026-06-15",
                    "policy_end": "2026-06-01",  # Before start date — should fail
                }
            ).insert(ignore_permissions=True)

    def test_customer_email_validation(self):
        """Test that customer validates email addresses."""
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(
                {
                    "doctype": "Insurance Customer",
                    "customer_id": "TEST-CUST-INVALID",
                    "customer_name": "Invalid Email",
                    "email": "not-an-email",
                }
            ).insert(ignore_permissions=True)

    def test_risk_score_caching(self):
        """Test that risk score is not recalculated if scored within 7 days."""
        policy = frappe.get_doc(
            {
                "doctype": "Insurance Policy",
                "policy_number": "POL-TEST-CACHE",
                "customer": self.customer.name,
                "insurer": self.insurer.name,
                "policy_type": "Vehicle",
                "premium": 10000,
                "sum_assured": 800000,
                "policy_start": frappe.utils.today(),
                "policy_end": frappe.utils.add_days(frappe.utils.today(), 365),
            }
        ).insert(ignore_permissions=True)

        first_score = policy.risk_score

        # Trigger validate again
        policy.validate()
        # Score should remain the same (cached)
        self.assertEqual(policy.risk_score, first_score)

    def test_get_notification_context(self):
        """Test notification context for policy status."""
        from policy_bazar.policies.doctype.insurance_policy.insurance_policy import (
            get_notification_context,
        )

        # Create a mock doc with an expired policy end date
        class MockDoc:
            policy_end = frappe.utils.add_days(frappe.utils.today(), -10)

        result = get_notification_context(MockDoc())
        self.assertEqual(result, ("Expired", 1))

        # Create a mock doc with a soon-to-expire policy
        class MockDoc2:
            policy_end = frappe.utils.add_days(frappe.utils.today(), 15)

        result2 = get_notification_context(MockDoc2())
        self.assertEqual(result2, ("Expiring Soon", 1))

        # Create a mock doc with a far-off policy end date
        class MockDoc3:
            policy_end = frappe.utils.add_days(frappe.utils.today(), 100)

        result3 = get_notification_context(MockDoc3())
        self.assertIsNone(result3)
