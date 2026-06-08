import frappe
import frappe.utils
from frappe.tests.utils import FrappeTestCase


class TestPolicyClaim(FrappeTestCase):
    """Unit tests for Policy Claim doctype."""

    def setUp(self):
        """Set up test dependencies."""
        self.customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_id": "TEST-CL-CUST-001",
                "customer_name": "Claim Test Customer",
                "email": "claimtest@example.com",
            }
        ).insert(ignore_permissions=True)

        self.insurer = frappe.get_doc(
            {
                "doctype": "Insurer",
                "insurer_code": "TEST-CL-INS-001",
                "insurer_name": "Claim Test Insurer",
            }
        ).insert(ignore_permissions=True)

        self.policy = frappe.get_doc(
            {
                "doctype": "Insurance Policy",
                "policy_number": "POL-CL-TEST-001",
                "customer": self.customer.name,
                "insurer": self.insurer.name,
                "policy_type": "Health",
                "premium": 5000,
                "sum_assured": 500000,
                "policy_start": frappe.utils.today(),
                "policy_end": frappe.utils.add_days(frappe.utils.today(), 365),
            }
        ).insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test documents."""
        frappe.db.rollback()

    def test_claim_creation(self):
        """Test that a basic claim can be created."""
        claim = frappe.get_doc(
            {
                "doctype": "Policy Claim",
                "claim_id": "CL-TEST-001",
                "policy": self.policy.name,
                "claimant_name": "John Doe",
                "date_of_claim": frappe.utils.today(),
                "claim_amount": 25000,
                "status": "Draft",
            }
        ).insert(ignore_permissions=True)

        self.assertEqual(claim.claim_id, "CL-TEST-001")
        self.assertEqual(claim.claim_amount, 25000)
        self.assertEqual(claim.status, "Draft")

    def test_claim_default_status(self):
        """Test that new claims get Draft status."""
        claim = frappe.get_doc(
            {
                "doctype": "Policy Claim",
                "claim_id": "CL-TEST-002",
                "policy": self.policy.name,
                "claimant_name": "Jane Doe",
                "date_of_claim": frappe.utils.today(),
                "claim_amount": 15000,
            }
        ).insert(ignore_permissions=True)

        self.assertEqual(claim.status, "Draft")
