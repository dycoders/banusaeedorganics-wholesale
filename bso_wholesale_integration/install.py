from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


CUSTOM_FIELDS = {
    "Lead": [
        {
            "fieldname": "custom_bso_wholesale_section",
            "label": "Website Wholesale Inquiry",
            "fieldtype": "Section Break",
            "insert_after": "request_type",
            "collapsible": 1,
        },
        {
            "fieldname": "custom_bso_source_id",
            "label": "Website Inquiry ID",
            "fieldtype": "Data",
            "insert_after": "custom_bso_wholesale_section",
            "unique": 1,
            "read_only": 1,
            "in_standard_filter": 1,
        },
        {
            "fieldname": "custom_bso_products_interested_in",
            "label": "Products Interested In",
            "fieldtype": "Long Text",
            "insert_after": "custom_bso_source_id",
        },
        {
            "fieldname": "custom_bso_source_url",
            "label": "Website Source URL",
            "fieldtype": "Data",
            "options": "URL",
            "insert_after": "custom_bso_products_interested_in",
            "read_only": 1,
        },
        {
            "fieldname": "custom_bso_submitted_at",
            "label": "Website Submission Date",
            "fieldtype": "Datetime",
            "insert_after": "custom_bso_source_url",
            "read_only": 1,
        },
    ]
}


def _create_fields():
    create_custom_fields(CUSTOM_FIELDS, update=True)


def after_install():
    _create_fields()


def after_migrate():
    _create_fields()

