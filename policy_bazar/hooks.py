from . import __version__ as app_version

app_name = "policy_bazar"
app_title = "Policy Bazar"
app_publisher = "Your Name"
app_description = "Insurance application with AI-based risk scoring"
app_icon = "octicon octicon-shield"
app_color = "blue"
app_email = "you@example.com"
app_license = "MIT"

# Include custom JS
app_include_js = "policy_bazar.js"

# Desk module configuration
desktop.py = "policy_bazar.config.desk"

# Notifications
notification_config = "policy_bazar.config.notification.get_notification_config"

# Workspace
workspace_name = "Insurance Dashboard"

# DocType JS - Client-side scripts per doctype
doctype_js = {
    "Insurance Policy": "public/js/insurance_policy.js",
}

# Scheduled Tasks (daily expiry reminders)
scheduler_events = {
    "daily": [
        "policy_bazar.policies.doctype.insurance_policy.insurance_policy.send_expiry_reminders",
    ],
}

# Override standard methods (optional - uncomment as needed)
# override_whitelisted_methods = {
#     "erpnext.selling.doctype.quotation.quotation.make_sales_order":
#         "policy_bazar.policies.doctype.insurance_policy.insurance_policy.make_sales_order"
# }

# Custom pages
page_js = {
    "policy-comparison": "public/js/policy_comparison.js",
}

# Website generators
# website_generators = []

# Jinja methods available in templates
# jinja = {}

# -----------------------------------------------------------------------
# Fixtures - auto-loaded on bench migrate
# -----------------------------------------------------------------------
fixtures = [
    {"dt": "AI Prompt", "filters": [["name", "in", ["Risk Scoring", "Policy Recommendations", "Claim Auto-Fill", "Fraud Detection"]]]},
    {"dt": "Role", "filters": [["role_name", "in", ["Insurance Manager", "Insurance User"]]]},
    {"dt": "Dashboard Chart", "filters": [["chart_name", "in", ["Average Risk by Insurer", "Monthly Fraud Rate"]]]},
    {"dt": "Number Card", "filters": [["name", "in", ["Active Policies", "Total Premium Written", "Pending Claims"]]]},
]

# -----------------------------------------------------------------------
# After install - runs once after app is installed
# -----------------------------------------------------------------------
after_install = "policy_bazar.setup.install.after_install"
