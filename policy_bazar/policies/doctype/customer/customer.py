import frappe
from frappe.model.document import Document


class Customer(Document):
    def validate(self):
        if self.email and not frappe.utils.validate_email_address(self.email):
            frappe.throw("Invalid Email Address")
