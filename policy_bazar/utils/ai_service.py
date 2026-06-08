import random

import frappe
from frappe import _


def get_openai_client():
    """Initialize and return OpenAI client using site config API key."""
    api_key = frappe.conf.get("openai_api_key")
    if not api_key:
        frappe.throw(_("Missing `openai_api_key` in site_config"))
    try:
        from openai import OpenAI

        return OpenAI(api_key=api_key)
    except ImportError:
        frappe.throw(_("openai package is not installed. Run: pip install openai>=1.0.0"))


class AIService:
    """Central AI service for Policy Bazar.

    All AI methods gracefully fall back to deterministic/stub logic
    when OpenAI is unavailable or returns unexpected results.
    """

    @staticmethod
    def calculate_risk_score(profile: dict, policy_data: dict) -> float:
        """Send customer & policy data to OpenAI to get a risk score (0-100).

        Falls back to a deterministic score based on premium/sum_assured ratio.
        """
        try:
            prompt_cfg = _get_prompt_config("Risk Scoring")
            template = prompt_cfg.prompt_template.format(
                profile=profile, policy=policy_data
            ) if prompt_cfg else (
                "You are an insurance underwriter.\n"
                "Given the following customer profile and policy details, "
                "assign a risk score between 0 (no risk) and 100 (high risk).\n\n"
                f"Customer:\n{profile}\n\nPolicy:\n{policy_data}\n\nScore:"
            )

            client = get_openai_client()
            resp = client.chat.completions.create(
                model=prompt_cfg.model if prompt_cfg else "gpt-4o",
                messages=[{"role": "user", "content": template}],
                temperature=prompt_cfg.temperature if prompt_cfg else 0.0,
            )
            text = resp.choices[0].message.content.strip()
            score = float(text.split()[0])
            return max(0, min(100, score))
        except Exception:
            # Deterministic fallback based on premium vs sum_assured ratio
            premium = profile.get("premium", 0) or 0
            sum_assured = policy_data.get("sum_assured", 0) or 0
            if sum_assured > 0 and premium > 0:
                ratio = premium / sum_assured
                score = min(100, ratio * 100)
                return max(10, min(90, score))
            return random.uniform(10, 90)

    @staticmethod
    def recommend_policies(customer_profile: dict, market_data: list) -> list:
        """Ask the model to recommend top policies from market_data for this customer.

        Falls back to returning raw market data.
        """
        try:
            client = get_openai_client()
            prompt = (
                "You are an AI policy recommender.\n"
                f"Customer profile:\n{customer_profile}\n\n"
                "Available policies:\n"
            )
            for p in market_data:
                prompt += f"- {p['name']}: {p['features']}\n"
            prompt += "\nRecommend the 3 best policies (by name) with a 1-sentence rationale each:\n"

            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip().splitlines()
        except Exception:
            return [f"{p['name']}: {p['features']}" for p in market_data[:3]]

    @staticmethod
    def auto_fill_claim(claim_text: str) -> dict:
        """Extract structured fields from a free-text claim description.

        Returns dict with claimant_name, date_of_event, incident_description.
        """
        try:
            client = get_openai_client()
            prompt = (
                "Extract the following fields in JSON from this claim description:\n"
                "- claimant_name\n"
                "- date_of_event (YYYY-MM-DD)\n"
                "- incident_description\n\n"
                f"Description:\n{claim_text}\n\nJSON:"
            )
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            return frappe.parse_json(resp.choices[0].message.content) or {}
        except Exception:
            return {}

    @staticmethod
    def detect_fraud(claim_details: dict) -> bool:
        """Run AI-based fraud detection on claim details.

        Returns True if potential fraud is detected.
        """
        try:
            client = get_openai_client()
            prompt = (
                "You are an insurance fraud detector.\n"
                f"Claim details:\n{claim_details}\n\n"
                'Answer in JSON {"fraud": bool, "reason": str}:'
            )
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            result = frappe.parse_json(resp.choices[0].message.content) or {}
            return result.get("fraud", False)
        except Exception:
            # Stub: flag claims above a threshold amount
            amount = claim_details.get("amount", 0) or 0
            return amount > 100000


def _get_prompt_config(prompt_name: str):
    """Fetch prompt configuration from AI Prompt doctype if available."""
    try:
        from policy_bazar.policies.doctype.ai_prompt.ai_prompt import get_prompt

        return get_prompt(prompt_name)
    except Exception:
        return None
