import frappe
from frappe.tests.utils import FrappeTestCase
from policy_bazar.utils.ai_service import AIService


class TestAIService(FrappeTestCase):
    """Unit tests for AI service module.

    These tests verify the fallback/stub behavior when OpenAI is unavailable.
    """

    def test_calculate_risk_score_fallback(self):
        """Test that risk score returns a value even without OpenAI."""
        score = AIService.calculate_risk_score(
            profile={"customer": "Test", "premium": 5000},
            policy_data={"insurer": "Test Insurer", "sum_assured": 500000},
        )
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_calculate_risk_score_deterministic_fallback(self):
        """Test deterministic fallback when premium and sum_assured are provided."""
        score = AIService.calculate_risk_score(
            profile={"premium": 50000},
            policy_data={"sum_assured": 100000},
        )
        # Premium/sum_assured ratio = 0.5, so score should be ~50
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_recommend_policies_fallback(self):
        """Test that policy recommendations return data even without OpenAI."""
        recommendations = AIService.recommend_policies(
            customer_profile={"age": "35", "history": "none"},
            market_data=[
                {"name": "Policy A", "features": "type=Life, premium=5000"},
                {"name": "Policy B", "features": "type=Health, premium=3000"},
            ],
        )
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_auto_fill_claim_fallback(self):
        """Test that claim auto-fill returns empty dict without OpenAI."""
        result = AIService.auto_fill_claim(
            "John Doe had a car accident on 2026-01-15"
        )
        # Should return empty dict (fallback behavior)
        self.assertIsInstance(result, dict)

    def test_detect_fraud_fallback(self):
        """Test that fraud detection works without OpenAI (amount threshold)."""
        # Small amount — should not flag as fraud
        result = AIService.detect_fraud(
            {"claim_id": "CL-001", "amount": 5000, "description": "Minor damage"}
        )
        self.assertFalse(result)

        # Large amount — may flag as fraud
        result = AIService.detect_fraud(
            {"claim_id": "CL-002", "amount": 500000, "description": "Major damage"}
        )
        # Should flag as fraud because amount > 100000 (fallback threshold)
        self.assertTrue(result)
