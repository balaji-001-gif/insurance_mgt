import frappe
from frappe.model.document import Document


class AIPrompt(Document):
    pass


def get_prompt(prompt_name: str):
    """Fetch an AI Prompt configuration by name.

    Args:
        prompt_name: The name of the prompt (as set in the doctype).

    Returns:
        AIPrompt document or None if not found.
    """
    prompts = frappe.get_all(
        "AI Prompt",
        filters={"prompt_name": prompt_name},
        limit=1,
    )
    if prompts:
        return frappe.get_doc("AI Prompt", prompts[0].name)
    return None
